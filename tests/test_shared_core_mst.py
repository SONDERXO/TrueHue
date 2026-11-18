from copy import deepcopy
import pytest
from src.ita_estimation.shared_core_mst import predict_score


def artifact():
    return dict(schema_version='truehue_shared_core_development_mst_v1',status='development_unvalidated_transfer',
        measurement_core_sha256='core',feature_control_contract_sha256='application',ita_knots=[-40.,0.,40.],
        mst_score_knots=[9.,5.,2.],calibration_admitted=False,runtime_adopted=False)


def score(a,x,**kwargs):return predict_score(a,x,measurement_core_sha256=kwargs.get('core','core'),feature_control_contract_sha256=kwargs.get('application','application'))


def test_fractional_interpolation_and_explicit_endpoint_support():
    a=artifact();middle=score(a,20.)
    assert middle['score']==3.5 and not middle['endpoint_clipped']
    assert score(a,-100.)['score']==9. and score(a,-100.)['outside_fitting_support']
    assert score(a,100.)['score']==2. and score(a,100.)['endpoint_clipped']
    assert not score(a,40.)['endpoint_clipped']


@pytest.mark.parametrize('bad',['core','application','status','admission','increasing','nan'])
def test_contract_or_invalid_mapping_rejected(bad):
    a=artifact();kwargs={};x=10.
    if bad in ('core','application'):kwargs[bad]='wrong'
    elif bad=='status':a['status']='production'
    elif bad=='admission':a['calibration_admitted']=True
    elif bad=='increasing':a['mst_score_knots']=[2.,5.,9.]
    else:x=float('nan')
    with pytest.raises(ValueError):score(a,x,**kwargs)


def test_prediction_uses_knots_and_input_not_unrelated_training_metadata():
    a=artifact();changed=deepcopy(a);changed['source_labels']=['not an inference input'];changed['target_controls']=[999]
    assert score(a,10.)==score(changed,10.)
