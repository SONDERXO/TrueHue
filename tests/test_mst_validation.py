import copy
import pytest
from src.evaluation.mst_validation import evaluate_mst


def fixture():
    attempts=[dict(image_id='a1',subject_id='a',mst=1,lighting='well',measured=True),
        dict(image_id='a2',subject_id='a',mst=1,lighting='poor',measured=True),
        dict(image_id='b1',subject_id='b',mst=3,lighting='well',measured=True),
        dict(image_id='b2',subject_id='b',mst=3,lighting='poor',measured=False)]
    folds=[dict(held_subject='a',fit_subject_labels={'b':3}),dict(held_subject='b',fit_subject_labels={'a':1})]
    predictions=[dict(image_id='a1',prediction=1,baseline=3),dict(image_id='a2',prediction=3,baseline=3),
                 dict(image_id='b1',prediction=3,baseline=1)]
    return attempts,predictions,folds


def test_paired_subject_balancing_failure_and_support_denominators():
    args=fixture();before=copy.deepcopy(args);report=evaluate_mst(*args);r=report['overall']
    assert r['attempts']==4 and r['processing_failures']==1 and r['available_predictions']==3
    assert r['candidate']['ordinal_mae']==pytest.approx(2/3)
    assert r['candidate']['equal_subject_mae']==.5
    assert r['measured_without_held_category_support']==3 and r['supported_candidate'] is None
    assert report['by_mst']['10']['attempts']==0 and args==before


def test_none_prediction_is_unavailable_not_wrong_and_baseline_pairing_matches():
    a,p,f=fixture();p[1]['prediction']=None;r=evaluate_mst(a,p,f)['overall']
    assert r['unavailable_predictions']==1 and r['candidate']['exact_accuracy']==1
    assert r['paired_baseline']['images']==2 and r['all_measured_baseline']['images']==3


@pytest.mark.parametrize('change',[
    lambda a,p,f:p.pop(),lambda a,p,f:p.append(copy.deepcopy(p[0])),
    lambda a,p,f:p[0].update(prediction=0),lambda a,p,f:p[0].update(prediction=True),
    lambda a,p,f:p[0].update(baseline=1),lambda a,p,f:f[0]['fit_subject_labels'].update(a=1),
    lambda a,p,f:f.pop(),lambda a,p,f:a.append(copy.deepcopy(a[0])),
    lambda a,p,f:a[1].update(mst=2),lambda a,p,f:a[0].update(measured=1),
    lambda a,p,f:p.append(dict(image_id='b2',prediction=3,baseline=1))])
def test_invalid_leaking_or_silently_missing_evidence_fails(change):
    a,p,f=fixture();change(a,p,f)
    with pytest.raises(ValueError):evaluate_mst(a,p,f)
