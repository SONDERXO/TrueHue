from copy import deepcopy
import pytest
from src.ita_estimation.reviewed_contextual_validation import evaluate


def fixture():
    rows=[dict(case_id=f'c{s}_{i}',subject_id=f's{s}',condition=f'light{i}',source_mst_exact_decimal=str(2+s),
        measurement_core_sha256='generated',status='available',user_review='reviewed_selection',
        calibration_admitted=False,training_admitted=False,features=dict(input_ita_degrees=45-15*s+i,
            input_mean_l_star=60-8*s+2*i,input_mean_a_star=5+s+i,input_mean_b_star=15-s+3*i)) for s in range(4) for i in range(3)]
    folds=[dict(held_subject=f's{s}',fitting_subjects=[f's{k}' for k in range(4) if k!=s],
        fitting_cases=[r['case_id'] for r in rows if r['subject_id']!=f's{s}'],evaluation_cases=[r['case_id'] for r in rows if r['subject_id']==f's{s}'],
        fitting_weights={r['case_id']:1/3 for r in rows if r['subject_id']!=f's{s}'}) for s in range(4)]
    comparators=[dict(case_id=r['case_id'],subject_id=r['subject_id'],condition=r['condition'],source_mst_exact_decimal=r['source_mst_exact_decimal'],
        predicted_mst_score=5.,absolute_error=abs(5-float(r['source_mst_exact_decimal'])),median_baseline=5.,baseline_absolute_error=abs(5-float(r['source_mst_exact_decimal']))) for r in rows]
    gates=dict(equal_subject_MAE_strictly_below=3.,median_MAE_strictly_below=3.,condition_MAE_not_above={f'light{i}':3. for i in range(3)},maximum_absolute_error_not_above=5.,comparison_tolerance=1e-12)
    return rows,folds,comparators,gates


def test_held_labels_cannot_change_that_fold_model_or_scaling():
    rows,folds,old,gates=fixture();before=deepcopy(rows);result=evaluate(rows,folds,old,gates)
    assert rows==before and result['mapping_fits']==4 and len(result['predictions'])==12
    assert not result['calibration_admitted'] and not result['PPR_application_qualified'] and not result['all_data_fit']
    changed=deepcopy(rows);comparators=deepcopy(old)
    for r in changed:
        if r['subject_id']=='s1':r['source_mst_exact_decimal']='8.0'
    for p in comparators:
        if p['subject_id']=='s1':p['source_mst_exact_decimal']='8.0'
    second=evaluate(changed,folds,comparators,gates)
    assert next(f for f in result['folds'] if f['held_subject']=='s1')==next(f for f in second['folds'] if f['held_subject']=='s1')


@pytest.mark.parametrize('bad',['leak','weight','admitted','core','comparator'])
def test_invalid_input_design_rejected(bad):
    rows,folds,old,gates=fixture()
    if bad=='leak':folds[0]['fitting_cases'].append(folds[0]['evaluation_cases'][0])
    elif bad=='weight':folds[0]['fitting_weights']['c1_0']=1
    elif bad=='admitted':rows[0]['calibration_admitted']=True
    elif bad=='core':rows[0]['measurement_core_sha256']='other'
    else:old[0]['subject_id']='wrong'
    with pytest.raises(ValueError):evaluate(rows,folds,old,gates)
