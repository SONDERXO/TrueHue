from copy import deepcopy
import numpy as np
import pytest
from src.ita_estimation.contextual_mst_experiment import FEATURES,METHODS,evaluate_subject_held,predict

def generated_rows():
    """Arithmetic software fixture, not a skin/lighting simulation or dataset."""
    rows=[]
    for s,score in enumerate(['1.2','2.8','4.1','6.3','8.0','9.7']):
        for c in range(3):
            rows.append(dict(case_id=f'generated_{s}_{c}',subject_id=f'generated_subject_{s}',condition=f'generated_condition_{c}',
                source_mst_exact_decimal=score,measurement_contract_sha256='a'*64,calibration_admitted=True,status='available',
                features=dict(zip(FEATURES,[float(50-8*s+4*c),float(70-6*s+3*c),float(3+s-c),float(10+2*c)]))))
    return rows

def fold(result,held='generated_subject_0'):
    return next(f for f in result['folds'] if f['held_subject']==held)

def test_subject_held_and_training_only_scaling_and_labels():
    rows=generated_rows();before=deepcopy(rows);first=evaluate_subject_held(rows)
    changed=deepcopy(rows)
    for r in changed:
        if r['subject_id']=='generated_subject_0':
            r['source_mst_exact_decimal']='5.55';r['features']=dict(zip(FEATURES,[-85.,5.,-40.,-80.]))
    second=evaluate_subject_held(changed)
    assert fold(first)==fold(second) and rows==before
    for f in first['folds']:
        assert f['held_subject'] not in f['training_subjects']
        assert not set(f['training_cases'])&set(f['evaluation_cases'])
    assert first['mapping_ridge_fits']==12 and first['correction_tree_fits']==0
    assert not first['integer_category_output'] and not first['scientific_validation']

def test_duplicate_all_photos_of_one_training_subject_preserves_weighted_fit():
    rows=generated_rows();more=deepcopy(rows)
    for i in range(4):
        for r in rows:
            if r['subject_id']=='generated_subject_1':
                clone=deepcopy(r);clone['case_id']+=f'_copy_{i}';more.append(clone)
    a=fold(evaluate_subject_held(rows));b=fold(evaluate_subject_held(more))
    for name in ['ita_lab_ridge','ita_only_ridge']:
        for key in ['mean','scale','coefficient','intercept']:
            assert np.allclose(a['models'][name][key],b['models'][name][key],rtol=1e-12,atol=1e-12)
    assert a['median_baseline']==b['median_baseline']

def test_ridge_satisfies_declared_weighted_objective():
    rows=generated_rows();f=fold(evaluate_subject_held(rows));model=f['models']['ita_lab_ridge']
    training=[r for r in rows if r['case_id'] in f['training_cases']]
    x=np.array([[r['features'][n] for n in FEATURES] for r in training]);z=(x-model['mean'])/model['scale']
    y=np.array([float(r['source_mst_exact_decimal']) for r in training]);coef=np.array(model['coefficient'])
    weights=np.full(len(training),1/3)
    residual=z@coef+model['intercept']-y
    assert np.allclose(z.T@(weights*residual)+coef,0,atol=1e-11)
    assert abs(weights@residual)<1e-10

def test_conditions_are_reporting_only_and_decimals_survive():
    rows=generated_rows();first=evaluate_subject_held(rows)
    for r in rows:r['condition']='different_reporting_label'
    second=evaluate_subject_held(rows)
    assert [r['predictions'] for r in first['records']]==[r['predictions'] for r in second['records']]
    assert {r['source_mst_exact_decimal'] for r in first['records']}=={'1.2','2.8','4.1','6.3','8.0','9.7'}
    for m in METHODS:
        assert first['metrics'][m]['available_predictions']==18
        assert sum(v[m]['attempts'] for v in first['by_condition'].values())==18

def test_unavailable_rows_stay_in_denominator_without_fabricated_error():
    rows=generated_rows()[:6]
    for r in rows[:3]:r.update(status='unavailable',features=None,reason='generated_missing_measurement')
    result=evaluate_subject_held(rows)
    for m in METHODS:
        assert result['metrics'][m]['attempts']==6
        assert result['metrics'][m]['available_predictions']==0
        assert result['metrics'][m]['image_MAE'] is None
        assert result['metrics'][m]['equal_subject_MAE'] is None
    assert result['mapping_ridge_fits']==2

@pytest.mark.parametrize('change',[
    lambda r:r.update(calibration_admitted=False),
    lambda r:r.update(source_mst_exact_decimal=2.8),
    lambda r:r.update(source_mst_exact_decimal='NaN'),
    lambda r:r.update(source_mst_exact_decimal='10.1'),
    lambda r:r.update(measurement_contract_sha256='b'*64),
    lambda r:r['features'].update(reference_mst=5),
    lambda r:r['features'].update(input_mean_l_star=float('nan')),
    lambda r:r['features'].update(input_mean_b_star=True),
])
def test_rejects_unadmitted_rows_bad_scores_contract_mixing_and_feature_leakage(change):
    rows=generated_rows();change(rows[0])
    with pytest.raises(ValueError):evaluate_subject_held(rows)

def test_rejects_subject_label_conflict_and_duplicate_case():
    rows=generated_rows();rows[0]['source_mst_exact_decimal']='1.3'
    with pytest.raises(ValueError):evaluate_subject_held(rows)
    rows=generated_rows();rows[1]['case_id']=rows[0]['case_id']
    with pytest.raises(ValueError):evaluate_subject_held(rows)

def test_zero_variance_feature_and_prediction_clipping_are_explicit():
    rows=generated_rows()
    for r in rows:r['features']['input_mean_b_star']=5.
    model=fold(evaluate_subject_held(rows))['models']['ita_lab_ridge']
    assert model['scale'][3]==1. and model['coefficient'][3]==0.
    probe=dict(features=['x'],mean=[0.],scale=[1.],coefficient=[2.],intercept=0.)
    assert predict(probe,{'x':8.})==dict(raw=16.,score=10.)
    assert predict(probe,{'x':-8.})==dict(raw=-16.,score=1.)
