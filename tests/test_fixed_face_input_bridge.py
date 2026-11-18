import numpy as np
import pytest
from src.skin_masking.fixed_face_input_bridge import crop_face,native_projection


def test_crop_is_exact_native_slice_and_mapping_has_fixed_margin():
    image=np.random.default_rng(8).integers(0,256,(224,224,3),dtype=np.uint8);before=image.copy()
    crop,report=crop_face(image,[100,130,32,40])
    assert crop.shape==(53,53,3)
    x,y,r,b=report['native_bounds']
    assert np.array_equal(crop,image[y:b,x:r]) and np.array_equal(image,before)
    assert report['source_to_normalized_linear_scale']==256/53
    assert not report['new_detail_created'] and not report['padding_added']


def test_edge_square_shifts_instead_of_padding_or_retry():
    crop,report=crop_face(np.zeros((224,224,3),np.uint8),[0,0,30,40])
    assert report['native_bounds'][:2]==[0,0] and crop.shape[:2]==(53,53)
    assert report['edge_shift']!=[0,0]


def test_upsampled_count_does_not_become_native_sample_count():
    _,report=crop_face(np.zeros((224,224,3),np.uint8),[100,130,32,40])
    mask=np.full((256,256),255,np.uint8);native,counts=native_projection(mask,report)
    assert counts['normalized_selected_pixels']==65536
    assert counts['selected_native_grid_locations']==53*53==np.count_nonzero(native)
    assert counts['source_area_equivalent_pixels']==53*53
    assert counts['effective_independent_sample_size'] is None and not counts['calibration_admitted']


@pytest.mark.parametrize('box',[[-1,0,20,20],[0,0,0,10],[250,0,20,20],[True,1,20,20],[0,0,256,256]])
def test_invalid_or_unfittable_crop_fails_without_alternative(box):
    with pytest.raises(ValueError):crop_face(np.zeros((224,224,3),np.uint8),box)
