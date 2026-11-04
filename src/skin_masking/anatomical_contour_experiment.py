"""Isolated fixed anatomical/contour ablation. No runtime pipeline imports this."""
import cv2
import numpy as np

from src.skin_masking.landmark_exclusion import build_feature_region_masks
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
from src.skin_masking.face_outline_experiment import restrict_to_face_outline


def anatomy(image, landmarks):
    """Full-frame geometry; add 3% inter-eye-distance eye/brow margins only."""
    points = np.asarray(landmarks)
    if points.ndim != 2 or points.shape[0] < 468 or points.shape[1] != 2 or not np.isfinite(points).all():
        raise ValueError('Finite full-frame face landmarks required')
    # Eye corner pairs locate two eye centers without iris-specific indices.
    eye_a = (points[33] + points[133]) / 2
    eye_b = (points[362] + points[263]) / 2
    separation = float(np.linalg.norm(eye_a-eye_b))
    if separation < 5 or separation > max(image.shape[:2]):
        raise ValueError('Implausible inter-eye geometry')
    radius = max(1, int(np.ceil(.03*separation)))
    regions = build_feature_region_masks(image, points)
    original = np.zeros(image.shape[:2], bool)
    expanded = original.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*radius+1, 2*radius+1))
    for name, mask in regions.items():
        original |= mask > 0
        expanded |= (cv2.dilate(mask, kernel) if name in ('left_eye', 'right_eye', 'left_eyebrow', 'right_eyebrow') else mask) > 0
    _, mouth = exclude_complete_mouth(np.full(original.shape, 255, np.uint8), points)
    original |= mouth > 0
    expanded |= mouth > 0
    _, oval = restrict_to_face_outline(np.full(original.shape, 255, np.uint8), points)
    return original, expanded, oval > 0, dict(inter_eye_distance=separation, exclusion_radius=radius)


def removal(mask, excluded):
    if mask.dtype != bool or excluded.dtype != bool or mask.shape != excluded.shape:
        raise ValueError('Matching boolean masks required')
    return mask & ~excluded


def extend(image, old, excluded, oval, categories, measurement, face_box, geometry_allowed):
    """Union bounded semantic/material additions, then apply mandatory exclusions.

    Existing support may be removed only by exclusions. Added pixels do not use
    HSV/YCrCb: this explicit ablation replaces their absolute color gate with
    face-skin class, local distance and existing robust relative-Lab distance.
    """
    shape = image.shape[:2]
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError('Expected uint8 BGR image')
    for mask in (old, excluded, oval, measurement):
        if mask.dtype != bool or mask.shape != shape:
            raise ValueError('Matching full-frame boolean masks required')
    if categories.dtype != np.uint8 or categories.shape != shape or (categories > 5).any():
        raise ValueError('Invalid native category map')
    if not geometry_allowed:
        raise ValueError('Prior oval-retention geometry gate failed; no extension fallback')
    x, y, w, h = map(int, face_box)
    if min(x, y) < 0 or min(w, h) <= 0 or x+w > shape[1] or y+h > shape[0]:
        raise ValueError('Invalid face box')
    seeds = measurement & ~excluded
    if seeds.sum() < 1000:
        raise ValueError('Fewer than 1000 measurement seeds after exclusions')
    radius = max(1, int(np.ceil(.02*max(w, h))))
    near_old = cv2.distanceTransform((~old).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE) <= radius
    near_oval = cv2.distanceTransform((~oval).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE) <= radius
    bounds = np.zeros(shape, bool)
    bounds[max(0,y-radius):min(shape[0],y+h+radius), max(0,x-radius):min(shape[1],x+w+radius)] = True
    lab = cv2.cvtColor(image.astype(np.float32)/255, cv2.COLOR_BGR2LAB)
    samples = lab[seeds].astype(float)
    center = np.median(samples, axis=0)
    scale = np.maximum(1.4826*np.median(np.abs(samples-center), axis=0), [12.,6.,6.])
    distance = np.sqrt(np.sum(((lab-center)/scale)**2, axis=2))
    additions = ~old & ~excluded & near_old & near_oval & bounds & (categories == 3) & (distance <= 3)
    candidate = (old | additions) & ~excluded
    assert not (candidate & excluded).any()
    assert not ((old & ~candidate) & ~excluded).any()
    return candidate, dict(extension_radius=radius, added_pixels=int(additions.sum()),
                          removed_pixels=int((old & excluded).sum()))
