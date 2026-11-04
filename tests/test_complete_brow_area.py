import cv2
import numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.face_outline_experiment import FACE_OVAL
from src.skin_masking.landmark_exclusion import FEATURE_INDICES
from src.skin_masking.mouth_exclusion import OUTER_LIPS
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.skin_masking.complete_brow_area import include_complete_brow_area


def example():
    points=np.full((468,2),50.,float)
    def ellipse(ids,cx,cy,rx,ry):
        angles=np.linspace(0,2*np.pi,len(ids),endpoint=False)
        points[list(ids)]=np.column_stack((cx+rx*np.cos(angles),cy+ry*np.sin(angles)))
    ellipse(FACE_OVAL,50,50,43,46)
    ellipse(OUTER_LIPS,50,70,12,5)
    for name,cx,cy,rx,ry in [('left_eyebrow',35,30,12,6),('right_eyebrow',65,30,12,6),
                            ('left_eye',35,45,8,4),('right_eye',65,45,8,4)]:ellipse(FEATURE_INDICES[name],cx,cy,rx,ry)
    image=np.full((100,100,3),120,np.uint8)
    face=build_face_coverage(image,points).mask
    cats=np.ones((100,100),np.uint8);cats[28:30,30:40]=2;cats[28:30,60:70]=3
    return image,FaceNeckSupport(face,np.zeros_like(face),face.copy(),{}),cats,points


def test_full_brow_exclusion_skin_included_even_far_from_predicted_hairs():
    image,base,cats,points=example()
    r=include_complete_brow_area(image,base,cats,points)
    assert not base.measurement_mask[30,25] and r.correction_mask[30,25]
    assert np.array_equal(r.measurement_mask,base.measurement_mask)
    assert r.report['eligible_brow_skin_fully_included']


def test_eye_and_protected_pixels_remain_excluded():
    image,base,cats,points=example();veto=np.zeros((100,100),bool);veto[30,25]=True
    r=include_complete_brow_area(image,base,cats,points,protected=veto)
    assert not r.correction_mask[45,35] and not r.correction_mask[30,25]
