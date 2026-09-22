"""Tests for src.skin_masking.skin_mask."""

import numpy as np
import pytest

from src.skin_masking.skin_mask import (
    create_skin_mask_bgr,
    keep_largest_connected_component,
)


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