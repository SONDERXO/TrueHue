"""
Anatomical feature exclusion masks from MediaPipe face landmarks.

Problem
-------
The HSV/YCrCb candidate mask frequently leaks non-skin facial features:
eyelid skin around the eyes, eyebrows, and lips. These have a "skin-like"
colour but are not the facial skin we want to average for ITA.

Approach
--------
This module uses MediaPipe Face Landmarker (478 landmarks) on the BGR *face
crop* and draws filled polygons over five anatomical features to build an
*exclusion mask* whose pixels are later removed from the skin mask:

- subject-left eye   (image right)
- subject-right eye  (image left)
- subject-left eyebrow
- subject-right eyebrow
- lips / mouth (outer lip ring)

The final skin-mask pipeline reads this mask and applies
``candidate AND largest-component AND NOT exclusion`` (see
``src.skin_masking.skin_mask``).

Design notes
------------
- Input stays an OpenCV ``uint8`` BGR face crop; the original image pixels
  are never modified.
- If MediaPipe is not installed, the model file is missing, or no face is
  detected in the crop, the pipeline is told explicitly via
  ``landmarks_available=False`` and a human-readable ``status`` string. Callers
  then decide how to fall back (they must not silently ignore the status).
- This is the desktop reference implementation. MediaPipe offers the same
  Face Landmarker model on Android, so the exclusion regions can be ported
  on-device using the identical landmark indices listed in ``FEATURE_INDICES``.
"""

from __future__ import annotations

import urllib.request
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.utilities.config import get_config

# ---------------------------------------------------------------------------
# Optional MediaPipe import
# ---------------------------------------------------------------------------
# The rest of the module (mask construction, fallback handling) must work even
# when MediaPipe is not installed, so the import is guarded.
try:
    import mediapipe as mp  # noqa: F401  (used only for its Image class)
    from mediapipe.tasks.python import BaseOptions
    from mediapipe.tasks.python.vision import (  # type: ignore[import-not-found]
        FaceLandmarker,
        FaceLandmarkerOptions,
        RunningMode,
    )

    _MEDIAPIPE_AVAILABLE = True
    _MEDIAPIPE_IMPORT_ERROR: Exception | None = None
except Exception as _exc:  # pragma: no cover - environment dependent
    BaseOptions = None
    FaceLandmarker = None
    FaceLandmarkerOptions = None
    RunningMode = None
    _MEDIAPIPE_AVAILABLE = False
    _MEDIAPIPE_IMPORT_ERROR = _exc

# ---------------------------------------------------------------------------
# Face landmark indices (MediaPipe FaceMesh / Face Landmarker convention).
# Landmarks are 0..477; the sets below use the well-known 468-point numbering,
# which is shared identically by Face Mesh and Face Landmarker for these
# features. "Left"/"right" below refer to the SUBJECT's left/right (i.e. the
# mirrored image side).
# ---------------------------------------------------------------------------

FEATURE_INDICES: dict[str, list[int]] = {
    "left_eye": [
        362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,
        384, 398,
    ],
    "right_eye": [
        33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161,
        246,
    ],
    "left_eyebrow": [70, 63, 105, 66, 107, 55, 65, 52, 53, 46],
    "right_eyebrow": [336, 296, 334, 293, 300, 276, 283, 282, 295, 285],
    "lips": [
        61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402,
        317, 14, 87, 178, 88, 95,
    ],
}

_MAX_LANDMARK_INDEX: int = max(
    index for indices in FEATURE_INDICES.values() for index in indices
)


@dataclass
class LandmarkDetection:
    """Outcome of detecting face landmarks in a crop.

    Attributes
    ----------
    landmarks_available : bool
        ``True`` when landmarks were detected and are usable.
    landmarks : np.ndarray | None
        Landmark points as pixel coordinates of shape ``(N, 2)`` (x, y), or
        ``None`` when detection failed.
    status : str
        Human-readable description of the outcome.
    """

    landmarks_available: bool
    landmarks: np.ndarray | None
    status: str


@dataclass
class FeatureExclusionResult:
    """Outcome of building the anatomical feature exclusion mask.

    Attributes
    ----------
    mask : np.ndarray
        ``uint8`` mask (H, W) with ``255`` on pixels to exclude and ``0``
        elsewhere. All zeros when landmarks were not available.
    landmarks_available : bool
        ``True`` only when the mask was built from detected landmarks.
    status : str
        Why the mask exists, or exactly why the fallback (all-zero mask) was
        returned.
    """

    mask: np.ndarray
    landmarks_available: bool
    status: str


