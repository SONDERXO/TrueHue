"""Fixed quantization-aware luminance-headroom bound on positive exposure gain.

This is not an exposure-necessity classifier. It changes no learned parameters
and does not claim that an in-bound correction is desirable or colour accurate.
"""
import numpy as np

from .luminance_chroma_operator import parameters, decode, W


def cap_exposure_headroom(image, alpha, protected, controls):
    image = np.asarray(image); alpha = np.asarray(alpha); protected = np.asarray(protected)
    raw = parameters(controls).tolist()
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[-1] != 3:
        raise ValueError('RGB8 image required')
    if (alpha.shape != image.shape[:2] or alpha.dtype.kind != 'f'
            or not np.isfinite(alpha).all() or np.any(alpha < 0) or np.any(alpha > 1)):
        raise ValueError('Matching finite floating alpha in[0,1] required')
    if (protected.shape != alpha.shape or protected.dtype != bool
            or np.any(alpha[protected] != 0)):
        raise ValueError('Matching boolean protection with zero alpha required')
    selected = (alpha > 0) & ~protected
    if not selected.any(): raise ValueError('Nonempty application support required')
    q,g,r,b,s = raw
    info = dict(raw_controls=raw, effective_controls=raw.copy(), applied=False,
                policy='quantized_luminance_headroom_v1', reason='not_brightening',
                quantization_half_code=.5, maximum_lower_luminance_power=None)
    if g <= 1: return info
    lower = np.maximum(image[selected].astype(np.float64)-.5, 0)/255.
    linear = decode(lower)*np.array([r,1.,b])
    maximum = float(np.max(np.power(linear @ W, q)))
    info['maximum_lower_luminance_power'] = maximum
    if maximum == 0 or g*maximum <= 1:
        info['reason'] = 'within_quantized_headroom'; return info
    bound = float(np.nextafter(1./maximum, 0.))
    if bound < 1:
        info['effective_controls'] = [1.]*5
        info['reason'] = 'identity_no_positive_exposure_headroom'
    else:
        effective = raw.copy(); effective[1] = min(g,bound)
        assert effective[1]*maximum <= 1.
        info['effective_controls'] = parameters(effective).tolist()
        info['reason'] = 'positive_exposure_capped'
    info['applied'] = info['effective_controls'] != raw
    return info
