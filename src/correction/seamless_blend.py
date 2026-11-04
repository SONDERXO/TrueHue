"""Inward-only boundary blending; measurement and permitted support stay fixed."""
import cv2
import numpy as np
from src.distortion_generation.paper_gamma import transform_rgb

VERSION='whole_face_inward_blend_v1'


def inward_alpha(mask,*,face_width,protected=None):
    if not isinstance(mask,np.ndarray) or mask.dtype!=np.uint8 or mask.ndim!=2 or not set(np.unique(mask))<={0,255}:
        raise ValueError('Binary uint8 correction mask required')
    if isinstance(face_width,bool) or not isinstance(face_width,(int,np.integer)) or face_width<1:
        raise ValueError('Positive integer face width required')
    selected=mask>0
    if protected is not None:
        if protected.dtype!=bool or protected.shape!=mask.shape:raise ValueError('Matching protected pixels required')
        selected=selected&~protected
    width=max(2,int(np.ceil(face_width*.03)))
    # One transform of the UNION avoids artificial face/neck seam boundaries.
    distance=cv2.distanceTransform(selected.astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
    t=np.clip(distance/width,0,1).astype(np.float64)
    alpha=t*t*(3-2*t);alpha[~selected]=0
    return alpha,dict(version=VERSION,edge_width_pixels=width,rule='inward_distance_smoothstep_3percent_face_width',
        feather_pixels=int(((alpha>0)&(alpha<1)).sum()),outside_support_alpha=0,
        limitation='Softens permitted outer edges; does not establish correct geometry or recover missing/clipped colors.')


def apply_blended(image_bgr,correction_mask,parameters,*,face_width,protected=None):
    image=np.asarray(image_bgr)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or image.shape[:2]!=correction_mask.shape:
        raise ValueError('Matching uint8 BGR image and support required')
    alpha,report=inward_alpha(correction_mask,face_width=face_width,protected=protected)
    rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    target=transform_rgb(rgb.astype(float)/255,*parameters)*255
    output=rgb.copy();selected=alpha>0
    values=rgb.astype(float)*(1-alpha[:,:,None])+target*alpha[:,:,None]
    output[selected]=np.rint(values[selected]).astype(np.uint8)
    return cv2.cvtColor(output,cv2.COLOR_RGB2BGR),alpha,report
