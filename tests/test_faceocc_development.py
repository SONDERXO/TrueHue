from types import SimpleNamespace
import numpy as np
from src.ita_estimation.faceocc_development import evaluate_parent,measure
from src.skin_masking.faceocc_mediapipe_bridge import template_five


def example():
    template=np.zeros((68,3))
    template[36]=template[39]=[-1,1,0];template[42]=template[45]=[1,1,0]
    template[30]=[0,0,1];template[48]=[-.7,-1,0];template[54]=[.7,-1,0]
    anchors=template_five(template);xy=np.column_stack((58*anchors[:,0]+120,255-(58*anchors[:,1]+130)))
    points=np.zeros((478,2))
    for indices,p in zip([(33,133),(362,263),(1,),(61,),(291,)],xy):points[list(indices)]=p
    image=np.full((256,256,3),[80,110,150],np.uint8)
    mask=np.zeros((256,256),np.uint8);mask[80:160,80:160]=255
    return SimpleNamespace(image=image,mask=mask,report={'status':'success','features':{'old':99}}),points,template


def test_success_stays_unverified_and_does_not_mutate_parent():
    parent,points,template=example();before=parent.mask.copy()
    result=evaluate_parent(parent,points,template,lambda _:np.ones((256,256),np.float32))
    assert result.report['status']=='success'
    assert result.report['actual_skin_validity']=='unverified' and result.report['mst'] is None
    assert not result.report['training_admitted'] and not result.report['calibration_admitted']
    assert np.array_equal(parent.mask,before) and parent.report['features']=={'old':99}


def test_parent_failure_prevents_model_and_stale_features():
    parent,points,template=example();parent.report['status']='failed'
    def forbidden(_):raise AssertionError('Predictor must not run')
    result=evaluate_parent(parent,points,template,forbidden)
    assert result.report['features'] is None and result.mask is None and result.logits is None


def test_prediction_errors_and_insufficient_support_never_reuse_features():
    parent,points,template=example()
    bad=evaluate_parent(parent,points,template,lambda _:np.full((256,256),np.nan))
    assert bad.report['status']=='failed' and bad.report['features'] is None
    empty=evaluate_parent(parent,points,template,lambda _:np.full((256,256),-1.))
    assert empty.report['status']=='failed' and empty.report['features'] is None


def test_end_to_end_detection_failure_never_enters_landmarks_or_predictor():
    parent,_,template=example()
    def forbidden(*_):raise AssertionError('Unavailable parent must stop pipeline')
    result=measure(parent.image,lambda _:[],forbidden,None,forbidden,template)
    assert result.report['status']=='failed' and result.report['stage']=='parent_measurement'
    assert result.report['features'] is None and result.report['mst'] is None
