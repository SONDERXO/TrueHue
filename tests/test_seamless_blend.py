import numpy as np
from src.correction.seamless_blend import inward_alpha,apply_blended


def example():
    im=np.full((100,100,3),(70,110,150),np.uint8)
    mask=np.zeros((100,100),np.uint8);mask[10:70,20:80]=255;mask[60:90,35:65]=255
    return im,mask


def test_inward_blend_never_spills_and_retains_full_strength_interior():
    im,mask=example();out,alpha,report=apply_blended(im,mask,[.7,1.1,.9],face_width=60)
    assert np.array_equal(out[mask==0],im[mask==0])
    assert not alpha[mask==0].any()
    assert 0<alpha[10,40]<1 and alpha[40,40]==1
    assert report['edge_width_pixels']==2


def test_union_has_no_internal_face_neck_blending_seam():
    _,mask=example();alpha,_=inward_alpha(mask,face_width=60)
    assert (alpha[55:80,45:55]==1).all()


def test_identity_and_explicit_protected_pixels_remain_exact():
    im,mask=example();veto=np.zeros(mask.shape,bool);veto[35:40,35:40]=True
    out,_,_=apply_blended(im,mask,[1,1,1],face_width=60)
    assert np.array_equal(out,im)
    changed,alpha,_=apply_blended(im,mask,[.7,1.1,.9],face_width=60,protected=veto)
    assert np.array_equal(changed[veto],im[veto]) and not alpha[veto].any()


def test_full_frame_and_absent_support_have_finite_alpha():
    for value in [0,255]:
        alpha,_=inward_alpha(np.full((10,10),value,np.uint8),face_width=10)
        assert np.isfinite(alpha).all()
        assert (alpha==(1 if value else 0)).all()
