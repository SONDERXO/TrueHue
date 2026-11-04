"""Clipping-free red/blue attenuation probes, explicitly different from Table2."""
import numpy as np
from src.distortion_generation.table2_composite import SETTINGS

VERSION = 'core_directional_gamma_single_channel_attenuation_v1'


def render_rgb(reference, alpha, group, cast, direction='none'):
    """Cool attenuates red; warm attenuates blue; green gain remains one.

    k=1-abs(Table2 corresponding slider)/255. Exposure, if specified, uses
    direct exponent1/g under or g over. Clip-free float transform -> blend ->
    one RGB8 round. Relative casts also darken; they are not pure chromaticity
    changes, additive-slider equivalents, or calibrated physical white balance.
    """
    reference = np.asarray(reference); alpha = np.asarray(alpha)
    if reference.dtype != np.uint8 or reference.ndim != 3 or reference.shape[-1] != 3 or not reference.size:
        raise ValueError('Nonempty RGB8 reference required')
    if (alpha.shape != reference.shape[:2] or not np.issubdtype(alpha.dtype, np.floating)
            or not np.isfinite(alpha).all() or (alpha < 0).any() or (alpha > 1).any()
            or not (alpha > 0).any()):
        raise ValueError('Nonempty finite floating alpha within [0,1] required')
    if group not in SETTINGS or cast not in ('cool', 'warm') or direction not in ('none', 'under', 'over'):
        raise ValueError('Explicit severity, cast and optional exposure direction required')
    settings = dict(SETTINGS[group])
    gamma = settings['gamma']
    exponent = 1. if direction == 'none' else (1/gamma if direction == 'under' else gamma)
    gains = np.ones(3)
    index, slider = (0, 'cyan_red') if cast == 'cool' else (2, 'yellow_blue')
    gains[index] = 1-abs(settings[slider])/255
    if not 0 < gains[index] <= 1:
        raise ValueError('Table-derived attenuation must be positive and at most one')
    x = reference.astype(float)/255
    raw = x**exponent*gains
    selected = alpha > 0
    clipped = ((raw < 0) | (raw > 1)) & selected[..., None]
    output = np.rint(255*(x*(1-alpha[..., None])+raw*alpha[..., None])).astype(np.uint8)
    output[~selected] = reference[~selected]
    return output, dict(recipe_version=VERSION, group=group, cast=cast, direction=direction,
        scenario='color' if direction == 'none' else 'combined',
        effective_direct_exponent=exponent, gains=gains.tolist(), table2_settings=settings,
        clipped_channel_samples=int(clipped.sum()), clipped_pixels=int(clipped.any(axis=2).sum()),
        new_endpoint_channel_samples=int(np.count_nonzero(
            ((output == 0) | (output == 255)) & (reference > 0) & (reference < 255)
            & selected[..., None])),
        brightness_offset=0, contrast_extra=0,
        status='experimental_development_not_training_admission_or_panel_approval',
        training_admitted=False, runtime_output_schema_changed=False)
