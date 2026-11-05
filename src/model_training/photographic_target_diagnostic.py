"""Fixed photo operator-capacity probes; never creates admitted tree labels."""
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
from src.distortion_generation.development_roles import core_exposure,assign_role
from src.distortion_generation.core_colour_recipe import render_rgb as core_colour
from src.distortion_generation.directional_exposure_recipe import render_rgb as stress

PRESET = 'medium'  # common engineering severity, never a photo's skin/MST category


def case_matrix():
    rows=[dict(id='clean',layer='clean',scenario='clean',direction='none',cast='none')]
    for direction in ('under','over'):
        rows.append(dict(id='exposure_'+direction,layer='core',scenario='exposure',direction=direction,cast='none'))
    for cast in ('cool','warm'):
        rows.append(dict(id='colour_'+cast,layer='core',scenario='color',direction='none',cast=cast))
        for direction in ('under','over'):
            rows.append(dict(id='combined_'+cast+'_'+direction,layer='core',scenario='combined',direction=direction,cast=cast))
    for scenario in ('exposure','color','combined'):
        for direction in (('none',) if scenario=='color' else ('under','over')):
            rows.append(dict(id='stress_'+scenario+'_'+direction,layer='composite_stress_design',scenario=scenario,direction=direction,cast='additive'))
    return rows


def distort(reference,alpha,case):
    if case['layer']=='clean':
        image=reference.copy();recipe=dict(version='exact_identity',clipped_channel_samples=0)
    elif case['layer']=='composite_stress_design':
        image,recipe=stress(reference,alpha,PRESET,case['scenario'],case['direction'])
    elif case['scenario']=='exposure':
        image,recipe=core_exposure(reference,alpha,PRESET,case['direction'])
    else:
        image,recipe=core_colour(reference,alpha,PRESET,case['cast'],case['direction'])
    role=assign_role(reference,image,alpha,scenario=case['scenario'],clipped_channel_samples=recipe['clipped_channel_samples'])
    return image,recipe,role


def metrics(image,reference,mask):
    if image.dtype!=np.uint8 or reference.dtype!=np.uint8 or image.shape!=reference.shape:
        raise ValueError('Matching RGB8 image/reference required')
    if mask.dtype!=bool or mask.shape!=image.shape[:2] or not mask.any():
        raise ValueError('Nonempty explicit boolean scoring mask required')
    # Decode identical selected RGB values; no assumption of calibrated physical colour.
    first=image[mask].astype(float)/255;second=reference[mask].astype(float)/255
    de=deltaE_ciede2000(rgb2lab(first),rgb2lab(second))
    return dict(rgb8_mae_codes=float(np.abs(image[mask].astype(float)-reference[mask]).mean()),
        relative_deltaE00_mean=float(de.mean()),scoring_pixels=int(mask.sum()))
