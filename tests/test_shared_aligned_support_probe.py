import numpy as np
import pytest
from src.skin_masking.shared_aligned_support_probe import common_support

IDENTITY=np.array([[1.,0,0],[0,1.,0]])

def test_identity_intersection_and_no_source_mutation():
    a=np.zeros((256,256),np.uint8);a[10:80,10:90]=255
    b=a.copy();b[:30]=0;c=a.copy();c[:,60:]=0
    originals=[x.copy() for x in [a,b,c]]
    common,mapped=common_support([a,b,c],[IDENTITY]*3)
    expected=a&b&c
    assert np.array_equal(common,expected)
    assert all(np.array_equal(x,expected) for x in mapped)
    assert all(np.array_equal(x,y) for x,y in zip([a,b,c],originals))

def test_translation_matches_corresponding_region_and_never_adds_pixels():
    a=np.zeros((256,256),np.uint8);a[20:80,20:80]=255
    b=np.zeros_like(a);b[20:80,30:90]=255
    shift=np.array([[1.,0,-10],[0,1.,0]])
    common,mapped=common_support([a,b,a],[IDENTITY,shift,IDENTITY])
    assert np.array_equal(common,a) and np.array_equal(mapped[1],b)
    assert all(not x[y==0].any() for x,y in zip(mapped,[a,b,a]))

def test_disjoint_masks_remain_empty_without_fallback():
    a=np.zeros((256,256),np.uint8);a[:10,:10]=255
    b=np.zeros_like(a);b[-10:,-10:]=255
    common,mapped=common_support([a,b,a],[IDENTITY]*3)
    assert not common.any() and not any(m.any() for m in mapped)

def test_incomplete_group_or_singular_geometry_rejected():
    a=np.zeros((256,256),np.uint8)
    with pytest.raises(ValueError):common_support([a]*2,[IDENTITY]*2)
    with pytest.raises(ValueError):common_support([a]*3,[np.zeros((2,3))]*3)
