"""Tests for src.skin_masking.landmark_exclusion."""

from pathlib import Path

import numpy as np
import pytest

from src.skin_masking import landmark_exclusion as lex
from src.utilities.config import get_config


def _valid_bgr(height: int = 200, width: int = 200) -> np.ndarray:
    return np.full((height, width, 3), 128, dtype=np.uint8)


def _synthetic_landmarks(image_hw=(200, 200)) -> np.ndarray:
    """A 478x2 pixel-coordinate array with feature clusters in the centre."""
    points = np.zeros((478, 2), dtype=np.float64)
    height, width = image_hw
    points[:] = [width * 0.4, height * 0.4]
    return points


def test_feature_indices_lists_are_valid():
    """Each feature has indices, all inside the 0..477 landmark range."""
    expected_features = {
        "left_eye",
        "right_eye",
        "left_eyebrow",
        "right_eyebrow",
        "lips",
    }
    assert set(lex.FEATURE_INDICES) == expected_features
    for indices in lex.FEATURE_INDICES.values():
        assert len(indices) >= 3
        for index in indices:
            assert 0 <= index < 478


def test_build_feature_region_masks_shape_type_and_binary():
    """Each feature mask matches the crop, is uint8, and is binary."""
    img = _valid_bgr()
    regions = lex.build_feature_region_masks(img, _synthetic_landmarks(img.shape[:2]))

    assert set(regions) == set(lex.FEATURE_INDICES)
    for feature, mask in regions.items():
        assert mask.shape == img.shape[:2], feature
        assert mask.dtype == np.uint8, feature
        assert set(np.unique(mask)) <= {0, 255}, feature


def test_build_feature_region_masks_produces_nonzero_regions():
    """Clustered landmarks must yield filled (nonzero) regions."""
    img = _valid_bgr()
    regions = lex.build_feature_region_masks(img, _synthetic_landmarks(img.shape[:2]))

    for feature, mask in regions.items():
        assert np.count_nonzero(mask) > 0, feature


def test_build_feature_exclusion_mask_shape_type_and_binary():
    """Combined mask combines every region and stays a binary uint8 map."""
    img = _valid_bgr()
    mask = lex.build_feature_exclusion_mask(
        img, _synthetic_landmarks(img.shape[:2]), dilation=1
    )

    assert mask.shape == img.shape[:2]
    assert mask.dtype == np.uint8
    assert set(np.unique(mask)) <= {0, 255}
    assert np.count_nonzero(mask) > 0


def test_build_feature_exclusion_mask_zero_dilation_equal_union():
    """dilation=0 must equal the plain union of all region masks."""
    img = _valid_bgr()
    points = _synthetic_landmarks(img.shape[:2])

    regions = lex.build_feature_region_masks(img, points)
    union = np.zeros(img.shape[:2], dtype=np.uint8)
    for region in regions.values():
        union = np.bitwise_or(union, region)

    mask = lex.build_feature_exclusion_mask(img, points, dilation=0)
    assert np.array_equal(mask, union)


def test_build_feature_region_masks_rejects_bad_landmark_shape():
    """1D or tiny landmark arrays must raise ValueError."""
    img = _valid_bgr()
    with pytest.raises(ValueError):
        lex.build_feature_region_masks(img, np.zeros((100,), dtype=np.float64))
    with pytest.raises(ValueError):
        lex.build_feature_region_masks(img, np.zeros((100, 2), dtype=np.float64))


def test_detect_face_landmarks_fallback_without_mediapipe(monkeypatch):
    """Graceful failure when MediaPipe is unavailable must be explicit."""
    monkeypatch.setattr(lex, "_MEDIAPIPE_AVAILABLE", False)
    monkeypatch.setattr(lex, "_MEDIAPIPE_IMPORT_ERROR", ImportError("stub missing"))

    result = lex.detect_face_landmarks(_valid_bgr())

    assert result.landmarks_available is False
    assert result.landmarks is None
    assert "MediaPipe" in result.status


def test_detect_face_landmarks_fallback_without_model(monkeypatch):
    """Graceful failure when the model file is missing must be explicit."""
    monkeypatch.setattr(lex, "_MEDIAPIPE_AVAILABLE", True)
    monkeypatch.setattr(lex, "_resolve_model_path", lambda model_path: None)

    result = lex.detect_face_landmarks(_valid_bgr())

    assert result.landmarks_available is False
    assert result.landmarks is None
    assert "model" in result.status.lower()


def test_detect_face_landmarks_rejects_invalid_crop():
    """None/empty/non-BGR crops raise a clear ValueError."""
    with pytest.raises(ValueError):
        lex.detect_face_landmarks(None)
    with pytest.raises(ValueError):
        lex.detect_face_landmarks(np.zeros((0, 0, 3), dtype=np.uint8))
    with pytest.raises(ValueError):
        lex.detect_face_landmarks(np.zeros((10, 10), dtype=np.uint8))


def test_compute_feature_exclusion_mask_fallback_on_detection_failure(monkeypatch):
    """Detection failure must yield an all-zero mask plus a clear status."""
    monkeypatch.setattr(
        lex,
        "detect_face_landmarks",
        lambda _face, model_path=None: lex.LandmarkDetection(
            landmarks_available=False,
            landmarks=None,
            status="no face detected in the crop",
        ),
    )

    img = _valid_bgr()
    result = lex.compute_feature_exclusion_mask(img)

    assert result.landmarks_available is False
    assert result.mask.shape == img.shape[:2]
    assert result.mask.dtype == np.uint8
    assert np.count_nonzero(result.mask) == 0
    assert "no face detected" in result.status


def test_compute_feature_exclusion_mask_rejects_invalid_crop():
    with pytest.raises(ValueError):
        lex.compute_feature_exclusion_mask(None)


@pytest.mark.skipif(
    (not lex._MEDIAPIPE_AVAILABLE)
    or (not Path(get_config().FACE_LANDMARKER_MODEL_PATH).exists()),
    reason="MediaPipe or the face_landmarker.task model is not available",
)
def test_real_landmarker_reports_no_face_on_blank_image():
    """Integration: with the real model, a blank crop yields no landmarks."""
    result = lex.detect_face_landmarks(np.zeros((200, 160, 3), dtype=np.uint8))

    assert result.landmarks_available is False
    assert "no face detected" in result.status.lower()