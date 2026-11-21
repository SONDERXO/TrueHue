"""Research-only attenuation of positive exposure at clipped facial pixels."""
import numpy as np

from .luminance_chroma_operator import parameters, render_float


def soften_local_rgb_highlights(image, baseline, measurement, alpha, protected, controls):
    """Attenuate the existing exposure contribution only at newly full pixels."""
    raw = parameters(controls)
    if (image.dtype != np.uint8 or image.ndim != 3 or image.shape[-1] != 3
            or baseline.dtype != np.uint8 or baseline.shape != image.shape):
        raise ValueError("Matching RGB8 input and output required")
    if (measurement.shape != image.shape[:2] or measurement.dtype != bool
            or protected.shape != measurement.shape or protected.dtype != bool):
        raise ValueError("Matching boolean measurement and protection required")
    if (alpha.shape != measurement.shape or alpha.dtype.kind != "f" or not np.isfinite(alpha).all()
            or np.any((alpha < 0) | (alpha > 1)) or np.any(alpha[protected] != 0)):
        raise ValueError("Matching finite application alpha required")

    result = baseline.copy()
    if raw[1] <= 1:
        return result
    eligible = (measurement & (alpha > 0) & ~protected
                & ~np.any(image == 255, axis=-1) & np.any(baseline == 255, axis=-1))
    y, x = np.nonzero(eligible)
    if not y.size:
        return result
    pixels = image[y, x] / 255.
    weights = alpha[y, x]
    veto = np.zeros(y.size, dtype=bool)
    unit = raw.copy()
    unit[1] = 1.
    start = 255. * render_float(pixels, weights, veto, unit)
    movable = ~np.any(np.rint(start) == 255, axis=-1)
    if not movable.any():
        return result
    y, x = y[movable], x[movable]
    start = start[movable]
    stop = 255. * render_float(pixels[movable], weights[movable], veto[movable], raw)
    if not np.array_equal(np.rint(stop).astype(np.uint8), baseline[y, x]):
        raise ValueError("Saved output does not match the frozen exposure render")

    # Scaling the added RGB contribution per pixel keeps neighbouring midtones
    # unchanged. The half-code boundary rounds to 254 with the existing renderer.
    delta = stop - start
    limits = np.ones_like(delta)
    np.divide(254.5 - start, delta, out=limits, where=delta > 0)
    fraction = np.clip(limits.min(axis=-1), 0., 1.)
    adjusted = np.minimum(start + fraction[:, None] * delta, 254.5)
    result[y, x] = np.rint(adjusted).astype(np.uint8)
    return result
