import numpy as np
import pytest
from src.evaluation.mask_support_quality import support_retention


def test_large_lower_face_can_pass_pixel_minimum_but_fail_regional_screen():
    reference=np.ones((100,100),bool)
    partial=reference.copy();partial[:50]=False
    assert partial.sum()>1000
    result=support_retention(reference,partial,partial)
    assert not result['screen_pass']
    assert 'upper_left:estimation_loss' in result['flags']
    assert 'lower_left:estimation_loss' not in result['flags']


def test_correction_completion_does_not_hide_bad_estimation():
    reference=np.ones((100,100),bool)
    estimation=reference.copy();estimation[:50]=False
    result=support_retention(reference,estimation,reference)
    assert not result['screen_pass']
    assert all('estimation_loss' in reason for reason in result['flags'])


def test_additions_do_not_count_as_recovered_reference_pixels():
    reference=np.zeros((100,100),bool);reference[20:80,20:80]=True
    correction=~reference
    result=support_retention(reference,reference,correction)
    assert not result['screen_pass']
    assert result['regions']['whole']['correction_retention']==0
    assert result['correction_outside_reference_pixels']==6400


def test_small_quadrant_not_scored_and_inputs_unchanged():
    reference=np.zeros((20,20),bool);reference[:2,:2]=True
    before=reference.copy()
    result=support_retention(reference,reference,reference)
    assert result['screen_pass']
    assert not result['regions']['upper_left']['evaluated']
    np.testing.assert_array_equal(reference,before)


@pytest.mark.parametrize('mask',[np.ones((2,2),np.uint8),np.ones((2,3),bool)])
def test_bad_mask_contract_rejected(mask):
    with pytest.raises(ValueError):support_retention(np.ones((2,2),bool),mask,mask)


def test_empty_reference_rejected():
    empty=np.zeros((10,10),bool)
    with pytest.raises(ValueError):support_retention(empty,empty,empty)
