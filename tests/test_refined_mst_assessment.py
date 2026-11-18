from copy import deepcopy
import pytest
from src.ita_estimation.refined_mst_assessment import assess


def fixture():
    rows = [dict(case_id=f'c{s}_{i}', subject_id=f's{s}', condition=f'light{i}',
        source_mst_exact_decimal=str(s+2), measurement_method_sha256='generated_only',
        status='available', user_review='reviewed_selection', calibration_admitted=False,
        training_admitted=False, features=dict(input_ita_degrees=50-20*s+i))
        for s in range(4) for i in range(2)]
    folds = [dict(held_subject=f's{s}', fitting_subjects=[f's{k}' for k in range(4) if k != s],
        fitting_cases=[r['case_id'] for r in rows if r['subject_id'] != f's{s}'],
        evaluation_cases=[r['case_id'] for r in rows if r['subject_id'] == f's{s}'],
        fitting_weights={r['case_id']: .5 for r in rows if r['subject_id'] != f's{s}'}) for s in range(4)]
    return rows, folds


def test_fixed_mapping_has_subject_isolation_and_explicit_clipping():
    rows, folds = fixture()
    result = assess(rows, folds)
    assert result['calibration_fits'] == 4 and len(result['predictions']) == 8
    assert not result['calibration_admitted'] and not result['all_data_fit']
    assert result['metrics']['outside_support'] == 4
    for fold in result['folds']:
        assert fold['held_subject'] not in fold['fitting_subjects']
        assert all(a >= b for a, b in zip(fold['mst_knots'], fold['mst_knots'][1:]))
    changed = deepcopy(rows)
    for r in changed:
        if r['subject_id'] == 's1':
            r['source_mst_exact_decimal'] = '9.0'
    repeated = assess(changed, folds)
    old = next(f for f in result['folds'] if f['held_subject'] == 's1')
    new = next(f for f in repeated['folds'] if f['held_subject'] == 's1')
    assert old == new  # Held scores cannot alter that fold's fit or baseline.


@pytest.mark.parametrize('bad', ['leakage', 'weights', 'mixed_method', 'duplicate'])
def test_rejects_invalid_design_before_fitting(bad):
    rows, folds = fixture()
    if bad == 'leakage':
        folds[0]['fitting_cases'].append(folds[0]['evaluation_cases'][0])
    elif bad == 'weights':
        folds[0]['fitting_weights']['c1_0'] = 1
    elif bad == 'mixed_method':
        rows[0]['measurement_method_sha256'] = 'other'
    else:
        rows.append(deepcopy(rows[0]))
    with pytest.raises(ValueError):
        assess(rows, folds)
