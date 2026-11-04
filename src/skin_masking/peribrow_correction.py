"""Correction-only skin around brows, separate from fixed measurement support."""
import cv2
import numpy as np
from src.skin_masking.correction_facial_features import include_brows_lips
from src.skin_masking.face_neck_support import FaceNeckSupport

VERSION='preferred_support_peribrow_v2'


def include_features_and_peribrow(base,categories,*,protected=None):
    support=include_brows_lips(base,categories,protected=protected)
    face=base.measurement_mask
    yy,xx=np.nonzero(face);y,x=np.indices(face.shape)
    corridor=(x>=xx.min())&(x<=xx.max())&(y>=yy.min())&(y<=yy.max())
    brows=np.isin(categories,[2,3])&corridor
    # Fixed single engineering choice: 2% of face width, at least one pixel.
    radius=max(1,int(np.ceil((int(xx.max())-int(xx.min())+1)*.02)))
    nearby=cv2.dilate(brows.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*radius+1,2*radius+1)))>0
    additions=nearby&corridor&np.isin(categories,[1,10])&(support.correction_mask==0)
    if protected is not None:additions&=~protected
    correction=support.correction_mask.copy();correction[additions]=255
    report=dict(support.report,correction_support_version=VERSION,
        peribrow_added_pixels=int(additions.sum()),peribrow_radius=radius,
        peribrow_rule='near_selected_brows_predicted_skin_or_nose_only',
        measurement_mask_unchanged=True,
        peribrow_limitation='Parser mistakes may still include non-skin. The added band is not a validated anatomical boundary.')
    return FaceNeckSupport(support.measurement_mask.copy(),support.neck_mask.copy(),correction,report)
