import numpy as np
import pytest
from src.distortion_generation.paper_gamma import transform_rgb,legacy_to_paper_parameters,composite_rgb,COMPOSITE_VERSION
from src.distortion_generation.generate_distortions import transform_rgb as legacy


def test_gamma_direction_matches_proposal_definition():
    image=np.full((2,2,3),.25)
    np.testing.assert_allclose(transform_rgb(image,.5),.5)
    np.testing.assert_allclose(transform_rgb(image,2.),.0625)
    np.testing.assert_array_equal(transform_rgb(image,1.),image)


@pytest.mark.parametrize('gamma',[.25,.7,1.,2.,4.])
def test_explicit_conversion_preserves_legacy_prediction_pixels(gamma):
    image=np.random.default_rng(42).uniform(.01,.9,(10,10,3))
    original=image.copy();params=legacy_to_paper_parameters(gamma,.9,1.1)
    np.testing.assert_allclose(transform_rgb(image,**params),legacy(image,gamma,.9,1.1),rtol=0,atol=1e-14)
    np.testing.assert_array_equal(image,original)


@pytest.mark.parametrize('gamma',[0,-1,float('nan'),float('inf'),True])
def test_invalid_gamma_not_used(gamma):
    with pytest.raises(ValueError):transform_rgb(np.full((2,2,3),.5),gamma)


def test_composite_is_explicitly_versioned_and_does_not_mutate_source():
    from src.distortion_generation.table2_composite import composite_rgb as old_composite
    image=np.full((4,4,3),128,np.uint8);original=image.copy()
    old,_=old_composite(image,'medium');new,report=composite_rgb(image,'medium')
    assert new.mean()>old.mean() and report['transform_version']==COMPOSITE_VERSION
    assert report['total_channel_samples']==image.size
    np.testing.assert_array_equal(image,original)


def test_uint8_input_is_not_silently_treated_as_normalized_rgb():
    with pytest.raises(ValueError):transform_rgb(np.full((2,2,3),128,np.uint8),.7)
