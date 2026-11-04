"""Experimental face-oval restriction; does not alter the frozen V2 pipeline."""
import cv2
import numpy as np

# Ordered MediaPipe face-oval contour, using the shared 468-point topology.
FACE_OVAL = (10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
             397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
             172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109)


def restrict_to_face_outline(v2_mask, landmarks):
    """Intersect V2 with a filled oval; never add pixels or fill V2 holes.

    Points must already be mapped to the selected face crop. Rasterize the
    original polygon without clamping individual vertices, which would distort
    contours at image edges. OpenCV clips the raster to the crop bounds.
    """
    if v2_mask.ndim != 2 or v2_mask.dtype != np.uint8 or not v2_mask.size:
        raise ValueError("Expected a nonempty uint8 mask")
    points = np.asarray(landmarks)
    if points.ndim != 2 or points.shape[0] <= max(FACE_OVAL) or points.shape[1] < 2:
        raise ValueError("Expected face landmarks in crop pixel coordinates")
    contour = points[list(FACE_OVAL), :2]
    if not np.isfinite(contour).all() or np.abs(contour).max() > 1e6:
        raise ValueError("Invalid face-oval coordinates")
    polygon = np.rint(contour).astype(np.int32)
    if abs(cv2.contourArea(polygon)) < 1:
        raise ValueError("Degenerate face oval")
    oval = np.zeros_like(v2_mask)
    cv2.fillPoly(oval, [polygon], 255)
    return cv2.bitwise_and(v2_mask, oval), oval
