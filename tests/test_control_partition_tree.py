import numpy as np
import pytest
from src.model_training.control_partition_tree import fit_control_partition_tree
from src.model_training.portable_tree import PortableTree


def test_separate_labels_and_average_distortion_parameters():
    x=[[0],[0],[2],[2]];y=[[1,1,1],[1,1,1],[2,1.1,.9],[3,1.3,.7]]
    payload,model,audit=fit_control_partition_tree(x,y,np.array([True,True,False,False]),['x'])
    tree=PortableTree(payload)
    assert tree.predict_one([0])==[1.,1.,1.]
    np.testing.assert_allclose(tree.predict_one([2]),[2.5,1.2,.8])
    assert tree.leaf_id([2])==int(model.apply([[2]])[0])


def test_indistinguishable_clean_and_distorted_fit_rows_preserve_control():
    payload,_,audit=fit_control_partition_tree([[0],[0]],[[1,1,1],[2,1,1]],np.array([True,False]),['x'])
    assert PortableTree(payload).predict_one([0])==[1.,1.,1.]
    assert audit[0]['identity_members']==1


def test_nonidentity_control_target_rejected():
    with pytest.raises(ValueError,match='identity targets'):
        fit_control_partition_tree([[0],[1]],[[1.1,1,1],[2,1,1]],np.array([True,False]),['x'])


def test_control_flags_must_be_explicit_and_classes_supported():
    with pytest.raises(ValueError,match='boolean'):
        fit_control_partition_tree([[0],[1]],[[1,1,1],[2,1,1]],[1,0],['x'])
    with pytest.raises(ValueError,match='Both'):
        fit_control_partition_tree([[0],[1]],[[1,1,1],[1,1,1]],np.array([True,True]),['x'])
