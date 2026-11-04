import numpy as np
import pytest
from src.model_training.facial_endpoint_features import facial_endpoint_features


def test_exact_channel_counts_and_bgr_order():
    image = np.full((40, 40, 3), 100, np.uint8)
    image[:10, :, 2] = 0; image[10:30, :, 0] = 255
    result = facial_endpoint_features(image, np.ones((40, 40), bool))['features']
    assert result == dict(input_red_zero_fraction=.25, input_red_full_fraction=0.,
        input_green_zero_fraction=0., input_green_full_fraction=0.,
        input_blue_zero_fraction=0., input_blue_full_fraction=.5)


def test_outside_mask_invariance_and_no_mutation():
    image = np.full((50, 50, 3), 100, np.uint8)
    mask = np.zeros((50, 50), bool); mask[5:45, 5:45] = True
    changed = image.copy(); changed[~mask] = 255
    before = changed.copy()
    assert facial_endpoint_features(image, mask) == facial_endpoint_features(changed, mask)
    np.testing.assert_array_equal(changed, before)


def test_near_endpoints_are_not_counted():
    image = np.full((40, 40, 3), [1, 254, 100], np.uint8)
    assert set(facial_endpoint_features(image, np.ones((40, 40), bool))['features'].values()) == {0.}


def test_support_boundary_and_types():
    image = np.zeros((40, 40, 3), np.uint8); mask = np.zeros((40, 40), bool)
    mask.flat[:999] = True
    assert not facial_endpoint_features(image, mask)['valid']
    mask.flat[999] = True
    assert facial_endpoint_features(image, mask)['valid']
    with pytest.raises(ValueError): facial_endpoint_features(image, mask.astype(np.uint8))
    with pytest.raises(ValueError): facial_endpoint_features(image.astype(float), mask)
