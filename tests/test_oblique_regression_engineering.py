"""Generated numerical fixtures only; no scientific records or photographs."""
import json
import math
from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest

from src.model_training.portable_oblique_tree import (
    PortableObliqueTree, payload, from_axis_tree, float32,
)
from src.model_training.oblique_regression_tao import (
    train_oblique, raw_sse, fold_scaling, logistic_objective, guarded_update,
    refresh_leaves,
)


def stump(width=2):
    return payload([f'f{j}' for j in range(width)], [
        dict(kind='split', weights=[1.]+[0.]*(width-1), intercept=0., left=1, right=2),
        dict(kind='leaf', values=[1., 1., 1.]),
        dict(kind='leaf', values=[1.4, 1.02, 1.03])])


def diagonal():
    x = np.array([(a, b) for a in [-3., -2., -1., 1., 2., 3.]
                  for b in [-3., -2., -1., 1., 2., 3.]])
    y = np.array([[1.4, 1.02, 1.03] if a+b > .25 else [1., 1., 1.] for a, b in x])
    return x, y, refresh_leaves(stump(), x, y)


def test_diagonal_boundary_and_portable_three_output_roundtrip():
    x, y, initial = diagonal()
    trained, report = train_oblique(initial, x, y)
    assert report['final_SSE'] < report['initial_SSE']
    assert report['final_SSE'] < 1e-20
    assert sum(abs(w) > 1e-9 for w in trained['nodes'][0]['weights']) == 2
    tree = PortableObliqueTree(json.loads(json.dumps(trained)))
    np.testing.assert_allclose(tree.predict(x), y, atol=1e-12)
    for row in x:
        n = trained['nodes'][0]
        # Independent scalar, exact canonical multiplication/addition convention.
        s = math.fsum([n['intercept']]+[a*float32(b) for a, b in zip(n['weights'], row)])
        expected = 2 if s > 0 else 1
        assert tree.leaf_id(row) == expected
        assert tree.predict_one(dict(zip(tree.feature_names, row))) == n_values(trained, expected)
    assert all(b['SSE'] <= a['SSE'] for a,b in zip(report['SSE_history'], report['SSE_history'][1:]))


def n_values(model, i):
    return model['nodes'][i]['values']


def test_gradient_against_central_finite_differences():
    rng = np.random.default_rng(12)
    x = rng.normal(size=(9, 3));labels = np.array([0,1,0,1,1,0,0,1,0])
    weights = np.arange(1, 10, dtype=float);weights /= weights.sum()
    theta = np.array([.2, -.4, .1, .3])
    _, actual = logistic_objective(theta, x, labels, weights)
    numerical = []
    for j in range(4):
        delta = np.zeros(4);delta[j] = 1e-6
        numerical.append((logistic_objective(theta+delta,x,labels,weights)[0]-
                          logistic_objective(theta-delta,x,labels,weights)[0])/2e-6)
    np.testing.assert_allclose(actual, numerical, rtol=1e-6, atol=1e-9)


def test_fold_scaling_algebra_and_raw_tie_policy():
    w = [.7, -.2];b = .5;mean = [10., -7.];scale = [3., 5.]
    raw_w,raw_b = fold_scaling(w,b,mean,scale)
    for row in [[8., 6.], [13., -11.], [2., 9.]]:
        assert math.fsum([raw_b]+[a*v for a,v in zip(raw_w,row)]) == pytest.approx(
            b+sum(a*(v-m)/s for a,v,m,s in zip(w,row,mean,scale)),abs=1e-14)
    t = PortableObliqueTree(stump())
    assert t.leaf_id([0., 5.]) == 1
    assert t.leaf_id([1e-10, 5.]) == 2
    # Values indistinguishable after float32 rounding follow the same raw route.
    m=stump();m['nodes'][0]['intercept']=-1.
    assert PortableObliqueTree(m).leaf_id([1.+1e-9, 5.]) == 1


