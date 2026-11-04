"""Compare preserved application policies; freeze measurements and fold predictions.

Rejected sources are mask-only diagnostics, never evaluation admissions.
"""
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.square_measurement import contract
from src.data_preparation.controlled_training_table import FEATURES, FEATURE_KEYS
from src.skin_masking.material_checked_support import material_checked_support
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter, hair_veto_support
from src.skin_masking.additions_boundary_experiment import restrict_new_support
from src.evaluation.correction_prototype import apply_correction, image_errors

OUT = ROOT / 'outputs/table2_application_mask_comparison_v1'
PARENT = ROOT / 'outputs/table2_reviewed_expansion_evaluation_v1'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2), encoding='utf-8')


def save(path, image):
    if not cv2.imwrite(str(path), image):
        raise OSError(path)


def tile(image, label, mask=None):
    image = image.copy()
    if mask is not None:
        image[mask] = np.rint(.55 * image[mask] + .45 * np.array([0, 220, 0])).astype(np.uint8)
    image = cv2.copyMakeBorder(image, 28, 0, 0, 0, cv2.BORDER_CONSTANT)
    cv2.putText(image, label, (3, 18), cv2.FONT_HERSHEY_SIMPLEX, .35, (255, 255, 255), 1)
    return image


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    config = get_config()
    prepare = importlib.import_module('11_prepare_training_manifests')
    ycb = importlib.import_module('56_compare_ycrcb_estimation')
    veto = importlib.import_module('83_compare_non_skin_veto').veto
    plan = read(PARENT / 'fit_plan.json')
    previous = read(PARENT / 'summary.json')
    predictions = {r['pair_id']: r for r in previous['records']}
    rows = [dict(r, diagnostic_only=False) for r in plan['rows']]
    # All four rejected scenes, on exactly the reviewed identity/severity images.
    for item in plan['excluded']:
        name, variant = item['pair_id'].split('__')
        folder = ROOT / ('outputs/table2_known_source_feasibility_v1' if name == '51739'
                         else 'outputs/table2_stress_expansion_v1')
        severity = variant.removeprefix('table2_')
        stem = name + ('_reference' if variant == 'identity' else
                       '_' + severity if name == '51739' else '')
        image = folder / (stem + '.png' if variant == 'identity' else stem + '_input.png')
        mask = folder / (stem + '_mask.png' if variant == 'identity' or name == '51739' else name + '_input_mask.png')
        rows.append(dict(pair_id=item['pair_id'], variant=variant, diagnostic_only=True,
                         rejection_reason=item['reason'], input_path=str(image.relative_to(ROOT)),
                         input_mask_path=str(mask.relative_to(ROOT)),
                         reference_path=str((folder / (name + '_reference.png')).relative_to(ROOT)),
                         reference_mask_path=str((folder / (name + '_reference_mask.png')).relative_to(ROOT))))
    assert len(rows) == 24 and len(predictions) == 16
    _, identity = contract(ROOT)
    assert identity == plan['rows'][0]['measurement_contract_sha256']
    model = ROOT / config.SELFIE_SEGMENTER_MODEL_PATH
    assert digest(model) == read(model.with_suffix('.provenance.json'))['sha256']
    paths = [PARENT / 'fit_plan.json', PARENT / 'summary.json', PARENT / 'verification.json',
             PARENT / 'user_review.json', ROOT / 'outputs/table2_stress_evaluation_v2/user_review.json',
             ROOT / 'outputs/mst_monotone_square256_v1/development_lookup.json',
             Path(__file__), model, ROOT / config.FACE_MODEL_PATH, ROOT / config.FACE_LANDMARKER_MODEL_PATH]
    paths += list((ROOT / 'src/skin_masking').glob('*.py'))
    paths += [ROOT / 'scripts' / p for p in ['11_prepare_training_manifests.py', '56_compare_ycrcb_estimation.py', '83_compare_non_skin_veto.py']]
    paths += list(PARENT.glob('fold_*/*'))
    for row in rows:
        paths += [ROOT / row[k] for k in ['input_path', 'input_mask_path', 'reference_path', 'reference_mask_path']]
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    OUT.mkdir(); (OUT / 'images').mkdir(); (OUT / 'boards').mkdir()
    write(OUT / 'run_status.json', dict(status='running'))
    write(OUT / 'policy.json', dict(
        scope='Application-only diagnostic; no fitting, adoption, measurement edits or new labels',
        measurement_contract_sha256=identity,
        methods=dict(current='Saved HSV AND YCrCb measurement mask used for application',
                     legacy_broad='Script59: material/hair support of HSV and YCrCb seeds; additions-only boundary',
                     legacy_non_skin='Script85 correction branch: legacy_broad intersect predicted body/face skin'),
        predictions='Existing held-source five-feature parameters reused verbatim; no oracle substitution',
        denominator='Same saved photographic reference and reference mask for every method',
        rejected='All four rejected sources mask-only; no predictions, fitting or aggregate admission',
        failures='No geometry/invalid-YCrCb fallback; unavailable candidates reported',
        caveat='Mask coverage/agreement and semantic categories are not annotated segmentation accuracy. Neck not evaluated.'))
    segmenter = SelfieMaterialSegmenter(model)
    records = []
    try:
        for row in rows:
            pair = row['pair_id']; image = cv2.imread(str(ROOT / row['input_path']))
            baseline = cv2.imread(str(ROOT / row['input_mask_path']), 0) > 0
            scoring = cv2.imread(str(ROOT / row['reference_mask_path']), 0) > 0
            reference = cv2.imread(str(ROOT / row['reference_path']))
            boxes = prepare._detect_face_boxes(image, ROOT / config.FACE_MODEL_PATH, .85)
            assert len(boxes) == 1
            x, y, w, h = boxes[0]; crop = image[y:y+h, x:x+w]
            result = prepare.compute_versioned_skin_mask(crop, image, boxes[0], ROOT / config.FACE_LANDMARKER_MODEL_PATH, 'v2_complete_mouth_v1')
            assert result.landmarks_available
            replay = np.zeros_like(baseline); replay[y:y+h, x:x+w] = result.mask > 0
            np.testing.assert_array_equal(replay, baseline)
            stats = compute_masked_lab_statistics(image, result_mask := baseline.astype(np.uint8)*255, 1000)
            assert stats['valid']
            if not row['diagnostic_only']:
                np.testing.assert_allclose([stats[k] for k in FEATURE_KEYS], [row[k] for k in FEATURES], atol=1e-5, rtol=0)
            exclude = result.exclusion_mask > 0
            proposal = ycb.ycrcb_mask(crop, exclude)
            proposal_stats = compute_masked_lab_statistics(crop, proposal.astype(np.uint8)*255, 1000)
            cats = segmenter.categories_bgr(image)
            save(OUT / 'images' / (pair + '_categories.png'), cats)
            excluded = np.zeros_like(baseline); excluded[y:y+h, x:x+w] = exclude
            save(OUT / 'images' / (pair + '_exclusions.png'), excluded.astype(np.uint8)*255)
            masks = {'current': baseline}; failure = None; geometry = None
            try:
                if not proposal_stats['valid']:
                    raise ValueError(proposal_stats['reason'])
                supports = []
                for seed in [result.mask > 0, proposal]:
                    full = np.zeros_like(baseline)
                    full[y:y+h, x:x+w] = material_checked_support(crop, seed, exclude)
                    supports.append(hair_veto_support(cats, full))
                landmarks, _, _ = prepare.detect_landmarks_with_margin(image, boxes[0], ROOT / config.FACE_LANDMARKER_MODEL_PATH)
                if landmarks is None:
                    raise ValueError('Boundary landmarks unavailable')
                bounded, geometry = restrict_new_support(supports[0][y:y+h, x:x+w], supports[1][y:y+h, x:x+w], landmarks)
                broad = np.zeros_like(baseline); broad[y:y+h, x:x+w] = bounded
                masks.update(legacy_broad=broad, legacy_non_skin=veto(broad, cats))
            except ValueError as error:
                failure = str(error)
            record = dict(pair_id=pair, variant=row['variant'], diagnostic_only=row['diagnostic_only'],
                          rejection_reason=row.get('rejection_reason'), input_path=row['input_path'],
                          reference_path=row['reference_path'], reference_mask_path=row['reference_mask_path'],
                          input_mask_path=row['input_mask_path'], features={k: stats[v] for k, v in zip(FEATURES, FEATURE_KEYS)},
                          boundary=geometry, candidate_failure=failure, masks={}, metrics={})
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB); ref_rgb = cv2.cvtColor(reference, cv2.COLOR_BGR2RGB)
            panels = [tile(image, 'Input: ' + row['variant'])]
            corrected_panels = [tile(reference, 'Photographic reference'), tile(image, 'No correction')]
            if not row['diagnostic_only']:
                record['parameters'] = predictions[pair]['parameters']
                record['metrics']['no_correction'] = image_errors(ref_rgb, rgb, scoring)
            for method, mask in masks.items():
                assert not np.any(mask & excluded)
                save(OUT / 'images' / (pair + '_' + method + '_mask.png'), mask.astype(np.uint8)*255)
                record['masks'][method] = dict(pixels=int(mask.sum()), added=int((mask & ~baseline).sum()),
                    removed=int((baseline & ~mask).sum()), reference_support_retained=float((mask & scoring).sum()/scoring.sum()),
                    outside_reference_support=int((mask & ~scoring).sum()), predicted_hair_selected=int((mask & (cats == 1)).sum()))
                panels.append(tile(image, method, mask))
                if row['diagnostic_only']:
                    continue
                corrected = apply_correction(rgb, mask, record['parameters'])
                save(OUT / 'images' / (pair + '_' + method + '_corrected.png'), cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR))
                record['metrics'][method] = image_errors(ref_rgb, corrected, scoring)
                corrected_panels.append(tile(cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR), method))
                if method == 'current':
                    assert record['metrics'][method] == predictions[pair]['learned']
                    assert digest(OUT/'images'/(pair+'_current_corrected.png')) == predictions[pair]['output_sha256']
            save(OUT / 'boards' / (pair + '_masks.png'), np.hstack(panels))
            if not row['diagnostic_only']:
                save(OUT / 'boards' / (pair + '_outputs.png'), np.hstack(corrected_panels))
            records.append(record)
            print(pair, failure or 'available', flush=True)
        accepted = [r for r in records if not r['diagnostic_only']]
        aggregate = {}
        for group, subset in [('all', accepted), ('identity', [r for r in accepted if r['variant']=='identity']),
                              ('distorted', [r for r in accepted if r['variant']!='identity'])]:
            aggregate[group] = {}
            for method in ['no_correction', 'current', 'legacy_broad', 'legacy_non_skin']:
                available = [r for r in subset if method in r['metrics']]
                aggregate[group][method] = dict(pairs=len(available), ciede2000=float(np.mean([r['metrics'][method]['ciede2000_source_mask'] for r in available])) if available else None)
        assert hashes == {p: digest(ROOT / p) for p in hashes}
        write(OUT / 'summary.json', dict(status='complete', records=records, aggregate=aggregate, input_sha256=hashes,
            measurement_contract_sha256=identity, runtime_replaced=False, refitted=False))
        sections = []
        for r in records:
            pair = r['pair_id']
            badge = 'REJECTED: mask diagnostic only; ' + r['rejection_reason'] if r['diagnostic_only'] else 'Accepted source; changed application masks await review'
            sections.append(f'<section><h2>{pair}</h2><p>{badge}</p><img src="boards/{pair}_masks.png">' +
                            ('' if r['diagnostic_only'] else f'<img src="boards/{pair}_outputs.png">') + '</section>')
        (OUT / 'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Table 2 application masks</title><style>body{font:16px sans-serif;background:#17191e;color:#eee;margin:24px}img{max-width:100%;display:block;margin:10px 0}section{border-top:1px solid #777;padding:12px 0}</style><h1>Frozen prediction: application-mask comparison</h1><p>Green is selected support, not a correctness label. Same input, measurements and parameters. Broader masks cannot repair wrong parameters. Rejected scenes remain excluded. Methods: current / legacy_broad / legacy_non_skin.</p>' + ''.join(sections), encoding='utf-8')
        (OUT / 'review-index.md').write_text('# Application-mask diagnostic\n\n[Open all comparisons](review.html)\n\nFrozen features and predictions; no model adoption. Four rejected sources are mask-only diagnostics.\n', encoding='utf-8')
        write(OUT / 'run_status.json', dict(status='complete'))
        print(json.dumps(aggregate, indent=2))
    except Exception as error:
        write(OUT / 'run_status.json', dict(status='failed', error=str(error), completed=len(records)))
        raise
    finally:
        segmenter.close()


if __name__ == '__main__':
    main()
