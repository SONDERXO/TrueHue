"""Whole face for correction; separately guarded facial skin for measurement."""
import cv2
import numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage,RASTER_SCALE
from src.skin_masking.face_neck_support import build_face_neck_support,FaceNeckSupport

VERSION='whole_face_correction_nostril_measurement_v4'
# Conservative nasal-base guards using the installed MediaPipe nose topology.
# These deliberately exclude nearby nasal skin, not just exact nostril holes.
NASAL_BASE=((98,97,2,94,19,64),(327,326,2,94,19,294))


def nostril_guard(shape,landmarks):
    points=np.asarray(landmarks)
    if points.ndim!=2 or points.shape[0]<468 or points.shape[1]<2 or not np.isfinite(points).all():
        raise ValueError('Finite full-face landmarks required')
    canvas=np.zeros((shape[0]*RASTER_SCALE,shape[1]*RASTER_SCALE),np.uint8)
    for indices in NASAL_BASE:
        contour=points[list(indices),:2]
        if abs(cv2.contourArea(contour.astype(np.float32)))<.1:
            raise ValueError('Nasal-base geometry unavailable')
        polygon=cv2.convexHull(np.rint(contour*RASTER_SCALE).astype(np.int32))
        cv2.fillPoly(canvas,[polygon],255)
    mask=cv2.resize(canvas,(shape[1],shape[0]),interpolation=cv2.INTER_AREA)>0
    return cv2.dilate(mask.astype(np.uint8),np.ones((3,3),np.uint8))>0


def build_full_face_support(image,facial_skin_mask,categories,landmarks,*,face_count,protected=None):
    neck=build_face_neck_support(image,facial_skin_mask,categories,face_count=face_count,protected=protected)
    geometry=build_face_coverage(image,landmarks)
    guard=nostril_guard(facial_skin_mask.shape,landmarks)
    measurement=(facial_skin_mask>0)&np.isin(categories,[1,10])&~(geometry.exclusion_mask>0)&~guard
    # No class/anatomical cut-outs INSIDE the selected facial outline.
    correction=(geometry.face_outline>0)|(facial_skin_mask>0)|(neck.neck_mask>0)
    if protected is not None:correction&=~protected
    return FaceNeckSupport(measurement.astype(np.uint8)*255,neck.neck_mask.copy(),correction.astype(np.uint8)*255,
        dict(neck.report,version=VERSION,correction_policy='everything_inside_face_outline_plus_retained_face_skin_and_associated_neck',
            measurement_policy='semantic_facial_skin_minus_conservative_nasal_base_guard',
            nostril_guard_removed_pixels=int(((facial_skin_mask>0)&guard).sum()),
            whole_face_without_anatomical_holes=True,old_lookup_compatible=False,
            includes_eye_mouth_hair_objects_inside_face=True,
            limitation='Whole-face correction also affects eyes, teeth, glasses and occluders inside the outline. Nasal guard is conservative geometry, not validated nostril segmentation. Parser hair/beard mistakes remain possible in measurement.'))
