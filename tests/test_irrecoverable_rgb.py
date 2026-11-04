import numpy as np
import pytest
from src.evaluation.irrecoverable_rgb import irrecoverable_rgb_floor
from src.distortion_generation.paper_gamma import transform_rgb


def test_endpoint_invariants_and_white_red_blue_are_not_fixed():
    image=np.array([[[0,255,255],[255,0,0]]],np.uint8)
    reference=np.array([[[100,200,100],[100,100,100]]],np.uint8)
    mask=np.ones((1,2),bool)
    r=irrecoverable_rgb_floor(image,reference,mask,mask)
    assert r['fixed_inside_channel_samples']==4
    assert r['rgb_mae_lower_bound']==pytest.approx((100+55+100+100)/(6*255))


def test_support_and_endpoint_floors_do_not_double_count():
    image=np.zeros((2,2,3),np.uint8);reference=np.full_like(image,100)
    application=np.zeros((2,2),bool);application[0,0]=True
    scoring=np.ones((2,2),bool)
    r=irrecoverable_rgb_floor(image,reference,application,scoring)
    assert r['rgb_mae_lower_bound']==pytest.approx(100/255)
    assert r['outside_support_rgb_mae_floor']==pytest.approx(75/255)
    assert r['inside_endpoint_rgb_mae_floor']==pytest.approx(25/255)


def test_bound_holds_across_positive_parameters_and_inputs_unchanged():
    rng=np.random.default_rng(42)
    image=rng.integers(0,256,(10,10,3),dtype=np.uint8);image[:3]=0;image[3:5,:,1]=255
    reference=rng.integers(0,256,image.shape,dtype=np.uint8);before=image.copy()
    application=rng.random((10,10))>.3;scoring=rng.random((10,10))>.2
    floor=irrecoverable_rgb_floor(image,reference,application,scoring)['rgb_mae_lower_bound']
    for params in ([.25,.5,2.],[1.,1.,1.],[4.,4.,.25]):
        output=image.copy();output[application]=np.rint(transform_rgb(image.astype(float)/255,*params)[application]*255).astype(np.uint8)
        assert np.abs(output.astype(float)-reference)[scoring].mean()/255+1e-12>=floor
    np.testing.assert_array_equal(image,before)


def test_invalid_images_and_masks_rejected():
    image=np.zeros((2,2,3),np.uint8);mask=np.ones((2,2),bool)
    with pytest.raises(ValueError):irrecoverable_rgb_floor(image.astype(float),image,mask,mask)
    with pytest.raises(ValueError):irrecoverable_rgb_floor(image,image,mask.astype(np.uint8),mask)
    with pytest.raises(ValueError):irrecoverable_rgb_floor(image,image,mask,~mask)
