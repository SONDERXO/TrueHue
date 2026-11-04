import numpy as np
import pytest
from src.skin_masking.face_outline_experiment import FACE_OVAL, restrict_to_face_outline


def oval_points():
    points = np.zeros((478, 2))
    angles = np.linspace(0, 2*np.pi, len(FACE_OVAL), endpoint=False)
    points[list(FACE_OVAL)] = np.column_stack((20 + 12*np.cos(angles), 20 + 15*np.sin(angles)))
    return points


def test_restriction_removes_outside_pixels_preserves_holes_and_inputs():
    mask = np.full((40, 40), 255, np.uint8)
    mask[19:22, 19:22] = 0
    original = mask.copy()
    result, oval = restrict_to_face_outline(mask, oval_points())
    assert np.array_equal(mask, original)
    assert result[0, 0] == 0 and oval[20, 20] == 255
    assert not result[19:22, 19:22].any()
    assert np.all(result <= mask)
    assert 0 < np.count_nonzero(result) < np.count_nonzero(mask)


def test_empty_baseline_stays_empty():
    result, _ = restrict_to_face_outline(np.zeros((40, 40), np.uint8), oval_points())
    assert not result.any()


def test_invalid_or_degenerate_geometry_rejected():
    mask = np.zeros((40, 40), np.uint8)
    for points in (np.zeros((10, 2)), np.zeros((478, 2)), np.full((478, 2), np.nan)):
        with pytest.raises(ValueError):
            restrict_to_face_outline(mask, points)
