import numpy as np
import pytest
from src.distortion_generation.three_variant_recipe import render_rgb,VARIANTS
from src.distortion_generation.paper_gamma import composite_rgb


@pytest.mark.parametrize('group',['light','medium','dark'])
def test_combined_matches_previous_versioned_direct_gamma_candidate(group):
    image=np.random.default_rng(42).integers(0,256,(20,20,3),dtype=np.uint8)
    expected,report=composite_rgb(image,group);actual,current=render_rgb(image,group,'combined')
    np.testing.assert_array_equal(actual,expected)
    for key in ['clipped_pixels','clipped_channel_samples','total_channel_samples']:assert current[key]==report[key]


def test_exposure_preserves_achromatic_color_and_color_preserves_green():
    gray=np.full((10,10,3),128,np.uint8)
    exposure,_=render_rgb(gray,'medium','exposure')
    assert np.array_equal(exposure[:,:,0],exposure[:,:,1]) and np.array_equal(exposure[:,:,1],exposure[:,:,2])
    color,_=render_rgb(gray,'medium','color')
    np.testing.assert_array_equal(color[:,:,1],gray[:,:,1])
    assert color[0,0,0]<128 and color[0,0,2]>128


def test_variant_calls_never_mutate_shared_reference():
    image=np.full((8,8,3),128,np.uint8);original=image.copy()
    for variant in VARIANTS:render_rgb(image,'light',variant)
    np.testing.assert_array_equal(image,original)


def test_clipping_is_reported_not_silently_treated_as_invertible():
    image=np.zeros((2,2,3),np.uint8)
    result,report=render_rgb(image,'dark','color')
    assert report['clipped_pixels']==4 and report['clipped_channel_samples']==4
    assert result[0,0,2]>0


def test_unknown_variant_does_not_fall_back_to_combined():
    with pytest.raises(ValueError):render_rgb(np.zeros((2,2,3),np.uint8),'light','unknown')
