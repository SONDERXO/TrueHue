import cv2
import numpy as np
import pytest
from src.model_training.facial_chromatic_features import facial_chromatic_features, ADDITIONS


def test_known_chromatic_distribution_and_channel_units():
    image = np.zeros((40, 40, 3), np.uint8)
    image[:20] = [70, 110, 160]; image[20:] = [110, 130, 170]
    result = facial_chromatic_features(image, np.ones((40, 40), bool))
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(float) - 128
    expected = []
    for channel in (1, 2):
        values = sorted(lab[:, :, channel].ravel())
        # Equal halves: quartiles are endpoints, median is their midpoint.
        expected.extend([(values[0] + values[-1]) / 2, values[-1] - values[0]])
    assert result['features'] == dict(zip(ADDITIONS, expected))


def test_pixels_outside_mask_cannot_change_features():
    image = np.full((50, 50, 3), 100, np.uint8)
    mask = np.zeros((50, 50), bool); mask[5:45, 5:45] = True
    changed = image.copy(); changed[~mask] = [255, 0, 255]
    assert facial_chromatic_features(image, mask) == facial_chromatic_features(changed, mask)


def test_constant_color_zero_spread_and_no_mutation():
    image = np.full((40, 40, 3), [80, 110, 150], np.uint8)
    before = image.copy(); mask = np.ones((40, 40), bool)
    result = facial_chromatic_features(image, mask)
    assert result['features']['input_a_iqr'] == result['features']['input_b_iqr'] == 0
    np.testing.assert_array_equal(image, before)
    assert mask.all()


def test_support_and_dtype_contract():
    image = np.zeros((40, 40, 3), np.uint8); mask = np.zeros((40, 40), bool)
    assert not facial_chromatic_features(image, mask)['valid']
    mask.flat[:999] = True
    assert not facial_chromatic_features(image, mask)['valid']
    mask.flat[999] = True
    assert facial_chromatic_features(image, mask)['valid']
    with pytest.raises(ValueError): facial_chromatic_features(image, mask.astype(np.uint8))
    with pytest.raises(ValueError): facial_chromatic_features(image.astype(float), mask)
