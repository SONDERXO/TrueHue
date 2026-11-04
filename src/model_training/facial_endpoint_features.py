"""Masked channel endpoint fractions; not proof of physical sensor clipping."""
import numpy as np

ADDITIONS = tuple(f'input_{channel}_{endpoint}_fraction' for channel in ('red', 'green', 'blue') for endpoint in ('zero', 'full'))


def facial_endpoint_features(image_bgr, mask):
    image, selected = np.asarray(image_bgr), np.asarray(mask)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3 or selected.dtype != bool or selected.shape != image.shape[:2]:
        raise ValueError('Matching uint8 BGR image and boolean measurement mask required')
    count = int(selected.sum())
    if count < 1000:
        return dict(valid=False, reason='fewer_than_1000_mask_pixels', skin_pixels=count)
    rgb = image[selected][:, ::-1]
    values = [float(np.count_nonzero(rgb[:, channel] == value) / count) for channel in range(3) for value in (0, 255)]
    return dict(valid=True, reason='available', skin_pixels=count, features=dict(zip(ADDITIONS, values)))
