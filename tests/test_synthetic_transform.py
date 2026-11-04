import numpy as np
import pytest
from src.distortion_generation.generate_distortions import transform_rgb, inverse_parameters


@pytest.mark.parametrize('params',[(.7,.85,.95),(1.25,1.08,.95),(1,.85,1.15)])
def test_analytic_inverse_recovers_unclipped_samples(params):
    image=np.random.default_rng(42).uniform(0,.5,(20,30,3))
    original=image.copy()
    distorted=transform_rgb(image,*params)
    restored=transform_rgb(distorted,**inverse_parameters(*params))
    np.testing.assert_allclose(restored,image,atol=1e-12,rtol=0)
    assert np.array_equal(image,original)


def test_gamma_convention_rgb_channel_order_and_green_gain():
    image=np.full((1,1,3),.25)
    np.testing.assert_allclose(transform_rgb(image,2,1,.5),[[[.5,.5,.25]]])
    assert inverse_parameters(2,2,.5)=={'gamma':.5,'red_gain':.25,'blue_gain':4}


def test_clipping_is_irreversible_and_quantization_is_separate():
    image=np.full((1,1,3),.9)
    raw=transform_rgb(image,1,2,1,clip=False)
    assert raw[0,0,0]>1
    restored=transform_rgb(np.clip(raw,0,1),**inverse_parameters(1,2,1))
    assert restored[0,0,0]==.5 and restored[0,0,0]!=image[0,0,0]


@pytest.mark.parametrize('params',[(0,1,1),(-1,1,1),(1,0,1),(1,1,float('nan')),(float('inf'),1,1)])
def test_invalid_parameters_rejected(params):
    with pytest.raises(ValueError):
        transform_rgb(np.zeros((1,1,3),float),*params)


@pytest.mark.parametrize('image',[np.zeros((2,2,3),np.uint8),np.zeros((2,2)),
    np.full((2,2,3),np.nan),np.full((2,2,3),1.1)])
def test_invalid_images_rejected(image):
    with pytest.raises(ValueError):
        transform_rgb(image,1,1,1)
