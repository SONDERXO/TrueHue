from copy import deepcopy
import numpy as np
import pytest
from src.model_training.signed_benefit_gate import fit_signed_benefit,signed_benefit_decision
from src.model_training.clean_constrained_gate import fit_clean_constrained_gate,MARGIN

def fixture():
    x=np.array([[0.,7.],[.1,7.],[1.,7.],[1.1,7.]]);y=np.array([-1.,100.,-1.,100.]);base=fit_signed_benefit(x,y,['a','a','b','b']);return x,y,base

def test_clean_constraints_hold_with_frozen_scaling_and_weights():
    x,y,base=fixture();before=deepcopy(base);p=fit_clean_constrained_gate(base,x,y,[0,2])
    assert base==before and p['mean']==base['mean'] and p['scale']==base['scale'] and p['weights']==base['weights']
    for i in [0,2]:assert signed_benefit_decision(p,x[i])['predicted_rgb_mae_gain']<=-MARGIN/2 and not signed_benefit_decision(p,x[i])['apply_correction']
    assert p['solver']['success'] and p['coefficient'][1]==0

def test_constrained_objective_cannot_beat_unconstrained_minimum():
    x,y,base=fixture();p=fit_clean_constrained_gate(base,x,y,[0,2]);z=(x-base['mean'])/base['scale'];w=np.array(base['weights'])
    def loss(g):return float(np.sum(w*(y-z@np.array(g['coefficient'])-g['intercept'])**2)+np.dot(g['coefficient'],g['coefficient']))
    assert loss(p)>=loss(base)-1e-8

def test_invalid_constraint_rows_rejected():
    x,y,base=fixture()
    for indices in [[],[0,0],[-1],[4]]:
        with pytest.raises(ValueError):fit_clean_constrained_gate(base,x,y,indices)
