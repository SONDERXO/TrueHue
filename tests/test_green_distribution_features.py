import numpy as np
import pytest
from src.model_training.green_distribution_features import green_distribution_features,ADDITIONS

def test_uses_green_and_only_selected_pixels():
    im=np.zeros((256,256,3),np.uint8);im[:,:,0]=255;im[:,:,2]=99
    im[:40,:25,1]=np.arange(1000).reshape(40,25)%256
    mask=np.zeros((256,256),np.uint8);mask[:40,:25]=255
    r=green_distribution_features(im,mask);v=im[:40,:25,1].reshape(-1)
    q=np.percentile(v,[10,50,90],method='linear')
    assert r['valid'] and r['skin_pixels']==1000
    assert list(r['features'].values())==[*q,float(np.log((q[2]+1)/(q[0]+1)))]

def test_zero_green_has_finite_zero_contrast():
    r=green_distribution_features(np.zeros((256,256,3),np.uint8),np.full((256,256),255,np.uint8))
    assert r['features']==dict.fromkeys(ADDITIONS,0.)

def test_guard_returns_unavailable_without_imputation():
    mask=np.zeros((256,256),np.uint8);mask.flat[:999]=255
    r=green_distribution_features(np.zeros((256,256,3),np.uint8),mask)
    assert not r['valid'] and r['features'] is None

def test_rejects_nonbinary_or_wrong_coordinate_support():
    with pytest.raises(ValueError):green_distribution_features(np.zeros((256,256,3),np.uint8),np.ones((256,256),np.uint8))
    with pytest.raises(ValueError):green_distribution_features(np.zeros((224,224,3),np.uint8),np.zeros((224,224),np.uint8))
