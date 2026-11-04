from types import SimpleNamespace
import numpy as np
import pytest
from src.correction.development_mst_pipeline import DevelopmentMSTPipeline
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.chroma_distribution import ADDITIONS


class Lookup:
    measurement_contract_sha256='test-contract'
    def __init__(self):self.values=[]
    def label(self,value):self.values.append(value);return 4


class Model:
    target_names=TARGETS
    def __init__(self,nine=False):self.feature_names=tuple(MST_FEATURES)+(ADDITIONS if nine else ());self.inputs=[]
    def predict_one(self,values):self.inputs.append(values);return [1.2,1.,1.]


def masker(image,box):
    x,y,w,h=box;mask=np.full((h,w),255,np.uint8);excluded=np.zeros((h,w),np.uint8)
    excluded[80:100,80:100]=255;mask[excluded>0]=0
    return SimpleNamespace(mask=mask,exclusion_mask=excluded,landmarks_available=True)


@pytest.mark.parametrize('nine',[False,True])
def test_input_only_square_mst_features_and_protected_pixels(nine):
    image=np.full((150,180,3),[60,100,150],np.uint8);before=image.copy();lookup=Lookup();model=Model(nine)
    result=DevelopmentMSTPipeline(lambda im:[(10,10,230,230)],masker,lookup,model,'test-contract').run(image)
    assert result.report['status']=='development_experimental_mst'
    assert result.image.shape==(256,256,3) and model.inputs[0][4]==3
    assert lookup.values==[result.report['features']['input_ita_degrees']]
    assert len(model.inputs[0])==(9 if nine else 5)
    assert not result.report['proposal_complete'] and not result.report['quality_gate_passed']
    np.testing.assert_array_equal(result.corrected[result.mask==0],result.image[result.mask==0])
    np.testing.assert_array_equal(image,before)


def test_detection_failure_never_calls_lookup_or_model():
    lookup=Lookup();model=Model()
    result=DevelopmentMSTPipeline(lambda im:[],masker,lookup,model,'test-contract').run(np.zeros((256,256,3),np.uint8))
    assert result.report['failed_stage']=='face_detection' and result.corrected is None
    assert not lookup.values and not model.inputs and result.report['mst'] is None


def test_missing_landmarks_never_fall_back():
    def missing(im,box):
        value=masker(im,box);value.landmarks_available=False;return value
    lookup=Lookup();model=Model()
    result=DevelopmentMSTPipeline(lambda im:[(10,10,230,230)],missing,lookup,model,'test-contract').run(np.zeros((256,256,3),np.uint8))
    assert result.report['failed_stage']=='skin_mask' and not model.inputs


def test_contract_and_schema_rejected_before_processing():
    with pytest.raises(ValueError,match='contract'):DevelopmentMSTPipeline(None,None,Lookup(),Model(),'other')
    model=Model();model.feature_names=tuple(reversed(MST_FEATURES))
    with pytest.raises(ValueError,match='schema'):DevelopmentMSTPipeline(None,None,Lookup(),model,'test-contract')


def test_invalid_prediction_is_not_saved_as_success():
    model=Model();model.predict_one=lambda values:[0.,1.,1.]
    result=DevelopmentMSTPipeline(lambda im:[(10,10,230,230)],masker,Lookup(),model,'test-contract').run(np.full((256,256,3),[60,100,150],np.uint8))
    assert result.report['failed_stage']=='tree_prediction' and result.corrected is None and result.report['parameters'] is None
