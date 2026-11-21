import numpy as np

from src.model_training.local_rgb_highlights import soften_local_rgb_highlights
from src.model_training.luminance_chroma_operator import render_rgb8


def test_limits_only_newly_clipped_measured_pixels():
    image = np.array([[
        [239,153,120], [160,90,70], [239,153,120], [239,153,120], [255,153,120],
    ]], np.uint8)
    measurement = np.array([[True, True, False, True, True]])
    protected = np.array([[False, False, False, True, False]])
    alpha = np.array([[1., 1., 1., 0., 1.]])
    controls = [1., 2 ** .5, 1.04, .95, 1.]
    baseline = render_rgb8(image, alpha, protected, controls)
    assert baseline[0, 0, 0] == 255
    result = soften_local_rgb_highlights(image, baseline, measurement, alpha, protected, controls)
    assert np.array_equal(result[:, 1:], baseline[:, 1:])
    assert int(result[0, 0].max()) == 254
    unit = render_rgb8(image, alpha, protected, [1., 1., 1.04, .95, 1.])
    assert unit[0, 0, 1] <= result[0, 0, 1] <= baseline[0, 0, 1]


def test_keeps_clipping_already_caused_by_the_colour_adjustment():
    image = np.array([[[251,153,120]]], np.uint8)
    measurement = np.ones((1, 1), dtype=bool)
    protected = ~measurement
    alpha = np.ones((1, 1))
    controls = [1., 1.414, 1.12, .95, 1.]
    unit = render_rgb8(image, alpha, protected, [1., 1., 1.12, .95, 1.])
    assert unit[0, 0, 0] == 255
    baseline = render_rgb8(image, alpha, protected, controls)
    assert np.array_equal(
        soften_local_rgb_highlights(image, baseline, measurement, alpha, protected, controls), baseline
    )


def test_preserves_feathered_pixels_without_added_clipping_and_negative_exposure():
    image = np.array([[[239,153,120]]], np.uint8)
    measurement = np.ones((1, 1), dtype=bool)
    protected = ~measurement
    for alpha_value, gain in ((.05, 1.414), (1., .707)):
        alpha = np.array([[alpha_value]])
        controls = [1., gain, 1.04, .95, 1.]
        baseline = render_rgb8(image, alpha, protected, controls)
        assert np.array_equal(
            soften_local_rgb_highlights(image, baseline, measurement, alpha, protected, controls), baseline
        )
