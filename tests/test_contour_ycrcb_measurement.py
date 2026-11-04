from types import SimpleNamespace
import numpy as np
from src.ita_estimation import contour_ycrcb_measurement as candidate
from src.skin_masking.face_outline_experiment import FACE_OVAL


def test_containment_removes_background_component_and_preserves_exclusions(monkeypatch):
    colors=np.zeros((30,30),np.uint8);colors[:8,:8]=255;colors[15:23,15:23]=255
    excluded=np.zeros_like(colors);excluded[18,18]=255
    monkeypatch.setattr(candidate,'base_build_mask',lambda *args:SimpleNamespace(mask=colors.copy(),candidate_mask=colors.copy(),exclusion_mask=excluded.copy(),landmarks_available=True,status='old'))
    points=np.full((478,2),18.,float)
    # Fixed rectangular contour for a synthetic input-only test.
    corners=np.array([[13,13],[25,13],[25,25],[13,25]])
    for i,index in enumerate(FACE_OVAL):points[index]=corners[min(3,i*4//len(FACE_OVAL))]
    result=candidate.build_mask(np.zeros((30,30,3),np.uint8),points)
    assert np.count_nonzero(result.mask)==63 and result.mask[18,18]==0 and result.mask[0,0]==0


def test_missing_landmarks_stay_failed_without_rectangular_fallback():
    result=candidate.measure(np.full((256,256,3),(100,140,180),np.uint8),lambda im:[(0,0,256,256)],lambda *args:None)
    assert result.report['status']=='failed' and result.report['features'] is None
    assert result.report['mask_version']==candidate.VERSION and not result.mask.any()


def test_no_face_never_invokes_landmarks():
    def invalid(*args):raise AssertionError('Should not obtain geometry without face')
    result=candidate.measure(np.zeros((256,256,3),np.uint8),lambda im:[],invalid)
    assert result.report['stage']=='face_detection' and result.report['features'] is None
