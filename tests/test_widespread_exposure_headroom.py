import numpy as np
import pytest

from src.model_training.luminance_chroma_operator import render_rgb8
from src.model_training.widespread_exposure_headroom import cap_widespread_exposure


@pytest.mark.parametrize("count, method", [(5, "original"), (4, "facial_rgb")])
def test_quarter_boundary_excludes_sparse_clipping(count, method):
    image = np.array([[[239, 153, 120]] + [[160, 90, 70]] * (count - 1)], dtype=np.uint8)
    selected = np.ones(image.shape[:2], dtype=bool)
    alpha = selected.astype(float)
    raw = np.array([1., 2 ** .5, 1.04, .95, 1.])
    baseline = render_rgb8(image, alpha, ~selected, raw)
    result = cap_widespread_exposure(image, baseline, selected, alpha, ~selected, raw)
    assert result["exposure_clipped_pixels"] == 1
    assert result["method"] == method
    assert np.array_equal(result["controls"][[0, 2, 3, 4]], raw[[0, 2, 3, 4]])
    assert (result["controls"][1] < raw[1]) == (method == "facial_rgb")


def test_preserves_existing_facial_luminance_adjustment_when_it_applies():
    image = np.full((1, 4, 3), 233, dtype=np.uint8)
    selected = np.ones(image.shape[:2], dtype=bool)
    alpha = selected.astype(float)
    raw = np.array([1., 2 ** .5, 1., 1., 1.])
    baseline = render_rgb8(image, alpha, ~selected, raw)
    result = cap_widespread_exposure(image, baseline, selected, alpha, ~selected, raw)
    assert result["method"] == "facial_luminance"
    assert result["exposure_clipped_pixels"] == 4
    assert 1 < result["controls"][1] < raw[1]


def test_excludes_clipping_already_present_with_colour_correction():
    image = np.array([[[251, 153, 120]] * 4], dtype=np.uint8)
    selected = np.ones(image.shape[:2], dtype=bool)
    alpha = selected.astype(float)
    raw = np.array([1., 2 ** .5, 1.12, .95, 1.])
    baseline = render_rgb8(image, alpha, ~selected, raw)
    result = cap_widespread_exposure(image, baseline, selected, alpha, ~selected, raw)
    assert result["exposure_clipped_pixels"] == 0
    assert np.array_equal(result["controls"], raw)
