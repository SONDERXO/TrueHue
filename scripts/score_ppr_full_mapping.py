"""Score sealed PPR outputs with the existing metrics environment; no torch or fitting."""
from pathlib import Path
import sys
import json
import hashlib
import math
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.evaluation.directional_recoverability import metrics, regions

OUT = ROOT / 'outputs/ppr_full_pipeline_prediction_v1'
WB = ROOT / 'outputs/wb_feature_direct_prediction_v1'
ROLES = ['identity', 'colour_only', 'exposure_under', 'exposure_over', 'combined_under', 'combined_over']


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a, b):
    assert abs(a - b) <= 1e-10 * max(1, abs(a), abs(b)), (a, b)


def main():
    if (OUT / 'scoring_started.json').exists():
        raise FileExistsError('Existing scoring attempt')
    seal = read(OUT / 'predictions_sealed.json')
    assert seal['passed'] and seal['cases'] == len(seal['records']) == 66 and seal['no_reference_access']
    assert sha(OUT / 'bindings.json') == seal['bindings_sha256']
    for path, digest in read(OUT / 'bindings.json').items():
        assert sha(ROOT / path) == digest
    for r in seal['records']:
        assert sha(OUT / 'predictions' / (r['case_id'] + '.npz')) == r['npz_sha256']
    parents = {r['case_id']: r for r in read(WB / 'records.json')}
    write(OUT / 'scoring_started.json', dict(seal_sha256=sha(OUT / 'predictions_sealed.json'),
          script_sha256=sha(Path(__file__)), python=sys.executable, numpy=np.__version__, reference_access_after_seal=True))
    records = []
    try:
        for r in seal['records']:
            with np.load(WB / 'evaluation' / (r['case_id'] + '.npz'), allow_pickle=False) as pack:
                image, reference, alpha, protected, wb, constant = [pack[k] for k in ['input', 'reference', 'alpha', 'protected', '314', 'constant']]
            with np.load(OUT / 'predictions' / (r['case_id'] + '.npz'), allow_pickle=False) as pack:
                candidate = pack['candidate']
                native_rgb = pack['native_rgb']
            assert hashlib.sha256(candidate.tobytes()).hexdigest() == r['candidate_RGB8_sha256']
            independent = np.empty_like(candidate)
            for iy, ix, channel in np.ndindex(candidate.shape):
                a = float(alpha[iy, ix])
                independent[iy, ix, channel] = round((1 - a) * int(image[iy, ix, channel]) + a * int(native_rgb[iy, ix, channel]))
            assert np.array_equal(candidate, independent)
            assert np.array_equal(candidate[protected], image[protected])
            assert np.array_equal(candidate[alpha == 0], image[alpha == 0])
            outputs = dict(input=image, constant=constant, saved314=wb, ppr=candidate)
            masks = regions(alpha)
            scored = {name: {label: metrics(value, reference, mask) for label, value in outputs.items()}
                      for name, mask in masks.items()}
            reference_lab = rgb2lab(reference / 255.)
            for label, value in outputs.items():
                rgb = np.abs(value.astype(float) - reference)
                de = deltaE_ciede2000(rgb2lab(value / 255.), reference_lab)
                for name, mask in masks.items():
                    n = int(mask.sum())
                    if not n:
                        assert scored[name][label] is None
                        continue
                    close(scored[name][label]['RGB'], math.fsum(float(v) for v in rgb[mask].flat) / (3 * n))
                    close(scored[name][label]['DE'], math.fsum(float(v) for v in de[mask]) / n)
                    if label != 'ppr':
                        parent_label = '314' if label == 'saved314' else label
                        for metric in ['RGB', 'DE']:
                            close(scored[name][label][metric], parents[r['case_id']]['regions'][name][parent_label][metric])
            records.append({k: r[k] for k in ['case_id', 'source_id', 'role', 'changed_pixels',
                           'raw_min', 'raw_max', 'below_zero_channels', 'above_one_channels']} | dict(regions=scored))
            if len(records) % 11 == 0:
                print('PPR scalar composite/metrics verified ' + str(len(records)) + '/66', flush=True)
        means = {role: {label: {metric: math.fsum(r['regions']['primary'][label][metric]
                 for r in records if r['role'] == role) / 11 for metric in ['RGB', 'DE']}
                 for label in ['input', 'constant', 'saved314', 'ppr']} for role in ROLES}
        gates = {role: all(means[role]['ppr'][m] < means[role][b][m] - 1e-10
                 for m in ['RGB', 'DE'] for b in ['input', 'constant']) for role in ROLES[1:]}
        under = all(means['exposure_under']['ppr'][m] < means['exposure_under']['saved314'][m] - 1e-10 for m in ['RGB', 'DE'])
        colour = all(means['colour_only']['ppr'][m] <= means['colour_only']['saved314'][m] + 1e-10 for m in ['RGB', 'DE'])
        passed = all(gates.values()) and under and colour
        summary = dict(by_role=means, role_gates=gates, under_improvement=under, colour_nonworse=colour,
              numerical_eligible=passed, model_ready=False, identity_changed=sum(r['role'] == 'identity'
              and r['changed_pixels'] > 0 for r in records), nonidentity_harms=[r['case_id'] for r in records
              if r['role'] != 'identity' and any(r['regions']['primary']['ppr'][m] >
              r['regions']['primary']['input'][m] + 1e-10 for m in ['RGB', 'DE'])],
              parameter_MAE='NOT_APPLICABLE_TO_LUT_MIXING_COEFFICIENTS',
              decision='NUMERICAL_PASS_PRESERVATION_USEFULNESS_PENDING' if passed else 'FAILED_CLOSED_NO_REVIEW_OR_TUNING')
        write(OUT / 'records.json', records)
        write(OUT / 'summary.json', summary)
        for path, digest in read(OUT / 'bindings.json').items():
            assert sha(ROOT / path) == digest
        for r in seal['records']:
            assert sha(OUT / 'predictions' / (r['case_id'] + '.npz')) == r['npz_sha256']
        write(OUT / 'verification.json', dict(passed=True, actual_mappings=66, new_training=0,
              new_CNN_calls=0, composites_independently_replayed=66, metric_checks=66,
              outputs_sealed_before_references=True, numerical_eligible=passed, model_ready=False,
              artifacts={p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob('*') if p.is_file()}))
        print('COMPLETE PPR full mapping; numerical_eligible=' + str(passed), flush=True)
    except Exception as error:
        write(OUT / 'scoring_failure.json', dict(error=repr(error), completed=len(records), further_attempts_allowed=False))
        raise


if __name__ == '__main__':
    main()
