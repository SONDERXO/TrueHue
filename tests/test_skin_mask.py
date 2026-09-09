"""Tests for src.skin_masking.skin_mask."""

import numpy as np

from src.skin_masking.skin_mask import create_skin_mask


def test_output_shape():
    """Mask must match the spatial dimensions of the input image."""
    img = np.random.randint(0, 256, (100, 120, 3), dtype=np.uint8)
    mask = create_skin_mask(img)
    assert mask.shape == (100, 120), f"Expected (100, 120), got {mask.shape}"


def test_binary_values():
    """Mask values must be 0 or 1 (binary)."""
    img = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    mask = create_skin_mask(img)
    unique = set(np.unique(mask))
    assert unique <= {0, 1}, f"Expected binary mask, got values {unique}"


def test_dtype():
    """Mask dtype should be uint8."""
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    mask = create_skin_mask(img)
    assert mask.dtype == np.uint8, f"Expected uint8, got {mask.dtype}"
