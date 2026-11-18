from copy import deepcopy
import pytest
from src.ita_estimation.exploratory_real_mst import evaluate
from src.ita_estimation.contextual_mst_experiment import FEATURES


def rows():
    return [dict(case_id=f'{s}_{c}',subject_id=str(s),condition=str(c),source_mst_exact_decimal=str(2+s),
        calibration_admitted=False,training_admitted=False,actual_skin_validity='unverified',status='available',reason=None,
        features=dict(zip(FEATURES,[10+s+c,35+5*s+c,4+s,10+c]))) for s in range(3) for c in range(2)]


def test_held_label_cannot_change_own_fold_and_rows_immutable():
    data=rows();before=deepcopy(data);a=evaluate(data);changed=deepcopy(data)
    for r in changed:
        if r['subject_id']=='0':r['source_mst_exact_decimal']='9.7'
    b=evaluate(changed)
    assert a['folds'][0]==b['folds'][0] and data==before
    assert a['calibration_admissions']==0 and a['mapping_ridge_fits']==6
    assert all(f['held_subject'] not in f['training_subjects'] for f in a['folds'])


def test_failure_in_attempts_not_negative_or_filled():
    data=rows();data[0].update(status='unavailable',features=None,reason='landmark failure')
    result=evaluate(data)
    for m in result['metrics'].values():
        assert m['attempts']==6 and m['available_predictions']==5 and m['unavailable_predictions']==1
    assert all(v is None for v in result['records'][0]['predictions'].values())


@pytest.mark.parametrize('change', ['admission','extra','nonfinite','label','failure'])
def test_contract_errors(change):
    data=rows()
    if change=='admission':data[0]['calibration_admitted']=True
    if change=='extra':data[0]['features']['reference_mst']=2
    if change=='nonfinite':data[0]['features'][FEATURES[0]]=float('nan')
    if change=='label':data[0]['source_mst_exact_decimal']='2.9'
    if change=='failure':data[0].update(status='unavailable',features=None,reason='')
    with pytest.raises(ValueError):evaluate(data)
