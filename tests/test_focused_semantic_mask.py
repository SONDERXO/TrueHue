import numpy as np
import pytest
from src.skin_masking.focused_semantic_mask import semantic_supports


def test_excludes_foreign_classes_and_outside_face_without_old_mask_fallback():
    categories=np.arange(19,dtype=np.uint8)[None,:].repeat(3,axis=0)
    baseline=np.full(categories.shape,255,np.uint8)
    removal,candidate=semantic_supports(categories,baseline,[(0,1,19,1)])
    expected=np.zeros_like(baseline);expected[1,[1,10]]=255
    np.testing.assert_array_equal(candidate,expected)
    np.testing.assert_array_equal(removal,expected)


def test_candidate_can_recover_pixels_but_removal_arm_cannot_add():
    categories=np.ones((5,5),np.uint8);baseline=np.zeros_like(categories)
    baseline[2,2]=255
    removal,candidate=semantic_supports(categories,baseline,[(1,1,3,3)])
    assert np.count_nonzero(candidate)==9 and np.count_nonzero(removal)==1
    assert not np.shares_memory(candidate,baseline)


@pytest.mark.parametrize('boxes',[[],[(0,0,2,2),(1,1,2,2)],[(0,0,8,8)],[(True,0,2,2)]])
def test_invalid_face_selection_is_not_silently_rescued(boxes):
    with pytest.raises(ValueError):semantic_supports(np.ones((5,5),np.uint8),np.zeros((5,5),np.uint8),boxes)


def test_rejects_nonbinary_baseline():
    with pytest.raises(ValueError):semantic_supports(np.ones((5,5),np.uint8),np.ones((5,5),np.uint8),[(0,0,5,5)])
