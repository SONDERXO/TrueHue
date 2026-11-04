"""Separate correction support; the supplied facial measurement mask is immutable."""
from dataclasses import dataclass
import cv2
import numpy as np

VERSION = 'semantic_face_neck_correction_support_v1'


@dataclass(frozen=True)
class FaceNeckSupport:
    measurement_mask: np.ndarray
    neck_mask: np.ndarray
    correction_mask: np.ndarray
    report: dict


def build_face_neck_support(image, face_mask, categories, *, face_count, protected=None):
    """Associate predicted neck components with the lower selected face.

    Fixed geometry: attachment radius 10% of facial-mask width; neck corridor
    spans its x bounds and from its vertical midpoint to one facial-mask height
    below its bottom. Components must intersect the lower-face attachment band.
    Geometry associates class14, never adds unclassified skin or fills holes.
    These are declared engineering rules, not validated anatomical guarantees.
    """
    if not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3:
        raise ValueError('uint8 BGR frame required')
    shape=image.shape[:2]
    if face_count!=1 or isinstance(face_count,bool):raise ValueError('Exactly one selected face required')
    for mask in (face_mask,categories):
        if not isinstance(mask,np.ndarray) or mask.dtype!=np.uint8 or mask.shape!=shape:
            raise ValueError('Matching uint8 facial mask and categories required')
    if not set(np.unique(face_mask))<={0,255} or not face_mask.any():raise ValueError('Nonempty binary facial mask required')
    if (categories>18).any():raise ValueError('Expected parser classes0–18')
    if protected is None:protected=np.zeros(shape,bool)
    if not isinstance(protected,np.ndarray) or protected.dtype!=bool or protected.shape!=shape:
        raise ValueError('Matching boolean protected pixels required')
    face=face_mask>0;yy,xx=np.nonzero(face)
    left,right,top,bottom=int(xx.min()),int(xx.max())+1,int(yy.min()),int(yy.max())+1
    width,height=right-left,bottom-top
    y,x=np.indices(shape);mid=top+height//2
    radius=max(1,int(np.ceil(width*.1)))
    lower=face&(y>=mid)
    attachment=cv2.dilate(lower.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*radius+1,2*radius+1)))>0
    corridor=(x>=left)&(x<right)&(y>=mid)&(y<min(shape[0],bottom+height))
    predicted=(categories==14)&corridor&~protected&~face
    count,labels=cv2.connectedComponents(predicted.astype(np.uint8),connectivity=8)
    accepted=set(np.unique(labels[predicted&attachment]).tolist())-{0}
    neck=np.isin(labels,sorted(accepted))&predicted
    correction=(face|neck)&~protected
    return FaceNeckSupport(face_mask.copy(),neck.astype(np.uint8)*255,correction.astype(np.uint8)*255,
        dict(version=VERSION,neck_status='candidate_available' if neck.any() else 'unavailable_no_associated_predicted_neck',
             neck_pixels=int(neck.sum()),face_pixels=int(face.sum()),correction_pixels=int(correction.sum()),
             associated_neck_components=len(accepted),rejected_neck_components=count-1-len(accepted),
             measurement_mask_unchanged=True,attachment_radius=radius,
             neck_corridor=[left,mid,right,min(shape[0],bottom+height)],
             requires_quality_review=True,beard_specific_model=False,
             limitation='Predicted neck may include objects or miss skin. Geometry does not prove person identity. No neck color/lighting equivalence or mask accuracy claimed.'))


def apply_shared_parameters(image,support,gamma,red_gain,blue_gain):
    """Direct gamma with identical face/neck parameters; diagnostic, no model."""
    from src.distortion_generation.paper_gamma import transform_rgb
    rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    transformed=np.rint(transform_rgb(rgb.astype(float)/255,gamma,red_gain,blue_gain)*255).astype(np.uint8)
    output=rgb.copy();selected=support.correction_mask>0;output[selected]=transformed[selected]
    return cv2.cvtColor(output,cv2.COLOR_RGB2BGR)
