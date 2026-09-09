"""
Skin region masking using HSV and YCrCb colour spaces.

Current version: placeholder that returns a zero mask.
Replace the body of ``create_skin_mask`` with real thresholding logic.
"""

from __future__ import annotations

import numpy as np


def create_skin_mask(image: np.ndarray) -> np.ndarray:
    """Return a binary mask of detected skin pixels.

    Parameters
    ----------
    image : np.ndarray
        RGB image of shape (H, W, 3), dtype uint8.

    Returns
    -------
    np.ndarray
        Binary mask of shape (H, W), dtype uint8.
        1 = skin pixel, 0 = non-skin.

    Notes
    -----
    TODO: Implement HSV + YCrCb dual-threshold skin detection.
    """
    h, w = image.shape[:2]

    # --- Placeholder: replace with real logic ---
    # 1. Convert to HSV, apply bounds for skin hue/saturation/value.
    # 2. Convert to YCrCb, apply bounds for Cr/Cb skin range.
    # 3. Combine masks with bitwise AND.
    # 4. Apply morphological open/close to clean up noise.
    mask = np.zeros((h, w), dtype=np.uint8)

    return mask
