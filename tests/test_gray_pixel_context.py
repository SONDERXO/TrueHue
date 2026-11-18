"""Generated-only independent scalar GP pipeline checks."""
import math

import numpy as np
import pytest

from src.model_training.gray_pixel_context import gray_pixel_context, local_log_statistics


def scalar_reference(rgb):
    h, w, _ = rgb.shape
    logs = np.zeros((h, w, 3), float)
    np.log(rgb.astype(float)/255, out=logs, where=rgb > 0)
    pad = np.pad(logs, ((1, 1), (1, 1), (0, 0)), mode='reflect')
    pos = np.pad(np.all(rgb > 0, axis=2), 1, mode='reflect')
    raw = np.zeros((h, w)); valid = np.zeros((h, w), bool)
    for i in range(h):
        for j in range(w):
            values = pad[i:i+3, j:j+3].reshape(9, 3)
            sd = []
            for c in range(3):
                z = [float(x-values[0, c]) for x in values[:, c]]
                mu = math.fsum(z)/9
                sd.append(math.sqrt(math.fsum((x-mu)**2 for x in z)/9))
            m = math.fsum(sd)/3
            if pos[i:i+3, j:j+3].all() and m > 0:
                valid[i, j] = True
                p = math.sqrt(math.fsum((x-m)**2 for x in sd)/(3*m))
                raw[i, j] = p/(math.fsum(int(x) for x in rgb[i, j])/(3*255))
    rp = np.pad(raw, 3, mode='reflect'); vp = np.pad(valid, 3, mode='reflect')
    result = []
    for i in range(h):
        for j in range(w):
            if vp[i:i+7, j:j+7].all():
                result.append((math.fsum(rp[i:i+7, j:j+7].ravel())/49, i*w+j))
    result.sort()
    return result


def test_complete_pipeline_against_scalar_reference():
    rgb = np.random.default_rng(42).integers(20, 230, (16, 16, 3), dtype=np.uint8)
    expected = scalar_reference(rgb)
    actual = gray_pixel_context(rgb)
    assert actual['selected_flat_indices'] == [expected[0][1]]
    assert actual['cutoff_score'] == pytest.approx(expected[0][0], abs=1e-13)
    pixel = rgb.reshape(-1, 3)[expected[0][1]].astype(float)
    assert list(actual['features'].values()) == pytest.approx([math.log(pixel[0]/pixel[1]), math.log(pixel[2]/pixel[1])])


def test_equation_denominator_inside_sqrt():
    rgb = np.random.default_rng(3).integers(20, 220, (16, 16, 3), dtype=np.uint8)
    p, valid, _ = local_log_statistics(rgb)
    values = np.log(rgb[6:9, 6:9].astype(float)/255).reshape(9, 3)
    sd = values.std(axis=0);m = sd.mean()
    assert valid[7, 7]
    assert p[7, 7] == pytest.approx(math.sqrt(np.mean((sd-m)**2)/m))
    assert abs(p[7, 7]-sd.std()/m) > 1e-5


@pytest.mark.parametrize('value', [0, 1, 127, 255])
def test_flat_frames_explicitly_unavailable(value):
    r = gray_pixel_context(np.full((16, 16, 3), value, np.uint8))
    assert not r['available'] and r['features'] is None and r['selected_count'] == 0


def test_exact_ties_count_and_neutrality():
    plane = np.tile(np.arange(1, 65, dtype=np.uint8), (64, 1))
    r = gray_pixel_context(np.repeat(plane[:, :, None], 3, axis=2))
    assert r['selected_flat_indices'] == [0]
    assert r['cutoff_equal_candidates'] == 4096
    assert list(r['features'].values()) == [0., 0.]


def test_nonzero_dark_and_saturated_values_retained():
    plane = np.tile(np.array([1, 255], np.uint8), (16, 8))
    r = gray_pixel_context(np.repeat(plane[:, :, None], 3, axis=2))
    assert r['available'] and r['saturated_channel_pixels'] == 128


def test_256_frame_uses_seven_pixels_and_averages_selected_codes():
    plane = np.tile(np.arange(1, 257).clip(1, 255).astype(np.uint8), (256, 1))
    rgb = np.repeat(plane[:, :, None], 3, axis=2)
    r = gray_pixel_context(rgb)
    assert r['requested_count'] == r['selected_count'] == 7
    assert r['selected_flat_indices'] == list(range(7))
    assert r['selected_mean_rgb_codes'] == [4., 4., 4.]


def test_zero_channel_no_fake_epsilon():
    rgb = np.random.default_rng(42).integers(1, 255, (32, 32, 3), dtype=np.uint8)
    rgb[:, :, 0] = 0
    assert not gray_pixel_context(rgb)['available']


def test_determinism_nonmutation_and_channel_swap():
    rgb = np.random.default_rng(7).integers(20, 235, (32, 32, 3), dtype=np.uint8)
    copy = rgb.copy();a = gray_pixel_context(rgb);b = gray_pixel_context(rgb)
    assert a == b and np.array_equal(rgb, copy)
    swapped = gray_pixel_context(rgb[:, :, ::-1].copy())
    assert a['selected_flat_indices'] == swapped['selected_flat_indices']
    assert list(a['features'].values()) == pytest.approx(list(swapped['features'].values())[::-1])


@pytest.mark.parametrize('rgb', [np.zeros((8, 8, 3), np.uint8), np.zeros((16, 16), np.uint8), np.zeros((16, 16, 3), float)])
def test_bad_inputs(rgb):
    with pytest.raises(ValueError):
        gray_pixel_context(rgb)
