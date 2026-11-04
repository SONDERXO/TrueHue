"""Synthetic schema fixtures only: these thresholds are NOT real calibration."""
import copy
import pytest
from src.ita_estimation.mst_lookup import CalibratedMstLookup,mst_model_features,MST_FEATURES


def payload():
    return dict(schema_version='truehue_ita_mst_lookup_v1',ita_thresholds_degrees=list(range(-40,41,10)),
        mst_labels_low_to_high_ita=list(range(10,0,-1)),boundary_rule='upper_bin_at_equal',
        calibration=dict(dataset='MST-E',subject_ids=['synthetic_train'],measurement_contract_sha256='a'*64),
        validation=dict(status='passed',subject_ids=['synthetic_validation'],report_sha256='b'*64))


def lookup(value=None):return CalibratedMstLookup(payload() if value is None else value,measurement_contract_sha256='a'*64)


def test_label_direction_and_boundary_rule():
    model=lookup()
    assert model.label(-90)==10 and model.label(90)==1
    assert model.label(-40.001)==10 and model.label(-40)==9
    assert [model.label(v) for v in range(-90,91)]==sorted([model.label(v) for v in range(-90,91)],reverse=True)


def test_lookup_is_independent_of_caller_mutation():
    data=payload();model=lookup(data);data['ita_thresholds_degrees'][0]=-80
    assert model.label(-60)==10


@pytest.mark.parametrize('change',[
    lambda p:p.update(schema_version='unknown'), lambda p:p.update(ita_thresholds_degrees=[0]),
    lambda p:p['ita_thresholds_degrees'].__setitem__(0,float('nan')),
    lambda p:p['ita_thresholds_degrees'].__setitem__(0,True),
    lambda p:p['ita_thresholds_degrees'].__setitem__(0,100),
    lambda p:p.update(mst_labels_low_to_high_ita=list(range(1,11))),
    lambda p:p.update(boundary_rule='unspecified'),
    lambda p:p['calibration'].update(dataset='guessed_from_fairface_race'),
    lambda p:p['calibration'].update(measurement_contract_sha256='c'*64),
    lambda p:p['validation'].update(subject_ids=['synthetic_train']),
    lambda p:p['validation'].update(status='unvalidated'),
    lambda p:p['validation'].update(report_sha256='missing')])
def test_invalid_or_unvalidated_artifact_fails(change):
    data=payload();change(data)
    with pytest.raises(ValueError):lookup(data)


def test_features_use_input_ita_without_reference_label_and_config_indexing():
    data=dict(input_mean_l_star=50,input_mean_a_star=10,input_mean_b_star=20,input_ita_degrees=20)
    original=copy.deepcopy(data)
    result=mst_model_features(data,lookup(),measurement_contract_sha256='a'*64)
    assert tuple(result)==MST_FEATURES and result['input_mst_index']==2 and data==original
    data['source_mst_label']=1
    with pytest.raises(ValueError):mst_model_features(data,lookup(),measurement_contract_sha256='a'*64)


@pytest.mark.parametrize('value',[None,float('nan'),float('inf'),True,'20'])
def test_invalid_ita_fails(value):
    with pytest.raises(ValueError):lookup().label(value)


def test_missing_lookup_or_mismatched_measurement_contract_does_not_fall_back():
    data=dict(input_mean_l_star=50,input_mean_a_star=10,input_mean_b_star=20,input_ita_degrees=20)
    for model,contract in [(None,'a'*64),(lookup(),'c'*64)]:
        with pytest.raises(ValueError):mst_model_features(data,model,measurement_contract_sha256=contract)
