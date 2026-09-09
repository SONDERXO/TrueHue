"""
Lightweight image I/O helpers.

Thin wrappers around OpenCV so the rest of the pipeline
never imports cv2 directly for loading/saving.
"""

from __future__ import annotations

import cv2
import numpy as np


def load_image(path: str, *, as_rgb: bool = True) -> np.ndarray:
    """Load an image from disk.

    Parameters
    ----------
    path : str
        Filesystem path to the image.
    as_rgb : bool
        If True (default) convert BGR → RGB on load.

    Returns
    -------
    np.ndarray
        Image array of shape (H, W, 3) in uint8.
    """
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    if as_rgb:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def save_image(image: np.ndarray, path: str) -> None:
    """Write an image to disk.

    Parameters
    ----------
    image : np.ndarray
        RGB image array (H, W, 3), uint8.
    path : str
        Destination file path (e.g. ``output.png``).
    """
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, bgr)
