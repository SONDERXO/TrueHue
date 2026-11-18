import numpy as np
import pytest
from src.model_training.layer_balanced_tree import fit_balanced
from src.model_training.portable_tree import PortableTree


def test_one_leaf_uses_weighted_raw_mean_not_row_mean():
    y=[[1,1,1],[2,1,1],[2,1,1],[4,1,1]]
    payload,_,meta=fit_balanced([[0]]*4,y,['x'],['one']*4,['clean','core','core','composite_stress_design'])
    np.testing.assert_allclose(meta['weights'],[1/3,1/6,1/6,1/3])
    np.testing.assert_allclose(PortableTree(payload).predict_one([0]),[7/3,1,1])
    assert meta['scale'][1:]==[1.,1.]


def test_duplication_within_key_layer_preserves_objective():
    layers=['clean','core','composite_stress_design'];y=[[1,1,1],[2,1.1,.9],[3,1.2,.8]]
    a,_,ma=fit_balanced([[0]]*3,y,['x'],['one']*3,layers)
    b,_,mb=fit_balanced([[0]]*4,y+[y[1]],['x'],['one']*4,layers+['core'])
    np.testing.assert_allclose(PortableTree(a).predict_one([0]),PortableTree(b).predict_one([0]))
    np.testing.assert_allclose(ma['mean'],mb['mean']);np.testing.assert_allclose(ma['scale'],mb['scale'])


def test_missing_layer_and_invalid_weights_inputs_reject():
    with pytest.raises(ValueError):fit_balanced([[0]],[[1,1,1]],['x'],['one'],['clean'])
    with pytest.raises(ValueError):fit_balanced([[0]]*3,[[1,1,1]]*3,['x'],['one']*2,['clean','core','composite_stress_design'])
