"""Whole-face geometric support; separate from the calibrated color-mask path.

This defines a face surface, not a semantic skin/occluder classifier. An explicit
non-skin veto can protect known hair/glasses/objects; none is guessed from color.
Existing ITA/MST masks and their dependency hashes are deliberately untouched.
"""
from dataclasses import dataclass
import cv2
import numpy as np

from src.skin_masking.face_outline_experiment import FACE_OVAL
from src.skin_masking.landmark_exclusion import FEATURE_INDICES
from src.skin_masking.mouth_exclusion import OUTER_LIPS

VERSION = 'anatomical_face_coverage_v1'
RASTER_SCALE = 4


@dataclass(frozen=True)
class FaceCoverage:
    mask: np.ndarray
    alpha: np.ndarray
    face_outline: np.ndarray
    exclusion_mask: np.ndarray
    report: dict


def build_face_coverage(image_bgr, landmarks, *, non_skin_veto=None):
    """Rasterize complete visible face support in full-image coordinates.

    Preserve eye, brow and filled outer-mouth exclusions after supersampling.
    Avoid clipping geometry to the detector rectangle and avoid deriving an
    outer boundary from a fragmented color mask. No hole-size/color tuning.
    ``non_skin_veto`` is optional explicit evidence, not automatically supplied
    by an unapproved learned parser. Missing landmarks fail, without fallback.
    Binary mask and edge alpha are separate: alpha never enters ITA here.
    """
    image = np.asarray(image_bgr)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3 or not image.size:
        raise ValueError('Nonempty uint8 BGR image required')
    points = np.asarray(landmarks)
    if points.ndim != 2 or points.shape[0] < 468 or points.shape[1] < 2:
        raise ValueError('Full-image face landmarks required')
    xy = points[:, :2]
    if not np.isfinite(xy).all() or np.abs(xy).max() > 1e6:
        raise ValueError('Finite, bounded face landmarks required')
    shape = image.shape[:2]
    if non_skin_veto is None:
        veto = np.zeros(shape, bool)
    else:
        veto = np.asarray(non_skin_veto)
        if veto.dtype != bool or veto.shape != shape:
            raise ValueError('Matching boolean non-skin veto required')

    def polygon(indices, *, hull=False):
        vertices = xy[list(indices)]
        if abs(cv2.contourArea(vertices.astype(np.float32))) < 1:
            raise ValueError('Degenerate facial geometry')
        # Clip only during rasterization, not individual vertex coordinates.
        high_points = np.rint(vertices * RASTER_SCALE).astype(np.int32)
        if hull:
            high_points = cv2.convexHull(high_points)
        raster = np.zeros((shape[0]*RASTER_SCALE, shape[1]*RASTER_SCALE), np.uint8)
        cv2.fillPoly(raster, [high_points], 255)
        return cv2.resize(raster, (shape[1], shape[0]), interpolation=cv2.INTER_AREA)

    outline_alpha = polygon(FACE_OVAL)
    outline = outline_alpha >= 128
    if not outline.any():
        raise ValueError('Face outline is outside the visible image')
    exclusion = np.zeros(shape, bool)
    for name in ('left_eye', 'right_eye', 'left_eyebrow', 'right_eyebrow'):
        exclusion |= polygon(FEATURE_INDICES[name], hull=True) > 0
    exclusion |= polygon(OUTER_LIPS, hull=True) > 0
    exclusion |= veto
    selected = outline & ~exclusion
    alpha = outline_alpha.copy()
    alpha[~outline | exclusion] = 0
    mask = selected.astype(np.uint8)*255
    return FaceCoverage(mask=mask, alpha=alpha,
        face_outline=outline.astype(np.uint8)*255,
        exclusion_mask=exclusion.astype(np.uint8)*255,
        report=dict(version=VERSION, selected_pixels=int(selected.sum()),
            outline_pixels=int(outline.sum()), excluded_outline_pixels=int((outline & exclusion).sum()),
            source='full_image_landmark_surface_not_color_threshold_support',
            non_skin_veto_supplied=non_skin_veto is not None,
            measurement_compatible_with_existing_lookup=False,
            requires_occlusion_review=True,
            limitation='Geometry cannot identify all hair, facial hair, glasses, paint or objects inside the face outline; visible off-frame skin cannot be recovered.'))
