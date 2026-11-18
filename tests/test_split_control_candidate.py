from copy import deepcopy
import numpy as np
import pytest
from src.model_training.split_control_candidate import fit_split_predictors,predict_split


def test_head_objectives_do_not_depend_on_other_head_targets():
    x=np.arange(16).reshape(-1,1);y=np.array([[1+.1*(i%2),.8+.03*i,1.2-.02*i] for i in range(16)])
    a,_=fit_split_predictors(x,y,['x']);changed=y.copy();changed[:,1:]*=2
    b,_=fit_split_predictors(x,changed,['x']);assert a['heads']['gamma']==b['heads']['gamma']
    changed=y.copy();changed[:,0]*=2;c,_=fit_split_predictors(x,changed,['x']);assert a['heads']['gains']==c['heads']['gains']


def test_raw_leaf_order_and_duplicate_input_means():
    p,_=fit_split_predictors([[0],[0]],[[1,.8,1.2],[3,1.2,.8]],['x'])
    np.testing.assert_allclose(predict_split(p,[0]),[2,1,1])
    assert p['heads']['gamma']['tree']['target_names']==['target_gamma']
    assert p['heads']['gains']['tree']['target_names']==['target_red_gain','target_blue_gain']


def test_constant_axes_and_schema_mismatch():
    p,_=fit_split_predictors([[0],[1]],[[1,1,1],[1,1,1]],['x'])
    assert predict_split(p,[999])==[1,1,1]
    bad=deepcopy(p);bad['heads']['gains']['tree']['target_names'].reverse()
    with pytest.raises(ValueError):predict_split(bad,[0])
    with pytest.raises(ValueError):fit_split_predictors([[0]],[[0,1,1]],['x'])
