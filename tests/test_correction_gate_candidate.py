import numpy as np
import pytest
from src.model_training.correction_gate_candidate import fit_gate,gate_decision


def test_weighted_training_only_scaling_and_export():
    x=[[-2,7],[2,7],[3,7],[-1,7],[4,7]];y=[0,1,1,0,1];keys=['a','a','a','b','b']
    p,m=fit_gate(x,y,keys);w=np.array(p['weights'])
    assert abs(w.sum()-len(x))<1e-12
    for key in set(keys):
        for label in [0,1]:
            assert abs(sum(w[i] for i in range(len(x)) if keys[i]==key and y[i]==label)-len(x)/4)<1e-12
    np.testing.assert_allclose(p['mean'],np.average(x,axis=0,weights=w));assert p['scale'][1]==1
    points=[[-999,7],[999,7]]
    np.testing.assert_allclose([gate_decision(p,v)['logit'] for v in points],m.decision_function((np.array(points)-p['mean'])/p['scale']),atol=1e-12,rtol=0)


def test_zero_is_noop_without_tuned_threshold():
    p=dict(mean=[0.],scale=[1.],coefficient=[1.],intercept=0.)
    assert not gate_decision(p,[0.])['apply_correction']
    assert gate_decision(p,[.001])['apply_correction']
    assert not gate_decision(p,[-.001])['apply_correction']


@pytest.mark.parametrize('labels,keys', [([0,1],['a','b']),([False,True],['a','a']),([0,2],['a','a'])])
def test_incomplete_group_or_bad_labels_reject(labels,keys):
    with pytest.raises(ValueError):fit_gate([[0],[1]],labels,keys)


def test_bad_features_reject():
    with pytest.raises(ValueError):fit_gate([[0],[float('nan')]],[0,1],['a','a'])
    with pytest.raises(ValueError):gate_decision(dict(mean=[0],scale=[1],coefficient=[1],intercept=0),[float('inf')])
