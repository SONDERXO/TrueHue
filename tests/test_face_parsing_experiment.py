import numpy as np
import pytest

from src.skin_masking.face_parsing_experiment import preprocess,decode,facial_skin


def test_bgr_to_rgb_normalization_and_input_preservation():
    image=np.zeros((2,3,3),np.uint8);image[:,:,2]=255;original=image.copy()
    tensor=preprocess(image)
    assert tensor.shape==(1,3,512,512) and tensor.dtype==np.float32
    np.testing.assert_allclose(tensor[0,:,10,10],[(1-.485)/.229,-.456/.224,-.406/.225],atol=1e-6)
    np.testing.assert_array_equal(image,original)


def test_argmax_precedes_nearest_native_restore():
    logits=np.zeros((1,19,2,2),np.float32)
    for y,x,label in [(0,0,1),(0,1,10),(1,0,4),(1,1,17)]:logits[0,label,y,x]=5
    result=decode(logits,4,4)
    np.testing.assert_array_equal(result,[[1,1,10,10],[1,1,10,10],[4,4,17,17],[4,4,17,17]])


def test_skin_nose_selection_excludes_features_ears_neck_hair():
    categories=np.arange(19,dtype=np.uint8)[None]
    np.testing.assert_array_equal(np.flatnonzero(facial_skin(categories)),[1,10])


def test_bad_categories_and_nonfinite_outputs_fail_explicitly():
    with pytest.raises(ValueError):facial_skin(np.array([[19]],np.uint8))
    with pytest.raises(ValueError):decode(np.full((1,19,2,2),np.nan,np.float32),4,4)
    with pytest.raises(ValueError):preprocess(np.zeros((2,2,3),np.float32))
