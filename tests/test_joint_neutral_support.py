import numpy as np
from src.model_training.joint_neutral_support import prepare_policy, predict_policy


def model():
    def tree(targets, left, right):
        return dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',
            threshold_dtype='float64',comparison='<=',root=0,feature_names=['x','y'],
            target_names=targets,nodes=[dict(kind='split',feature=0,threshold=0,left=1,right=2),
                dict(kind='leaf',values=left),dict(kind='leaf',values=right)])
    return dict(feature_names=['x','y'],heads={
        'gamma':dict(tree=tree(['gamma'],[1.4],[.7])),
        'gains':dict(tree=tree(['red','blue'],[1.2,.8],[.9,1.1]))})


def test_clean_leaf_anchors_all_controls_but_other_leaf_keeps_values():
    m=model();p=prepare_policy(m,[[-2,0],[-1,1],[1,0],[2,1]],[True,False,False,False])
    assert predict_policy(m,p,[-1,1])['parameters']==[1,1,1]
    assert predict_policy(m,p,[1,0])['parameters']==[.7,.9,1.1]


def test_range_guard_uses_unused_axes_and_inclusive_float32_boundaries():
    m=model();p=prepare_policy(m,[[-2,0],[-1,1],[1,0],[2,1]],[False]*4)
    assert predict_policy(m,p,[2,1])['supported']
    r=predict_policy(m,p,[1,2])
    assert not r['supported'] and r['parameters']==[1,1,1]
    assert r['heads']['gamma']['outside_axes']==[1]
    assert predict_policy(m,p,[2+1e-8,1])['supported']


def test_one_unsupported_head_neutralizes_both_and_inputs_are_preserved():
    m=model();x=np.array([[-2,0],[-1,1],[1,0],[2,1.]])
    before=x.copy();p=prepare_policy(m,x,[False]*4)
    p['heads']['gains']['2']['maximum'][1]=.5
    r=predict_policy(m,p,[1,1])
    assert r['heads']['gamma']['outside_axes']==[]
    assert r['parameters']==[1,1,1] and not r['supported']
    np.testing.assert_array_equal(x,before)
