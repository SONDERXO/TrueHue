import cv2
import numpy as np
import pytest
from tests.test_full_face_support import setup
from src.skin_masking.correction_preview import render_preview


def example():
    image,base,categories,points=setup()
    image=cv2.resize(image,(256,256));facial=cv2.resize(base.measurement_mask,(256,256),interpolation=cv2.INTER_NEAREST)
    categories=cv2.resize(categories,(256,256),interpolation=cv2.INTER_NEAREST)
    points=points*2.56
    categories[90:115,90:120]=6
    visible=np.full((256,256),255,np.uint8);visible[90:115,90:120]=0
    return image,facial,categories,points,visible


def test_uncertain_exposes_choice_and_keeps_glasses_protected():
    args=example();result=render_preview(*args)
    assert result.report['requires_glasses_choice'] and result.report['status']=='needs_glasses_choice'
    assert not result.alpha[90:115,90:120].any()
    assert np.array_equal(result.output[90:115,90:120],args[0][90:115,90:120])
    assert result.report['MST'] is None and not result.report['training_admitted']


def test_clear_choice_restores_lens_interior_but_keeps_rim_and_same_measurement():
    args=example();opaque=render_preview(*args,glasses='opaque');clear=render_preview(*args,glasses='clear')
    assert not clear.report['requires_glasses_choice']
    assert clear.alpha[102,105]>0 and opaque.alpha[102,105]==0
    assert clear.alpha[90,105]==0
    assert np.array_equal(clear.support.measurement_mask,opaque.support.measurement_mask)
    assert not clear.report['correction_model_used']


def test_explicit_protection_cannot_be_overridden_by_clear_choice():
    args=example();protected=np.zeros((256,256),bool);protected[100:105,100:105]=True
    result=render_preview(*args,glasses='clear',protected=protected)
    assert not result.alpha[protected].any()
    assert np.array_equal(result.output[protected],args[0][protected])


@pytest.mark.parametrize('mode',['auto','none',True,None])
def test_unknown_or_implicit_classifier_mode_is_rejected(mode):
    with pytest.raises(ValueError):render_preview(*example(),glasses=mode)


def test_missing_visibility_does_not_fall_back_to_whole_face():
    args=list(example());args[-1]=None
    with pytest.raises(ValueError):render_preview(*args)


def test_no_parser_glasses_does_not_require_choice_or_claim_validated_detection():
    args=list(example());args[2][args[2]==6]=1
    result=render_preview(*args)
    assert not result.report['requires_glasses_choice']
    assert not result.report['glasses_detection_validated']
