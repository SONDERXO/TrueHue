import numpy as np
import pytest
from src.model_training.whole_scene_features import scene_features,SCENE_FEATURES


def test_constant_neutral_scene_has_zero_ratios_and_no_endpoints():
    image=np.full((12,12,3),100,np.uint8);before=image.copy();f=scene_features(image)
    assert tuple(f)==SCENE_FEATURES and f['scene_log_r_over_g']==f['scene_log_b_over_g']==0
    assert f['scene_l_p10']==f['scene_l_p50']==f['scene_l_p90']
    assert f['scene_any_zero_fraction']==f['scene_any_full_fraction']==0
    assert np.array_equal(image,before)


def test_rgb_channel_order_and_fixed_code_stabilizer():
    image=np.zeros((2,3,3),np.uint8);image[:,:,0]=255
    f=scene_features(image)
    assert f['scene_log_r_over_g']==float(np.log(256)) and f['scene_log_b_over_g']==0
    assert f['scene_any_zero_fraction']==f['scene_any_full_fraction']==1


def test_linear_quantiles_and_endpoint_fractions():
    image=np.zeros((10,10,3),np.uint8);image[5:]=255;f=scene_features(image)
    assert f['scene_l_p10']==0 and f['scene_l_p50']==50 and f['scene_l_p90']==100
    assert f['scene_any_zero_fraction']==f['scene_any_full_fraction']==.5


@pytest.mark.parametrize('value',[np.zeros((2,2),np.uint8),np.zeros((2,2,3),float),np.zeros((0,2,3),np.uint8),None])
def test_invalid_scene_rejects(value):
    with pytest.raises(ValueError):scene_features(value)
