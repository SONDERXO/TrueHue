"""Map analysis support and render controls on untouched original RGB pixels.

Only masks are resized. This does not create a native-resolution skin detector
or qualify the boundaries inferred from the 256-pixel analysis image.
"""
import cv2
import numpy as np

from src.model_training.luminance_chroma_operator import parameters, render_rgb8


def lift_analysis_support(alpha, protected, original_shape):
    """Lift square analysis coordinates back to the full original frame.

    Bilinear alpha is restricted to nearest-neighbour application membership;
    nearest-neighbour protection overrides it. No positive support is invented
    outside the mapped analysis support, including at interpolation boundaries.
    """
    if (not isinstance(alpha, np.ndarray) or alpha.shape != (256, 256)
            or not np.issubdtype(alpha.dtype, np.floating) or not np.isfinite(alpha).all()
            or np.any(alpha < 0) or np.any(alpha > 1)):
        raise ValueError('Finite 256x256 analysis alpha in [0,1] required')
    if (not isinstance(protected, np.ndarray) or protected.dtype != bool
            or protected.shape != alpha.shape or np.any(alpha[protected] != 0)):
        raise ValueError('Matching boolean analysis protection with zero alpha required')
    if (len(original_shape) != 3 or original_shape[2] != 3
            or any(not isinstance(v, (int, np.integer)) or v <= 0 for v in original_shape)):
        raise ValueError('Positive original HxWx3 shape required')
    height, width = original_shape[:2]
    size = (int(width), int(height))
    membership = cv2.resize((alpha > 0).astype(np.uint8), size, interpolation=cv2.INTER_NEAREST) > 0
    veto = cv2.resize(protected.astype(np.uint8), size, interpolation=cv2.INTER_NEAREST) > 0
    lifted = np.clip(cv2.resize(alpha.astype(np.float64), size, interpolation=cv2.INTER_LINEAR), 0., 1.)
    lifted[~membership | veto] = 0.
    return lifted, veto


def render_original_rgb8(original, alpha, protected, controls):
    """Use the existing pointwise renderer in strips to bound temporary memory."""
    if (not isinstance(original, np.ndarray) or original.dtype != np.uint8
            or original.ndim != 3 or original.shape[2] != 3 or not original.size):
        raise ValueError('Nonempty original RGB8 required')
    if (not isinstance(alpha, np.ndarray) or alpha.shape != original.shape[:2]
            or not np.issubdtype(alpha.dtype, np.floating) or not np.isfinite(alpha).all()
            or np.any(alpha < 0) or np.any(alpha > 1)):
        raise ValueError('Matching finite original-resolution alpha in [0,1] required')
    if (not isinstance(protected, np.ndarray) or protected.dtype != bool
            or protected.shape != alpha.shape or np.any(alpha[protected] != 0)):
        raise ValueError('Matching original-resolution boolean protection required')
    bounded = parameters(controls)
    if np.array_equal(bounded, np.ones(5)):
        return original.copy()
    result = np.empty_like(original)
    for start in range(0, original.shape[0], 128):
        rows = slice(start, start + 128)
        result[rows] = render_rgb8(original[rows], alpha[rows], protected[rows], bounded)
    return result
