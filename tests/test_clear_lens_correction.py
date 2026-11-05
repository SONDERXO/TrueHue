import numpy as np
import pytest
from src.skin_masking.face_neck_support import FaceNeckSupport
from src.skin_masking.clear_lens_correction import protect_with_clear_lenses
from src.correction.seamless_blend import apply_blended


def example():
    mask=np.zeros((256,256),np.uint8);mask[30:220,30:220]=255
    categories=np.ones_like(mask)
    categories[90:120,60:100]=6;categories[90:120,130:170]=6
    categories[102:104,100:130]=6  # thin bridge should remain protected
    visible=np.full_like(mask,255);visible[categories==6]=0
    return FaceNeckSupport(mask.copy(),np.zeros_like(mask),mask,{}),categories,visible,mask.copy()


def test_clear_lenses_restore_eyes_but_protect_rims_bridge_and_other_objects():
    support,cats,visible,outline=example();cats[150:180,70:100]=18
    revised,veto,lenses,rims=protect_with_clear_lenses(support,cats,visible,outline,transparent_glasses=True)
    assert revised.correction_mask[105,80] and revised.correction_mask[105,150]
    assert not revised.correction_mask[90,80] and not revised.correction_mask[102,115]
    assert not revised.correction_mask[150:180,70:100].any()
    image=np.full((256,256,3),90,np.uint8)
    output,alpha,_=apply_blended(image,revised.correction_mask,[.7,1.1,.9],face_width=190,protected=veto)
    assert alpha[105,80]==1 and np.any(output[105,80]!=image[105,80])
    assert np.array_equal(output[rims>0],image[rims>0]) and not alpha[rims>0].any()
    assert np.array_equal(support.measurement_mask,revised.measurement_mask)


def test_opaque_unknown_glasses_remain_fully_protected():
    support,cats,visible,outline=example()
    revised,_,lenses,_=protect_with_clear_lenses(support,cats,visible,outline)
    assert not revised.correction_mask[cats==6].any() and not lenses.any()


def test_anatomical_eye_label_inside_lens_is_restored_but_explicit_protection_wins():
    support,cats,visible,outline=example();cats[100:110,75:85]=4
    protected=np.zeros(cats.shape,bool);protected[105,80]=True
    revised,veto,_,_=protect_with_clear_lenses(support,cats,visible,outline,transparent_glasses=True,protected=protected)
    assert revised.correction_mask[104,80] and not revised.correction_mask[105,80]
    assert veto[105,80] and not revised.correction_mask[support.correction_mask==0].any()


def test_no_glasses_has_no_fabricated_lens_region():
    support,cats,visible,outline=example();cats[:]=1
    revised,_,lenses,_=protect_with_clear_lenses(support,cats,visible,outline,transparent_glasses=True)
    assert not lenses.any() and revised.report['glasses_policy'].startswith('clear_lens_interior_unavailable')


def test_ambiguous_type_is_not_silently_treated_as_clear():
    support,cats,visible,outline=example()
    with pytest.raises(ValueError):protect_with_clear_lenses(support,cats,visible,outline,transparent_glasses='yes')
