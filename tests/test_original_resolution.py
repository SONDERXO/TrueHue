"""Geometry and pixel preservation with generated data, no trained model calls."""
import cv2
import numpy as np
import pytest

from src.correction.original_resolution import lift_analysis_support, render_original_rgb8
from src.model_training.luminance_chroma_operator import render_rgb8


@pytest.mark.parametrize('shape', [(521, 293, 3), (293, 521, 3), (256, 256, 3)])
def test_striped_render_matches_pointwise_original_and_preserves_unselected_pixels(shape):
    rng = np.random.default_rng(42)
    original = rng.integers(0, 256, size=shape, dtype=np.uint8)
    alpha = np.zeros((256, 256), np.float32); alpha[40:210, 30:200] = .8
    protected = np.zeros((256, 256), bool); protected[80:120, 80:120] = True
    alpha[protected] = 0
    full_alpha, full_protected = lift_analysis_support(alpha, protected, shape)
    controls = [1.03, 1.12, 1.02, .97, .94]
    before = original.tobytes(), alpha.tobytes(), protected.tobytes()
    actual = render_original_rgb8(original, full_alpha, full_protected, controls)
    expected = render_rgb8(original, full_alpha, full_protected, controls)
    np.testing.assert_array_equal(actual, expected)
    assert actual.shape == original.shape and actual.dtype == np.uint8
    untouched = full_protected | (full_alpha == 0)
    np.testing.assert_array_equal(actual[untouched], original[untouched])
    assert before == (original.tobytes(), alpha.tobytes(), protected.tobytes())
    nearest = cv2.resize((alpha > 0).astype(np.uint8), (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST) > 0
    assert not full_alpha[~nearest].any() and not full_alpha[full_protected].any()


def test_identity_keeps_original_detail_and_returns_an_independent_copy():
    original = np.random.default_rng(9).integers(0, 256, size=(1920, 1080, 3), dtype=np.uint8)
    alpha = np.ones((1920, 1080), np.float32); protected = np.zeros(alpha.shape, bool)
    actual = render_original_rgb8(original, alpha, protected, [1.] * 5)
    np.testing.assert_array_equal(actual, original)
    assert not np.shares_memory(actual, original)


@pytest.mark.parametrize('fault', ['nan', 'overlap', 'shape', 'dtype'])
def test_invalid_lift_cannot_create_application_support(fault):
    alpha = np.ones((256, 256), np.float32); protected = np.zeros((256, 256), bool)
    if fault == 'nan': alpha[0, 0] = np.nan
    if fault == 'overlap': protected[0, 0] = True
    if fault == 'shape': alpha = alpha[:100]
    if fault == 'dtype': protected = protected.astype(np.uint8)
    with pytest.raises(ValueError): lift_analysis_support(alpha, protected, (300, 500, 3))


def test_identity_fast_path_still_checks_protection():
    original = np.zeros((300, 500, 3), np.uint8)
    alpha = np.ones((300, 500)); protected = np.ones(alpha.shape, bool)
    with pytest.raises(ValueError): render_original_rgb8(original, alpha, protected, [1.] * 5)
