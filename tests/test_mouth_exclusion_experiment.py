import numpy as np
import pytest
from src.skin_masking.mouth_exclusion_experiment import OUTER_LIPS, exclude_complete_mouth


def mouth_points():
    points=np.zeros((478,2))
    angles=np.linspace(0,2*np.pi,len(OUTER_LIPS),endpoint=False)
    points[list(OUTER_LIPS)]=np.column_stack((20+10*np.cos(angles),20+6*np.sin(angles)))
    return points


def test_outer_ring_is_ordered_cycle_in_installed_mediapipe_topology():
    from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarksConnections
    edges={frozenset((e.start,e.end)) for e in FaceLandmarksConnections.FACE_LANDMARKS_LIPS}
    assert len(set(OUTER_LIPS))==20
    assert all(frozenset((a,b)) in edges for a,b in zip(OUTER_LIPS,OUTER_LIPS[1:]+OUTER_LIPS[:1]))
    assert 0 in OUTER_LIPS and 17 in OUTER_LIPS


def test_filled_mouth_removes_upper_and_lower_interior_preserving_other_pixels():
    mask=np.full((40,40),255,np.uint8)
    mask[1,1]=0
    before=mask.copy()
    final,mouth=exclude_complete_mouth(mask,mouth_points())
    assert np.array_equal(mask,before)
    assert mouth[18,20]==mouth[22,20]==255
    assert final[18,20]==final[22,20]==0
    assert final[5,5]==255 and final[1,1]==0
    assert not np.any((final>0)&(mask==0))


def test_empty_baseline_stays_empty_and_invalid_geometry_fails():
    mask=np.zeros((40,40),np.uint8)
    final,_=exclude_complete_mouth(mask,mouth_points())
    assert not final.any()
    for points in (np.zeros((10,2)),np.zeros((478,2)),np.full((478,2),np.nan)):
        with pytest.raises(ValueError):
            exclude_complete_mouth(mask,points)


def test_fresh_sampling_excludes_development_and_failures_and_is_order_stable():
    import importlib
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
    runner=importlib.import_module('19_compare_complete_mouth')
    source={str(i):{'processing_status':'success'} for i in range(20)}
    source['failed']={'processing_status':'excluded'}
    ids,size=runner.select_fresh_ids(source,{'0','1'},10,42)
    again,_=runner.select_fresh_ids(dict(reversed(list(source.items()))),{'0','1'},10,42)
    assert ids==again and len(set(ids))==10 and size==18
    assert not set(ids)&{'0','1','failed'}
