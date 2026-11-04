import numpy as np
from tests.test_full_face_support import setup
from src.ita_estimation.face_contained_measurement import measure_saved
from src.skin_masking.anatomical_face_coverage import build_face_coverage


def test_spill_removed_without_adding_pixels_or_mutating_parent():
    image, _, _, points = setup()
    image[:] = [80, 110, 150]
    baseline = np.full(image.shape[:2], 255, np.uint8)
    before = baseline.copy()
    mask, report = measure_saved(image, baseline, points)
    outline = build_face_coverage(image, points).face_outline
    assert np.array_equal(mask, outline)
    assert report['removed_pixels'] > 0 and report['status'] == 'success'
    assert np.array_equal(before, baseline)


def test_insufficient_skin_and_bad_geometry_have_no_stale_features():
    image, _, _, points = setup()
    baseline = np.zeros(image.shape[:2], np.uint8); baseline[45, 50] = 255
    _, report = measure_saved(image, baseline, points)
    assert report['status'] == 'failed' and report['features'] is None
    mask, report = measure_saved(image, baseline, np.zeros((468, 2)))
    assert mask is None and report['features'] is None
