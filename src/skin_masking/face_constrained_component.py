"""Rule-based component selection inside a face contour; experimental version."""
import cv2
import numpy as np
from src.skin_masking.skin_mask import keep_largest_connected_component

VERSION='face_constrained_component_v1'


def face_constrained_component(color_candidate, oval, exclusions):
    """Constrain existing color support before selection, then exclude anatomy.

    Never fills missing color support or falls back to background. Exclusions
    follow selection so feature holes cannot change the component competition.
    """
    masks=[np.asarray(m) for m in (color_candidate,oval,exclusions)]
    if any(m.ndim!=2 or m.dtype!=np.uint8 or not m.size or m.shape!=masks[0].shape
           or not set(np.unique(m))<={0,255} for m in masks):
        raise ValueError('Matching nonempty binary uint8 masks required')
    if not masks[1].any():raise ValueError('Nonempty face contour required; no fallback')
    bounded=cv2.bitwise_and(masks[0],masks[1])
    selected=keep_largest_connected_component(bounded)
    return cv2.bitwise_and(selected,cv2.bitwise_not(masks[2]))
