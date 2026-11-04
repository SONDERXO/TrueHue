from copy import deepcopy
import pytest
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.model_training.portable_tree import PortableTree


def payload():
    return dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,
        feature_names=['x'],target_names=['gamma','red','blue'],nodes=[dict(kind='split',feature=0,threshold=1.,left=1,right=2),
        dict(kind='leaf',values=[.7,1.,1.1]),dict(kind='leaf',values=[.5,.9,1.2])])


def test_only_fitting_control_leaves_change_and_source_is_immutable():
    original=payload();before=deepcopy(original)
    changed,audit=protect_identity_leaves(original,[[0.],[.5],[2.]],[True,False,False])
    assert changed['nodes'][0]==original['nodes'][0] and changed['nodes'][2]==original['nodes'][2]
    assert PortableTree(changed).predict_one([.8])==[1.,1.,1.]
    assert PortableTree(changed).predict_one([3.])==[.5,.9,1.2]
    assert audit['protected_leaves']==[1] and original==before


def test_no_controls_does_not_invent_an_identity_leaf():
    original=payload();changed,audit=protect_identity_leaves(original,[[0.],[2.]],[False,False])
    assert changed['nodes']==original['nodes'] and audit['protected_leaves']==[]


def test_bad_flags_or_unaligned_rows_rejected():
    with pytest.raises(ValueError):protect_identity_leaves(payload(),[[0.]],[1])
    with pytest.raises(ValueError):protect_identity_leaves(payload(),[[0.]],[])
