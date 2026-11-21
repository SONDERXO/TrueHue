import numpy as np
import pytest

from src.model_training.luminance_chroma_operator import render_rgb8
from src.model_training.rgb_exposure_headroom import cap_facial_rgb_exposure


def test_red_channel_limits_gain_below_the_luminance_ceiling():
    image = np.array([[[239, 153, 120], [160, 90, 70]]], np.uint8)
    select = np.ones((1, 2), dtype=bool)
    protected = ~select
    alpha = np.ones((1, 2), dtype=float)
    controls = [1, 2 ** .5, 1.04, .95, 1]
    assert render_rgb8(image, alpha, protected, controls)[0, 0, 0] == 255
    result = cap_facial_rgb_exposure(image, select, alpha, protected, controls)
    assert 1 < result[1] < controls[1]
    assert np.array_equal(result[[0, 2, 3, 4]], np.asarray(controls)[[0, 2, 3, 4]])
    assert not np.any(render_rgb8(image, alpha, protected, result) == 255)


@pytest.mark.parametrize("pixel, measured, alpha, protected, gain", [
    ([239, 153, 120], False, 1., False, 1.414),
    ([239, 153, 120], True, 0., True, 1.414),
    ([239, 153, 120], True, .02, False, 1.414),
    ([255, 153, 120], True, 1., False, 1.414),
    ([251, 153, 120], True, 1., False, 1.414),
    ([239, 153, 120], True, 1., False, 1.0),
    ([239, 153, 120], True, 1., False, .707),
])
def test_preserves_gain_when_exposure_adds_no_full_channel(pixel, measured, alpha, protected, gain):
    image = np.array([[pixel]], np.uint8)
    controls = [1, gain, 1.12, .95, 1]
    actual = cap_facial_rgb_exposure(image, np.array([[measured]]), np.array([[alpha]]),
                                    np.array([[protected]]), controls)
    assert np.array_equal(actual, controls)