def _validate_face_bgr(face_bgr: np.ndarray) -> None:
    """Raise ValueError for an unusable BGR face crop."""
    if face_bgr is None or face_bgr.size == 0:
        raise ValueError("face_bgr must be a non-empty BGR face crop.")
    if face_bgr.ndim != 3 or face_bgr.shape[2] != 3:
        raise ValueError(
            f"face_bgr must be a 3-channel BGR image, got shape {face_bgr.shape}."
        )


def download_landmarker_model(
    model_path: str | None = None,
    model_url: str | None = None,
) -> str:
    """Download the Face Landmarker ``.task`` model if it is not present.

    The model is downloaded from the default Google AI Edge URL into
    ``models/face_landmarker/face_landmarker.task`` (see
    ``src.utilities.config.Config``). Pass explicit paths to override.

    Parameters
    ----------
    model_path : str | None
        Destination file path. Defaults to the configured path.
    model_url : str | None
        Source URL. Defaults to the configured URL.

    Returns
    -------
    str
        The local path of the model file.

    Raises
    ------
    RuntimeError
        If the download fails.
    """
    config = get_config()
    dest = Path(model_path or config.FACE_LANDMARKER_MODEL_PATH)
    url = model_url or config.FACE_LANDMARKER_MODEL_URL

    if dest.exists():
        return str(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(url, dest)  # noqa: S310 - pinned URL above
    except Exception as exc:  # pragma: no cover - network dependent
        raise RuntimeError(
            f"Failed to download face landmarker model from {url}: {exc}"
        ) from exc
    return str(dest)


def _resolve_model_path(model_path: str | None) -> str | None:
    """Return an existing model path, or None when it cannot be used."""
    if model_path is not None:
        path = Path(model_path)
        return str(path) if path.exists() else None
    default = Path(get_config().FACE_LANDMARKER_MODEL_PATH)
    return str(default) if default.exists() else None


def detect_face_landmarks(
    face_bgr: np.ndarray,
    model_path: str | None = None,
) -> LandmarkDetection:
    """Detect face landmarks inside a BGR face crop.

    The crop is passed straight to MediaPipe; landmarks are returned as pixel
    coordinates within the crop. No detection is attempted — and a descriptive
    failure is reported — when MediaPipe is missing, the model file is absent,
    or no face is found.

    Parameters
    ----------
    face_bgr : np.ndarray
        BGR face crop, shape ``(H, W, 3)``, dtype ``uint8``.
    model_path : str | None
        Path to ``face_landmarker.task``. Defaults to the configured path.

    Returns
    -------
    LandmarkDetection
        Detection outcome with ``landmarks_available`` flag and a status
        message.

    Raises
    ------
    ValueError
        If ``face_bgr`` is ``None``, empty, or not 3-channel BGR.
    """
    _validate_face_bgr(face_bgr)

    if not _MEDIAPIPE_AVAILABLE:
        reason = f"MediaPipe is not installed ({_MEDIAPIPE_IMPORT_ERROR})"
        return LandmarkDetection(False, None, reason)

    resolved_path = _resolve_model_path(model_path)
    if resolved_path is None:
        return LandmarkDetection(
            False,
            None,
            "face landmarker model file not found; call "
            "download_landmarker_model() or pass model_path",
        )

    height, width = face_bgr.shape[:2]
    landmarker = _get_landmarker(resolved_path)

    # MediaPipe expects an RGB uint8 image.
    rgb = np.ascontiguousarray(cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB))
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)  # type: ignore[attr-defined]
    result = landmarker.detect(mp_image)

    if not result.face_landmarks:
        return LandmarkDetection(
            False,
            None,
            "no face detected in the crop by MediaPipe Face Landmarker",
        )

    landmark_list = result.face_landmarks[0]
    pixel_points = np.array(
        [[landmark.x * width, landmark.y * height] for landmark in landmark_list],
        dtype=np.float64,
    )
    return LandmarkDetection(
        True,
        pixel_points,
        f"landmarks detected ({len(landmark_list)} points)",
    )


# Cache of created FaceLandmarker instances, keyed by model path, so that
# repeated calls (e.g. in a batch script) do not rebuild the TFLite graph.
_LANDMARKER_CACHE: "dict[str, FaceLandmarker]" = {}


def _get_landmarker(model_path: str) -> "FaceLandmarker":
    """Return a cached FaceLandmarker instance for the given model file."""
    if model_path in _LANDMARKER_CACHE:
        return _LANDMARKER_CACHE[model_path]

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=(
            get_config().FACE_LANDMARKER_MIN_DETECTION_CONFIDENCE
        ),
    )
    landmarker = FaceLandmarker.create_from_options(options)
    _LANDMARKER_CACHE[model_path] = landmarker
    return landmarker


