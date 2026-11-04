"""Experimental inward feathering; does not alter estimation masks or models."""
import cv2
import numpy as np

from src.distortion_generation.generate_distortions import transform_rgb


def inward_alpha(mask, width):
    """Ramp within existing support, never spreading into excluded features.

    Zero padding treats image borders as boundaries too. Width is in pixels.
    """
    mask = np.asarray(mask)
    if mask.ndim != 2 or mask.dtype != bool:
        raise ValueError('Expected 2D boolean mask')
    if not np.isfinite(width) or width <= 0:
        raise ValueError('Expected finite positive feather width')
    padded = np.pad(mask.astype(np.uint8), 1)
    distance = cv2.distanceTransform(padded, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)[1:-1, 1:-1]
    t = np.clip(distance / width, 0, 1)
    return t * t * (3 - 2 * t)


def feather_correction(image_rgb, mask, parameters, width):
    image = np.asarray(image_rgb)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError('Expected uint8 RGB image')
    alpha = inward_alpha(mask, width)
    if alpha.shape != image.shape[:2]:
        raise ValueError('Mask shape differs from image')
    normalized = image.astype(float) / 255
    transformed = transform_rgb(normalized, *np.asarray(parameters, float))
    output = np.rint((normalized + alpha[..., None] * (transformed - normalized)) * 255).astype(np.uint8)
    return output, alpha


def correction_edge_jump(image_rgb, output_rgb, mask):
    """Mean correction-residual jump across mask edges, not perceptual quality."""
    residual = (output_rgb.astype(float) - image_rgb.astype(float)) / 255
    values = []
    for axis in (0, 1):
        crossing = np.diff(mask.astype(np.int8), axis=axis) != 0
        jump = np.abs(np.diff(residual, axis=axis))
        if crossing.any():
            values.append(jump[crossing].reshape(-1))
    return float(np.concatenate(values).mean()) if values else 0.0
