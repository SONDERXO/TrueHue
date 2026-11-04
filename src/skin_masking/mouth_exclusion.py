"""Complete-mouth exclusion for the explicit v2_complete_mouth_v1 pipeline."""
import cv2
import numpy as np

# Ordered outer lip boundary in MediaPipe's shared face-landmark topology.
OUTER_LIPS = (61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
              375, 321, 405, 314, 17, 84, 181, 91, 146)


def exclude_complete_mouth(v2_mask, landmarks):
    """Remove the filled outer-mouth region from V2 without adding skin pixels.

    This retains all baseline exclusions, including its lower-mouth polygon.
    Vertices are clipped/truncated using the existing exclusion convention.
    Missing/nonfinite/degenerate geometry fails explicitly, with no fallback.
    """
    if v2_mask.ndim != 2 or v2_mask.dtype != np.uint8 or not v2_mask.size:
        raise ValueError("Expected a nonempty uint8 mask")
    points = np.asarray(landmarks)
    if points.ndim != 2 or points.shape[0] <= max(OUTER_LIPS) or points.shape[1] < 2:
        raise ValueError("Expected landmarks in face-crop pixel coordinates")
    contour = points[list(OUTER_LIPS), :2]
    if not np.isfinite(contour).all():
        raise ValueError("Nonfinite mouth coordinates")
    h, w = v2_mask.shape
    polygon = np.clip(contour, (0, 0), (w-1, h-1)).astype(np.int32)
    if abs(cv2.contourArea(polygon)) < 1:
        raise ValueError("Degenerate mouth polygon")
    mouth = np.zeros_like(v2_mask)
    cv2.fillPoly(mouth, [polygon], 255)
    return cv2.bitwise_and(v2_mask, cv2.bitwise_not(mouth)), mouth
