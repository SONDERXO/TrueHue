import numpy as np
import pytest
from src.skin_masking.material_checked_support import material_checked_support


@pytest.mark.parametrize('bgr',[(55,75,100),(130,160,190)])
def test_relative_color_recovers_matching_interior_for_different_seed_brightness(bgr):
    image = np.full((100,100,3),bgr,np.uint8)
    mask = np.zeros((100,100),bool); mask[10:90,10:20] = True; mask[10:90,80:90] = True
    original = image.copy()
    excluded = np.zeros_like(mask); excluded[45:55,45:55] = True
    result = material_checked_support(image,mask,excluded)
    assert result[30,50] and not result[excluded].any()
    assert np.all(result[mask]) and not result[:10].any()
    np.testing.assert_array_equal(image,original)


def test_vivid_paint_and_dissimilar_dark_material_not_added_but_baseline_is_preserved():
    image = np.full((100,100,3),(130,160,190),np.uint8)
    mask = np.zeros((100,100),bool); mask[10:90,10:20] = True; mask[10:90,80:90] = True
    image[30:40,40:60] = [255,0,255]; image[60:70,40:60] = [10,10,10]
    result = material_checked_support(image,mask,np.zeros_like(mask))
    assert not result[30:40,40:60].any() and not result[60:70,40:60].any()
    assert result[50,50] and np.all(result[mask])


def test_unreliable_seed_and_mismatched_image_fail_explicitly():
    mask = np.zeros((100,100),bool); mask[10:20,10:20] = True
    with pytest.raises(ValueError,match='1000'): material_checked_support(np.zeros((100,100,3),np.uint8),mask,np.zeros_like(mask))
    mask[:] = True
    with pytest.raises(ValueError,match='dimensions'): material_checked_support(np.zeros((50,50,3),np.uint8),mask,np.zeros_like(mask))
