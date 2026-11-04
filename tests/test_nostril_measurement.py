import numpy as np
from tests.test_full_face_support import setup
from src.ita_estimation import nostril_measurement as n
from src.ita_estimation.square_measurement import SquareMeasurement


def test_new_measurement_recomputes_features_without_mutating_parent_mask(monkeypatch):
    _,base,_,points=setup();image=np.full((100,100,3),(80,120,160),np.uint8)
    before=base.measurement_mask.copy()
    def parent(im,detector,capture,parser):
        capture(im,None)
        return SquareMeasurement(dict(status='success',features={'stale':123},mask_report={},mst=9),im,before)
    monkeypatch.setattr(n.semantic_measurement,'measure',parent)
    result=n.measure(image,None,lambda *args:points,None)
    assert result.report['status']=='success' and result.report['mst'] is None
    assert 'stale' not in result.report['features'] and result.report['nostril_guard_removed_pixels']>0
    assert np.array_equal(before,base.measurement_mask)
    assert np.count_nonzero(result.mask)<np.count_nonzero(before)


def test_missing_nasal_geometry_cannot_return_stale_features(monkeypatch):
    def parent(im,detector,capture,parser):
        capture(im,None)
        return SquareMeasurement(dict(status='success',features={'stale':123},mask_report={}),im,np.full((100,100),255,np.uint8))
    monkeypatch.setattr(n.semantic_measurement,'measure',parent)
    result=n.measure(np.ones((100,100,3),np.uint8),None,lambda *args:np.zeros((468,2)),None)
    assert result.report['status']=='failed' and result.report['features'] is None
    assert result.report['mst'] is None and not result.report['old_lookup_compatible']
