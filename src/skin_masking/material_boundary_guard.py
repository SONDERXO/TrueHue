"""Fixed two-native-pixel uncertainty margin around chroma material outliers."""
import cv2
import numpy as np


def guard_material_boundary(base,chroma):
    if base.dtype!=bool or chroma.dtype!=bool or base.ndim!=2 or base.shape!=chroma.shape or not base.size:
        raise ValueError('Matching nonempty boolean masks required')
    if (chroma & ~base).any():raise ValueError('Chroma mask must be a subset of anatomical base')
    outliers=base & ~chroma
    if not outliers.any():return chroma.copy(),outliers
    distance=cv2.distanceTransform((~outliers).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
    return chroma & (distance>2),outliers
