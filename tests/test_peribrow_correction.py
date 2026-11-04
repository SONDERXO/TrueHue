import numpy as np
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.skin_masking.peribrow_correction import include_features_and_peribrow


def test_surrounding_skin_is_corrected_without_changing_measurement():
    face=np.zeros((100,100),np.uint8);face[10:80,10:90]=255;face[23:31,25:65]=0
    cats=np.ones(face.shape,np.uint8);cats[26:28,30:60]=2
    base=FaceNeckSupport(face,np.zeros_like(face),face.copy(),{})
    result=include_features_and_peribrow(base,cats)
    assert result.correction_mask[25,40] and not face[25,40]
    assert np.array_equal(result.measurement_mask,face)
    assert not result.correction_mask[23,25] # no indiscriminate hole filling


def test_predicted_eyes_and_explicit_veto_stay_out():
    face=np.zeros((100,100),np.uint8);face[10:80,10:90]=255;face[23:31,25:65]=0
    cats=np.ones(face.shape,np.uint8);cats[26:28,30:60]=2;cats[28:30,30:60]=4
    veto=np.zeros(face.shape,bool);veto[25,40]=True
    base=FaceNeckSupport(face,np.zeros_like(face),face.copy(),{})
    result=include_features_and_peribrow(base,cats,protected=veto)
    assert not result.correction_mask[28:30,30:60].any()
    assert not result.correction_mask[25,40]
