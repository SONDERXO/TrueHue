"""Development-only geometric support completion; not an ITA estimation mask."""
import cv2
import numpy as np


def complete_correction_support(input_mask, exclusion_mask):
    """Bridge gaps with the convex hull of input skin, restoring exclusions.

    No reference image or reference mask is accepted. This may include non-skin
    inside the hull, so it requires visual review and is not a production mask.
    Empty or degenerate input fails explicitly rather than filling a face box.
    """
    mask = np.asarray(input_mask); excluded = np.asarray(exclusion_mask)
    if mask.ndim != 2 or mask.dtype != bool or excluded.dtype != bool or excluded.shape != mask.shape:
        raise ValueError('Expected matching 2D boolean masks')
    points = cv2.findNonZero(mask.astype(np.uint8))
    if points is None or len(points) < 3:
        raise ValueError('Insufficient input skin support')
    hull = cv2.convexHull(points)
    if cv2.contourArea(hull) <= 0:
        raise ValueError('Degenerate input skin support')
    filled = np.zeros(mask.shape,np.uint8)
    cv2.fillConvexPoly(filled,hull,1)
    return (filled > 0) & ~excluded
