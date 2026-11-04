import numpy as np
import pytest
from src.evaluation.preferred_regions import evaluate_regions,REGIONS


def sample():
    image=np.full((10,10,3),100,np.uint8);regions={k:np.zeros((10,10),bool) for k in REGIONS}
    for i,k in enumerate(REGIONS):regions[k][i,:5]=True
    application=np.logical_or.reduce(list(regions.values()))
    return image,regions,application


def test_identity_control_and_empty_region_are_explicit():
    im,regions,app=sample();regions['neck'][:]=False
    r=evaluate_regions(im,im,im,regions,app,identity_control=True)
    assert r['clean_gate_pass'] and r['union']['ciede2000']==0
    assert r['regions']['neck']['ciede2000'] is None and not r['regions']['neck']['available']


def test_changed_neck_cannot_be_hidden_in_face_score():
    im,regions,app=sample();out=im.copy();out[regions['neck']]=200
    r=evaluate_regions(im,im,out,regions,app,identity_control=True)
    assert r['regions']['face']['ciede2000']==0 and r['regions']['neck']['ciede2000']>0
    assert not r['clean_gate_pass'] and r['outside_application_preserved']


def test_scoring_keeps_missed_generation_pixels():
    ref,regions,app=sample();distorted=ref.copy();distorted[regions['lips']]=200
    app[regions['lips']]=False
    r=evaluate_regions(ref,distorted,distorted,regions,app)
    assert r['regions']['lips']['ciede2000']>0
    assert r['regions']['lips']['generation_pixels_outside_application']==5


def test_outside_application_change_is_a_failure_even_outside_scoring_support():
    im,regions,app=sample();out=im.copy();out[9,9]=200
    r=evaluate_regions(im,im,out,regions,app)
    assert r['union']['ciede2000']==0 and not r['outside_application_preserved']
    assert r['outside_application_changed_pixels']==1 and r['changed_pixels_outside_generation']==1


def test_overlapping_regions_cannot_double_count():
    im,regions,app=sample();regions['brows']|=regions['face']
    with pytest.raises(ValueError):evaluate_regions(im,im,im,regions,app)
