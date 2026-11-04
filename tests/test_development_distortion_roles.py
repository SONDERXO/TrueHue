import numpy as np
import pytest
from src.distortion_generation.development_roles import core_exposure, assign_role


def data():
    im = np.tile(np.arange(256, dtype=np.uint8)[None, :, None], (4, 1, 3))
    alpha = np.ones(im.shape[:2]); alpha[:, :3] = 0; alpha[0, 3:] = .5
    return im, alpha


@pytest.mark.parametrize('direction', ['under', 'over'])
def test_core_direction_severity_clipping_and_input_preservation(direction):
    im, alpha = data(); saved = im.copy(); outputs = []
    for group in ('light', 'medium', 'dark'):
        out, report = core_exposure(im, alpha, group, direction)
        assert report['clipped_channel_samples'] == 0
        np.testing.assert_array_equal(out[alpha == 0], im[alpha == 0])
        role = assign_role(im, out, alpha, scenario='exposure', clipped_channel_samples=0)
        assert role['role'] == 'core_candidate' and not role['training_admitted']
        outputs.append(out.astype(int))
    sign = 1 if direction == 'under' else -1
    assert np.all(sign*(outputs[0]-im.astype(int)) <= 0)
    assert np.all(sign*(outputs[1]-outputs[0]) <= 0)
    assert np.all(sign*(outputs[2]-outputs[1]) <= 0)
    np.testing.assert_array_equal(im, saved)


def test_endpoints_do_not_fabricate_clipping_and_new_quantisation_loss_is_reported():
    im, alpha = data(); out, report = core_exposure(im, alpha, 'dark', 'under')
    assert report['new_endpoint_channel_samples'] > 0
    assert report['clipped_channel_samples'] == 0
    assert assign_role(im, out, alpha, scenario='exposure', clipped_channel_samples=0)['role'] == 'core_candidate'


def test_stress_retained_regardless_of_small_actual_change():
    im, alpha = data(); out = im.copy(); out[1, 10, 0] += 1
    role = assign_role(im, out, alpha, scenario='combined', clipped_channel_samples=1)
    assert role['role'] == 'clipping_stress' and not role['automatic_target_acceptance']


def test_clean_requires_exact_identity_and_no_clipping():
    im, alpha = data()
    assert assign_role(im, im, alpha, scenario='clean', clipped_channel_samples=0)['role'] == 'clean_control'
    out = im.copy(); out[1, 10, 0] += 1
    assert assign_role(im, out, alpha, scenario='clean', clipped_channel_samples=0)['role'] == 'invalid_clean'
    assert assign_role(im, im, alpha, scenario='clean', clipped_channel_samples=1)['role'] == 'invalid_clean'
    assert assign_role(im, im, alpha, scenario='exposure', clipped_channel_samples=0)['role'] == 'unchanged_distortion'


def test_outside_change_is_not_ignored():
    im, alpha = data(); out = im.copy(); out[0, 0, 0] = 5
    assert assign_role(im, out, alpha, scenario='combined', clipped_channel_samples=2)['role'] == 'invalid_support'


@pytest.mark.parametrize('count', [-1, True, .5, None, 1000000])
def test_invalid_clipping_evidence_rejected(count):
    im, alpha = data()
    with pytest.raises(ValueError):
        assign_role(im, im, alpha, scenario='clean', clipped_channel_samples=count)
