"""Experimental native-coordinate crop contract; not connected to runtime.

The old fixed_face_input_bridge.crop_face expects boxes on a stretched 256
frame. This separate entry point accepts a box measured on the original image.
It does not detect/select faces, certify support or make old calibration valid.
"""
import math
import numpy as np

VERSION = 'native_anchor_square_context_1p5_v1'


def crop_native_anchor(image, *, native_box):
    """Take an exact 1.5-context square slice, shifting at edges without padding."""
    if (not isinstance(image, np.ndarray) or image.dtype != np.uint8
            or image.ndim != 3 or image.shape[2] != 3 or not image.size):
        raise ValueError('Nonempty original BGR8 image required')
    if (len(native_box) != 4 or any(isinstance(v, (bool, np.bool_))
            or not isinstance(v, (int, np.integer)) for v in native_box)):
        raise ValueError('Integer native-image x/y/width/height required')
    x, y, w, h = map(int, native_box)
    height, width = image.shape[:2]
    if min(x, y) < 0 or min(w, h) < 1 or x+w > width or y+h > height:
        raise ValueError('Native anchor must lie inside original image')
    side = math.ceil(1.5 * max(w, h))
    if side > min(height, width):
        raise ValueError('Fixed square context cannot fit; no fallback')
    wanted_left = math.floor(x + w/2 - side/2)
    wanted_top = math.floor(y + h/2 - side/2)
    left = max(0, min(width-side, wanted_left))
    top = max(0, min(height-side, wanted_top))
    bounds = [left, top, left+side, top+side]
    report = dict(version=VERSION, anchor_coordinate_space='original_native_pixels',
        source_shape=list(image.shape), native_face_box=[x, y, w, h],
        native_bounds=bounds, native_side=side, context_scale=1.5,
        edge_shift=[left-wanted_left, top-wanted_top],
        source_to_normalized_linear_scale=256/side,
        exact_native_slice=True, padding_added=False, new_detail_created=False,
        old_wholeframe_lookup_compatible=False, old_fitting_costs_compatible=False,
        training_admitted=False, runtime_adopted=False)
    return image[top:top+side, left:left+side].copy(), report
