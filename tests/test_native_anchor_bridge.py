import numpy as np
import pytest
from src.skin_masking.native_anchor_bridge import crop_native_anchor
from src.skin_masking.fixed_face_input_bridge import native_projection, crop_face
from src.model_training.aligned_correction_support import project_alpha


@pytest.mark.parametrize('shape', [(48, 32, 3), (32, 48, 3)])
def test_same_native_box_has_same_geometry_for_both_orientations(shape):
    image=np.arange(np.prod(shape),dtype=np.uint8).reshape(shape)
    before=image.copy()
    crop,r=crop_native_anchor(image,native_box=[10,8,8,10])
    assert r['native_bounds']==[6,5,21,20] and crop.shape==(15,15,3)
    np.testing.assert_array_equal(crop,image[5:20,6:21])
    crop[:]=0
    np.testing.assert_array_equal(image,before)
    assert r['anchor_coordinate_space']=='original_native_pixels'
    assert not r['old_fitting_costs_compatible']


def test_edge_shift_preserves_pixels_without_padding():
    image=np.full((32,48,3),71,np.uint8)
    crop,r=crop_native_anchor(image,native_box=[0,0,4,6])
    assert r['native_bounds']==[0,0,9,9] and r['edge_shift']==[3,2]
    assert crop.shape==(9,9,3) and (crop==71).all()


def test_native_mask_and_alpha_retain_location_and_protected_pixels():
    _,r=crop_native_anchor(np.zeros((32,48,3),np.uint8),native_box=[10,8,8,10])
    mask=np.zeros((256,256),np.uint8);mask[:128]=255
    native,counts=native_projection(mask,r)
    expected=np.zeros((32,48),np.uint8);expected[5:13,6:21]=255
    np.testing.assert_array_equal(native,expected)
    assert counts['selected_native_grid_locations']==120
    alpha,protected=project_alpha(np.ones((256,256),float),mask>0,r)
    assert not alpha[protected].any()
    assert np.count_nonzero(alpha)==105
    assert np.count_nonzero(alpha[:5])==np.count_nonzero(alpha[20:])==0
    assert np.count_nonzero(alpha[:,:6])==np.count_nonzero(alpha[:,21:])==0


def test_square256_contract_matches_old_crop_when_coordinates_are_identical():
    image=np.arange(256*256*3,dtype=np.uint8).reshape(256,256,3)
    a,ra=crop_native_anchor(image,native_box=[80,100,30,40])
    b,rb=crop_face(image,[80,100,30,40])
    np.testing.assert_array_equal(a,b)
    assert ra['native_bounds']==rb['native_bounds']
    assert ra['version']!=rb['version']


@pytest.mark.parametrize('box', [[-1,0,4,6],[0,0,0,6],[40,0,12,6],
                                 [True,0,4,6],[0,0,4.0,6],[0,0,40,30]])
def test_invalid_or_unfittable_boxes_fail_without_rescue(box):
    with pytest.raises(ValueError):
        crop_native_anchor(np.zeros((32,48,3),np.uint8),native_box=box)
