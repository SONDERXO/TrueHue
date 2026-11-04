"""Explicit engineering decomposition of Table2, not recipes quoted from paper."""
import numpy as np
from src.distortion_generation.table2_composite import SETTINGS

VERSION='table2_three_variant_direct_gamma_v1'
VARIANTS=('exposure','color','combined')


def render_rgb(image,group,variant):
    """Return encoded RGB and final-clipping report; preserve source pixels."""
    image=np.asarray(image)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[-1]!=3 or not image.size:
        raise ValueError('Nonempty uint8RGB required')
    if group not in SETTINGS or variant not in VARIANTS:raise ValueError('Declared severity and variant required')
    settings=dict(SETTINGS[group]);raw=image.astype(float)/255
    if variant in ('exposure','combined'):
        raw=np.power(raw,settings['gamma'])
        raw=(raw-.5)*(1+settings['contrast']/100)+.5+settings['brightness']/255
    if variant in ('color','combined'):
        raw+=np.array([settings['cyan_red'],0,settings['yellow_blue']])/255
    clipped=(raw<0)|(raw>1)
    return np.rint(np.clip(raw,0,1)*255).astype(np.uint8),dict(recipe_version=VERSION,variant=variant,
        group=group,settings=settings,gamma_convention='direct_exponent',
        clipped_pixels=int(clipped.any(axis=2).sum()),clipped_channel_samples=int(clipped.sum()),
        total_channel_samples=int(raw.size),recipe_status='engineering_choice_not_fully_specified_by_proposal')
