"""Experimental input-only spatial descriptor; no learned score or correction.

Equations inspired by Mittal, Moorthy and Bovik, TIP 2012,
doi:10.1109/TIP.2012.2214050. Independently implemented; not BRISQUE parity.
See docs/spatial-input-representation-design-2026-11-11.md for conventions.
"""
from functools import lru_cache
import math

import cv2
import numpy as np
from scipy.special import gammaln


SPATIAL_NSS_FEATURES = tuple(
    f'spatial_nss_s{s}_{name}' for s in (1, 2)
    for name in ('coefficient_shape', 'coefficient_variance', *(
        f'{direction}_{parameter}' for direction in ('h', 'v', 'd1', 'd2')
        for parameter in ('shape', 'mean', 'left_variance', 'right_variance'))))


@lru_cache(maxsize=1)
def _shape_lookup():
    shapes = np.arange(200, 10001, dtype=np.float64) / 1000
    ratios = np.exp(2*gammaln(2/shapes)-gammaln(1/shapes)-gammaln(3/shapes))
    return shapes, ratios


def _shape(ratio):
    shapes, ratios = _shape_lookup()
    return float(shapes[np.argmin(np.abs(ratios-ratio))])


def coefficient_parameters(values):
    """Zero-centered symmetric GGD moment shape and empirical second moment."""
    values = np.asarray(values, dtype=np.float64)
    if not values.size or not np.isfinite(values).all():
        raise ValueError('Finite nonempty coefficients required')
    variance = float(np.mean(values**2))
    if variance == 0:
        return [2., 0.]
    return [_shape(float(np.mean(np.abs(values)))**2/variance), variance]


def product_parameters(values):
    """AGGD moment parameters with explicit zero/single-sided conventions."""
    values = np.asarray(values, dtype=np.float64)
    if not values.size or not np.isfinite(values).all():
        raise ValueError('Finite nonempty products required')
    left, right = values[values < 0], values[values > 0]
    lv = float(np.mean(left**2)) if left.size else 0.
    rv = float(np.mean(right**2)) if right.size else 0.
    energy = float(np.mean(values**2))
    if energy == 0:
        return [2., 0., 0., 0.], 'zero_energy'
    ratio = float(np.mean(np.abs(values)))**2/energy
    if lv == 0 or rv == 0:
        # Limit of the AGGD normalized-moment factor as side ratio -> 0/inf.
        factor = 1.
        status = 'single_sided'
    else:
        side = math.sqrt(lv/rv)
        factor = ((side**3+1)*(side+1))/((side**2+1)**2)
        status = 'two_sided'
    shape = _shape(ratio*factor)
    beta_scale = math.exp(.5*(math.lgamma(1/shape)-math.lgamma(3/shape)))
    mean = (math.sqrt(rv)-math.sqrt(lv))*beta_scale*math.exp(
        math.lgamma(2/shape)-math.lgamma(1/shape))
    return [shape, mean, lv, rv], status


def normalized_coefficients(luma):
    luma = np.asarray(luma, dtype=np.float64)
    if luma.ndim != 2 or not luma.size or not np.isfinite(luma).all():
        raise ValueError('Finite nonempty 2D luma required')
    if np.ptp(luma) == 0:
        return np.zeros_like(luma)
    mean = cv2.GaussianBlur(luma, (7, 7), 7/6, borderType=cv2.BORDER_REFLECT_101)
    second = cv2.GaussianBlur(luma*luma, (7, 7), 7/6, borderType=cv2.BORDER_REFLECT_101)
    return (luma-mean)/(np.sqrt(np.maximum(second-mean*mean, 0))+1)


def spatial_nss_features(rgb):
    if (not isinstance(rgb, np.ndarray) or rgb.dtype != np.uint8 or
            rgb.ndim != 3 or rgb.shape[2] != 3 or min(rgb.shape[:2]) < 16):
        raise ValueError('RGB8 frame at least 16x16 required')
    luma = np.einsum('ijk,k->ij', rgb.astype(np.float64), [.299, .587, .114])
    values, statuses = [], []
    for scale in (1, 2):
        if scale == 2:
            luma = cv2.resize(luma, (rgb.shape[1]//2, rgb.shape[0]//2), interpolation=cv2.INTER_AREA)
        coeff = normalized_coefficients(luma)
        values.extend(coefficient_parameters(coeff))
        products = (coeff[:, :-1]*coeff[:, 1:], coeff[:-1, :]*coeff[1:, :],
                    coeff[:-1, :-1]*coeff[1:, 1:], coeff[:-1, 1:]*coeff[1:, :-1])
        for direction, product in zip(('h', 'v', 'd1', 'd2'), products):
            parameters, status = product_parameters(product)
            values.extend(parameters)
            statuses.append(dict(scale=scale, direction=direction, status=status))
    assert len(values) == 36 and np.isfinite(values).all()
    return dict(zip(SPATIAL_NSS_FEATURES, values)), statuses
