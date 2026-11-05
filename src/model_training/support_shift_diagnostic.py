"""Consistency against saved support; never calls imperfect masks ground truth."""
import numpy as np
from src.model_training.blended_recovery_targets import fit_target


def compare_masks(source,current):
    for mask in (source,current):
        if not isinstance(mask,np.ndarray) or mask.dtype!=np.uint8 or mask.ndim!=2 or not set(np.unique(mask))<={0,255}:
            raise ValueError('Binary uint8 masks required')
    if source.shape!=current.shape:raise ValueError('Matching mask shapes required')
    a=source>0;b=current>0;union=int((a|b).sum());overlap=int((a&b).sum())
    return dict(source_pixels=int(a.sum()),current_pixels=int(b.sum()),intersection_pixels=overlap,
        lost_pixels=int((a&~b).sum()),added_pixels=int((b&~a).sum()),
        consistency_iou=overlap/union if union else None,ground_truth_accuracy=False)


def fit_current_support(image,reference,source_alpha,current_alpha):
    if source_alpha.shape!=image.shape[:2] or current_alpha.shape!=source_alpha.shape:
        raise ValueError('Matching alpha shapes required')
    for alpha in (source_alpha,current_alpha):
        if not np.issubdtype(alpha.dtype,np.floating) or not np.isfinite(alpha).all() or (alpha<0).any() or (alpha>1).any():
            raise ValueError('Finite floating alpha within[0,1] required')
    score=(source_alpha>0)&(current_alpha>0)
    report=dict(original_scoring_pixels=int((source_alpha>0).sum()),
        fit_intersection_pixels=int(score.sum()),
        missed_original_scoring_pixels=int(((source_alpha>0)&(current_alpha==0)).sum()),training_admitted=False)
    if not score.any():return dict(report,status='unavailable_empty_support_intersection',parameters=None)
    return dict(fit_target(image,reference,current_alpha,score),**report)


def outside_changes(output,image,source_alpha,source_protected):
    outside=source_alpha==0;changed=np.any(output!=image,axis=2)
    return dict(changed_pixels_outside_source=int((changed&outside).sum()),
        changed_channels_outside_source=int(np.count_nonzero(output[outside]!=image[outside])),
        outside_source_MAE=float(np.abs(output[outside].astype(float)-image[outside]).mean()) if outside.any() else None,
        changed_source_protected_pixels=int((changed&source_protected).sum()),
        source_protection_is_ground_truth=False)
