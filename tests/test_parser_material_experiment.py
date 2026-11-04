import cv2
import numpy as np
import pytest

from src.skin_masking.parser_material_experiment import combined_supports


def inputs():
    image=np.full((64,64,3),140,np.uint8)
    dense=np.ones((64,64),bool);categories=np.full(dense.shape,3,np.uint8)
    excluded=np.zeros_like(dense);measurement=np.zeros_like(dense);measurement[12:52,12:52]=True
    return image,dense,categories,excluded,[8,8,48,48],measurement


def test_anatomical_and_spatial_vetoes_override_all_support():
    args=inputs();args[3][25,25]=True;args[2][25,26]=1;args[1][25,27]=False
    arms,*_=combined_supports(*args)
    for value in arms.values():
        assert not value[25,25:28].any()
        assert not value[0,:].any()


def test_chroma_arm_omits_only_lightness_and_full_is_subset():
    args=inputs();args[0][30,55]=[30,30,30]
    arms,*_=combined_supports(*args)
    assert arms['A'][30,55] and arms['C'][30,55]
    assert not arms['F'][30,55]
    assert not (arms['F'] & ~arms['C']).any()


def test_strong_red_material_is_rejected_without_annotation():
    args=inputs();args[0][30,55]=[0,0,255]
    arms,*_=combined_supports(*args)
    assert arms['A'][30,55]
    assert not arms['F'][30,55] and not arms['C'][30,55]


def test_insufficient_seeds_fails_without_reference_fallback():
    args=inputs();args[5][:]=False
    with pytest.raises(ValueError,match='1000'):combined_supports(*args)
