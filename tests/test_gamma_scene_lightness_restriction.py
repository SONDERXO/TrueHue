from copy import deepcopy
import numpy as np
import pytest
from src.model_training.gamma_scene_lightness_restriction import fit_restricted_gamma,EXCLUDED
from src.model_training.portable_tree import PortableTree

def base():
    names=['input_ita_degrees','input_mst_score',*EXCLUDED]
    tree=dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',
        threshold_dtype='float64',comparison='<=',root=0,feature_names=names,
        target_names=['target_gamma'],nodes=[dict(kind='leaf',values=[1.])])
    gains=deepcopy(tree);gains['target_names']=['target_red_gain','target_blue_gain'];gains['nodes'][0]['values']=[1.1,.9]
    return dict(feature_names=names,heads=dict(gamma=dict(tree=tree),gains=dict(tree=gains)))

def test_fixed_exclusion_invariance_raw_means_and_frozen_gains():
    prior=base();before=deepcopy(prior)
    x=np.array([[i%3,i%2,i,i*2,i*3] for i in range(24)],float)
    y=np.array([[.7+.2*(i%3),1.1,.9] for i in range(24)])
    fitted=fit_restricted_gamma(prior,x,y);tree=PortableTree(fitted['heads']['gamma']['tree'])
    assert prior==before and fitted['heads']['gains']==prior['heads']['gains']
    assert all(n['feature']<2 for n in fitted['heads']['gamma']['tree']['nodes'] if n['kind']=='split')
    assert tree.predict_one([1,0,-1e6,0,1e6])==tree.predict_one([1,0,1e6,1e6,0])
    for row in x:
        leaf=tree.leaf_id(row);members=[i for i,v in enumerate(x) if tree.leaf_id(v)==leaf]
        assert abs(tree.predict_one(row)[0]-y[members,0].mean())<1e-12

def test_invalid_data_and_missing_exclusion_rejected_before_fit():
    p=base()
    with pytest.raises(ValueError):fit_restricted_gamma(p,[[0]*5],[[0,1,1]])
    p['feature_names']=['a','b','c','d','e']
    with pytest.raises(ValueError):fit_restricted_gamma(p,[[0]*5],[[1,1,1]])
