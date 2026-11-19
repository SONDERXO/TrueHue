"""Generated region-selection regressions; no participant images or model assets."""
import math
import numpy as np
import pytest

from src.model_training.exposure_headroom import cap_exposure_headroom
from src.model_training.facial_exposure_headroom import cap_facial_exposure_headroom


def sample():
    return (np.full((4,5,3),100,np.uint8),np.full((4,5),255,np.uint8),
            np.ones((4,5),float),np.zeros((4,5),bool),[1,math.sqrt(2),1,1,1])


@pytest.mark.parametrize('alpha_value',[1.,.15625,1e-9])
def test_nonmeasurement_accessory_or_edge_cannot_cap_face(alpha_value):
    image,m,a,p,c=sample();image[0,0]=251;m[0,0]=0;a[0,0]=alpha_value
    assert cap_exposure_headroom(image,a,p,c)['applied']
    result=cap_facial_exposure_headroom(image,m,a,p,c)
    assert result['effective_controls']==c and not result['applied']


def test_in_measurement_highlight_retains_same_cap():
    image,m,a,p,c=sample();image[1,2]=250
    assert cap_facial_exposure_headroom(image,m,a,p,c)['effective_controls']==cap_exposure_headroom(image,a,p,c)['effective_controls']


def test_measurement_outside_application_is_not_used():
    image,m,a,p,c=sample();image[0,0]=255;a[0,0]=0
    assert not cap_facial_exposure_headroom(image,m,a,p,c)['applied']


def test_protected_highlight_is_not_used():
    image,m,a,p,c=sample();image[0,0]=255;a[0,0]=0;p[0,0]=True
    assert not cap_facial_exposure_headroom(image,m,a,p,c)['applied']


def test_original_application_and_all_arrays_are_unchanged():
    args=list(sample());before=[v.tobytes() for v in args[:4]];controls=args[4].copy()
    cap_facial_exposure_headroom(*args)
    assert [v.tobytes() for v in args[:4]]==before and args[4]==controls


@pytest.mark.parametrize('kind',['float_mask','mask_shape','mask_value','empty_intersection','bad_alpha_outside_measurement','protected_overlap'])
def test_invalid_or_empty_scope_is_rejected(kind):
    image,m,a,p,c=sample()
    if kind=='float_mask':m=m.astype(float)
    if kind=='mask_shape':m=m[:1]
    if kind=='mask_value':m[0,0]=127
    if kind=='empty_intersection':m[:]=0
    if kind=='bad_alpha_outside_measurement':m[0,0]=0;a[0,0]=np.nan
    if kind=='protected_overlap':m[0,0]=0;p[0,0]=True
    with pytest.raises(ValueError):cap_facial_exposure_headroom(image,m,a,p,c)
