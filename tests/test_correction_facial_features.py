import numpy as np
import pytest
from src.skin_masking.face_neck_support import FaceNeckSupport,apply_shared_parameters
from src.skin_masking.correction_facial_features import include_brows_lips


def sample():
    face=np.zeros((40,40),np.uint8);face[5:30,5:35]=255
    face[10:15,10:30]=0;face[20:25,10:30]=0
    cats=np.zeros((40,40),np.uint8);cats[10:12,10:20]=2;cats[10:12,20:30]=3
    cats[20:22,10:30]=12;cats[23:25,10:30]=13;cats[22,10:30]=11
    return FaceNeckSupport(face,np.zeros_like(face),face.copy(),{}),cats


def test_brows_lips_added_only_to_correction_and_input_is_immutable():
    base,cats=sample();before=base.correction_mask.copy();r=include_brows_lips(base,cats)
    assert r.correction_mask[10,12] and r.correction_mask[20,12]
    assert not r.correction_mask[22,12] # mouth interior
    assert np.array_equal(r.measurement_mask,base.measurement_mask)
    assert np.array_equal(base.correction_mask,before)
    assert not np.shares_memory(r.measurement_mask,base.measurement_mask)


@pytest.mark.parametrize('label',[4,5,6,11,17])
def test_eyes_glasses_mouth_and_hair_are_not_added(label):
    base,cats=sample();cats[10:15,10:30]=label
    r=include_brows_lips(base,cats)
    assert not r.correction_mask[10:15,10:30].any()


def test_other_face_features_outside_bounds_and_veto_stay_unchanged():
    base,cats=sample();cats[35:39,0:4]=12
    veto=np.zeros(cats.shape,bool);veto[20:22,10:30]=True
    r=include_brows_lips(base,cats,protected=veto)
    assert not r.correction_mask[35:39,0:4].any() and not r.correction_mask[veto].any()
    im=np.full((40,40,3),(80,120,160),np.uint8)
    a=apply_shared_parameters(im,base,.85,1.05,.95);b=apply_shared_parameters(im,r,.85,1.05,.95)
    added=(r.correction_mask>0)&(base.correction_mask==0)
    assert np.array_equal(a[~added],b[~added])