def test_axis_conversion_preserves_threshold_equality():
    axis=dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',
        threshold_dtype='float64', comparison='<=',root=0,feature_names=['a','b'],
        target_names=['gamma','red_gain','blue_gain'],nodes=[
            dict(kind='split',feature=1,threshold=.5,left=1,right=2),
            dict(kind='leaf',values=[1.,1.,1.]),dict(kind='leaf',values=[1.4,1.02,1.03])])
    t=PortableObliqueTree(from_axis_tree(axis))
    assert [t.leaf_id([2.,v]) for v in [.49,.5,.51]] == [1,1,2]


def test_worsening_empty_and_nonfinite_proposals_are_rejected():
    x=np.array([[-1.,0.],[1.,0.]])
    y=np.array([[1.,1.,1.],[1.4,1.02,1.03]])
    m=stump();copy=deepcopy(m)
    for w,b,reason in [([-1.,0.],0.,'no_strict_raw_SSE_gain'),
                       ([0.,0.],1.,'empty_child'),([float('nan'),0.],0.,'nonfinite_or_invalid')]:
        kept,actual,_=guarded_update(m,0,w,b,x,y,1e-12)
        assert kept == copy and actual == reason and m == copy


def test_three_output_leaf_means_and_empty_leaf_retention():
    x=np.array([[-1.,0.],[-2.,0.]])
    y=np.array([[1.,1.2,1.4],[2.,2.2,2.4]])
    m=refresh_leaves(stump(),x,y)
    np.testing.assert_allclose(m['nodes'][1]['values'],[1.5,1.7,1.9])
    assert m['nodes'][2]['values'] == stump()['nodes'][2]['values']


def test_one_leaf_constant_features_and_constant_targets():
    m=payload(['x'],[dict(kind='leaf',values=[1.,1.,1.])])
    x=np.ones((4,1));y=np.tile([1.1,1.2,1.3],(4,1))
    trained,r=train_oblique(m,x,y)
    np.testing.assert_allclose(trained['nodes'][0]['values'],y[0])
    assert r['final_SSE'] == 0 and r['fitting_scale'] == [1.]


def test_zero_weight_routing_skipped():
    m=stump();m['nodes'][2]['values']=[1.,1.,1.]
    trained,r=train_oblique(m,[[-1.,0.],[1.,0.]],[[1.,1.,1.],[1.,1.,1.]])
    assert r['reasons']['zero_routing_loss_weights'] == 1 and r['solver_attempts'] == 0


def test_single_pseudolabel_is_skipped():
    _,r=train_oblique(stump(),[[-1.,0.],[1.,0.]],[[1.,1.,1.],[1.,1.,1.]],max_passes=1)
    assert r['reasons']['single_routing_label'] == 1 and r['solver_attempts']==0


@pytest.mark.parametrize('budget,expected', [({'max_passes':0},'pass_cap'),
    ({'max_proposals':0},'proposal_cap'),({'max_seconds':0},'time_cap')])
def test_budget_exhaustion_without_restart(budget,expected):
    x,y,m=diagonal();trained,r=train_oblique(m,x,y,**budget)
    assert r['status']==expected and r['solver_attempts']==0
    assert trained['nodes']==m['nodes'] and r['final_SSE']==r['initial_SSE']


def test_timeout_inside_solver_retains_previous_feasible_tree(monkeypatch):
    import src.model_training.oblique_regression_tao as module
    now=[0.]
    def solver(fun,start,**kwargs):
        now[0]=61.
        fun(start)
    monkeypatch.setattr(module,'minimize',solver)
    x,y,m=diagonal();trained,r=train_oblique(m,x,y,clock=lambda:now[0])
    assert r['status']=='time_cap' and r['solver_attempts']==1
    assert trained['nodes']==m['nodes']