def build_feature_region_masks(
    face_bgr: np.ndarray,
    landmarks: np.ndarray,
) -> dict[str, np.ndarray]:
    """Build one filled-region mask per anatomical feature.

    Each mask is ``uint8`` of shape ``(H, W)`` with ``255`` inside the feature
    polygon and ``0`` outside.

    Parameters
    ----------
    face_bgr : np.ndarray
        BGR face crop, provides the mask dimensions.
    landmarks : np.ndarray
        Pixel coordinates of shape ``(N, 2)`` or ``(N, 3)`` (only x, y used),
        as returned by :func:`detect_face_landmarks`.

    Returns
    -------
    dict[str, np.ndarray]
        Mapping of feature name to its region mask.

    Raises
    ------
    ValueError
        If ``landmarks`` has an unexpected shape or too few points.
    """
    _validate_face_bgr(face_bgr)
    if landmarks is None or landmarks.ndim != 2 or landmarks.shape[1] < 2:
        raise ValueError(
            "landmarks must be an (N, 2) or (N, 3) array of pixel coordinates."
        )
    if landmarks.shape[0] <= _MAX_LANDMARK_INDEX:
        raise ValueError(
            f"landmarks must contain at least {_MAX_LANDMARK_INDEX + 1} points, "
            f"got {landmarks.shape[0]}."
        )

    height, width = face_bgr.shape[:2]
    regions: dict[str, np.ndarray] = {}
    point_xy = landmarks[:, :2]

    for feature, indices in FEATURE_INDICES.items():
        polygon = point_xy[indices]
        polygon = np.clip(
            polygon, (0, 0), (width - 1, height - 1)
        ).astype(np.int32)

        region = np.zeros((height, width), dtype=np.uint8)
        if len(polygon) >= 3:
            cv2.fillPoly(region, [polygon], 255)
        regions[feature] = region

    return regions


def build_feature_exclusion_mask(
    face_bgr: np.ndarray,
    landmarks: np.ndarray,
    dilation: int = 0,
) -> np.ndarray:
    """Combine all feature region masks into one exclusion mask.

    Parameters
    ----------
    face_bgr : np.ndarray
        BGR face crop, provides the mask dimensions.
    landmarks : np.ndarray
        Pixel coordinates of shape ``(N, 2)`` or ``(N, 3)``.
    dilation : int
        Number of 3x3 elliptical dilations applied to the combined mask
        (default 0). Use small values (1-2) to cover pixels that fall between
        sparse landmarks (e.g. eyebrow edges).

    Returns
    -------
    np.ndarray
        ``uint8`` mask (H, W): ``255`` on pixels excluded from skin, ``0``
        elsewhere.
    """
    regions = build_feature_region_masks(face_bgr, landmarks)

    combined = np.zeros(regions["left_eye"].shape, dtype=np.uint8)
    for region in regions.values():
        combined = cv2.bitwise_or(combined, region)

    if dilation > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        for _ in range(int(dilation)):
            combined = cv2.dilate(combined, kernel, iterations=1)

    return combined


def compute_feature_exclusion_mask(
    face_bgr: np.ndarray,
    model_path: str | None = None,
    dilation: int = 0,
) -> FeatureExclusionResult:
    """Detect landmarks and return the anatomical feature exclusion mask.

    This is the high-level entry point used by the skin-mask pipeline. When
    landmarks cannot be obtained the result is an all-zero mask with an
    explicit ``landmarks_available=False`` and a descriptive ``status`` (the
    caller decides how to fall back — it is never hidden here).

    Parameters
    ----------
    face_bgr : np.ndarray
        BGR face crop, shape ``(H, W, 3)``, dtype ``uint8``.
    model_path : str | None
        Path to ``face_landmarker.task``. Defaults to the configured path.
    dilation : int
        Optional dilation applied to the combined mask (see
        :func:`build_feature_exclusion_mask`).

    Returns
    -------
    FeatureExclusionResult
        Exclusion mask plus availability flag and status.

    Raises
    ------
    ValueError
        If ``face_bgr`` is ``None``, empty, or not 3-channel BGR.
    """
    _validate_face_bgr(face_bgr)

    detection = detect_face_landmarks(face_bgr, model_path=model_path)
    if not detection.landmarks_available or detection.landmarks is None:
        empty = np.zeros(face_bgr.shape[:2], dtype=np.uint8)
        return FeatureExclusionResult(empty, False, detection.status)

    mask = build_feature_exclusion_mask(face_bgr, detection.landmarks, dilation=dilation)
    return FeatureExclusionResult(mask, True, detection.status)