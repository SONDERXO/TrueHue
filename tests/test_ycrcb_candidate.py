import cv2
import numpy as np
import pytest
from src.skin_masking.ycrcb_candidate import ycrcb_color_candidate


def test_fixed_chroma_rule_retains_supported_patches_at_different_brightness():
    for luminance in [80,160]:
        encoded=np.full((20,20,3),[luminance,150,100],np.uint8)
        image=cv2.cvtColor(encoded,cv2.COLOR_YCrCb2BGR)
        assert np.all(ycrcb_color_candidate(image)==255)
    unsupported=cv2.cvtColor(np.full((20,20,3),[120,100,100],np.uint8),cv2.COLOR_YCrCb2BGR)
    assert not ycrcb_color_candidate(unsupported).any()


def test_no_new_threshold_admits_exact_gray():
    image=np.full((20,20,3),128,np.uint8)
    assert not ycrcb_color_candidate(image).any()


def test_bad_image_is_not_treated_as_empty_skin():
    with pytest.raises(ValueError):ycrcb_color_candidate(np.zeros((5,5),np.uint8))
