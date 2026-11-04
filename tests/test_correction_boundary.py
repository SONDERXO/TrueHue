import numpy as np
import pytest
from src.evaluation.correction_boundary import inward_alpha, feather_correction, correction_edge_jump
from src.evaluation.correction_prototype import apply_correction


def test_feather_preserves_exclusions_and_reaches_full_correction():
    mask = np.zeros((17,17), bool); mask[2:15,2:15] = True
    image = np.full((17,17,3),64,np.uint8)
    original = image.copy()
    out,alpha = feather_correction(image,mask,[2,1,1],4)
    hard = apply_correction(image,mask,[2,1,1])
    assert np.array_equal(image,original)
    assert np.array_equal(out[~mask],image[~mask])
    assert alpha[8,8] == 1 and 0 < alpha[2,8] < 1
    assert np.array_equal(out[8,8],hard[8,8])
    assert correction_edge_jump(image,out,mask) < correction_edge_jump(image,hard,mask)


def test_identity_empty_and_full_frame_masks():
    image = np.random.default_rng(42).integers(0,256,(10,10,3),dtype=np.uint8)
    for mask in (np.ones((10,10),bool),np.zeros((10,10),bool)):
        out,_ = feather_correction(image,mask,[1,1,1],3)
        assert np.array_equal(out,image)
    alpha = inward_alpha(np.ones((10,10),bool),3)
    assert alpha[0,0] < alpha[4,4]


@pytest.mark.parametrize('width',[0,-1,float('nan'),float('inf')])
def test_invalid_width_rejected(width):
    with pytest.raises(ValueError): inward_alpha(np.ones((3,3),bool),width)
