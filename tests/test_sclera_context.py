from copy import deepcopy
import math
import numpy as np
import cv2
import pytest
from src.model_training.sclera_context import extract_sclera_context
from src.skin_masking.landmark_exclusion import FEATURE_INDICES

def fixture():
    image=np.full((256,256,3),[150,100,85],np.uint8);cat=np.zeros((256,256),np.uint8);points=np.zeros((478,2));truth=np.zeros((256,256),bool);irises=np.zeros_like(truth)
    for name,x,center,ring,label in [('right_eye',80,468,[469,470,471,472],5),('left_eye',176,473,[474,475,476,477],4)]:
        angle=np.arange(16)*2*np.pi/16;contour=np.c_[x+18*np.cos(angle),100+9*np.sin(angle)]
        points[FEATURE_INDICES[name]]=contour;points[center]=[x,100]
        points[ring]=[[x+6,100],[x,106],[x-6,100],[x,94]]
        aperture=np.zeros_like(cat);cv2.fillPoly(aperture,[np.rint(contour).astype(np.int32)],255)
        iris=np.zeros_like(cat);cv2.circle(iris,(x,100),6,255,-1)
        cat[aperture>0]=label;image[aperture>0]=[210,205,200];image[iris>0]=[45,55,65]
        truth|=(aperture>0)&(iris==0);irises|=iris>0
    return image,cat,points,truth,irises

def test_valid_geometry_selection_independent_ratios_and_inputs_immutable():
    image,cat,points,truth,iris=fixture();copies=[a.copy() for a in [image,cat,points]]
    result=extract_sclera_context(image,cat,points);assert result['valid']
    assert not (result['mask']&~truth).any() and not (result['mask']&iris).any()
    assert result['features']['sclera_context_available']==1
    assert math.isclose(result['features']['sclera_context_log_r_over_g'],math.log(211/206),abs_tol=1e-15)
    assert math.isclose(result['features']['sclera_context_log_b_over_g'],math.log(201/206),abs_tol=1e-15)
    assert all(np.array_equal(a,b) for a,b in zip([image,cat,points],copies))

@pytest.mark.parametrize('mode',['missing_iris','sunglasses','one_covered','closed','off_center'])
def test_missing_is_flagged_not_fake_neutral_measurement(mode):
    image,cat,points,*_=fixture()
    if mode=='missing_iris':points=points[:468]
    if mode=='sunglasses':cat[np.isin(cat,[4,5])]=6
    if mode=='one_covered':cat[cat==4]=6
    if mode=='closed':points[FEATURE_INDICES['left_eye']]=[176,100]
    if mode=='off_center':points[473]=[1,1]
    r=extract_sclera_context(image,cat,points)
    assert not r['valid'] and not r['mask'].any() and list(r['features'].values())==[0.,0.,0.]

def test_labelled_skin_removed_but_mislabelled_skin_not_magically_detected():
    image,cat,points,truth,_=fixture();patch=np.zeros_like(truth);patch[96:99,165:168]=True
    image[patch]=[170,90,65];cat[patch]=1
    good=extract_sclera_context(image,cat,points);assert not good['mask'][patch].any()
    cat[patch]=4;bad=extract_sclera_context(image,cat,points)
    assert bad['mask'][patch].any() and not bad['actual_sclera_validated']

def test_coloured_sclera_is_measured_without_whitening():
    image,cat,points,truth,_=fixture();image[truth]=[180,155,130]
    r=extract_sclera_context(image,cat,points)
    assert r['valid'] and r['eyes'][0]['mean_RGB']==[180.,155.,130.]
    assert r['features']['sclera_context_log_r_over_g']>0

def test_malformed_rejected():
    image,cat,points,*_=fixture()
    with pytest.raises(ValueError):extract_sclera_context(image.astype(float),cat,points)
    with pytest.raises(ValueError):extract_sclera_context(image,cat.astype(float),points)
    points[0]=float('nan')
    with pytest.raises(ValueError):extract_sclera_context(image,cat,points)
