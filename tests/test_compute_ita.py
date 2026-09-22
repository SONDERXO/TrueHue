"""Tests for src.ita_estimation.compute_ita."""

import math

import cv2
import numpy as np
import pytest

from src.ita_estimation.compute_ita import (
    compute_ita,
    compute_masked_lab_statistics,
    opencv_lab_to_cielab,
)


def test_compute_ita_known_value():
    """L*=60, b*=15 must reproduce the reference formula exactly."""
    result = compute_ita(60.0, 15.0)
    expected = math.degrees(math.atan((60.0 - 50.0) / 15.0))

    assert result is not None
    assert abs(result - expected) < 1e-9


def test_compute_ita_zero_b_returns_none():
    """b* near zero must return None instead of dividing by zero."""
    assert compute_ita(60.0, 0.0) is None
    assert compute_ita(60.0, 1e-7) is None  # within the 1e-6 epsilon
    assert compute_ita(0.0, -1e-9) is None


def test_compute_ita_negative_b():
    """Regression guard: negative b* must still produce a finite angle."""
    result = compute_ita(60.0, -15.0)
    assert result is not None
    assert abs(result - (-math.degrees(math.atan(10.0 / 15.0)))) < 1e-9


def test_opencv_lab_to_cielab_conversion():
    """L scales by 100/255; a and b are shifted by -128."""
    lab = np.array([[[255, 128, 138]]], dtype=np.uint8)  # shape (1, 1, 3)

    cielab = opencv_lab_to_cielab(lab)

    assert cielab.shape == (1, 1, 3)
    assert cielab.dtype in (np.float32, np.float64)
    assert cielab[0, 0, 0] == pytest.approx(255.0 * (100.0 / 255.0), abs=1e-3)
    assert cielab[0, 0, 1] == pytest.approx(0.0, abs=1e-3)    # 128 - 128
    assert cielab[0, 0, 2] == pytest.approx(10.0, abs=1e-3)   # 138 - 128


def test_opencv_lab_to_cielab_raises_on_wrong_shape():
    """A non-(H, W, 3) input must raise ValueError."""
    with pytest.raises(ValueError):
        opencv_lab_to_cielab(np.zeros((5, 5), dtype=np.uint8))
    with pytest.raises(ValueError):
        opencv_lab_to_cielab(None)


def test_compute_masked_lab_statistics_valid():
    """A constant-colour face fully covered by the mask must compute cleanly."""
    height, width = 16, 16
    bgr = np.zeros((height, width, 3), dtype=np.uint8)
    bgr[:] = (0, 128, 255)  # orange-ish BGR colour
    skin_mask = np.full((height, width), 255, dtype=np.uint8)

    result = compute_masked_lab_statistics(bgr, skin_mask, minimum_skin_pixels=100)

    assert result["valid"] is True
    assert result["reason"] == "ITA computed successfully"
    assert result["skin_pixels"] == height * width
    for key in ("mean_l_star", "mean_a_star", "mean_b_star", "ita_degrees"):
        assert result[key] is not None

    # Cross-check against the single-pixel conversion of the same colour:
    # the whole image has one constant colour, so means equal that pixel.
    single = opencv_lab_to_cielab(cv2.cvtColor(bgr[0:1, 0:1], cv2.COLOR_BGR2LAB))
    expected_l = float(single[0, 0, 0])
    expected_a = float(single[0, 0, 1])
    expected_b = float(single[0, 0, 2])

    assert abs(expected_b) > 1e-6  # colour chosen so ITA is well defined
    assert result["mean_l_star"] == pytest.approx(expected_l, abs=1e-4)
    assert result["mean_a_star"] == pytest.approx(expected_a, abs=1e-4)
    assert result["mean_b_star"] == pytest.approx(expected_b, abs=1e-4)

    expected_ita = compute_ita(expected_l, expected_b)
    assert expected_ita is not None
    assert result["ita_degrees"] == pytest.approx(expected_ita, abs=1e-4)


def test_compute_masked_lab_statistics_insufficient_pixels():
    """Too few selected pixels must invalidate the result."""
    bgr = np.zeros((32, 32, 3), dtype=np.uint8)
    skin_mask = np.zeros((32, 32), dtype=np.uint8)
    skin_mask[0, 0] = 255
    skin_mask[1, 1] = 255  # 2 pixels total

    result = compute_masked_lab_statistics(bgr, skin_mask, minimum_skin_pixels=100)

    assert result["valid"] is False
    assert result["skin_pixels"] == 2
    assert result["ita_degrees"] is None
    assert result["mean_l_star"] is None
    assert result["mean_a_star"] is None
    assert result["mean_b_star"] is None
    assert "insufficient" in result["reason"].lower()


def test_compute_masked_lab_statistics_dimension_mismatch():
    """A mask with different spatial size must return an invalid result."""
    bgr = np.zeros((10, 10, 3), dtype=np.uint8)
    bad_mask = np.zeros((5, 5), dtype=np.uint8)

    result = compute_masked_lab_statistics(bgr, bad_mask)

    assert result["valid"] is False
    assert "shape" in result["reason"].lower()
    assert result["skin_pixels"] == 0
    assert result["ita_degrees"] is None


def test_compute_masked_lab_statistics_invalid_image():
    """None or empty face input must report an invalid structured result."""
    with_mask = np.zeros((8, 8), dtype=np.uint8)
    result = compute_masked_lab_statistics(None, with_mask)
    assert result["valid"] is False
    assert result["ita_degrees"] is None
    assert result["skin_pixels"] == 0

    empty = np.zeros((0, 0, 3), dtype=np.uint8)
    result = compute_masked_lab_statistics(empty, with_mask)
    assert result["valid"] is False
    assert result["ita_degrees"] is None


def test_compute_masked_lab_statistics_no_skin_pixels():
    """An all-zero full-size mask must be reported as invalid."""
    bgr = np.zeros((8, 8, 3), dtype=np.uint8)
    zero_mask = np.zeros((8, 8), dtype=np.uint8)

    result = compute_masked_lab_statistics(bgr, zero_mask, minimum_skin_pixels=1)

    assert result["valid"] is False
    assert result["skin_pixels"] == 0
    assert result["ita_degrees"] is None


def test_compute_masked_lab_statistics_bad_minimum_raises():
    """A non-positive/float minimum_skin_pixels is a programming error."""
    bgr = np.zeros((8, 8, 3), dtype=np.uint8)
    full_mask = np.full((8, 8), 255, dtype=np.uint8)

    with pytest.raises(ValueError):
        compute_masked_lab_statistics(bgr, full_mask, minimum_skin_pixels=0)
    with pytest.raises(ValueError):
        compute_masked_lab_statistics(bgr, full_mask, minimum_skin_pixels=-5)
    with pytest.raises(ValueError):
        compute_masked_lab_statistics(bgr, full_mask, minimum_skin_pixels=100.5)