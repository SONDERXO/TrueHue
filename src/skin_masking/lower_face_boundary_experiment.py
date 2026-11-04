"""Experimental correction-only jaw/side fence; never changes ITA estimation."""
import numpy as np
from src.skin_masking.face_outline_experiment import restrict_to_face_outline


def lower_face_boundary(support, landmarks, minimum_retained_fraction=.75):
    """Clip below nose-bridge landmark168 to the oval; leave upper rows intact.

    Reject severe support loss explicitly; do not silently fall back. The75%
    guard is a fixed development safeguard, not validated geometry confidence.
    Anatomical exclusions/material/hair filtering must already be applied.
    """
    mask=np.asarray(support);points=np.asarray(landmarks)
    if mask.dtype!=bool or mask.ndim!=2 or not mask.size or not mask.any():
        raise ValueError('Expected nonempty boolean support with selected pixels')
    if points.ndim!=2 or points.shape[0]<=454 or points.shape[1]<2 or not np.isfinite(points[:,:2]).all():
        raise ValueError('Invalid crop landmarks')
    if not 0<=minimum_retained_fraction<=1:raise ValueError('Invalid retention guard')
    split=int(round(float(points[168,1])))
    if not 0<split<mask.shape[0]:raise ValueError('Nose-bridge split outside crop interior')
    _,oval=restrict_to_face_outline(mask.astype(np.uint8)*255,points)
    allowed=oval>0;allowed[:split]=True
    candidate=mask&allowed
    retained=float(candidate.sum()/mask.sum())
    if retained<minimum_retained_fraction:
        raise ValueError(f'Unsafe boundary retention {retained:.4f} < {minimum_retained_fraction}')
    return candidate,dict(split_row=split,retained_fraction=retained,removed_pixels=int((mask&~candidate).sum()))
