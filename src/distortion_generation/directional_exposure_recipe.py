"""Explicit revised Table2 interpretation; experimental development, not runtime."""
import numpy as np
from src.distortion_generation.table2_composite import SETTINGS

VERSION = 'directional_exposure_pivot_gamma_offset_rgb8_v1'


def render_rgb(image, alpha, group, variant, direction='none'):
    """Distort supplied RGB8 support; return image and provenance, never admission.

    Under: (1+c)*(x**(1/g)-1)+1-b; over: (1+c)*x**g+b.
    c=Table2 contrast/100; b=abs(Table2 brightness)/255.
    Colour: existing additive red/blue shifts/255, applied after exposure.
    Clip transformed float once, blend alpha, then round once to RGB8.
    Direction guarantees apply to exposure-only, before additive colour shifts.
    """
    image = np.asarray(image)
    alpha = np.asarray(alpha)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[-1] != 3 or not image.size:
        raise ValueError('Nonempty uint8 RGB required')
    if (alpha.shape != image.shape[:2] or not np.issubdtype(alpha.dtype, np.floating)
            or not np.isfinite(alpha).all() or (alpha < 0).any() or (alpha > 1).any()):
        raise ValueError('Matching finite floating alpha in [0,1] required')
    if group not in SETTINGS or variant not in ('clean', 'exposure', 'color', 'combined'):
        raise ValueError('Explicit severity group and variant required')
    expected = ('under', 'over') if variant in ('exposure', 'combined') else ('none',)
    if direction not in expected:
        raise ValueError('Exposure requires under/over; clean/color requires none')
    s = dict(SETTINGS[group])
    x = image.astype(float)/255
    raw = x.copy()
    exponent = None
    if direction != 'none':
        exponent = 1/s['gamma'] if direction == 'under' else s['gamma']
        contrast = 1+s['contrast']/100
        offset = abs(s['brightness'])/255
        if direction == 'under':
            raw = contrast*(x**exponent-1)+1-offset
        else:
            raw = contrast*x**exponent+offset
    if variant in ('color', 'combined'):
        raw += np.array([s['cyan_red'], 0, s['yellow_blue']])/255
    selected = alpha > 0
    clipped = ((raw < 0) | (raw > 1)) & selected[..., None]
    mixed = x*(1-alpha[..., None])+np.clip(raw, 0, 1)*alpha[..., None]
    output = np.rint(mixed*255).astype(np.uint8)
    output[~selected] = image[~selected]
    return output, dict(recipe_version=VERSION, group=group, variant=variant,
        direction=direction, table2_settings=s, effective_direct_exponent=exponent,
        clipping_scope='preblend transformed channels at positive alpha only',
        clipped_channel_samples=int(clipped.sum()),
        clipped_pixels=int(clipped.any(axis=2).sum()),
        application_pixels=int(selected.sum()),
        status='user_authorised_development_interpretation_not_panel_approved',
        training_admitted=False, runtime_output_schema_changed=False)
