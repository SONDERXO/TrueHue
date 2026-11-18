"""Independent stdlib weighted PAVA replay; no sklearn fitting or image access."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
from bisect import bisect_right
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/refined_mst_assessment_v1'
DESIGN = ROOT / 'outputs/refined_mst_grouped_design_v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))


def reconstruct(training, weights):
    tied = defaultdict(lambda: [0.0, 0.0])
    for row in training:
        x = row['features']['input_ita_degrees']
        w = weights[row['case_id']]
        tied[x][0] += w
        tied[x][1] += w * float(Decimal(row['source_mst_exact_decimal']))
    xs = sorted(tied)
    blocks = []
    for index, x in enumerate(xs):
        weight, total = tied[x]
        blocks.append([index, index, weight, total])
        while len(blocks) >= 2 and blocks[-2][3]/blocks[-2][2] < blocks[-1][3]/blocks[-1][2]:
            right = blocks.pop()
            left = blocks.pop()
            blocks.append([left[0], right[1], left[2]+right[2], left[3]+right[3]])
    ys = [0.0] * len(xs)
    for start, end, weight, total in blocks:
        for i in range(start, end+1):
            ys[i] = total/weight
    return xs, ys


def interpolate(xs, ys, value):
    if value <= xs[0]:
        return ys[0]
    if value >= xs[-1]:
        return ys[-1]
    i = bisect_right(xs, value)-1
    return ys[i] + (ys[i+1]-ys[i])*(value-xs[i])/(xs[i+1]-xs[i])


def main():
    dest = OUT / 'verification_PRIVATE.json'
    if dest.exists():
        raise FileExistsError('Preserve earlier verification')
    plan = read(OUT / 'execution_plan_PRIVATE.json')
    assert all(sha(p) == h for p, h in plan['input_sha256'].items())
    result = read(OUT / 'results_PRIVATE.json')
    rows = read(DESIGN / 'rows_PRIVATE.json')
    design = read(DESIGN / 'folds_PRIVATE.json')
    by_case = {r['case_id']: r for r in rows}
    predictions = {r['case_id']: r for r in result['predictions']}
    assert len(predictions) == len(result['predictions']) == len(rows) == 30
    assert len(result['folds']) == result['calibration_fits'] == 10
    assert result['correction_tree_fits'] == 0 and result['all_data_fit'] is False
    assert not any(result[k] for k in ['calibration_admitted', 'training_admitted', 'runtime_adopted'])
    close = lambda a, b: math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-11)
    checked = []
    for specification, fold in zip(design, result['folds']):
        for key in specification:
            assert specification[key] == fold[key]
        held = fold['held_subject']
        train = [by_case[c] for c in fold['fitting_cases']]
        assert len(train) == 27 and len(fold['evaluation_cases']) == 3
        assert all(r['subject_id'] != held for r in train)
        assert all(by_case[c]['subject_id'] == held for c in fold['evaluation_cases'])
        xs, ys = reconstruct(train, fold['fitting_weights'])
        assert all(a >= b for a, b in zip(fold['mst_knots'], fold['mst_knots'][1:]))
        for x, y in zip(fold['ita_knots'], fold['mst_knots']):
            assert close(interpolate(xs, ys, x), y)
        for x, y in zip(xs, ys):
            assert close(interpolate(fold['ita_knots'], fold['mst_knots'], x), y)
        scores = {r['subject_id']: float(Decimal(r['source_mst_exact_decimal'])) for r in train}
        baseline = statistics.median(scores.values())
        assert close(baseline, fold['median_baseline'])
        for case in fold['evaluation_cases']:
            p = predictions[case]
            row = by_case[case]
            x = row['features']['input_ita_degrees']
            y = interpolate(xs, ys, x)
            target = float(Decimal(row['source_mst_exact_decimal']))
            assert p['subject_id'] == held and p['condition'] == row['condition']
            assert p['source_mst_exact_decimal'] == row['source_mst_exact_decimal']
            assert p['input_ita_degrees'] == x
            assert close(y, p['predicted_mst_score']) and close(baseline, p['median_baseline'])
            assert close(abs(y-target), p['absolute_error']) and close(abs(baseline-target), p['baseline_absolute_error'])
            outside = x < xs[0] or x > xs[-1]
            assert outside == p['outside_fitting_support'] == p['endpoint_clipped']
            assert p['fitting_support'] == [xs[0], xs[-1]]
            checked.append(case)
    assert len(checked) == len(set(checked)) == 30
    def verify_metrics(records, metrics):
        grouped = defaultdict(list)
        for r in records:
            grouped[r['subject_id']].append(r)
        assert metrics['attempts'] == metrics['available_predictions'] == len(records)
        assert metrics['unavailable_predictions'] == 0 and metrics['subjects'] == len(grouped)
        assert close(metrics['image_MAE'], statistics.mean(r['absolute_error'] for r in records))
        assert close(metrics['baseline_image_MAE'], statistics.mean(r['baseline_absolute_error'] for r in records))
        assert close(metrics['equal_subject_MAE'], statistics.mean(statistics.mean(r['absolute_error'] for r in group) for group in grouped.values()))
        assert close(metrics['baseline_equal_subject_MAE'], statistics.mean(statistics.mean(r['baseline_absolute_error'] for r in group) for group in grouped.values()))
        assert metrics['outside_support'] == sum(r['outside_fitting_support'] for r in records)
        assert metrics['better_cases'] == sum(r['absolute_error'] < r['baseline_absolute_error'] for r in records)
        assert metrics['worse_cases'] == sum(r['absolute_error'] > r['baseline_absolute_error'] for r in records)
        assert metrics['equal_cases'] == sum(r['absolute_error'] == r['baseline_absolute_error'] for r in records)
    records = list(predictions.values())
    verify_metrics(records, result['metrics'])
    for c, m in result['by_condition'].items():
        verify_metrics([r for r in records if r['condition'] == c], m)
    for s, m in result['by_subject'].items():
        selected = [r for r in records if r['subject_id'] == s]
        verify_metrics(selected, m)
        values = [r['predicted_mst_score'] for r in selected]
        assert close(m['prediction_range'], max(values)-min(values))
    bound = {str(p): sha(p) for p in [Path(__file__), OUT / 'execution_plan_PRIVATE.json', OUT / 'results_PRIVATE.json',
                                     DESIGN / 'rows_PRIVATE.json', DESIGN / 'folds_PRIVATE.json']}
    dest.write_text(json.dumps(dict(passed=True, sklearn_candidate_fits=10, independent_weighted_PAVA_replays=10,
        checked_predictions=30, checked_conditions=3, checked_subjects=10,
        original_image_reads=0, holdout_bytes_read=0, correction_tree_fits=0,
        input_sha256=bound), indent=2), encoding='utf-8')
    print('PASS: 10 independent weighted-PAVA reconstructions, all30 predictions, all metrics and subject isolation')


if __name__ == '__main__':
    main()
