import numpy as np
import pytest
from sklearn.tree import DecisionTreeRegressor
from src.evaluation.tree_training_audit import gamma_direction,trace_tree


def test_gamma_direction_distinguishes_identity_from_opposite_exposure():
    assert gamma_direction(.8)=='darken' and gamma_direction(1.4)=='brighten'
    assert gamma_direction(1+1e-10)=='unchanged'
    for value in (0,-1,float('nan'),float('inf')):
        with pytest.raises(ValueError):gamma_direction(value)


def test_trace_matches_float32_routing_at_a_threshold_and_does_not_mutate_model():
    # Tiny synthetic fixture, unrelated to the saved thesis prototype model.
    model=DecisionTreeRegressor(max_depth=1,random_state=42).fit([[0.],[.2]],[1.,2.])
    original=model.tree_.value.copy();threshold=model.tree_.threshold[0]
    result=trace_tree(model,[threshold+1e-11],['feature'])
    assert result['rules'][0]['comparison']=='<='
    assert result['leaf_id']==model.apply([[threshold+1e-11]])[0]
    np.testing.assert_array_equal(model.tree_.value,original)


def test_trace_rejects_missing_or_nonfinite_features():
    model=DecisionTreeRegressor().fit([[0.],[1.]],[0.,1.])
    with pytest.raises(ValueError):trace_tree(model,[],['feature'])
    with pytest.raises(ValueError):trace_tree(model,[np.nan],['feature'])
