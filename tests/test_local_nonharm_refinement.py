import copy
from src.model_training.local_nonharm_refinement import refine_leaf


def fixture(features, costs, clean=None):
    n=len(features)
    return dict(tree=dict(nodes=[dict(kind='leaf',values=[1.,1.,1.])]),
        trace=[dict(node=0,rows=list(range(n)),depth=4,action=0,cost=sum(c[0] for c in costs))],
        costs=costs,clean=clean or [False]*n,nonharm=[True]+[False]*(n-1),
        actions=[[1.,1.,1.],[.7,1.,1.]])


def test_isolates_colour_blocker_without_relaxing_costs():
    x=[[2.],[0.],[1.]];m=fixture(x,[[1.,5.],[8.,1.],[8.,1.]])
    before=copy.deepcopy(m);out,r=refine_leaf(m,x,0)
    assert m==before and r['split_added']
    assert r['threshold']==1.5 and r['left_action']==1 and r['right_action']==0
    assert len(out['tree']['nodes'])==3 and r['final_cost']==3.
    assert out['trace'][1]['depth']==5


def test_identical_vectors_cannot_be_split_to_evade_blocker():
    x=[[0.],[0.]];m=fixture(x,[[1.,5.],[8.,1.]])
    out,r=refine_leaf(m,x,0)
    assert out==m and r['candidates']==0 and not r['split_added']


def test_no_gain_keeps_original_trace_and_clean_constraint():
    x=[[0.],[1.]];m=fixture(x,[[0.,1.],[0.,1.]],[True,True])
    out,r=refine_leaf(m,x,0)
    assert out==m and not r['split_added']


def test_schema_order_resolves_equivalent_feature_choices():
    x=[[2.,2.],[0.,0.],[1.,1.]];m=fixture(x,[[1.,5.],[8.,1.],[8.,1.]])
    out,r=refine_leaf(m,x,0)
    assert r['feature']==0 and len(out['tree']['nodes'])==3
