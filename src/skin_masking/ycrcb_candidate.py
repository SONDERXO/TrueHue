"""Existing detailed-method YCrCb color gate; no runtime masking replacement."""
import cv2
import numpy as np


def ycrcb_color_candidate(crop):
    """Use the pre-existing ablation's exact thresholds and morphology."""
    if not isinstance(crop,np.ndarray) or crop.dtype!=np.uint8 or crop.ndim!=3 or crop.shape[2]!=3 or not crop.size:
        raise ValueError('Nonempty uint8 BGR crop required')
    raw=cv2.inRange(cv2.cvtColor(crop,cv2.COLOR_BGR2YCrCb),
        np.array([0,133,77],np.uint8),np.array([255,173,127],np.uint8))
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    for operation in (cv2.MORPH_OPEN,cv2.MORPH_CLOSE,cv2.MORPH_CLOSE):
        raw=cv2.morphologyEx(raw,operation,kernel)
    return raw
