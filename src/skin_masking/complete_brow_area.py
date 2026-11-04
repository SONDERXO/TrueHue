"""Restore eligible skin across the full anatomical brow exclusion, correction only."""
import cv2
import numpy as np
from src.skin_masking.correction_facial_features import include_brows_lips
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.skin_masking.anatomical_face_coverage import build_face_coverage,RASTER_SCALE
from src.skin_masking.landmark_exclusion import FEATURE_INDICES

VERSION='preferred_support_complete_brow_area_v3'


def include_complete_brow_area(image,base,categories,landmarks,*,protected=None):
    support=include_brows_lips(base,categories,protected=protected)
    geometry=build_face_coverage(image,landmarks)
    points=np.asarray(landmarks)[:,:2];shape=base.measurement_mask.shape
    def polygon(name):
        vertices=points[FEATURE_INDICES[name]]
        if abs(cv2.contourArea(vertices.astype(np.float32)))<1:raise ValueError('Degenerate brow/eye geometry')
        canvas=np.zeros((shape[0]*RASTER_SCALE,shape[1]*RASTER_SCALE),np.uint8)
        contour=cv2.convexHull(np.rint(vertices*RASTER_SCALE).astype(np.int32))
        cv2.fillPoly(canvas,[contour],255)
        return cv2.resize(canvas,(shape[1],shape[0]),interpolation=cv2.INTER_AREA)>0
    brows=polygon('left_eyebrow')|polygon('right_eyebrow')
    eyes=polygon('left_eye')|polygon('right_eye')
    eligible=brows&~eyes&(geometry.face_outline>0)&np.isin(categories,[1,10])
    if protected is not None:eligible&=~protected
    additions=eligible&(support.correction_mask==0)
    correction=support.correction_mask.copy();correction[eligible]=255
    assert correction[eligible].all()
    return FaceNeckSupport(support.measurement_mask.copy(),support.neck_mask.copy(),correction,
        dict(support.report,correction_support_version=VERSION,
            full_brow_area_skin_added_pixels=int(additions.sum()),
            eligible_brow_skin_pixels=int(eligible.sum()),eligible_brow_skin_fully_included=True,
            measurement_mask_unchanged=True,eye_landmark_veto_for_added_skin=True,
            limitation='Covers eligible predicted skin across the full brow-exclusion polygons, not guaranteed actual-skin segmentation. Measurement exclusions remain unchanged.'))
