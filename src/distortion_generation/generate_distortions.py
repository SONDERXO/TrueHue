"""
Synthetic distortion generation.

Applies known gamma shifts and R/B gain changes to pristine
images so the ML model can learn correction parameters.
"""

from __future__ import annotations

import numpy as np


def apply_gamma(image: np.ndarray, gamma: float) -> np.ndarray:
    """Apply a gamma correction to a uint8 image.

    Parameters
    ----------
    image : np.ndarray
        RGB image, dtype uint8.
    gamma : float
        Gamma value (>1 brightens, <1 darkens).
    """
    inv = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv * 255 for i in range(256)]).astype("uint8")
    return np.take(table, image, mode="clip")


def apply_rgb_gain(image: np.ndarray, red_gain: float, blue_gain: float) -> np.ndarray:
    """Apply per-channel red and blue gain (green unchanged).

    Parameters
    ----------
    image : np.ndarray
        RGB image, dtype float or uint8.
    red_gain, blue_gain : float
        Multipliers for the R and B channels.
    """
    out = image.astype(np.float32)
    out[..., 0] *= red_gain
    out[..., 2] *= blue_gain
    return np.clip(out, 0, 255).astype(np.uint8)
