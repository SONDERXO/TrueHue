import numpy as np
import pytest
from src.model_training.aligned_correction_support import project_alpha,blended_action_costs
from src.model_training.blended_recovery_targets import render_rgb8

def test_projection_preserves_native_bounds_and_any_overlapping_protection():
    a=np.ones((256,256),float);p=np.zeros_like(a,dtype=bool);p[0,0]=True
    out,veto=project_alpha(a,p,dict(native_bounds=[2,3,6,7],source_shape=[10,12,3]))
    assert out.shape==(10,12) and veto[3,2] and out[3,2]==0
    assert out[:3].sum()==0 and out[:,6:].sum()==0 and not out[veto].any()
    assert np.count_nonzero(out)==15

def test_partial_alpha_costs_match_full_renderer_and_include_missed_support():
    im=np.arange(90,dtype=np.uint8).reshape(5,6,3)*2;ref=np.flip(im,axis=1).copy()
    a=np.linspace(0,1,30).reshape(5,6);mask=np.ones((5,6),bool);actions=[[1,1,1],[.7,1.1,.8],[1.8,.6,1.3]]
    costs=blended_action_costs(im,ref,a,mask,actions)
    for i,p in enumerate(actions):
        out=render_rgb8(im,a,p);assert costs[i]==np.abs(out.astype(float)-ref.astype(float)).mean()
    assert blended_action_costs(im,im,a,mask,[[1,1,1]])==[0.]

def test_invalid_projection_and_empty_scoring_rejected():
    with pytest.raises(ValueError):project_alpha(np.full((256,256),2.),np.zeros((256,256),bool),{})
    im=np.ones((2,2,3),np.uint8)
    with pytest.raises(ValueError):blended_action_costs(im,im,np.ones((2,2)),np.zeros((2,2),bool),[[1,1,1]])
