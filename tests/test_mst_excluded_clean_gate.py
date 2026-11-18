from copy import deepcopy
import numpy as np
import pytest
from src.model_training.signed_benefit_gate import fit_signed_benefit,signed_benefit_decision
from src.model_training.clean_constrained_gate import fit_clean_constrained_gate
from src.model_training.mst_excluded_clean_gate import fit_mst_excluded_clean_gate


def fixture():
    x=np.zeros((8,12));x[:,0]=[0,1,2,.2,-.1,1.1,2.1,.1];x[:,4]=[1,3,5,2,1,4,6,2]
    y=np.array([-1,2,3,-1,-1,2,3,-1],float)
    base=fit_signed_benefit(x,y,['a']*4+['b']*4)
    return x,y,base,[0,3,4,7]


def test_zero_mst_coefficient_preserves_other_frozen_inputs_and_clean_actions():
    x,y,base,indices=fixture();before=deepcopy(base)
    gate=fit_mst_excluded_clean_gate(base,x,y,indices)
    assert base==before and gate['coefficient'][4]==0.
    for key in ['mean','scale','weights','alpha','training_keys']:assert gate[key]==base[key]
    for i in indices:assert not signed_benefit_decision(gate,x[i])['apply_correction']
    assert signed_benefit_decision(gate,x[2])['apply_correction']
    changed=x[2].copy();changed[4]=1e9
    assert signed_benefit_decision(gate,x[2])==signed_benefit_decision(gate,changed)


def test_restricted_optimum_cannot_improve_unrestricted_objective():
    x,y,base,idx=fixture();a=fit_clean_constrained_gate(base,x,y,idx);b=fit_mst_excluded_clean_gate(base,x,y,idx)
    z=(x-base['mean'])/base['scale'];w=np.array(base['weights'])
    def loss(g):
        c=np.array(g['coefficient']);return float(np.sum(w*(z@c+g['intercept']-y)**2)+c@c)
    assert loss(b)>=loss(a)-1e-7


def test_wrong_schema_and_clean_constraints_rejected():
    x,y,base,idx=fixture()
    with pytest.raises(ValueError):fit_mst_excluded_clean_gate(base,x[:,:11],y,idx)
    with pytest.raises(ValueError):fit_mst_excluded_clean_gate(base,x,y,[0,0])
