"""Freeze input-only brightness features and audit existing31 inputs; no fitting."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.data_preparation.controlled_training_table import FEATURES, FEATURE_KEYS
from src.ita_estimation.compute_ita import compute_masked_lab_statistics, opencv_lab_to_cielab
from src.utilities.config import get_config

ADDITIONS = ('input_l_p10', 'input_l_median', 'input_l_p90', 'input_l_iqr',
             'input_l_left_minus_right', 'input_l_top_minus_bottom')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def brightness_features(image_bgr, mask, bounds=None):
    """Only input pixels and the existing estimation mask; no references/targets."""
    if image_bgr.dtype != np.uint8 or image_bgr.shape[:2] != mask.shape or mask.dtype != bool:
        raise ValueError('Expected uint8 BGR and matching boolean mask')
    yy, xx = np.nonzero(mask)
    if len(xx) < 1000:
        return dict(valid=False, reason='fewer_than_1000_mask_pixels', skin_pixels=len(xx))
    if bounds is None:
        bounds = [int(xx.min()), int(yy.min()), int(xx.max())+1, int(yy.max())+1]
    x0, y0, x1, y1 = bounds
    # Integer pixel centers are split at the midpoint of occupied pixel centers.
    xm, ym = (x0+x1-1)/2, (y0+y1-1)/2
    lightness = opencv_lab_to_cielab(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB))[:, :, 0]
    pixels = lightness[mask]
    groups = {'left': pixels[xx <= xm], 'right': pixels[xx > xm],
              'top': pixels[yy <= ym], 'bottom': pixels[yy > ym]}
    counts = {k: len(v) for k, v in groups.items()}
    if min(counts.values()) < 100:
        return dict(valid=False, reason='fewer_than_100_pixels_in_half', skin_pixels=len(xx), region_pixels=counts, bounds=bounds)
    p10, p25, p50, p75, p90 = np.percentile(pixels, [10,25,50,75,90], method='linear')
    values = [p10, p50, p90, p75-p25, float(groups['left'].mean())-float(groups['right'].mean()),
              float(groups['top'].mean())-float(groups['bottom'].mean())]
    assert np.isfinite(values).all()
    return dict(valid=True, reason='available', skin_pixels=len(xx), region_pixels=counts, bounds=bounds,
                features={k: float(v) for k,v in zip(ADDITIONS, values)})


def main():
    output = ROOT/'outputs/brightness_feature_audit_v1'
    if output.exists():
        raise FileExistsError(output)
    table = ROOT/'data/manifests/controlled_expansion31_v1/staged_train.csv'
    with table.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 31
    output.mkdir()
    schema = dict(version='brightness_feature_audit_v1', status='Frozen before measurement; no model fitting or outcome-based feature selection',
        baseline_features=list(FEATURES), proposed_features=list(FEATURES)+list(ADDITIONS),
        definition='OpenCV uint8 BGR to Lab, shared conventional L* conversion. Linear percentiles10/50/90, IQR75-25, mean left-right and top-bottom.',
        regions='Halves of occupied estimation-mask bounding box using pixel-center midpoints; image-relative, not anatomical or pose-normalized.',
        minimum_mask_pixels=1000, minimum_half_pixels=100,
        missing_policy='Mark unavailable; no imputation, silent fallback, reference substitution or cohort removal.',
        sensitivity='Remove one mask-boundary pixel with3x3 erosion, constant-zero border. Compare frozen original half boundaries as well as recomputed bounds. Diagnostic, not validated stability test.',
        exclusion='No reference image, target, source identity, distortion label, correction support or MST category used in feature calculation.',
        next_comparison='If available, fixed depth3/seed42/leaf1 eight-source folds: baseline4 versus proposed10, same31 probes/support/targets; no feature/depth search or automatic runtime promotion.')
    schema_path = output/'feature_schema.json'
    schema_path.write_text(json.dumps(schema, indent=2), encoding='utf-8')
    tracked = [Path(__file__), table, schema_path, ROOT/get_config().CORRECTION_PROTOTYPE_MODEL_PATH,
               ROOT/'src/ita_estimation/compute_ita.py']
    paths = {}
    for row in rows:
        image = ROOT/row['input_path']
        if row['pair_id'] in {r['pair_id'] for r in rows[:22]}:
            mask = ROOT/'outputs/ycrcb_estimation_ablation_v1'/(row['pair_id']+'_baseline_estimate.png')
        else:
            mask = image.with_name(image.name.replace('_input.png', '_baseline_estimate.png'))
        paths[row['pair_id']] = image, mask
        tracked += [image, mask]
    hashes = {str(p): digest(p) for p in tracked}
    records, feature_rows = [], []
    for row in rows:
        image_path, mask_path = paths[row['pair_id']]
        image = cv2.imread(str(image_path)); mask = cv2.imread(str(mask_path), 0)>0
        original = brightness_features(image, mask)
        assert original == brightness_features(image.copy(), mask.copy())
        stats = compute_masked_lab_statistics(image, mask.astype(np.uint8)*255, 1000)
        np.testing.assert_array_equal([stats[k] for k in FEATURE_KEYS], [float(row[k]) for k in FEATURES])
        eroded = cv2.erode(mask.astype(np.uint8), np.ones((3,3), np.uint8), borderType=cv2.BORDER_CONSTANT, borderValue=0)>0
        fixed = brightness_features(image, eroded, original.get('bounds'))
        moved = brightness_features(image, eroded)
        record = dict(pair_id=row['pair_id'], input_path=row['input_path'], estimation_mask_path=mask_path.relative_to(ROOT).as_posix(),
            original=original, eroded_fixed_bounds=fixed, eroded_recomputed_bounds=moved,
            retained_mask_fraction=float(eroded.sum()/mask.sum()),
            fixed_bounds_absolute_change={k: abs(fixed['features'][k]-original['features'][k]) for k in ADDITIONS} if original['valid'] and fixed['valid'] else None)
        records.append(record)
        feature_rows.append(dict(pair_id=row['pair_id'], available=original['valid'],
            **{k:row[k] for k in FEATURES}, **original.get('features', dict.fromkeys(ADDITIONS,''))))
    assert hashes == {p:digest(p) for p in hashes}
    changes = [r['fixed_bounds_absolute_change'] for r in records if r['fixed_bounds_absolute_change'] is not None]
    summary = dict(status='complete_no_fitting', pairs=31, original_available=sum(r['original']['valid'] for r in records),
        eroded_available=sum(r['eroded_fixed_bounds']['valid'] for r in records),
        minimum_half_pixels=min(min(r['original']['region_pixels'].values()) for r in records if r['original']['valid']),
        mask_retained_fraction_range=[min(r['retained_mask_fraction'] for r in records), max(r['retained_mask_fraction'] for r in records)],
        sensitivity={k:dict(median_absolute_change=float(np.median([r[k] for r in changes])), max_absolute_change=max(r[k] for r in changes)) for k in ADDITIONS},
        records=records, input_sha256=hashes,
        limitations='No validated stability cutoff. Erosion is a local mask-sensitivity probe, not lighting/pose robustness. Fixed masks may already be biased; no correction-performance claim. Neck and MST unimplemented.')
    (output/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    with (output/'input_features.csv').open('x', encoding='utf-8', newline='') as stream:
        writer=csv.DictWriter(stream, list(feature_rows[0])); writer.writeheader(); writer.writerows(feature_rows)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['records','input_sha256']}, indent=2))


if __name__ == '__main__':
    main()
