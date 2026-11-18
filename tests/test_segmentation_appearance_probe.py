import numpy as np
import pytest
from src.skin_masking.segmentation_appearance_probe import parser_input

def test_original_is_preserved_and_output_is_separate_deterministic():
    image=np.tile(np.arange(256,dtype=np.uint8),(256,1))
    image=np.stack([image//4,image//3,image//2],axis=-1)
    original=image.copy();first=parser_input(image);second=parser_input(image)
    assert np.array_equal(image,original) and np.array_equal(first,second)
    assert not np.shares_memory(image,first) and not np.array_equal(image,first)
    first[:]=0
    assert np.array_equal(image,original)

@pytest.mark.parametrize('image',[None,np.zeros((32,32,3),np.uint8),np.zeros((256,256),np.uint8),np.zeros((256,256,3),float)])
def test_invalid_inputs_fail(image):
    with pytest.raises(ValueError):parser_input(image)
