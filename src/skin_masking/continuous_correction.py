"""Fill enclosed correction gaps only; preserve the measurement contract."""
import cv2
import numpy as np
from src.skin_masking.face_neck_support import FaceNeckSupport

VERSION = 'enclosed_correction_holes_v1'


def fill_correction_holes(mask, *, protected=None):
    if not isinstance(mask, np.ndarray) or mask.dtype != np.uint8 or mask.ndim != 2 or not mask.size or not set(np.unique(mask)) <= {0, 255}:
        raise ValueError('Nonempty binary uint8 correction mask required')
    if protected is not None and (protected.dtype != bool or protected.shape != mask.shape):
        raise ValueError('Matching boolean protection required')
    # Padding gives one known exterior even when support touches the image edge.
    selected = np.pad(mask > 0, 1)
    exterior = (~selected).astype(np.uint8)
    cv2.floodFill(exterior, None, (0, 0), 2, flags=4)
    holes = (exterior == 1)[1:-1, 1:-1]
    result = (mask > 0) | holes
    if protected is not None:
        result &= ~protected
    result = result.astype(np.uint8) * 255
    return result, dict(version=VERSION, filled_pixels=int(((result > 0) & (mask == 0)).sum()),
        policy='fill_all_enclosed_background_4connected_no_outer_dilation_protection_overrides')


def continuous_support(support, *, protected=None):
    mask, report = fill_correction_holes(support.correction_mask, protected=protected)
    return FaceNeckSupport(support.measurement_mask.copy(), support.neck_mask.copy(), mask,
                          dict(support.report, correction_continuity=report))
