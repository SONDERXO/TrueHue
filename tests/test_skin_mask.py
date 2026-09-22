"""Tests for src.skin_masking.skin_mask."""

import numpy as np
import pytest

from src.skin_masking.landmark_exclusion import FeatureExclusionResult
from src.skin_masking.skin_mask import (
    compute_skin_mask_result,
    create_candidate_mask_bgr,
    create_skin_mask_bgr,
    keep_largest_connected_component,
    save_mask_visualization,
)


def _stub_face_bgr(height: int = 30, width: int = 40) -> np.ndarray:
    """Small constant-colour BGR crop used as a generic valid input."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = (150, 200, 255)  # arbitrary BGR colour
    return img


def test_keep_largest_connected_component_retains_biggest():
    """Only the largest connected foreground component must survive."""
    mask = np.zeros((20, 20), dtype=np.uint8)
    mask[2:4, 2:4] = 255  # small 2x2 component
    mask[10:18, 10:18] = 255  # large 8x8 component

    result = keep_largest_connected_component(mask)

    assert result.dtype == np.uint8
    assert set(np.unique(result)) <= {0, 255}
    assert np.count_nonzero(result) == 8 * 8
    assert np.all(result[10:18, 10:18] == 255)
    assert np.all(result[2:4, 2:4] == 0)


def test_keep_largest_connected_component_accepts_nonzero_foreground():
    """Foreground values other than 255 (e.g. 3, 7) must still be detected."""
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[1, 1] = 7  # small component (1 pixel)
    mask[5, 5] = 3  # large component (also 1 pixel, but chosen arbitrary)
    mask[5, 6] = 1  # makes the second component 2 pixels

    result = keep_largest_connected_component(mask)

    assert result[5, 5] == 255
    assert result[5, 6] == 255
    assert result[1, 1] == 0


def test_keep_largest_connected_component_empty_mask():
    """An all-zero mask must produce an all-zero uint8 output."""
    mask = np.zeros((6, 6), dtype=np.uint8)
    result = keep_largest_connected_component(mask)

    assert result.dtype == np.uint8
    assert np.count_nonzero(result) == 0
    assert result.shape == mask.shape


def test_keep_largest_connected_component_raises_on_3d_mask():
    """A multi-channel mask is invalid input and must raise ValueError."""
    mask = np.zeros((8, 8, 3), dtype=np.uint8)
    with pytest.raises(ValueError):
        keep_largest_connected_component(mask)


def test_create_skin_mask_bgr_shape_type_and_binary():
    """Mask must match image size, be uint8, and contain only 0/255."""
    img = np.zeros((30, 40, 3), dtype=np.uint8)
    img[:] = (0, 128, 128)  # arbitrary BGR colour

    mask = create_skin_mask_bgr(img)

    assert mask.shape == (30, 40)
    assert mask.dtype == np.uint8
    assert set(np.unique(mask)) <= {0, 255}


def test_create_skin_mask_bgr_handles_random_image():
    """A noisy colour image must not crash and must stay binary."""
    img = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    mask = create_skin_mask_bgr(img)

    assert mask.shape == (64, 64)
    assert mask.dtype == np.uint8
    assert set(np.unique(mask)) <= {0, 255}


def test_create_skin_mask_bgr_raises_on_empty_crop():
    """None or empty input must raise a clear ValueError."""
    with pytest.raises(ValueError):
        create_skin_mask_bgr(None)
    with pytest.raises(ValueError):
        create_skin_mask_bgr(np.zeros((0, 0, 3), dtype=np.uint8))


def test_create_skin_mask_bgr_raises_on_non_3channel():
    """A grayscale crop is invalid input for the BGR skin mask."""
    gray = np.zeros((20, 20), dtype=np.uint8)
    with pytest.raises(ValueError):
        create_skin_mask_bgr(gray)


def test_create_candidate_mask_bgr_shape_type_and_binary():
    """The raw HSV/YCrCb candidate must match crop size and stay binary."""
    img = _stub_face_bgr()
    mask = create_candidate_mask_bgr(img)

    assert mask.shape == img.shape[:2]
    assert mask.dtype == np.uint8
    assert set(np.unique(mask)) <= {0, 255}


def test_compute_skin_mask_result_default_structure():
    """Default call must yield the documented SkinMaskResult contract."""
    img = _stub_face_bgr()
    result = compute_skin_mask_result(img)

    assert result.mask.shape == img.shape[:2]
    assert result.mask.dtype == np.uint8
    assert set(np.unique(result.mask)) <= {0, 255}
    assert result.candidate_mask.shape == img.shape[:2]
    assert result.exclusion_mask.shape == img.shape[:2]
    assert isinstance(result.landmarks_available, bool)
    assert isinstance(result.status, str)
    assert len(result.status) > 0


def test_compute_skin_mask_result_without_exclusion():
    """exclude_features=False must return the V1 mask and no exclusion."""
    result = compute_skin_mask_result(_stub_face_bgr(), exclude_features=False)

    assert result.landmarks_available is False
    assert np.count_nonzero(result.exclusion_mask) == 0
    assert "without feature exclusion" in result.status
    # V1 result == candidate + largest component, no exclusion applied.
    assert np.array_equal(
        result.mask,
        keep_largest_connected_component(result.candidate_mask),
    )


def test_feature_exclusion_removes_overlapping_pixels(monkeypatch):
    """final = candidate AND largest-component AND NOT exclusion."""
    height, width = 40, 40
    img = _stub_face_bgr(height, width)

    # Force the full image to be a candidate so the boolean logic is tested
    # independently of the (tunable) colour thresholds.
    monkeypatch.setattr(
        "src.skin_masking.skin_mask.create_candidate_mask_bgr",
        lambda _face: np.full((height, width), 255, dtype=np.uint8),
    )

    exclusion_block = np.zeros((height, width), dtype=np.uint8)
    exclusion_block[5:15, 5:15] = 255
    monkeypatch.setattr(
        "src.skin_masking.skin_mask.compute_feature_exclusion_mask",
        lambda _face, model_path=None, dilation=0: FeatureExclusionResult(
            mask=exclusion_block, landmarks_available=True, status="stub detected"
        ),
    )

    result = compute_skin_mask_result(img)

    assert result.landmarks_available is True
    assert "feature exclusion" in result.status
    assert np.all(result.mask[5:15, 5:15] == 0)
    assert np.count_nonzero(result.mask) == height * width - 10 * 10
    assert set(np.unique(result.mask)) <= {0, 255}


def test_landmark_failure_falls_back_to_v1_mask(monkeypatch):
    """Unavailable landmarks must fall back without silently hiding it."""
    height, width = 30, 40
    img = _stub_face_bgr(height, width)

    monkeypatch.setattr(
        "src.skin_masking.skin_mask.compute_feature_exclusion_mask",
        lambda _face, model_path=None, dilation=0: FeatureExclusionResult(
            mask=np.zeros((height, width), dtype=np.uint8),
            landmarks_available=False,
            status="no face detected in the crop",
        ),
    )

    result = compute_skin_mask_result(img)

    assert result.landmarks_available is False
    assert np.count_nonzero(result.exclusion_mask) == 0
    assert "FALLBACK" in result.status
    assert np.array_equal(
        result.mask,
        keep_largest_connected_component(result.candidate_mask),
    )


def test_save_mask_visualization_writes_and_matches_size(tmp_path):
    """A valid grid must be written for a mismatched mask must raise."""
    height, width = 30, 40
    img = _stub_face_bgr(height, width)
    candidate = np.full((height, width), 255, dtype=np.uint8)
    exclusion = np.zeros((height, width), dtype=np.uint8)
    final = np.full((height, width), 255, dtype=np.uint8)

    out = tmp_path / "mask_review.png"
    save_mask_visualization(
        img, candidate, exclusion, final, str(out), landmarks_available=False
    )
    assert out.exists()
    assert out.stat().st_size > 0

    bad_exclusion = np.zeros((4, 4), dtype=np.uint8)
    with pytest.raises(ValueError):
        save_mask_visualization(
            img, candidate, bad_exclusion, final, str(tmp_path / "bad.png")
        )