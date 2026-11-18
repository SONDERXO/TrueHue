import numpy as np
import pytest
from src.model_training.histogram_gap_features import histogram_gap_features,NAMES

def test_hand_count_and_rgb_order():
    image=np.array([[[0,128,1],[2,130,1]]],dtype=np.uint8)
    result=histogram_gap_features(image)
    assert list(result['features'])==list(NAMES)
    assert list(result['features'].values())==[1/3,0.,0.,1/3,0.,0.]

def test_full_constant_and_empty_conventions():
    full=np.repeat(np.arange(256,dtype=np.uint8)[None,:,None],3,axis=2)
    assert not any(histogram_gap_features(full)['features'].values())
    const=np.full((2,2,3),128,np.uint8);before=const.copy();r=histogram_gap_features(const)
    assert not any(r['features'].values()) and r['channels'][0]['bands'][0]['band_outside_observed_range']
    assert np.array_equal(before,const)
    assert not histogram_gap_features(np.empty((0,2,3),np.uint8))['valid']

def test_replication_preserves_code_support_not_counts():
    image=np.array([[[10,20,30],[15,25,35],[128,130,140]]],np.uint8)
    repeated=np.repeat(np.repeat(image,4,axis=0),3,axis=1)
    assert histogram_gap_features(image)['features']==histogram_gap_features(repeated)['features']

@pytest.mark.parametrize('image',[None,np.zeros((2,2,3)),np.zeros((2,2),np.uint8),np.zeros((2,2,4),np.uint8)])
def test_malformed_rejected(image):
    with pytest.raises(ValueError):histogram_gap_features(image)
