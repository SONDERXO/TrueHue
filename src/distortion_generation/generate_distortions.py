"""
Synthetic distortion generation.

Applies known gamma shifts and R/B gain changes to reference
images so the ML model can learn correction parameters.
"""

from __future__ import annotations

import numpy as np


TRANSFORM_VERSION = "encoded_rgb_gamma_then_gain_v1"


def inverse_parameters(gamma: float, red_gain: float, blue_gain: float) -> dict:
    """Inverse targets for gain * x**(1/gamma), exact before clipping/encoding."""
    values = np.asarray([gamma, red_gain, blue_gain], dtype=np.float64)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("Gamma and gains must be finite and strictly positive")
    gamma, red_gain, blue_gain = values
    with np.errstate(over="ignore", invalid="ignore"):
        targets = [1.0 / gamma, red_gain ** (-gamma), blue_gain ** (-gamma)]
    if not np.isfinite(targets).all():
        raise ValueError("Inverse targets overflow")
    return dict(zip(("gamma", "red_gain", "blue_gain"), targets))


def transform_rgb(image: np.ndarray, gamma: float, red_gain: float,
                  blue_gain: float, *, clip: bool = True) -> np.ndarray:
    """Shared float RGB operator on encoded [0,1] samples; no quantization.

    Gamma > 1 brightens. Green gain is fixed at one. clip=False is intended
    only to measure pre-clipping overflow, not to feed out-of-range pixels
    into another transform. The input is never mutated.
    """
    image = np.asarray(image)
    if image.ndim != 3 or image.shape[-1] != 3 or not image.size:
        raise ValueError("Expected nonempty HxWx3 RGB image")
    if not np.issubdtype(image.dtype, np.floating):
        raise ValueError("Expected normalized floating-point RGB")
    if not np.isfinite(image).all() or (image < 0).any() or (image > 1).any():
        raise ValueError("RGB samples must be finite and within [0,1]")
    inverse_parameters(gamma, red_gain, blue_gain)  # validate shared parameter contract
    output = np.power(image.astype(np.float64), 1.0 / gamma)
    output *= np.array([red_gain, 1.0, blue_gain], dtype=np.float64)
    return np.clip(output, 0, 1) if clip else output


def apply_gamma(image: np.ndarray, gamma: float) -> np.ndarray:
    """Apply a gamma correction to a uint8 image.

    Parameters
    ----------
    image : np.ndarray
        RGB image, dtype uint8.
    gamma : float
        Gamma value (>1 brightens, <1 darkens).
    """
    inv = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv * 255 for i in range(256)]).astype("uint8")
    return np.take(table, image, mode="clip")


def apply_rgb_gain(image: np.ndarray, red_gain: float, blue_gain: float) -> np.ndarray:
    """Apply per-channel red and blue gain (green unchanged).

    Parameters
    ----------
    image : np.ndarray
        RGB image, dtype float or uint8.
    red_gain, blue_gain : float
        Multipliers for the R and B channels.
    """
    out = image.astype(np.float32)
    out[..., 0] *= red_gain
    out[..., 2] *= blue_gain
    return np.clip(out, 0, 255).astype(np.uint8)
