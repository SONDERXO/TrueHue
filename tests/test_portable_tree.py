import copy
import json
import math
import numpy as np
import pytest
from sklearn.tree import DecisionTreeRegressor,DecisionTreeClassifier
from src.model_training.portable_tree import PortableTree,export_tree,float32,SCHEMA

def payload():
    return dict(schema_version=SCHEMA,input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,
        feature_names=['L','a'],target_names=['gamma','red','blue'],
        nodes=[dict(kind='split',feature=0,threshold=1.,left=1,right=2),
               dict(kind='leaf',values=[1.,.9,1.1]),dict(kind='leaf',values=[.8,1.2,1.])])

def test_float32_routing_matches_sklearn_contract_at_double_precision_boundary():
    tree=PortableTree(payload());just_above_double=math.nextafter(1.,math.inf)
    assert just_above_double>1. and float32(just_above_double)==1.
    assert tree.leaf_id([just_above_double,0])==1
    right32=float(np.nextafter(np.float32(1),np.float32(np.inf)))
    assert tree.leaf_id([right32,0])==2

def test_json_roundtrip_named_feature_order_and_prediction_copy():
    original=payload();tree=PortableTree(json.loads(json.dumps(original)))
    original['nodes'][1]['values'][0]=99
    assert tree.predict_one({'a':5,'L':0})==[1.,.9,1.1]
    result=tree.predict_one([0,0]);result[0]=99
    assert tree.predict_one([0,0])[0]==1.
    assert tree.predict([])==[]

@pytest.mark.parametrize('features',[[0],[[0],0],[True,0],['1',0],[float('nan'),0],[float('inf'),0],[1e100,0],{'L':0},{'L':0,'a':0,'extra':0}])
def test_invalid_features_are_not_imputed_or_silently_rounded(features):
    with pytest.raises(ValueError):PortableTree(payload()).predict_one(features)

@pytest.mark.parametrize('mutation',[
    lambda p:p.update(schema_version='unknown'),lambda p:p.update(comparison='<'),
    lambda p:p.update(root=False),lambda p:p.update(root=0.),
    lambda p:p.update(feature_names=['L','L']),lambda p:p.update(target_names=[]),
    lambda p:p['nodes'][0].update(left=0),lambda p:p['nodes'][0].update(right=1),
    lambda p:p['nodes'][0].update(left=42),lambda p:p['nodes'][0].update(left=True),
    lambda p:p['nodes'][0].update(feature=-1),lambda p:p['nodes'][0].update(threshold=float('nan')),
    lambda p:p['nodes'][1].update(values=[1,1]),lambda p:p['nodes'][1].update(values=[0,1,1]),
    lambda p:p['nodes'].append(dict(kind='leaf',values=[1,1,1]))])
def test_invalid_schema_graph_or_leaf_fails_at_load(mutation):
    data=payload();mutation(data)
    with pytest.raises(ValueError):PortableTree(data)

def test_exported_fitted_regressor_matches_predictions_and_leaves_without_refitting():
    x=np.asarray([[0,1],[1,2],[2,3],[3,4]],float)
    y=np.asarray([[1,.9,1],[1,.9,1],[.8,1.2,1],[.8,1.2,1]],float)
    model=DecisionTreeRegressor(max_depth=2,random_state=42).fit(x,y)
    state=model.tree_.value.copy();data=export_tree(model,['L','a'],['gamma','red','blue'],{'source':'toy-test'})
    restored=PortableTree(json.loads(json.dumps(data)))
    np.testing.assert_array_equal(restored.predict(x),model.predict(x))
    assert [restored.leaf_id(row) for row in x]==model.apply(x).tolist()
    np.testing.assert_array_equal(model.tree_.value,state)
    with pytest.raises(ValueError,match='schema width'):export_tree(model,['L'],['gamma','red','blue'],{})

def test_classifier_is_not_exported_as_correction_parameters():
    model=DecisionTreeClassifier(random_state=42).fit([[0],[1]],[0,1])
    with pytest.raises(ValueError,match='regression tree'):export_tree(model,['L'],['gamma'],{})
