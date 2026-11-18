import numpy as np
import pytest
from src.evaluation.gamma_identity_feasibility import fixed_gain_identity_bounds


def test_neutral_gamma_is_inside_neutral_gain_interval_and_input_is_unchanged():
    image=np.arange(3*8*8,dtype=np.uint8).reshape(8,8,3);before=image.copy()
    result=fixed_gain_identity_bounds(image,np.ones((8,8),bool),1.,1.)
    assert not result['fixed_gain_identity_impossible']
    assert result['necessary_gamma_lower']<=1<=result['necessary_gamma_upper']
    np.testing.assert_array_equal(image,before)


def test_one_gamma_cannot_restore_conflicting_same_level_red_and_green():
    image=np.full((1,1,3),128,np.uint8)
    result=fixed_gain_identity_bounds(image,np.ones((1,1),bool),1.2,1.)
    assert result['fixed_gain_identity_impossible']
    assert result['necessary_gamma_lower']>result['necessary_gamma_upper']
    # Red needs gamma>1 to cancel its gain; green must stay near1.
    assert result['lower_witness']['channel']==0
    assert result['upper_witness']['channel']==1


def test_full_channel_attenuation_certificate_and_empty_mask_rejection():
    image=np.full((1,1,3),255,np.uint8)
    result=fixed_gain_identity_bounds(image,np.ones((1,1),bool),1.,.9)
    assert result['fixed_gain_identity_impossible'] and result['endpoint_witness']['channel']==2
    with pytest.raises(ValueError):fixed_gain_identity_bounds(image,np.zeros((1,1),bool),1.,1.)
