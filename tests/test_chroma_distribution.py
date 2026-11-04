import cv2
import numpy as np
import pytest
from src.model_training.chroma_distribution import chroma_distribution_features


def test_two_colors_have_analytic_spread_and_population_covariance():
    image=np.zeros((40,50,3),np.uint8)
    image[:20]=[30,80,140];image[20:]=[160,120,40]
    result=chroma_distribution_features(image,np.ones((40,50),bool))
    lab=cv2.cvtColor(np.array([[[30,80,140],[160,120,40]]],np.uint8),cv2.COLOR_BGR2LAB)[0].astype(float)
    # Shared measurement convention rounds conventional Lab to float32.
    lab[:,0]=lab[:,0].astype(np.float32)*np.float32(100/255)
    lab[:,1:]-=128
    delta=lab[1]-lab[0]
    expected=[abs(delta[1]),abs(delta[2]),delta[0]*delta[1]/4,delta[0]*delta[2]/4]
    np.testing.assert_allclose(list(result['features'].values()),expected,rtol=0,atol=1e-6)


def test_unselected_pixels_cannot_supply_features():
    image=np.full((40,50,3),80,np.uint8);mask=np.zeros((40,50),bool);mask[:20]=True
    before=chroma_distribution_features(image,mask)
    image[~mask]=[255,0,127]
    assert before==chroma_distribution_features(image,mask)
    assert all(v==0 for v in before['features'].values())


def test_pixel_minimum_and_mask_contract():
    image=np.zeros((40,50,3),np.uint8);mask=np.zeros((40,50),bool);mask.flat[:999]=True
    assert not chroma_distribution_features(image,mask)['valid']
    mask.flat[999]=True
    assert chroma_distribution_features(image,mask)['valid']
    with pytest.raises(ValueError):chroma_distribution_features(image,mask.astype(np.uint8))
