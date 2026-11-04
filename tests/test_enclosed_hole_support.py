import numpy as np
import pytest
from src.skin_masking.enclosed_hole_support import complete_enclosed_holes


def fixture():
    mask = np.zeros((11, 11), bool)
    mask[2:9, 2:9] = True
    return mask, np.zeros_like(mask), np.ones_like(mask)


def test_enclosed_hole_filled_without_expanding_outer_boundary():
    mask, excluded, outline = fixture(); mask[5, 5] = False
    expected = mask.copy(); expected[5, 5] = True
    result = complete_enclosed_holes(mask, excluded, outline)
    np.testing.assert_array_equal(result, expected)
    assert not mask[5, 5]  # Input is not mutated.


def test_diagonal_background_connection_prevents_filling():
    mask, excluded, outline = fixture()
    mask[2, 2] = mask[3, 3] = mask[4, 4] = False
    np.testing.assert_array_equal(complete_enclosed_holes(mask, excluded, outline), mask)


def test_entire_anatomical_component_stays_open():
    mask, excluded, outline = fixture(); mask[4:7, 4:7] = False
    excluded[5, 5] = True
    np.testing.assert_array_equal(complete_enclosed_holes(mask, excluded, outline), mask)


def test_hole_crossing_outline_not_partially_filled():
    mask, excluded, outline = fixture(); mask[4:7, 4:7] = False
    outline[5, 5] = False
    np.testing.assert_array_equal(complete_enclosed_holes(mask, excluded, outline), mask)


def test_separate_holes_treated_independently():
    mask, excluded, outline = fixture(); mask[3, 3] = mask[7, 7] = False
    excluded[3, 3] = True
    result = complete_enclosed_holes(mask, excluded, outline)
    assert not result[3, 3] and result[7, 7]


def test_invalid_support_and_contract_fail_explicitly():
    mask, excluded, outline = fixture()
    for bad in (mask.astype(np.uint8), mask[:, :2]):
        with pytest.raises(ValueError): complete_enclosed_holes(bad, excluded, outline)
    with pytest.raises(ValueError): complete_enclosed_holes(np.zeros_like(mask), excluded, outline)
    excluded[4, 4] = True
    with pytest.raises(ValueError): complete_enclosed_holes(mask, excluded, outline)
