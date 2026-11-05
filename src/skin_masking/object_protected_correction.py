"""Removal-only object protection after face/neck continuity, before blending.

This candidate does not change measurement or the pinned whole-face builder.
Parser and visibility predictions are evidence, not complete object detection.
"""
import numpy as np
from src.skin_masking.face_neck_support import FaceNeckSupport

VERSION = 'object_protected_face_neck_correction_v1'
# Keep facial features, ears and associated neck; protect predicted non-face items.
PROTECTED_CLASSES = (0, 6, 9, 15, 16, 17, 18)


def protect_correction_objects(support, categories, visible_face, face_outline, *, protected=None):
    """Return revised support and the hard veto required by downstream blending.

    Run AFTER hole filling. Never reconstruct holes after this veto. Visibility
    applies to the face, not the whole neck: FaceOcc is not a neck classifier.
    The geometric face outline also covers any overlapping predicted neck.
    Explicit caller protections always win. No dilation or new support is added.
    """
    shape = support.correction_mask.shape
    for name, mask in [('correction', support.correction_mask), ('measurement', support.measurement_mask),
                       ('neck', support.neck_mask), ('visibility', visible_face), ('outline', face_outline)]:
        if not isinstance(mask, np.ndarray) or mask.dtype != np.uint8 or mask.shape != shape or mask.ndim != 2 or not set(np.unique(mask)) <= {0, 255}:
            raise ValueError('Matching binary uint8 '+name+' mask required')
    if not isinstance(categories, np.ndarray) or categories.dtype != np.uint8 or categories.shape != shape or (categories > 18).any():
        raise ValueError('Matching parser categories0..18 required')
    if protected is not None and (not isinstance(protected, np.ndarray) or protected.dtype != bool or protected.shape != shape):
        raise ValueError('Matching boolean explicit protection required')
    old = support.correction_mask > 0
    semantic = np.isin(categories, PROTECTED_CLASSES)
    face = (face_outline > 0) | (old & (support.neck_mask == 0))
    occluded = face & (visible_face == 0)
    veto = semantic | occluded
    if protected is not None:
        veto |= protected
    selected = old & ~veto
    neck = (support.neck_mask > 0) & selected
    report = dict(support.report, version=VERSION,
        correction_policy='parent_support_minus_predicted_objects_and_face_occlusions',
        protected_parser_classes=list(PROTECTED_CLASSES),
        visibility_scope='geometric_face_plus_non_neck_parent_support',
        parent_correction_pixels=int(old.sum()), correction_pixels=int(selected.sum()),
        neck_pixels=int(neck.sum()), removed_pixels=int((old & veto).sum()),
        semantic_removed_pixels=int((old & semantic).sum()),
        visibility_removed_pixels=int((old & occluded).sum()),
        measurement_mask_unchanged=True, no_added_support=True,
        limitation='Objects misclassified as facial features/skin or neck can remain. FaceOcc may remove useful skin; it does not validate neck occlusions. Beard has no dedicated parser class. No object/skin accuracy guarantee.')
    return FaceNeckSupport(support.measurement_mask.copy(), neck.astype(np.uint8)*255,
                           selected.astype(np.uint8)*255, report), veto
