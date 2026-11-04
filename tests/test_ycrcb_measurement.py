import numpy as np
from src.ita_estimation.ycrcb_measurement import build_mask,measure,VERSION


def test_missing_landmarks_never_returns_unexcluded_color_support():
    image=np.full((80,80,3),(100,140,180),np.uint8)
    result=build_mask(image,None)
    assert not result.landmarks_available and not result.mask.any()


def test_failed_detection_never_calls_landmarks_or_supplies_features():
    def unavailable(*args):raise AssertionError('Landmarks should not run')
    result=measure(np.zeros((100,100,3),np.uint8),lambda im:[],unavailable)
    assert result.report['mask_version']==VERSION
    assert result.report['features'] is None and result.report['stage']=='face_detection'


def test_missing_input_geometry_does_not_reuse_a_reference_mask():
    result=measure(np.full((256,256,3),(100,140,180),np.uint8),lambda im:[(0,0,256,256)],lambda *args:None)
    assert result.report['status']=='failed' and result.report['features'] is None
    assert not result.mask.any()
