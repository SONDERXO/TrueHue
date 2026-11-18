import numpy as np
from src.model_training.colour_nonharm_action_tree import fit_action_tree
from src.model_training.portable_tree import PortableTree

def test_colour_constraint_prevents_aggregate_gain_harming_colour():
    # One colour row would be harmed despite a much greater total exposure gain.
    costs=[[1.,3.],[10.,0.],[10.,0.]]
    m=fit_action_tree([[0.],[0.],[0.]],costs,[False]*3,[[1.,1.,1.],[.7,1.,1.]],['x'],nonharm=[True,False,False])
    assert PortableTree(m['tree']).predict_one([0.])==[1.,1.,1.]

def test_equal_cost_is_permitted_and_clean_remains_exact():
    m=fit_action_tree([[0.],[1.],[1.]],[[0.,2.],[2.,2.],[10.,0.]],[True,False,False],[[1.,1.,1.],[.7,1.,1.]],['x'],nonharm=[False,True,False])
    t=PortableTree(m['tree']);assert t.predict_one([0.])==[1.,1.,1.];assert t.predict_one([1.])==[.7,1.,1.]
