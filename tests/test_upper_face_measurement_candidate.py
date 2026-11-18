import numpy as np
import pytest
from tests.test_full_face_support import setup
from src.skin_masking.upper_face_measurement_candidate import build

def inputs():
    *_,points=setup()
    return np.full((256,256,3),80,np.uint8),points*2.56,np.zeros((256,256),np.uint8),np.ones((256,256)),np.array([[1.,0,0],[0,1.,0]])

def test_background_recovery_is_upper_face_only_and_does_not_mutate():
    im,p,c,l,m=inputs();original=im.copy();mask,report=build(im,p,c,l,m)
    assert mask.any() and report['recovered_background_pixels']==np.count_nonzero(mask)
    assert not mask[np.indices(mask.shape)[0]>p[2,1]].any()
    assert np.array_equal(im,original)

@pytest.mark.parametrize('forbidden',[6,9,14,15,16,17,18,2,4])
def test_explicit_non_skin_classes_cannot_be_recovered(forbidden):
    im,p,c,l,m=inputs();c[:]=forbidden;mask,_=build(im,p,c,l,m);assert not mask.any()

def test_negative_visibility_and_invalid_nasal_geometry_do_not_fall_back():
    im,p,c,l,m=inputs();mask,_=build(im,p,c,-l,m);assert not mask.any()
    p[2,1]=300
    with pytest.raises(ValueError):build(im,p,c,l,m)
