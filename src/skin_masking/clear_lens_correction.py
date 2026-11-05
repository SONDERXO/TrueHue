"""Explicit clear-lens correction policy; no automatic glasses-type classifier.

The current parser has one glasses label. Its inner region approximates lenses;
the retained boundary band approximates rims/bridge, not exact frame truth.
"""
import cv2
import numpy as np
from src.skin_masking.object_protected_correction import protect_correction_objects
from src.skin_masking.continuous_correction import fill_correction_holes
from src.skin_masking.face_neck_support import FaceNeckSupport

VERSION = 'explicit_clear_lens_correction_v1'
RIM_WIDTH = 2  # fixed pixels on the existing256px analysis frame; no sweep


def protect_with_clear_lenses(support, categories, visible_face, face_outline, *,
                             transparent_glasses=False, protected=None):
    if not isinstance(transparent_glasses, bool):
        raise ValueError('Explicit boolean transparent-glasses designation required')
    if support.correction_mask.shape != (256,256):
        raise ValueError('This fixed rim approximation requires the existing256px frame')
    baseline,veto = protect_correction_objects(support,categories,visible_face,face_outline,protected=protected)
    lenses = np.zeros(categories.shape,bool); rims = np.zeros(categories.shape,bool)
    status = 'opaque_or_unknown_keep_whole_glasses_protected'
    if transparent_glasses:
        envelope,_ = fill_correction_holes((categories==6).astype(np.uint8)*255)
        distance = cv2.distanceTransform((envelope>0).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
        interior = distance > RIM_WIDTH
        rims = (envelope>0) & ~interior
        # Only restore facial skin/features/glasses, never another object class.
        lenses = interior & np.isin(categories,[1,2,3,4,5,6,10]) & (face_outline>0) & (support.correction_mask>0)
        if protected is not None:
            lenses &= ~protected
        veto = (veto & ~lenses) | rims
        if protected is not None:
            veto |= protected
        status = 'clear_lens_interiors_restored_rims_approximated' if lenses.any() else 'clear_lens_interior_unavailable_keep_protected'
    selected = (support.correction_mask>0) & ~veto
    neck = (support.neck_mask>0) & selected
    restored = selected & (baseline.correction_mask==0)
    report = dict(baseline.report,version=VERSION,transparent_glasses=transparent_glasses,
        glasses_policy=status,rim_band_pixels=RIM_WIDTH if transparent_glasses else None,
        lens_interior_pixels=int(lenses.sum()),restored_correction_pixels=int(restored.sum()),
        protected_rim_pixels=int((rims & (support.correction_mask>0)).sum()),
        correction_pixels=int(selected.sum()),neck_pixels=int(neck.sum()),
        removed_pixels=int(((support.correction_mask>0)&~selected).sum()),
        limitation='Glasses type must be designated explicitly. Two-pixel parser-envelope boundary approximates frames/rims/bridge; it cannot locate every wire, reflection or frame inside a lens. Other object/skin/neck limitations remain. Measurement unchanged.')
    return FaceNeckSupport(support.measurement_mask.copy(),neck.astype(np.uint8)*255,
        selected.astype(np.uint8)*255,report),veto,lenses.astype(np.uint8)*255,rims.astype(np.uint8)*255
