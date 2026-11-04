"""Isolated parser support candidate, not a calibrated measurement mask."""
import numpy as np
from src.skin_masking.face_parsing_experiment import facial_skin

VERSION = 'focused_semantic_face_support_v1'


def semantic_supports(categories, baseline, face_boxes):
    """Return removal-only and replacement arms inside the single selected box.

    No landmark or old-mask fallback. The parser's skin/nose classes are
    predicted semantics, not validated pixel ground truth.
    """
    dense = facial_skin(categories)
    if baseline.dtype != np.uint8 or baseline.shape != dense.shape or not set(np.unique(baseline)) <= {0,255}:
        raise ValueError('Matching binary uint8 baseline required')
    if len(face_boxes) != 1:
        raise ValueError('Exactly one fixed-detector face required')
    box = face_boxes[0]
    if len(box)!=4 or any(isinstance(v,(bool,np.bool_)) or not isinstance(v,(int,np.integer)) for v in box):
        raise ValueError('Integer detector bounds required')
    x,y,w,h=map(int,box)
    if min(x,y)<0 or min(w,h)<=0 or x+w>dense.shape[1] or y+h>dense.shape[0]:
        raise ValueError('Detector bounds outside image')
    bounded=np.zeros_like(dense)
    bounded[y:y+h,x:x+w]=dense[y:y+h,x:x+w]
    candidate=bounded.astype(np.uint8)*255
    removal=((baseline>0)&bounded).astype(np.uint8)*255
    return removal,candidate
