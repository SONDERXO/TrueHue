import numpy as np
import pytest
from src.model_training.image_loss_action_tree import fit_action_tree,action_costs
from src.model_training.portable_tree import PortableTree
from src.model_training.blended_recovery_targets import render_rgb8

A=[[1.,1.,1.],[.7,1.,1.]]

def test_mixed_root_learns_identity_and_correction_in_one_split():
    p=fit_action_tree([[0],[1]],[[0,10],[20,0]],[True,False],A,['x'])
    t=PortableTree(p['tree'])
    assert p['trace'][0]['action']==0 and p['trace'][0]['cost']==20
    assert t.predict_one([0])==A[0] and t.predict_one([1])==A[1]

def test_identical_features_cannot_escape_clean_constraint():
    p=fit_action_tree([[0],[0]],[[0,1],[100,0]],[True,False],A,['x'])
    assert len(p['tree']['nodes'])==1 and PortableTree(p['tree']).predict_one([0])==A[0]

def test_clean_harm_infeasible_even_when_unprotected_loss_is_lower_and_ties_identity():
    p=fit_action_tree([[0],[1]],[[0,1],[100,0]],[True,False],A,['x'],max_depth=0)
    assert p['trace'][0]['action']==0
    tie=fit_action_tree([[0]],[[0,0]],[False],A,['x'])
    assert tie['trace'][0]['action']==0

def test_costs_match_full_renderer_selected_pixels_with_clipping_and_rounding():
    im=np.arange(90,dtype=np.uint8).reshape(5,6,3)*2;ref=np.flip(im,axis=1).copy()
    mask=np.indices((5,6)).sum(axis=0)%2==0;actions=[*A,[1.8,1.3,.6]]
    costs=action_costs(im[mask],ref[mask],actions)
    for i,p in enumerate(actions):
        out=render_rgb8(im,mask.astype(float),p)
        assert costs[i]==np.abs(out[mask].astype(float)-ref[mask]).mean()
        np.testing.assert_array_equal(out[~mask],im[~mask])

def test_invalid_clean_identity_and_nonfinite_costs_rejected():
    with pytest.raises(ValueError):fit_action_tree([[0]],[[1,0]],[True],A,['x'])
    with pytest.raises(ValueError):fit_action_tree([[0]],[[0,float('nan')]],[False],A,['x'])
