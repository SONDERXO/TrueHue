from types import SimpleNamespace
import copy
import numpy as np
import pytest
from src.correction.core_pipeline import CorePipeline
from src.data_preparation.controlled_training_table import FEATURES

class Model:
    n_features_in_=4
    def __init__(self):self.calls=0
    def predict(self,x):self.calls+=1;return [[1.2,1.,1.]]

def example():
    image=np.full((80,80,3),[70,100,140],np.uint8)
    mask=np.full((70,70),255,np.uint8);exclusion=np.zeros_like(mask);exclusion[25:35,25:35]=255;mask[exclusion>0]=0
    return image,SimpleNamespace(mask=mask,exclusion_mask=exclusion,landmarks_available=True)

def test_available_correction_still_reports_missing_mst_and_preserves_exclusions():
    image,mask=example();original=image.copy();model=Model()
    result=CorePipeline(lambda image:[(5,5,70,70)],lambda image,box:mask,model).run(image)
    assert result.report['status']=='development_partial_mst_unavailable'
    assert result.report['proposal_complete'] is False
    assert result.report['mst']['label'] is None and result.report['mst']['status']=='unavailable'
    assert tuple(result.correction.features)==FEATURES and model.calls==1
    assert all(result.report['stages'][s]['status']=='success' for s in ['input','face_detection','skin_mask','measurement','correction'])
    np.testing.assert_array_equal(image,original)
    np.testing.assert_array_equal(result.correction.corrected_bgr[~result.correction.correction_mask],image[~result.correction.correction_mask])
    assert not result.correction.correction_mask[30:40,30:40].any()

@pytest.mark.parametrize('boxes',[[],[(0,0,20,20),(30,30,20,20)],[(0,0,81,80)],[(-1,0,70,70)],[(0.,0,70,70)]])
def test_invalid_or_multiple_faces_stop_before_mask_and_model(boxes):
    image,_=example();model=Model()
    def forbidden(*args):raise AssertionError('Mask must not run')
    result=CorePipeline(lambda image:boxes,forbidden,model).run(image)
    assert result.report['failed_stage']=='face_detection' and result.correction is None and model.calls==0
    assert result.report['mst']['status']=='not_run'

@pytest.mark.parametrize('change',[
    lambda m:setattr(m,'landmarks_available',False),
    lambda m:setattr(m,'mask',m.mask.astype(bool)),
    lambda m:setattr(m,'mask',m.mask[:20]),
    lambda m:m.mask.__setitem__((0,0),127),
    lambda m:m.mask.__setitem__((30,30),255)])
def test_invalid_masks_and_unavailable_landmarks_never_fall_back(change):
    image,mask=example();change(mask);model=Model()
    result=CorePipeline(lambda image:[(5,5,70,70)],lambda image,box:mask,model).run(image)
    assert result.report['failed_stage']=='skin_mask' and result.correction is None and model.calls==0

def test_insufficient_skin_retains_measurement_failure_without_parameters():
    image,mask=example();mask.mask[:]=0;mask.mask[:10,:10]=255;model=Model()
    result=CorePipeline(lambda image:[(5,5,70,70)],lambda image,box:mask,model).run(image)
    assert result.report['failed_stage']=='measurement' and model.calls==0
    assert result.report['stages']['correction']['status']=='not_run' and result.report['mst']['label'] is None

def test_bad_model_output_is_a_correction_failure_not_mst_success():
    image,mask=example();model=Model();model.predict=lambda x:[[0,1,1]]
    result=CorePipeline(lambda image:[(5,5,70,70)],lambda image,box:mask,model).run(image)
    assert result.report['failed_stage']=='correction' and result.correction is None
    assert result.report['mst']['status']=='unavailable' and not result.report['proposal_complete']

@pytest.mark.parametrize('image',[None,np.zeros((5,5),np.uint8),np.zeros((5,5,3),float),np.zeros((0,5,3),np.uint8)])
def test_invalid_input_is_reported_before_detection(image):
    def forbidden(*args):raise AssertionError('Detector must not run')
    result=CorePipeline(forbidden,forbidden,Model()).run(image)
    assert result.report['failed_stage']=='input' and result.correction is None

def test_mismatched_model_feature_order_is_rejected():
    model=Model();model.feature_names=tuple(reversed(FEATURES))
    with pytest.raises(ValueError,match='Feature order'):CorePipeline(None,None,model)
