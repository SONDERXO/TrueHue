import numpy as np
import pytest
from src.skin_masking.guarded_correction_support import guarded_correction_support
from src.skin_masking.correction_support_experiment import complete_correction_support


def test_guards_limit_only_new_pixels_and_preserve_interior_recovery():
    mask = np.zeros((100,100),bool)
    mask[10:90,10:15] = True; mask[10:90,85:90] = True
    excluded = np.zeros_like(mask); excluded[45:55,45:55] = True
    original = mask.copy()
    guard = guarded_correction_support(mask,excluded)
    hull = complete_correction_support(mask,excluded)
    assert np.all(guard[mask]) and not guard[~hull].any()
    assert guard[30,50] and not guard[11,50] and not guard[44,50]
    assert not guard[excluded].any() and (guard & ~mask).sum() < (hull & ~mask).sum()
    np.testing.assert_array_equal(mask,original)


def test_existing_baseline_spillover_is_not_silently_removed():
    mask = np.zeros((30,30),bool); mask[2:28,2:28] = True
    assert np.array_equal(guarded_correction_support(mask,np.zeros_like(mask)),mask)


def test_empty_support_remains_an_explicit_failure():
    with pytest.raises(ValueError): guarded_correction_support(np.zeros((10,10),bool),np.zeros((10,10),bool))
