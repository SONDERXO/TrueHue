"""Generated-only mathematical checks; fixtures are not scientific data."""
import math

import cv2
import numpy as np
import pytest

from src.model_training.spatial_nss_features import (
    SPATIAL_NSS_FEATURES, _shape, coefficient_parameters,
    normalized_coefficients, product_parameters, spatial_nss_features,
)


@pytest.mark.parametrize('shape', [.5, 1., 2., 5.])
def test_shape_against_independent_gamma_identity(shape):
    ratio = math.gamma(2/shape)**2/(math.gamma(1/shape)*math.gamma(3/shape))
    assert abs(_shape(ratio)-shape) <= .001


def test_local_normalization_against_explicit_window():
    image = np.arange(81, dtype=float).reshape(9, 9)**1.1
    weights = np.exp(-np.arange(-3, 4, dtype=float)**2/(2*(7/6)**2))
    weights /= weights.sum()
    kernel = weights[:, None]*weights[None, :]
    window = image[1:8, 1:8]
    mean = np.sum(window*kernel)
    variance = np.sum((window-mean)**2*kernel)
    expected = (image[4, 4]-mean)/(math.sqrt(variance)+1)
    assert normalized_coefficients(image)[4, 4] == pytest.approx(expected, abs=1e-13)


def test_distribution_symmetry_and_scaling():
    values = np.array([-3., -2., -1., 0., 1., 2., 3.])
    first, status = product_parameters(values)
    second, _ = product_parameters(2*values)
    assert status == 'two_sided' and first[1] == 0
    assert first[0] == second[0]
    assert second[2:] == pytest.approx(np.array(first[2:])*4)
    assert coefficient_parameters(2*values)[1] == pytest.approx(4*coefficient_parameters(values)[1])


@pytest.mark.parametrize('value', [0, 127, 255])
def test_constant_frame_is_finite_and_reports_degeneracy(value):
    f, statuses = spatial_nss_features(np.full((32, 32, 3), value, np.uint8))
    assert tuple(f) == SPATIAL_NSS_FEATURES
    assert all(s['status'] == 'zero_energy' for s in statuses)
    assert all(v == 0 for k, v in f.items() if not k.endswith('shape'))


def test_single_sided_and_invalid_distribution():
    f, status = product_parameters(np.arange(10, dtype=float))
    assert status == 'single_sided' and np.isfinite(f).all()
    with pytest.raises(ValueError):
        product_parameters(np.array([np.nan]))


@pytest.mark.parametrize('image', [np.zeros((8, 8, 3), np.uint8),
    np.zeros((32, 32), np.uint8), np.zeros((32, 32, 3), float)])
def test_reject_invalid_image(image):
    with pytest.raises(ValueError):
        spatial_nss_features(image)


def test_same_histogram_different_spatial_arrangement():
    a = np.tile(np.arange(64, dtype=np.uint8)*4, (64, 1))
    b = a.ravel()[np.random.default_rng(42).permutation(a.size)].reshape(a.shape)
    assert np.array_equal(np.sort(a.ravel()), np.sort(b.ravel()))
    fa, _ = spatial_nss_features(np.repeat(a[:, :, None], 3, axis=2))
    fb, _ = spatial_nss_features(np.repeat(b[:, :, None], 3, axis=2))
    assert not np.allclose(list(fa.values()), list(fb.values()))


def test_deterministic_nonmutation_and_reflected_boundary():
    rgb = np.random.default_rng(12).integers(0, 256, (32, 32, 3), dtype=np.uint8)
    copy = rgb.copy()
    assert spatial_nss_features(rgb) == spatial_nss_features(rgb)
    assert np.array_equal(rgb, copy)
    plane = rgb[:, :, 0].astype(float)
    padded = np.pad(plane, 3, mode='reflect')
    k = cv2.getGaussianKernel(7, 7/6).ravel()
    w = k[:, None]*k[None, :]
    mu = np.sum(w*padded[:7, :7])
    variance = np.sum(w*(padded[:7, :7]-mu)**2)
    assert normalized_coefficients(plane)[0, 0] == pytest.approx(
        (plane[0, 0]-mu)/(math.sqrt(variance)+1), abs=1e-13)
