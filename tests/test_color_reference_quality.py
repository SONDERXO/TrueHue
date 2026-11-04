import numpy as np
import pytest
from src.data_preparation.color_reference_quality import assess_color_reference


def test_exact_gray_and_explicit_source_rejection_are_preserved():
    gray=np.arange(16,dtype=np.uint8).reshape(4,4)
    image=np.repeat(gray[:,:,None],3,axis=2)
    result=assess_color_reference(image,human_rejected=True)
    assert result['reasons']==['human_rejected_reference','exact_achromatic_reference']
    assert not result['training_eligible']


def test_nearly_gray_color_is_not_rejected_by_an_invented_threshold():
    image=np.full((4,4,3),100,np.uint8);image[0,0,0]=101
    result=assess_color_reference(image)
    assert result['status']=='requires_reference_review' and not result['training_eligible']
    assert not result['exact_achromatic']


def test_human_rejection_applies_even_with_colored_artifacts():
    image=np.full((4,4,3),100,np.uint8);image[0,0,0]=101
    assert assess_color_reference(image,human_rejected=True)['reasons']==['human_rejected_reference']


def test_wrong_input_rejected():
    with pytest.raises(ValueError):assess_color_reference(np.zeros((4,4),np.uint8))
