import numpy as np
import pytest
from src.skin_masking.graphcut_correction_support import graphcut_correction_support


def test_refinement_can_remove_baseline_dark_material_without_losing_central_skin():
    image=np.full((100,100,3),[10,10,10],np.uint8)
    image[10:90,10:90]=[100,140,180]
    image[10:90,80:90]=[10,10,10]
    mask=np.zeros((100,100),bool);mask[10:90,10:90]=True
    excluded=np.zeros_like(mask);excluded[60:65,45:55]=True;mask[excluded]=False
    old_image=image.copy();old_mask=mask.copy()
    result=graphcut_correction_support(image,mask,excluded)
    assert not result[20:80,82:89].any()
    assert result[30:55,30:70].all() and not result[excluded].any()
    assert not result[~mask].any()
    np.testing.assert_array_equal(image,old_image);np.testing.assert_array_equal(mask,old_mask)
    np.testing.assert_array_equal(result,graphcut_correction_support(image,mask,excluded))


def test_no_reliable_input_skin_fails_instead_of_filling_face_box():
    with pytest.raises(ValueError):
        graphcut_correction_support(np.zeros((100,100,3),np.uint8),np.zeros((100,100),bool),np.zeros((100,100),bool))
