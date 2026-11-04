"""Explicit direct-exponent convention from proposal PDF38; legacy remains intact."""
import numpy as np
from src.distortion_generation.table2_composite import SETTINGS

TRANSFORM_VERSION='encoded_rgb_direct_gamma_then_gain_v1'
COMPOSITE_VERSION='table2_direct_gamma_sensitivity_v2'


def _parameters(gamma,red_gain,blue_gain):
    if any(isinstance(x,(bool,np.bool_)) for x in [gamma,red_gain,blue_gain]):
        raise ValueError('Numeric positive gamma/gains required')
    values=np.asarray([gamma,red_gain,blue_gain],dtype=float)
    if not np.isfinite(values).all() or (values<=0).any():raise ValueError('Finite positive gamma/gains required')
    return values


def legacy_to_paper_parameters(gamma,red_gain,blue_gain):
    """Preserve the old output curve by reciprocating gamma, not changing gains."""
    gamma,red,blue=_parameters(gamma,red_gain,blue_gain)
    reciprocal=1/gamma
    if not np.isfinite(reciprocal):raise ValueError('Reciprocal gamma overflow')
    return dict(gamma=float(reciprocal),red_gain=float(red),blue_gain=float(blue))


def transform_rgb(image,gamma,red_gain=1.,blue_gain=1.,*,clip=True):
    """Direct power: gamma<1 brightens; >1 darkens. Encoded float RGB [0,1]."""
    image=np.asarray(image)
    if image.ndim!=3 or image.shape[-1]!=3 or not image.size or not np.issubdtype(image.dtype,np.floating):
        raise ValueError('Nonempty normalized floating-point RGB required')
    if not np.isfinite(image).all() or (image<0).any() or (image>1).any():raise ValueError('Finite RGB within[0,1]required')
    gamma,red,blue=_parameters(gamma,red_gain,blue_gain)
    with np.errstate(over='raise',invalid='raise'):
        output=np.power(image.astype(float),gamma)*[red,1.,blue]
    return np.clip(output,0,1) if clip else output


def composite_rgb(image,group):
    """Gamma-convention sensitivity only; remaining v1 assumptions unchanged.

    Not the fully specified or approved three-variant thesis augmentation.
    Brightness/contrast units, order and additive channel shifts remain explicit
    inherited engineering choices, not claimed exact paper requirements.
    """
    image=np.asarray(image)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[-1]!=3 or not image.size:raise ValueError('Nonempty uint8RGB required')
    if group not in SETTINGS:raise ValueError('Explicit severity group required')
    settings=dict(SETTINGS[group])
    raw=np.power(image.astype(float)/255,settings['gamma'])
    raw=(raw-.5)*(1+settings['contrast']/100)+.5+settings['brightness']/255
    raw+=np.array([settings['cyan_red'],0,settings['yellow_blue']])/255
    clipped=(raw<0)|(raw>1)
    return np.rint(np.clip(raw,0,1)*255).astype(np.uint8),dict(transform_version=COMPOSITE_VERSION,
        gamma_convention='direct_exponent',settings=settings,clipped_pixels=int(clipped.any(axis=2).sum()),
        clipped_channel_samples=int(clipped.sum()),total_channel_samples=int(raw.size))
