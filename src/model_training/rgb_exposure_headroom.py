"""Research-only positive exposure limit based on rendered RGB8 highlights."""
import numpy as np

from .luminance_chroma_operator import parameters, render_rgb8


def cap_facial_rgb_exposure(image, measurement, alpha, protected, controls):
    """Keep the largest tested gain with no exposure-added full facial channels.

    The comparison is against the same colour correction at unit exposure.
    Pixels already at full scale in the input or the unit-exposure result
    are excluded. Bisection resolves the quantization boundary.
    """
    raw = parameters(controls)
    effective = raw.copy()
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[-1] != 3:
        raise ValueError("RGB8 image required")
    if (measurement.shape != image.shape[:2] or measurement.dtype != bool
            or protected.shape != measurement.shape or protected.dtype != bool):
        raise ValueError("Matching boolean measurement and protection required")
    if (alpha.shape != measurement.shape or alpha.dtype.kind != "f" or not np.isfinite(alpha).all()
            or np.any((alpha < 0) | (alpha > 1)) or np.any(alpha[protected] != 0)):
        raise ValueError("Matching finite application alpha required")
    if raw[1] <= 1:
        return effective

    eligible = measurement & (alpha > 0) & ~protected & ~np.any(image == 255, axis=-1)
    rgb = image[eligible]
    weights = alpha[eligible]
    if not rgb.size:
        return effective
    veto = np.zeros(weights.shape, dtype=bool)
    effective[1] = 1
    unit = render_rgb8(rgb, weights, veto, effective)
    original = render_rgb8(rgb, weights, veto, raw)
    affected = (~np.any(unit == 255, axis=-1)) & np.any(original == 255, axis=-1)
    if not affected.any():
        return raw.copy()

    rgb, weights, veto = rgb[affected], weights[affected], veto[affected]
    # Under neutral-ray gamut mapping, raising luminance cannot lower a channel.
    safe, unsafe = 1.0, float(raw[1])
    for _ in range(24):
        effective[1] = (safe + unsafe) / 2
        if np.any(render_rgb8(rgb, weights, veto, effective) == 255):
            unsafe = effective[1]
        else:
            safe = effective[1]
    effective[1] = safe
    return effective
