"""Research-only exposure protection for widespread additional facial clipping."""
import numpy as np

from .facial_exposure_headroom import cap_facial_exposure_headroom
from .luminance_chroma_operator import parameters, render_rgb8
from .rgb_exposure_headroom import cap_facial_rgb_exposure


def cap_widespread_exposure(image, baseline, measurement, alpha, protected, controls, *, analysis=None):
    """Apply headroom protection when at least a quarter of eligible pixels clip.

    A pixel counts only when the positive gain adds full-scale RGB clipping.
    Prefer the established facial-luminance adjustment. Use RGB headroom
    when the facial-luminance check leaves the positive gain in place.
    """
    raw = parameters(controls)
    if (image.dtype != np.uint8 or image.ndim != 3 or image.shape[-1] != 3
            or baseline.dtype != np.uint8 or baseline.shape != image.shape):
        raise ValueError("Matching RGB8 input and result required")
    if (measurement.shape != image.shape[:2] or measurement.dtype != bool
            or protected.shape != measurement.shape or protected.dtype != bool):
        raise ValueError("Matching boolean measurement and protection required")
    if (alpha.shape != measurement.shape or alpha.dtype.kind != "f" or not np.isfinite(alpha).all()
            or np.any((alpha < 0) | (alpha > 1)) or np.any(alpha[protected] != 0)):
        raise ValueError("Matching finite application alpha required")

    eligible = measurement & (alpha > 0) & ~protected & ~np.any(image == 255, axis=-1)
    count = int(eligible.sum())
    decision = {"controls": raw.copy(), "eligible_pixels": count, "exposure_clipped_pixels": 0,
                "method": "original"}
    if raw[1] <= 1 or not count:
        return decision
    possible = eligible & np.any(baseline == 255, axis=-1)
    if not possible.any():
        return decision
    unit = raw.copy()
    unit[1] = 1.
    weights = alpha[possible]
    colour_result = render_rgb8(image[possible], weights, np.zeros(weights.shape, dtype=bool), unit)
    clipped = int(np.count_nonzero(~np.any(colour_result == 255, axis=-1)))
    decision["exposure_clipped_pixels"] = clipped
    if 4 * clipped < count:
        return decision

    scope = analysis if analysis is not None else (image, measurement.astype(np.uint8) * 255, alpha, protected)
    luminance = np.asarray(cap_facial_exposure_headroom(*scope, raw)["effective_controls"])
    if 1 <= luminance[1] < raw[1] and np.array_equal(luminance[[0, 2, 3, 4]], raw[[0, 2, 3, 4]]):
        decision.update(controls=luminance, method="facial_luminance")
        return decision
    rgb = cap_facial_rgb_exposure(image, measurement, alpha, protected, raw)
    decision.update(controls=rgb, method="facial_rgb")
    return decision
