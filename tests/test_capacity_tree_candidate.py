import numpy as np
from src.model_training.capacity_tree_candidate import fit_capacity_tree
from src.model_training.portable_tree import PortableTree
from src.model_training.development_build import SETTINGS


def test_can_fit_more_than_eight_distinct_target_regions_without_changing_default():
    x=np.arange(20).reshape(-1,1);y=np.array([[1.+.1*(i%2),1.+.02*i,1.] for i in range(20)])
    payload,model,meta=fit_capacity_tree(x,y,['x'])
    np.testing.assert_allclose(PortableTree(payload).predict(x),y,atol=1e-12,rtol=0)
    assert model.get_n_leaves()>8 and model.get_params()['max_depth'] is None
    assert SETTINGS['max_depth']==3 and meta['constant_axes'][2]


def test_exact_duplicate_vectors_retain_mean_instead_of_claiming_perfect_fit():
    p,_,_=fit_capacity_tree([[0],[0]],[[1,1,1],[3,1.2,.8]],['x'])
    np.testing.assert_allclose(PortableTree(p).predict_one([0]),[2,1.1,.9])