def test_failed_solver_has_no_retry_or_mutation(monkeypatch):
    import src.model_training.oblique_regression_tao as module
    calls=[]
    def solver(fun,start,**kwargs):
        calls.append(1)
        return SimpleNamespace(success=False,status=1,nit=100,nfev=1000,x=start)
    monkeypatch.setattr(module,'minimize',solver)
    x,y,m=diagonal();trained,r=train_oblique(m,x,y)
    assert len(calls)==1 and r['reasons']['solver_unsuccessful']==1
    assert trained['nodes']==m['nodes']


def test_deterministic_coefficients_and_initial_nonmutation():
    x,y,m=diagonal();copy=deepcopy(m)
    a,ra=train_oblique(m,x,y);b,rb=train_oblique(m,x,y)
    assert a==b and ra['SSE_history']==rb['SSE_history'] and m==copy


@pytest.mark.parametrize('change', ['cycle','shared','unreachable','badwidth','nan','negativecontrol','wrongversion'])
def test_invalid_graph_schema_and_controls(change):
    m=stump()
    if change=='cycle':m['nodes'][0]['left']=0
    elif change=='shared':m['nodes'][0]['right']=1
    elif change=='unreachable':m['nodes'].append(dict(kind='leaf',values=[1.,1.,1.]))
    elif change=='badwidth':m['nodes'][0]['weights']=[1.]
    elif change=='nan':m['nodes'][0]['intercept']=float('nan')
    elif change=='negativecontrol':m['nodes'][1]['values'][0]=0.
    else:m['schema_version']='truehue_regression_tree_v1'
    with pytest.raises(ValueError):PortableObliqueTree(m)


@pytest.mark.parametrize('features', [[1.], [float('nan'),0.], [True,0.], [1e100,0.], {'bad':1}])
def test_invalid_inputs(features):
    with pytest.raises(ValueError):PortableObliqueTree(stump()).predict_one(features)


def test_bad_targets_and_oversized_budgets():
    with pytest.raises(ValueError):train_oblique(stump(),[[1.,2.]],[[1.,2.]])
    with pytest.raises(ValueError):train_oblique(stump(),[[1.,2.]],[[0.,1.,1.]])
    with pytest.raises(ValueError):train_oblique(stump(),[[1.,2.]],[[1.,1.,1.]],max_passes=21)


def test_sixteen_feature_export_and_constant_columns():
    x,y,_=diagonal();x=np.column_stack([x,np.full((len(x),14),7.)])
    initial=refresh_leaves(stump(16),x,y)
    trained,r=train_oblique(initial,x,y)
    assert len(trained['nodes'][0]['weights'])==16
    assert r['final_SSE']<1e-20 and r['fitting_scale'][2:]==[1.]*14
    assert np.isfinite(trained['nodes'][0]['weights']).all()


def test_no_global_guarantee_on_symmetric_plateau():
    x=np.array([[-1.,-1.],[-1.,1.],[1.,-1.],[1.,1.]])
    y=np.array([[1.,1.,1.],[1.4,1.02,1.03],[1.4,1.02,1.03],[1.,1.,1.]])
    initial=refresh_leaves(stump(),x,y)
    trained,r=train_oblique(initial,x,y)
    assert r['status']=='no_strict_gain' and r['final_SSE']==r['initial_SSE']
    assert not r['global_optimality_claim'] and trained['nodes']==initial['nodes']


def test_bad_root_deep_tree_and_overflow_rejected():
    m=stump();m['root']=False
    with pytest.raises(ValueError):PortableObliqueTree(m)
    nodes=[]
    # Five successive branches exceed the depth-four schema even with small size.
    for i in range(5):
        nodes.append(dict(kind='split',weights=[1.],intercept=0.,left=i+1,right=i+6))
    nodes.extend(dict(kind='leaf',values=[1.,1.,1.]) for _ in range(6))
    with pytest.raises(ValueError):PortableObliqueTree(payload(['x'],nodes))
    m=stump();m['nodes'][0]['weights']=[1e308,1e308]
    with pytest.raises(ValueError):PortableObliqueTree(m).predict_one([1e30,1e30])
    with pytest.raises(ValueError):train_oblique(stump(),[[1.,2.]],[[1e300,1.,1.]])
