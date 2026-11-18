"""Own bounded eye/iris geometry context; not calibrated white-point recovery."""
import math
import cv2
import numpy as np
from src.skin_masking.landmark_exclusion import FEATURE_INDICES

VERSION='geometric_iris_excluded_eye_context_v1'
NAMES=('sclera_context_available','sclera_context_log_r_over_g','sclera_context_log_b_over_g')

def extract_sclera_context(image_rgb,categories,landmarks):
    if not isinstance(image_rgb,np.ndarray) or image_rgb.dtype!=np.uint8 or image_rgb.shape!=(256,256,3):raise ValueError('Full256RGB8 required')
    if not isinstance(categories,np.ndarray) or categories.dtype!=np.uint8 or categories.shape!=(256,256) or (categories>18).any():raise ValueError('Matching19class categories required')
    selected=np.zeros((256,256),bool)
    def missing(reason):return dict(valid=False,reason=reason,version=VERSION,features=dict(zip(NAMES,[0.,0.,0.])),mask=np.zeros((256,256),bool),eyes=[],actual_sclera_validated=False)
    points=np.asarray(landmarks)
    if points.ndim!=2 or points.shape[1]<2:raise ValueError('Nx2 full-frame landmarks required')
    if points.shape[0]<478:return missing('refined_iris_landmarks_unavailable')
    points=points[:,:2]
    if not np.isfinite(points).all():raise ValueError('Finite landmarks required')
    eyes=[]
    for name,center,ring,category in [('right_eye',468,[469,470,471,472],5),('left_eye',473,[474,475,476,477],4)]:
        contour=points[FEATURE_INDICES[name]];origin=points[center];edge=points[ring]
        if np.any(contour<0) or np.any(contour>255) or np.any(edge<0) or np.any(edge>255):return missing('eye_geometry_outside_frame')
        if abs(cv2.contourArea(contour.astype(np.float32)))<1 or cv2.pointPolygonTest(contour.astype(np.float32),tuple(map(float,origin)),False)<0:
            return missing('eye_or_iris_geometry_invalid')
        radius=float(np.max(np.linalg.norm(edge-origin,axis=1)))
        if not math.isfinite(radius) or radius<=0:return missing('iris_radius_unavailable')
        aperture=np.zeros((256,256),np.uint8);cv2.fillPoly(aperture,[np.rint(contour).astype(np.int32)],255)
        aperture=cv2.erode(aperture,np.ones((3,3),np.uint8))>0
        yy,xx=np.indices((256,256));iris=(xx-origin[0])**2+(yy-origin[1])**2<=(math.ceil(radius)+1)**2
        mask=aperture&~iris&(categories==category)
        if not mask.any():return missing('no_usable_pixels_in_both_eyes')
        eyes.append(dict(eye=name,pixels=int(mask.sum()),mean_RGB=image_rgb[mask].mean(axis=0).tolist()))
        selected|=mask
    means=image_rgb[selected].mean(axis=0)
    return dict(valid=True,reason='geometric_context_available_not_anatomical_validation',version=VERSION,
        features=dict(zip(NAMES,[1.,float(np.log((means[0]+1)/(means[1]+1))),float(np.log((means[2]+1)/(means[1]+1)))])),
        mask=selected,eyes=eyes,actual_sclera_validated=False)
