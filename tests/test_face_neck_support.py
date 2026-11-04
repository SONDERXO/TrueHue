import numpy as np
import pytest
from src.skin_masking.face_neck_support import build_face_neck_support,apply_shared_parameters


def example():
    im=np.full((100,100,3),(80,120,160),np.uint8)
    face=np.zeros((100,100),np.uint8);face[10:50,25:75]=255
    cats=np.zeros((100,100),np.uint8);cats[face>0]=1;cats[50:80,35:65]=14
    return im,face,cats


def test_neck_extends_below_face_and_measurement_is_unchanged():
    im,face,cats=example();before=face.copy()
    r=build_face_neck_support(im,face,cats,face_count=1)
    assert r.neck_mask[70,50]==255 and np.array_equal(r.measurement_mask,before)
    assert np.array_equal(face,before) and not np.shares_memory(r.measurement_mask,face)
    assert not r.neck_mask[face>0].any()


@pytest.mark.parametrize('label',[0,6,7,8,9,15,16,17,18])
def test_non_neck_predicted_classes_stay_excluded(label):
    im,face,cats=example();cats[50:80,35:65]=label
    r=build_face_neck_support(im,face,cats,face_count=1)
    assert not r.neck_mask.any()
    assert np.array_equal(r.correction_mask,face)


def test_disconnected_other_person_neck_not_selected():
    im,face,cats=example();cats[80:90,0:10]=14
    r=build_face_neck_support(im,face,cats,face_count=1)
    assert not r.neck_mask[80:90,0:10].any()


def test_explicit_protected_pixels_and_outside_remain_unchanged():
    im,face,cats=example();protected=np.zeros((100,100),bool);protected[40:70,45:55]=True
    r=build_face_neck_support(im,face,cats,face_count=1,protected=protected)
    result=apply_shared_parameters(im,r,.8,1.1,.9)
    assert np.array_equal(result[protected],im[protected])
    assert np.array_equal(result[r.correction_mask==0],im[r.correction_mask==0])
    assert (result[r.neck_mask>0]!=im[r.neck_mask>0]).any()


def test_multiple_faces_fail_without_body_fallback():
    im,face,cats=example()
    with pytest.raises(ValueError):build_face_neck_support(im,face,cats,face_count=2)
