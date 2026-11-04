import numpy as np
import pytest
from src.skin_masking.selfie_material_segmenter import face_skin_support,hair_veto_support,normalize_category_map


def test_native_singleton_category_channel_is_normalized_without_resizing_or_aliasing():
    category=np.full((7,9,1),3,np.uint8)
    result=normalize_category_map(category,(7,9,3))
    assert result.shape==(7,9) and result.dtype==np.uint8
    result[0,0]=1
    assert category[0,0,0]==3
    with pytest.raises(ValueError): normalize_category_map(category,(9,7,3))
    with pytest.raises(ValueError): normalize_category_map(np.zeros((7,9,2),np.uint8),(7,9,3))


def test_face_skin_selects_only_correct_class_inside_face_and_preserves_exclusions():
    categories=np.full((10,10),3,np.uint8);categories[3,3]=1;categories[4,4]=2
    excluded=np.zeros((6,6),bool);excluded[3,3]=True
    original=categories.copy();result=face_skin_support(categories,(2,2,6,6),excluded)
    assert result[2,2] and not result[3,3] and not result[4,4] and not result[5,5]
    assert not result[:2].any() and not result[:,8:].any()
    np.testing.assert_array_equal(categories,original)


def test_hair_veto_removes_baseline_hair_without_adding_or_removing_other_classes():
    categories=np.array([[0,1,2],[3,4,5]],np.uint8)
    support=np.ones((2,3),bool);support[1,2]=False
    result=hair_veto_support(categories,support)
    assert result.sum()==4 and not result[0,1] and not result[1,2]
    assert result[0,0] and result[1,0]
    assert support[0,1]  # no mutation


def test_invalid_categories_box_and_exclusion_shapes_fail_explicitly():
    with pytest.raises(ValueError): face_skin_support(np.zeros((10,10),np.uint8),(-1,0,5,5),np.zeros((5,5),bool))
    with pytest.raises(ValueError): face_skin_support(np.zeros((10,10),np.uint8),(0,0,5,5),np.zeros((6,5),bool))
    with pytest.raises(ValueError): hair_veto_support(np.full((2,2),6,np.uint8),np.ones((2,2),bool))
