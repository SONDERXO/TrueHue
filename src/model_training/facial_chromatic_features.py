"""Input-only chromatic distribution statistics; no mask or ITA changes."""
import cv2
import numpy as np

ADDITIONS = ('input_a_median', 'input_a_iqr', 'input_b_median', 'input_b_iqr')


def facial_chromatic_features(image_bgr, mask):
    image, selected = np.asarray(image_bgr), np.asarray(mask)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3 or selected.dtype != bool or selected.shape != image.shape[:2]:
        raise ValueError('Matching uint8 BGR image and boolean measurement mask required')
    count = int(selected.sum())
    if count < 1000:
        return dict(valid=False, reason='fewer_than_1000_mask_pixels', skin_pixels=count)
    # OpenCV 8-bit chromatic axes differ from conventional a*/b* by 128.
    pixels = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)[selected, 1:].astype(float) - 128
    values = []
    for channel in pixels.T:
        lower, median, upper = np.percentile(channel, [25, 50, 75], method='linear')
        values.extend([float(median), float(upper - lower)])
    return dict(valid=True, reason='available', skin_pixels=count, features=dict(zip(ADDITIONS, values)))
