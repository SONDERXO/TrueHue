import numpy as np
import pytest
from src.skin_masking.facial_hair_exclusion import preprocess_auxiliary,lower_face_suggestion,paint_exclusions,apply_exclusions,MEAN,STD


def test_auxiliary_uses_documented_bgr_raw_pixel_normalization():
    image=np.full((10,10,3),[12,34,56],np.uint8)
    tensor=preprocess_auxiliary(image)
    assert tensor.shape==(1,3,384,384) and tensor.dtype==np.float32
    np.testing.assert_allclose(tensor[0,:,0,0],(np.array([12,34,56])-MEAN)/STD,rtol=1e-6)


def test_suggestion_is_only_lower_face_skin_and_not_automatic():
    base=np.full((20,20),255,np.uint8);primary=np.ones_like(base);primary[5:10,9:11]=10
    aux=np.zeros_like(base);veto,report=lower_face_suggestion(base,primary,aux)
    assert not veto[:10].any() and veto[15,5] and not report['automatically_applied']
    primary[15,5]=17;veto,_=lower_face_suggestion(base,primary,aux);assert not veto[15,5]


def test_auxiliary_skin_agreement_keeps_even_dark_skin_without_color_thresholds():
    base=np.full((20,20),255,np.uint8);primary=np.ones_like(base);primary[5:10,9:11]=10
    veto,_=lower_face_suggestion(base,primary,np.ones_like(base));assert not veto.any()


def test_missing_nose_does_not_fabricate_lower_face_boundary():
    with pytest.raises(ValueError):lower_face_suggestion(np.full((20,20),255,np.uint8),np.ones((20,20),np.uint8),np.zeros((20,20),np.uint8))


def test_brush_exclusion_continuous_stroke_and_no_base_mutation():
    base=np.full((30,30),255,np.uint8);base[10:13,10:13]=0;before=base.copy()
    veto=paint_exclusions(base.shape,[dict(mode='exclude',radius=2,points=[[5,20],[25,20]])])
    mask,alpha=apply_exclusions(base,veto)
    assert not mask[20,5:26].any() and not alpha[veto].any()
    assert np.array_equal(base,before) and not mask[base==0].any()


def test_restore_never_adds_pixels_outside_preferred_mask():
    base=np.zeros((20,20),np.uint8);base[5:15,5:15]=255
    strokes=[dict(mode='exclude',radius=4,points=[[10,10]]),dict(mode='restore',radius=4,points=[[10,10]])]
    mask,_=apply_exclusions(base,paint_exclusions(base.shape,strokes))
    assert np.array_equal(mask,base)


def test_initial_suggestion_can_be_undone_without_mutating_it():
    initial=np.ones((20,20),bool);before=initial.copy()
    veto=paint_exclusions(initial.shape,[dict(mode='restore',radius=3,points=[[10,10]])],initial=initial)
    assert not veto[10,10] and veto[0,0] and np.array_equal(initial,before)


@pytest.mark.parametrize('stroke',[dict(mode='exclude',radius=0,points=[[1,1]]),dict(mode='add',radius=2,points=[[1,1]]),dict(mode='exclude',radius=2,points=[[-1,2]]),dict(mode='exclude',radius=2,points=[[float('nan'),2]])])
def test_invalid_strokes_fail_without_changing_saved_masks(stroke):
    with pytest.raises(ValueError):paint_exclusions((20,20),[stroke])
