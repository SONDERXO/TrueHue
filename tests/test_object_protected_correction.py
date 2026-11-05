import numpy as np
import pytest
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.skin_masking.object_protected_correction import protect_correction_objects
from src.skin_masking.continuous_correction import continuous_support
from src.correction.seamless_blend import apply_blended


def fixture():
    mask = np.zeros((40,40),np.uint8); mask[4:34,4:36] = 255
    neck = np.zeros_like(mask); neck[25:34,10:30] = 255
    outline = mask.copy(); outline[25:] = 0
    cats = np.ones_like(mask); cats[neck>0] = 14
    visible = np.full_like(mask,255)
    return FaceNeckSupport(mask.copy(),neck,mask,{}),cats,visible,outline


def test_enclosed_objects_stay_protected_through_continuity_and_rendering():
    support,cats,visible,outline = fixture()
    for i,cls in enumerate([0,6,9,15,16,17,18]): cats[12:15,6+i*4:8+i*4] = cls
    revised,veto = protect_correction_objects(support,cats,visible,outline)
    revised = continuous_support(revised,protected=veto)
    image = np.full((40,40,3),90,np.uint8)
    output,alpha,_ = apply_blended(image,revised.correction_mask,[.7,1.1,.9],face_width=32,protected=veto)
    assert not revised.correction_mask[veto].any() and not alpha[veto].any()
    assert np.array_equal(image[veto],output[veto])
    assert np.any(output[~veto]!=image[~veto])


def test_visibility_removes_skin_labelled_occluder_without_erasing_neck():
    support,cats,visible,outline = fixture()
    visible[10:15,10:15] = 0  # e.g. a hand incorrectly labelled as skin
    visible[25:] = 0  # FaceOcc is face-only, not evidence of neck occlusion
    revised,veto = protect_correction_objects(support,cats,visible,outline)
    assert not revised.correction_mask[10:15,10:15].any()
    assert np.array_equal(revised.neck_mask,support.neck_mask)
    assert np.array_equal(revised.measurement_mask,support.measurement_mask)
    assert not np.shares_memory(revised.measurement_mask,support.measurement_mask)
    assert not revised.correction_mask[support.correction_mask==0].any()


def test_facial_features_stay_corrected_and_explicit_veto_wins():
    support,cats,visible,outline = fixture()
    for i,cls in enumerate([2,3,4,5,7,8,10,11,12,13]): cats[10,5+i] = cls
    protected = np.zeros(cats.shape,bool); protected[20,20] = True
    revised,_ = protect_correction_objects(support,cats,visible,outline,protected=protected)
    assert revised.correction_mask[10,5:15].all()
    assert not revised.correction_mask[20,20]
    assert support.correction_mask[20,20]  # no mutation


@pytest.mark.parametrize('bad', [None,np.zeros((3,3),np.uint8),np.full((40,40),7,np.uint8)])
def test_missing_or_invalid_visibility_fails_instead_of_silently_unprotecting(bad):
    support,cats,_,outline = fixture()
    with pytest.raises(ValueError):protect_correction_objects(support,cats,bad,outline)
