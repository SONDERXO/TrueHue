import cv2
import numpy as np
import pytest
from src.correction.seamless_blend import apply_blended, inward_alpha
from src.model_training.blended_recovery_targets import fit_target, render_rgb8


def fixture():
    im = np.random.default_rng(82).integers(35,210,(24,24,3),dtype=np.uint8)
    mask=np.zeros((24,24),np.uint8);mask[2:22,2:22]=255
    alpha,_=inward_alpha(mask,face_width=80)
    return im,mask,alpha


def test_actual_baseline_render_parity_and_outside_preservation():
    im,mask,alpha=fixture();p=[.8,1.1,.9]
    expected,_,_=apply_blended(cv2.cvtColor(im,cv2.COLOR_RGB2BGR),mask,p,face_width=80)
    actual=render_rgb8(im,alpha,p)
    np.testing.assert_array_equal(actual,cv2.cvtColor(expected,cv2.COLOR_BGR2RGB))
    np.testing.assert_array_equal(actual[alpha==0],im[alpha==0])


def test_target_generation_known_blended_forward_and_input_immutability():
    im,_,alpha=fixture();saved=im.copy();target=render_rgb8(im,alpha,[.8,1.1,.9])
    r=fit_target(im,target,alpha,alpha>0)
    assert r['status']=='available_approximate_target'
    np.testing.assert_allclose(r['parameters'],[.8,1.1,.9],atol=.004,rtol=0)
    assert r['rgb8_mae_codes']<.1 and not r['training_admitted']
    np.testing.assert_array_equal(im,saved)


def test_neutral_control_has_exact_identity_and_no_optimisation():
    im,_,alpha=fixture();r=fit_target(im,im,alpha,alpha>0)
    assert r['parameters']==[1.,1.,1.] and r['evaluations']==0
    np.testing.assert_array_equal(render_rgb8(im,alpha,r['parameters']),im)


def test_reference_never_changes_pixels_outside_alpha():
    im,_,alpha=fixture();target=im.copy();target[alpha==0]=255
    r=fit_target(im,target,alpha,alpha>0)
    assert r['outside_alpha_mismatch_channels'] > 0
    np.testing.assert_array_equal(render_rgb8(im,alpha,r['parameters']),im)


def test_unrecoverable_black_input_not_given_fabricated_target():
    im,_,alpha=fixture();r=fit_target(np.zeros_like(im),im,alpha,alpha>0)
    assert r['parameters'] is None


@pytest.mark.parametrize('case',['nan','outside','empty'])
def test_invalid_support_rejected(case):
    im,_,alpha=fixture();score=alpha>0
    if case=='nan':alpha[3,3]=np.nan
    if case=='outside':score[:]=True
    if case=='empty':score[:]=False
    with pytest.raises(ValueError):fit_target(im,im,alpha,score)
