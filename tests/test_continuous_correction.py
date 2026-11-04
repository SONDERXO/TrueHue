import numpy as np
from src.skin_masking.continuous_correction import fill_correction_holes, continuous_support
from src.skin_masking.face_neck_support import FaceNeckSupport


def test_enclosed_holes_filled_but_exterior_notches_stay_outside():
    mask = np.zeros((20, 20), np.uint8)
    mask[2:18, 2:18] = 255
    mask[5:7, 5:7] = 0
    mask[2:6, 10] = 0
    before = mask.copy()
    fixed, report = fill_correction_holes(mask)
    assert fixed[5:7, 5:7].all() and not fixed[2:6, 10].any()
    assert report['filled_pixels'] == 4 and np.array_equal(mask, before)


def test_edge_touching_support_and_explicit_protection():
    mask = np.full((12, 12), 255, np.uint8)
    mask[4:8, 4:8] = 0
    protected = np.zeros(mask.shape, bool)
    protected[5, 5] = True
    fixed, _ = fill_correction_holes(mask, protected=protected)
    assert not fixed[5, 5] and np.count_nonzero(fixed == 0) == 1


def test_measurement_and_neck_unchanged_and_not_aliased():
    mask = np.full((10, 10), 255, np.uint8)
    mask[5, 5] = 0
    support = FaceNeckSupport(mask.copy(), np.zeros_like(mask), mask.copy(), {})
    fixed = continuous_support(support)
    assert np.array_equal(fixed.measurement_mask, support.measurement_mask)
    assert np.array_equal(fixed.neck_mask, support.neck_mask)
    assert not np.shares_memory(fixed.measurement_mask, support.measurement_mask)
    assert fixed.correction_mask[5, 5] and not support.correction_mask[5, 5]
