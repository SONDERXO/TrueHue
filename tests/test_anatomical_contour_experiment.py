import numpy as np
import pytest

from src.skin_masking.anatomical_contour_experiment import removal, extend


def fixture_masks():
    image = np.full((64,64,3),128,np.uint8)
    old = np.zeros((64,64),bool)
    old[10:54,10:54] = True
    excluded = np.zeros_like(old)
    excluded[28:32,28:32] = True
    cats = np.full(old.shape,3,np.uint8)
    return image,old,excluded,cats


def test_exclusions_override_old_support_and_new_additions():
    image,old,excluded,cats = fixture_masks()
    result,_ = extend(image,old,excluded,old,cats,old,[8,8,48,48],True)
    assert not (result & excluded).any()
    assert np.array_equal(old & ~result,old & excluded)
    assert result[9,20]  # one-pixel local extension
    assert not result[7,20]  # extension limited to ceil(.02*48)=1
    assert np.array_equal(removal(old,excluded),old & ~excluded)


def test_added_hair_clothing_and_body_skin_are_rejected():
    image,old,excluded,cats = fixture_masks()
    for category in (0,1,2,4,5):
        cats[9,:] = category
        result,_ = extend(image,old,excluded,old,cats,old,[8,8,48,48],True)
        assert not result[9,:].any()


def test_failed_geometry_and_insufficient_seeds_never_fall_back():
    image,old,excluded,cats = fixture_masks()
    with pytest.raises(ValueError,match='geometry gate'):
        extend(image,old,excluded,old,cats,old,[8,8,48,48],False)
    with pytest.raises(ValueError,match='1000'):
        extend(image,old,excluded,old,cats,np.zeros_like(old),[8,8,48,48],True)


def test_relative_material_gate_rejects_dissimilar_new_pixels():
    image,old,excluded,cats = fixture_masks()
    image[9,:] = [255,0,0]
    result,_ = extend(image,old,excluded,old,cats,old,[8,8,48,48],True)
    assert not result[9,:].any()
