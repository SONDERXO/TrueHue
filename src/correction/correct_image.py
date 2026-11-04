"""Input-only correction using a frozen estimator and explicit mask policy."""
from dataclasses import dataclass
import numpy as np
import cv2
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.evaluation.correction_prototype import apply_correction
from src.skin_masking.material_checked_support import material_checked_support
from src.skin_masking.selfie_material_segmenter import hair_veto_support

LEGACY_POLICY='estimation_mask_v1'
MATERIAL_HAIR_POLICY='material_hair_veto_v1'
MASK_POLICIES=(LEGACY_POLICY,MATERIAL_HAIR_POLICY)
ESTIMATION_VERSION='v2_complete_mouth_v1'


@dataclass
class CorrectionResult:
    corrected_bgr: np.ndarray
    estimation_mask: np.ndarray
    correction_mask: np.ndarray
    features: dict
    parameters: dict
    metadata: dict


def correct_from_estimate(image_bgr,face_box,estimation_crop,exclusion_crop,model,
                          mask_policy=LEGACY_POLICY,segmenter=None,protected_mask=None):
    """Estimation is fixed; mask policy affects only correction application.

    Reference images, human labels, MST guesses and distortion targets are not
    accepted. Explicit protected pixels are preserved under either policy.
    Unavailable semantic segmentation fails instead of falling back to legacy.
    """
    if mask_policy not in MASK_POLICIES:raise ValueError('Unknown correction mask policy')
    image=np.asarray(image_bgr);estimate=np.asarray(estimation_crop);exclude=np.asarray(exclusion_crop)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
        raise ValueError('Expected nonempty uint8 BGR image')
    if len(face_box)!=4 or any(not isinstance(v,(int,np.integer)) for v in face_box):raise ValueError('Invalid face box')
    x,y,w,h=face_box
    if min(x,y)<0 or min(w,h)<=0 or x+w>image.shape[1] or y+h>image.shape[0]:raise ValueError('Face box outside image')
    if estimate.dtype!=bool or exclude.dtype!=bool or estimate.shape!=(h,w) or exclude.shape!=(h,w):
        raise ValueError('Expected matching boolean crop masks')
    if protected_mask is not None:
        protected=np.asarray(protected_mask)
        if protected.dtype!=bool or protected.shape!=image.shape[:2]:raise ValueError('Invalid protected-pixel mask')
    else:protected=np.zeros(image.shape[:2],bool)
    if np.any(estimate&exclude):raise ValueError('Estimation mask overlaps anatomical exclusions')
    crop=image[y:y+h,x:x+w]
    stats=compute_masked_lab_statistics(crop,estimate.astype(np.uint8)*255,1000)
    if not stats['valid']:raise ValueError('Insufficient/invalid original skin statistics: '+str(stats.get('reason','unknown')))
    values=np.asarray([stats[k] for k in FEATURE_KEYS],float)
    if not np.isfinite(values).all():raise ValueError('Nonfinite input features')
    if getattr(model,'n_features_in_',4)!=4:raise ValueError('Correction model must use four input features')
    parameters=np.asarray(model.predict(values[None,:]),float)
    if parameters.shape!=(1,3) or not np.isfinite(parameters).all() or (parameters<=0).any():raise ValueError('Invalid predicted correction parameters')
    full_estimate=np.zeros(image.shape[:2],bool);full_estimate[y:y+h,x:x+w]=estimate
    material_pixels=None;hair_removed=0
    if mask_policy==LEGACY_POLICY:mask=full_estimate.copy()
    else:
        if segmenter is None:raise ValueError('Semantic segmenter required; no fallback')
        material=material_checked_support(crop,estimate,exclude)
        full_material=np.zeros_like(full_estimate);full_material[y:y+h,x:x+w]=material
        categories=segmenter.categories_bgr(image)
        mask=hair_veto_support(categories,full_material)
        material_pixels=int(full_material.sum());hair_removed=int((full_material&~mask).sum())
    protected_removed=int((mask&protected).sum());mask=mask&~protected
    corrected_rgb=apply_correction(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),mask,parameters[0])
    corrected=cv2.cvtColor(corrected_rgb,cv2.COLOR_RGB2BGR)
    if not np.array_equal(corrected[~mask],image[~mask]):raise RuntimeError('Correction escaped application mask')
    return CorrectionResult(corrected,full_estimate,mask,
        dict(zip(FEATURES,map(float,values))),dict(zip(('gamma','red_gain','blue_gain'),map(float,parameters[0]))),
        dict(mask_policy=mask_policy,estimation_mask_version=ESTIMATION_VERSION,
            transform_version='encoded_rgb_gamma_then_gain_v1',face_box=list(map(int,face_box)),
            estimation_pixels=int(full_estimate.sum()),correction_pixels=int(mask.sum()),
            material_pixels=material_pixels,semantic_hair_pixels_removed=hair_removed,
            protected_pixels_removed=protected_removed,
            paint_handling='Existing input-relative color check on additions; not a universal paint classifier. Explicit protected pixels are always unchanged.',
            status='Development correction option; fixed prototype model, no MST grouping or final thesis performance claim'))
