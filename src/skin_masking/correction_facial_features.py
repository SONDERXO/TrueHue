"""Optional correction-only brows/lips experiment; immutable measurement support."""
import numpy as np
from src.skin_masking.face_neck_support import FaceNeckSupport

VERSION='correction_only_brows_lips_v1'


def include_brows_lips(base,categories,*,protected=None):
    face=base.measurement_mask
    if not isinstance(categories,np.ndarray) or categories.dtype!=np.uint8 or categories.shape!=face.shape or (categories>18).any():
        raise ValueError('Matching parser classes0–18 required')
    if protected is None:protected=np.zeros(face.shape,bool)
    if not isinstance(protected,np.ndarray) or protected.dtype!=bool or protected.shape!=face.shape:
        raise ValueError('Matching protected pixels required')
    yy,xx=np.nonzero(face)
    if not len(xx):raise ValueError('Selected facial measurement support required')
    y,x=np.indices(face.shape)
    corridor=(x>=xx.min())&(x<=xx.max())&(y>=yy.min())&(y<=yy.max())
    brows=np.isin(categories,[2,3])&corridor&~protected
    lips=np.isin(categories,[12,13])&corridor&~protected
    added=(brows|lips)&(base.correction_mask==0)
    correction=((base.correction_mask>0)|added)&~protected
    report=dict(base.report,facial_features_version=VERSION,
        correction_only_brow_pixels=int((brows&added).sum()),correction_only_lip_pixels=int((lips&added).sum()),
        measurement_mask_unchanged=True,feature_mask_approved=False,
        feature_limitation='Only predicted brows and lip classes inside selected face bounds; parser errors remain. Mouth interior/eyes are not added. Same settings do not guarantee appropriate lip or hair color.')
    return FaceNeckSupport(face.copy(),base.neck_mask.copy(),correction.astype(np.uint8)*255,report)
