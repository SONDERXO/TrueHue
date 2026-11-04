"""Reference scoring must preserve unknown pixels and floating geometry."""
import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    'boundary_refs', Path(__file__).parents[1]/'scripts/90_score_face_boundary_references.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_fractional_polygon_is_not_rounded_and_includes_boundary():
    points = [[.2, .2], [2., .2], [2., 2.], [.2, 2.]]
    mask = module.polygon_pixels(points, 4, 4)
    assert np.array_equal(np.argwhere(mask), [[1, 1], [1, 2], [2, 1], [2, 2]])


def test_label_priority_is_independent_of_polygon_order():
    square = [[1, 1], [3, 1], [3, 3], [1, 3]]
    polygons = [dict(label=label, points=square) for label in ['exclude', 'skin', 'uncertain']]
    labels = module.rasterize(polygons, 5, 5)
    assert (labels[1:4, 1:4] == 3).all()
    assert labels[0, 0] == 0
    assert (module.rasterize(polygons[1:], 5, 5)[1:4, 1:4] == 2).all()


def test_unlabeled_and_uncertain_selection_does_not_count_as_error():
    labels = np.array([[0, 1], [2, 3]], np.uint8)
    result = module.score(np.ones((2, 2), bool), labels)
    assert result['labeled_skin_pixels'] == result['selected_skin_pixels'] == 1
    assert result['labeled_exclusion_pixels'] == result['selected_exclusion_pixels'] == 1
    assert result['selected_uncertain_pixels'] == result['selected_unlabeled_pixels'] == 1
