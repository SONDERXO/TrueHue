import numpy as np
import pytest
from types import SimpleNamespace
from src.ita_estimation import semantic_measurement as m


def test_fullframe_pixels_outside_detector_box_are_measured(monkeypatch):
    image = np.full((256, 256, 3), (80, 120, 160), np.uint8)
    mask = np.zeros((256, 256), np.uint8)
    mask[10:60, 10:60] = 255  # Completely outside the detector rectangle.
    monkeypatch.setattr(m, 'build_semantic_face_coverage', lambda *a: SimpleNamespace(mask=mask, report={}))
    parser = SimpleNamespace(categories_bgr=lambda image: np.ones((256, 256), np.uint8))
    r = m.measure(image, lambda _: [(100, 100, 40, 40)], lambda *a: np.zeros((468, 2)), parser)
    assert r.report['status'] == 'success'
    assert r.report['skin_pixels'] == 2500
    assert r.report['mst'] is None and not r.report['training_admitted']
    assert len(r.report['features']) == 10


@pytest.mark.parametrize('boxes,points', [([], None), ([(1, 1, 20, 20)], None), ([(1, 1, 20, 20)]*2, None)])
def test_failed_detection_or_landmarks_never_uses_old_measurement(boxes, points):
    parser = SimpleNamespace(categories_bgr=lambda _: pytest.fail('Parser must not run'))
    r = m.measure(np.ones((256, 256, 3), np.uint8), lambda _: boxes, lambda *a: points, parser)
    assert r.report['status'] == 'failed'
    assert r.report['features'] is None and r.report['mst'] is None


def test_insufficient_mask_is_retained_as_failure_without_features(monkeypatch):
    mask = np.zeros((256, 256), np.uint8); mask[0, 0] = 255
    monkeypatch.setattr(m, 'build_semantic_face_coverage', lambda *a: SimpleNamespace(mask=mask, report={}))
    parser = SimpleNamespace(categories_bgr=lambda _: np.ones((256, 256), np.uint8))
    r = m.measure(np.ones((256, 256, 3), np.uint8), lambda _: [(1, 1, 20, 20)], lambda *a: np.zeros((468, 2)), parser)
    assert r.report['status'] == 'failed' and r.report['features'] is None
    assert r.report['skin_pixels'] == 1 and r.mask is not None
