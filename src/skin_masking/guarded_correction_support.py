"""Experimental interior-only additions; estimation masks remain unchanged."""
import cv2
import numpy as np
from src.skin_masking.correction_support_experiment import complete_correction_support


def guarded_correction_support(input_mask, exclusion_mask):
    """Keep baseline support, admitting new pixels only away from boundaries.

    New pixels must be >3% of the smaller crop dimension inside the hull and
    >2% away from anatomical exclusions (minimum 2 pixels for each). These
    fixed geometric rules are developmental, not skin classification guarantees.
    Existing baseline errors are deliberately not hidden or repaired here.
    """
    hull = complete_correction_support(input_mask, exclusion_mask)
    # Obtain the solid hull before anatomical holes for the outer-edge distance.
    solid = complete_correction_support(input_mask,np.zeros_like(exclusion_mask))
    outer = cv2.distanceTransform(np.pad(solid.astype(np.uint8),1),cv2.DIST_L2,
                                  cv2.DIST_MASK_PRECISE)[1:-1,1:-1]
    if exclusion_mask.any():
        away = cv2.distanceTransform((~exclusion_mask).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
    else:
        away = np.full(input_mask.shape,np.inf)
    scale = min(input_mask.shape)
    additions = hull & ~input_mask & (outer > max(2.,.03*scale)) & (away > max(2.,.02*scale))
    return (input_mask & ~exclusion_mask) | additions
