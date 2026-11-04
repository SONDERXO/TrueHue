import numpy as np
import pytest
from src.model_training.facial_brightness_features import facial_brightness_features


def test_pixels_outside_input_mask_cannot_change_features():
    image=np.full((80,80,3),100,np.uint8);mask=np.zeros((80,80),bool);mask[10:70,10:70]=True
    a=facial_brightness_features(image,mask);image[~mask]=255
    assert a==facial_brightness_features(image,mask) and a['valid']


def test_left_right_brightness_direction_and_no_fabricated_vertical_difference():
    image=np.full((64,64,3),50,np.uint8);image[:,32:]=180
    r=facial_brightness_features(image,np.ones((64,64),bool))
    assert r['valid'] and r['features']['input_l_left_minus_right']<0
    assert r['features']['input_l_top_minus_bottom']==0 and r['features']['input_l_iqr']>0


def test_insufficient_or_skewed_support_is_unavailable_not_imputed():
    image=np.full((64,64,3),100,np.uint8);mask=np.zeros((64,64),bool);mask[:20,:20]=True
    assert not facial_brightness_features(image,mask)['valid']
    mask[:]=False;mask[1:50,1:26]=True;mask[63,63]=True
    assert facial_brightness_features(image,mask)['reason']=='fewer_than_100_pixels_in_half'


def test_nonboolean_mask_rejected():
    with pytest.raises(ValueError):facial_brightness_features(np.zeros((64,64,3),np.uint8),np.ones((64,64),np.uint8))
