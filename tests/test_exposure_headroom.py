"""Meaningful physical-bound and protection cases, using generated pixels only."""
import math
import numpy as np
import pytest

from src.model_training.exposure_headroom import cap_exposure_headroom


def sample(code=250):
    return np.full((3,4,3),code,np.uint8),np.ones((3,4),float),np.zeros((3,4),bool)


def scalar_power(rgb,p):
    def dec(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
    values=[dec(max(int(c)-.5,0)/255.)*gain for c,gain in zip(rgb,[p[2],1,p[3]])]
    return math.fsum(v*w for v,w in zip(values,[.2126,.7152,.0722]))**p[0]


@pytest.mark.parametrize('code',[0,40,100,128])
def test_dark_input_retains_original_gain(code):
    args=sample(code);p=[1,math.sqrt(2),1,1,1]
    assert cap_exposure_headroom(*args,p)['effective_controls']==p


@pytest.mark.parametrize('code',[230,250,255])
def test_bright_bound_is_scalar_safe_without_gain_reversal(code):
    args=sample(code);p=[1,math.sqrt(2),1,1,1]
    result=cap_exposure_headroom(*args,p);effective=result['effective_controls']
    assert result['applied'] and 1<=effective[1]<p[1]
    assert effective[1]*scalar_power(args[0][0,0],p)<=1+1e-14
    assert [effective[i] for i in [0,2,3,4]]==[p[i] for i in [0,2,3,4]]


def test_protected_highlights_cannot_restrict_dark_face():
    image,alpha,protected=sample(100);image[0,0]=255;alpha[0,0]=0;protected[0,0]=True
    p=[1,math.sqrt(2),1,1,1]
    assert not cap_exposure_headroom(image,alpha,protected,p)['applied']


def test_small_feather_is_not_silently_excluded():
    image,alpha,protected=sample(100);image[0,0]=250;alpha[0,0]=1e-9
    assert cap_exposure_headroom(image,alpha,protected,[1,math.sqrt(2),1,1,1])['applied']


def test_balance_without_headroom_uses_identity_not_darkening():
    result=cap_exposure_headroom(*sample(250),[1,math.sqrt(2),4,4,1])
    assert result['effective_controls']==[1]*5
    assert result['reason']=='identity_no_positive_exposure_headroom'


@pytest.mark.parametrize('gain',[.5,1.])
def test_nonbrightening_controls_are_unchanged(gain):
    p=[1,gain,1.2,1.1,1]
    assert cap_exposure_headroom(*sample(),p)['effective_controls']==p


def test_arrays_and_controls_are_not_mutated():
    args=sample();p=[1,math.sqrt(2),1,1,1];before=[a.tobytes() for a in args]
    cap_exposure_headroom(*args,p)
    assert [a.tobytes() for a in args]==before and p==[1,math.sqrt(2),1,1,1]


@pytest.mark.parametrize('kind',['image','shape','nan','protected','empty','control'])
def test_invalid_contract_rejected(kind):
    image,alpha,protected=sample();p=[1,math.sqrt(2),1,1,1]
    if kind=='image':image=image.astype(float)
    if kind=='shape':alpha=alpha[:1]
    if kind=='nan':alpha[0,0]=np.nan
    if kind=='protected':protected[0,0]=True
    if kind=='empty':alpha[:]=0
    if kind=='control':p[1]=math.inf
    with pytest.raises(ValueError):cap_exposure_headroom(image,alpha,protected,p)
