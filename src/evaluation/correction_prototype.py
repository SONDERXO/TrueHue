"""Input-only matrices and mask-explicit correction metrics for development."""
import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000
from src.data_preparation.controlled_training_table import FEATURES, TARGETS
from src.distortion_generation.generate_distortions import transform_rgb


def model_arrays(rows):
    """Only declared columns enter X/y, never numeric provenance metadata."""
    x=np.asarray([[float(r[k]) for k in FEATURES] for r in rows],dtype=float)
    y=np.asarray([[float(r[k]) for k in TARGETS] for r in rows],dtype=float)
    if not len(rows) or not np.isfinite(x).all() or not np.isfinite(y).all() or (y<=0).any():
        raise ValueError('Nonempty finite features and positive targets required')
    return x,y


def apply_correction(image_rgb, input_mask, parameters):
    """Apply model parameters only on the distorted-input mask, preserving rest."""
    image=np.asarray(image_rgb);mask=np.asarray(input_mask)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[-1]!=3:
        raise ValueError('Expected uint8 RGB image')
    if mask.dtype!=bool or mask.shape!=image.shape[:2]:
        raise ValueError('Expected matching boolean correction mask')
    gamma,red,blue=np.asarray(parameters,float)
    transformed=transform_rgb(image.astype(float)/255,gamma,red,blue)
    out=image.copy()
    out[mask]=np.rint(transformed[mask]*255).astype(np.uint8)
    return out


def image_errors(reference_rgb, output_rgb, source_scoring_mask):
    """Score common clean-source region; it is not used to choose predictions.

    CIEDE2000 assumes the decoded image-encoded RGB values represent sRGB.
    This is a relative reconstruction metric, not calibrated skin-color truth.
    """
    reference=np.asarray(reference_rgb);output=np.asarray(output_rgb)
    mask=np.asarray(source_scoring_mask)
    if reference.dtype!=np.uint8 or output.dtype!=np.uint8 or reference.shape!=output.shape:
        raise ValueError('Expected same-shaped uint8 RGB images')
    if mask.dtype!=bool or mask.shape!=reference.shape[:2] or not mask.any():
        raise ValueError('Expected nonempty boolean scoring region')
    ref=reference.astype(float)/255;out=output.astype(float)/255
    diff=np.abs(ref-out)
    delta=deltaE_ciede2000(rgb2lab(ref),rgb2lab(out))
    return dict(rgb_mae_source_mask=float(diff[mask].mean()),
        ciede2000_source_mask=float(delta[mask].mean()),
        rgb_mae_whole_image=float(diff.mean()),
        rgb_mae_outside_source_mask=float(diff[~mask].mean()) if (~mask).any() else None)
