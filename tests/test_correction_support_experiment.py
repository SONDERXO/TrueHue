import numpy as np
import pytest
from src.skin_masking.correction_support_experiment import complete_correction_support


def test_completion_bridges_input_gaps_but_preserves_feature_exclusions_and_bounds():
    mask = np.zeros((20,20),bool)
    mask[3:17,3:6] = True; mask[3:17,14:17] = True
    excluded = np.zeros_like(mask); excluded[8:11,8:11] = True
    original = mask.copy()
    out = complete_correction_support(mask,excluded)
    assert out[5,10] and not out[excluded].any()
    assert not out[:3].any() and not out[:,17:].any()
    np.testing.assert_array_equal(mask,original)


@pytest.mark.parametrize('kind',['empty','line','wrong_type'])
def test_invalid_support_fails_without_silent_box_fill(kind):
    mask = np.zeros((10,10),bool)
    if kind == 'line': mask[5,:] = True
    if kind == 'wrong_type': mask = mask.astype(np.uint8)
    with pytest.raises(ValueError): complete_correction_support(mask,np.zeros((10,10),bool))
