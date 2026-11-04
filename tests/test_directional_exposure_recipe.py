import numpy as np
import pytest
from src.distortion_generation.directional_exposure_recipe import render_rgb


def ramp():
    image = np.tile(np.arange(256, dtype=np.uint8)[None, :, None], (3, 1, 3))
    alpha = np.ones(image.shape[:2], dtype=float)
    return image, alpha


@pytest.mark.parametrize('direction', ['under', 'over'])
def test_direction_and_severity_for_every_rgb8_level_and_fractional_alpha(direction):
    image, alpha = ramp()
    for weight in (0., .05, .5, 1.):
        outputs = [render_rgb(image, alpha*weight, g, 'exposure', direction)[0].astype(int)
                   for g in ('light', 'medium', 'dark')]
        base = image.astype(int)
        if direction == 'under':
            assert np.all(outputs[2] <= outputs[1])
            assert np.all(outputs[1] <= outputs[0]) and np.all(outputs[0] <= base)
        else:
            assert np.all(outputs[2] >= outputs[1])
            assert np.all(outputs[1] >= outputs[0]) and np.all(outputs[0] >= base)


def test_clean_is_identity_and_protected_support_is_preserved_without_input_mutation():
    image, alpha = ramp(); saved = image.copy()
    alpha[:, :20] = 0
    clean, _ = render_rgb(image, alpha, 'dark', 'clean')
    np.testing.assert_array_equal(clean, image)
    out, report = render_rgb(image, alpha, 'dark', 'combined', 'over')
    np.testing.assert_array_equal(out[:, :20], image[:, :20])
    np.testing.assert_array_equal(image, saved)
    assert report['clipped_channel_samples'] > 0 and not report['training_admitted']


def test_independent_formula_and_single_rounding():
    image, alpha = ramp(); alpha[:] = .37
    x = image.astype(float)/255
    raw = 1.08*(x**(1/.7)-1)+1-35/255+np.array([-10, 0, 10])/255
    expected = np.rint(255*(x*.63+np.clip(raw, 0, 1)*.37)).astype(np.uint8)
    actual, _ = render_rgb(image, alpha, 'medium', 'combined', 'under')
    np.testing.assert_array_equal(actual, expected)


def test_colour_only_preserves_green_and_uses_recorded_additive_shifts():
    image = np.full((2, 2, 3), 128, np.uint8)
    actual, _ = render_rgb(image, np.ones((2, 2)), 'dark', 'color')
    np.testing.assert_array_equal(actual, np.tile([114, 128, 142], (2, 2, 1)))


@pytest.mark.parametrize('variant,direction', [('clean', 'under'), ('exposure', 'none'),
                                              ('combined', 'unknown'), ('color', 'over')])
def test_ambiguous_scenarios_rejected(variant, direction):
    image, alpha = ramp()
    with pytest.raises(ValueError):
        render_rgb(image, alpha, 'light', variant, direction)
