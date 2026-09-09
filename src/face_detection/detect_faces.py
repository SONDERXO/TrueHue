"""
Face detection wrapper.

Uses OpenCV's DNN-based face detector (res10_300x300 SSD).
A Haar-cascade fallback can be added later.
"""

from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np


def detect_faces(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """Detect faces in an RGB image.

    Parameters
    ----------
    image : np.ndarray
        RGB image of shape (H, W, 3).

    Returns
    -------
    list of (x, y, w, h)
        Bounding boxes for each detected face.

    Notes
    -----
    TODO: Load a DNN model or Haar cascade and run detection.
    """
    # Placeholder – returns empty list until a model is wired in.
    return []
