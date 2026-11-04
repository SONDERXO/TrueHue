import numpy as np
import pytest
from src.model_training.target_scaled_tree import fit_target_scaled_tree
from src.model_training.portable_tree import PortableTree


def test_constant_axes_and_raw_parameter_export():
    payload,model,meta=fit_target_scaled_tree([[0],[1]],[[1,1,1],[2,1,1]],['x'])
    tree=PortableTree(payload)
    assert meta['applied_scale']==[.5,1.,1.] and meta['constant_axes']==[False,True,True]
    assert tree.predict_one([0])==[1.,1.,1.] and tree.predict_one([1])==[2.,1.,1.]
    inverse=model.predict([[0],[1]])*meta['applied_scale']+meta['fitting_target_mean']
    np.testing.assert_allclose(tree.predict([[0],[1]]),inverse,atol=1e-12,rtol=0)


def test_duplicate_feature_rows_export_raw_target_mean():
    y=np.array([[1.,1.,1.],[3.,1.2,.8]])
    payload,_,meta=fit_target_scaled_tree([[0],[0]],y,['x'])
    np.testing.assert_allclose(PortableTree(payload).predict_one([0]),[2,1.1,.9])
    assert meta['fitting_rows']==2


def test_statistics_use_only_supplied_fitting_targets():
    payload,_,meta=fit_target_scaled_tree([[0],[1]],[[1,1,1],[2,1.2,.8]],['x'])
    before=meta.copy();PortableTree(payload).predict([[999],[-999]])
    assert meta==before and meta['fitting_target_mean']==[1.5,1.1,.9]


def test_invalid_targets_and_schema_are_rejected():
    with pytest.raises(ValueError):fit_target_scaled_tree([[0],[1]],[[1,1,1],[0,1,1]],['x'])
    with pytest.raises(ValueError):fit_target_scaled_tree([[0,1],[1,2]],[[1,1,1],[2,1,1]],['x','x'])
