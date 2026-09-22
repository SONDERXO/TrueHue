"""
Face detection using OpenCV's YuNet ONNX detector.

OpenCV 5 removed Haar cascades and the Caffe importer, so the detector is
the YuNet ONNX model loaded via ``cv2.FaceDetectorYN``. The model file is
downloaded on first use to ``models/face_detector/`` (see Config).
"""

from __future__ import annotations

import urllib.request
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

from src.utilities.config import get_config


def _ensure_face_model() -> Path:
    """Return the YuNet model path, downloading it on first use."""
    path = Path(get_config().FACE_MODEL_PATH)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(get_config().FACE_MODEL_URL, path)
    return path


def _detect_face_boxes(
    image_bgr: np.ndarray,
    model_path: Path,
    score_threshold: float,
) -> List[Tuple[int, int, int, int]]:
    """Return all detected face boxes, clamped to image bounds and sorted largest first."""
    image_height, image_width = image_bgr.shape[:2]

    detector = cv2.FaceDetectorYN.create(
        str(model_path),
        "",
        (image_width, image_height),
        score_threshold,
        0.3,
        5000,
    )

    _, faces = detector.detect(image_bgr)

    if faces is None or len(faces) == 0:
        return []

    boxes = []
    for face in faces:
        if face[14] < score_threshold:
            continue
        x, y, width, height = face[:4].astype(int)
        x = max(0, min(x, image_width))
        y = max(0, min(y, image_height))
        width = max(1, min(width, image_width - x))
        height = max(1, min(height, image_height - y))
        boxes.append((x, y, width, height))

    boxes.sort(key=lambda rect: rect[2] * rect[3], reverse=True)
    return boxes


def detect_largest_face_bgr(
    image_bgr: np.ndarray,
    model_path: Path,
    score_threshold: float = 0.85,
) -> Optional[Tuple[int, int, int, int]]:
    """
    Detect the largest face in a BGR image using YuNet.

    Parameters
    ----------
    image_bgr
        Input image in OpenCV BGR format.
    model_path
        Path to the YuNet ONNX model.
    score_threshold
        Minimum confidence score for a detected face.

    Returns
    -------
    tuple[int, int, int, int] | None
        Bounding box as (x, y, width, height), or None when no face is found.
    """
    boxes = _detect_face_boxes(image_bgr, model_path, score_threshold)
    return boxes[0] if boxes else None


def detect_faces(
    image: np.ndarray,
    score_threshold: float = get_config().FACE_CONFIDENCE,
) -> List[Tuple[int, int, int, int]]:
    """Detect faces in an RGB image (library API).

    Parameters
    ----------
    image : np.ndarray
        RGB image of shape (H, W, 3), dtype uint8.
    score_threshold : float
        Minimum confidence score for a detected face.

    Returns
    -------
    list of (x, y, w, h)
        Bounding boxes for each detected face, ordered by area
        (largest first). Empty list if no face is found.
    """
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return _detect_face_boxes(bgr, _ensure_face_model(), score_threshold)