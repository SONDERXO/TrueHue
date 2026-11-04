import numpy as np
import pytest

from src.skin_masking.material_boundary_guard import guard_material_boundary


def test_fixed_margin_removes_only_local_neighbors_of_material_outliers():
    base=np.ones((15,15),bool);chroma=base.copy();chroma[7,7]=False
    result,outliers=guard_material_boundary(base,chroma)
    assert outliers.sum()==1
    assert not result[7,5:10].any()
    assert result[7,4] and result[7,10] and result[5,5]
    assert not (result & ~chroma).any()


def test_no_outliers_preserves_support_and_invalid_superset_fails():
    base=np.ones((8,8),bool);result,outliers=guard_material_boundary(base,base)
    np.testing.assert_array_equal(result,base);assert not outliers.any()
    base[0,0]=False
    with pytest.raises(ValueError,match='subset'):guard_material_boundary(base,np.ones_like(base))
