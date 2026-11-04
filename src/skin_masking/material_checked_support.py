"""Experimental input-relative Lab check for proposed correction additions.

This is a color-consistency heuristic, not a semantic skin/hair classifier.
It never changes the estimation mask or removes existing baseline support.
"""
import cv2
import numpy as np
from src.skin_masking.guarded_correction_support import guarded_correction_support


def material_checked_support(image_bgr, input_mask, exclusion_mask):
    """Keep guarded additions only if close to the input skin's robust Lab color.

    Fixed rule: distance <=3 in diagonally standardized Lab, using channel
    median and 1.4826*MAD, with scale floors [12,6,6] in float OpenCV Lab units.
    Relative color avoids an absolute light/dark skin cutoff. Similar-colored
    non-skin and contaminated seed masks remain limitations. No reference input.
    """
    image = np.asarray(image_bgr)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError('Expected uint8 BGR image')
    guard = guarded_correction_support(input_mask,exclusion_mask)
    if image.shape[:2] != input_mask.shape:
        raise ValueError('Image and mask dimensions differ')
    seeds = input_mask & ~exclusion_mask
    if seeds.sum() < 1000:
        raise ValueError('At least 1000 input skin pixels required for color check')
    lab = cv2.cvtColor(image.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
    samples = lab[seeds].astype(float)
    center = np.median(samples,axis=0)
    scale = np.maximum(1.4826*np.median(np.abs(samples-center),axis=0),[12.,6.,6.])
    distance = np.sqrt(np.sum(((lab-center)/scale)**2,axis=2))
    return seeds | (guard & ~seeds & (distance<=3.))
