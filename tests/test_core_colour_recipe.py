import numpy as np
import pytest
from src.distortion_generation.core_colour_recipe import render_rgb
from src.model_training.blended_recovery_targets import fit_target


def ramp():
    x = np.arange(256, dtype=np.uint8)
    image = np.tile(np.stack([x, x[::-1], ((x.astype(int)*37)%256).astype(np.uint8)], -1)[None], (4, 1, 1))
    return image, np.ones(image.shape[:2])


@pytest.mark.parametrize('cast', ['cool', 'warm'])
@pytest.mark.parametrize('direction', ['none', 'under', 'over'])
def test_full_range_no_clipping_support_and_source_unchanged(cast, direction):
    image, alpha = ramp(); saved = image.copy()
    alpha[0] = 0; alpha[1] = .37
    for group in ('light', 'medium', 'dark'):
        actual, report = render_rgb(image, alpha, group, cast, direction)
        assert report['clipped_channel_samples'] == 0 and not report['training_admitted']
        np.testing.assert_array_equal(actual[0], image[0])
    np.testing.assert_array_equal(image, saved)


@pytest.mark.parametrize('cast,index', [('cool', 0), ('warm', 2)])
def test_colour_only_changes_expected_channel_with_ordered_severity(cast, index):
    image, alpha = ramp(); outputs = []
    for group in ('light', 'medium', 'dark'):
        out, _ = render_rgb(image, alpha, group, cast)
        np.testing.assert_array_equal(out[..., 1], image[..., 1])
        np.testing.assert_array_equal(out[..., 2-index], image[..., 2-index])
        outputs.append(out[..., index].astype(int))
    assert np.all(outputs[2] <= outputs[1]) and np.all(outputs[1] <= outputs[0])


def test_independent_combined_formula_single_rounding():
    image, alpha = ramp(); alpha[:] = .41
    x = image.astype(float)/255
    raw = x**(1/.7)*[1., 1., 1-10/255]
    expected = np.rint(255*(x*.59+raw*.41)).astype(np.uint8)
    out, _ = render_rgb(image, alpha, 'medium', 'warm', 'under')
    np.testing.assert_array_equal(out, expected)


def test_three_control_target_exists_for_colour_probe_without_claiming_admission():
    image, alpha = ramp()
    out, _ = render_rgb(image, alpha, 'dark', 'cool')
    fit = fit_target(out, image, alpha, alpha > 0)
    assert fit['parameters'] is not None and fit['rgb8_mae_codes'] < 1
    assert not fit['training_admitted']


@pytest.mark.parametrize('group,cast,direction', [('unknown', 'cool', 'none'),
    ('light', 'blue', 'none'), ('light', 'cool', 'auto')])
def test_ambiguous_recipe_rejected(group, cast, direction):
    image, alpha = ramp()
    with pytest.raises(ValueError):
        render_rgb(image, alpha, group, cast, direction)
