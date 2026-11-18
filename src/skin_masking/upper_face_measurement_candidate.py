"""One isolated upper-face scope candidate, not a skin/beard classifier."""
import numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.skin_masking.faceocc_coordinates import map_visible_mask
VERSION='upper_face_nasal_base_visible_parser_bg_skin_nose_v1'

def build(image,points,categories,logits,matrix):
    if not isinstance(categories,np.ndarray) or categories.dtype!=np.uint8 or categories.shape!=(256,256) or (categories>18).any():
        raise ValueError('Native19class square256parser categories required')
    if np.asarray(image).shape!=(256,256,3):raise ValueError('Original square256BGR required')
    logits=np.asarray(logits)
    if logits.shape!=(256,256) or not np.isfinite(logits).all():raise ValueError('Finite saved256logits required')
    geometry=build_face_coverage(image,points);cutoff=float(np.asarray(points)[2,1])
    if not 0<=cutoff<256:raise ValueError('Nasal-base cutoff outside image')
    # Coordinates use integer pixel centres consistently with saved landmarks.
    upper=np.indices((256,256))[0]<=cutoff
    visible=map_visible_mask(np.where(logits>0,255,0).astype(np.uint8),(256,256),matrix)>0
    allowed=np.isin(categories,[0,1,10]);excluded=(geometry.exclusion_mask>0)|nostril_guard((256,256),points)
    domain=(geometry.face_outline>0)&upper&~excluded
    selected=domain&visible&allowed
    return selected.astype(np.uint8)*255,dict(version=VERSION,nasal_base_y=cutoff,domain_pixels=int(domain.sum()),
        selected_pixels=int(selected.sum()),recovered_background_pixels=int((selected&(categories==0)).sum()),
        measurement_scope_changed=True,beard_or_skin_accuracy_established=False,calibration_admitted=False)
