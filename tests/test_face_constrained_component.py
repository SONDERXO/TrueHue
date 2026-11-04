import numpy as np
import pytest
from src.skin_masking.face_constrained_component import face_constrained_component


def test_selects_facial_component_instead_of_larger_background_component():
    candidate=np.zeros((20,20),np.uint8);candidate[:10,:10]=255;candidate[12:17,12:17]=255
    oval=np.zeros_like(candidate);oval[11:19,11:19]=255
    excluded=np.zeros_like(candidate);excluded[14,14]=255
    result=face_constrained_component(candidate,oval,excluded)
    assert np.count_nonzero(result)==24
    assert result[12,12]==255 and result[0,0]==0 and result[14,14]==0


def test_never_adds_color_support_or_fills_excluded_holes():
    candidate=np.full((8,8),255,np.uint8);candidate[3,3]=0
    oval=np.full_like(candidate,255);excluded=np.zeros_like(candidate);excluded[4,4]=255
    result=face_constrained_component(candidate,oval,excluded)
    assert result[3,3]==result[4,4]==0
    assert not np.any((result>0)&(candidate==0))


def test_empty_colors_stay_empty_but_missing_contour_fails():
    empty=np.zeros((8,8),np.uint8);full=np.full_like(empty,255)
    assert not face_constrained_component(empty,full,empty).any()
    with pytest.raises(ValueError):face_constrained_component(full,empty,empty)


def test_invalid_binary_geometry_rejected():
    with pytest.raises(ValueError):face_constrained_component(np.ones((8,8),np.uint8),np.full((8,8),255,np.uint8),np.zeros((8,8),np.uint8))
