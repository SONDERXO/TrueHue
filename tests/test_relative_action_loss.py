import numpy as np
import pytest
from src.model_training.relative_action_loss import normalize_fitting_costs


def test_relative_costs_preserve_identity_feasibility_argmins_and_inputs():
    original=np.array([[0.,4.,8.],[20.,2.,30.],[2.,.2,3.]])
    before=original.copy();flags=np.array([True,False,False])
    normalized,scales=normalize_fitting_costs(original,flags)
    np.testing.assert_array_equal(original,before)
    np.testing.assert_array_equal(normalized[0],original[0])
    np.testing.assert_allclose(normalized[1],normalized[2])
    np.testing.assert_array_equal(normalized.argmin(axis=1),original.argmin(axis=1))
    np.testing.assert_array_equal(scales,[1.,20.,2.])


def test_nonidentity_row_units_do_not_change_normalized_costs():
    costs=np.array([[0.,2.,4.],[3.,.1,8.],[100.,2.,150.]])
    flags=np.array([True,False,False]);scaled=costs.copy();scaled[1]*=700;scaled[2]*=.003
    a,_=normalize_fitting_costs(costs,flags);b,_=normalize_fitting_costs(scaled,flags)
    np.testing.assert_allclose(a,b,rtol=1e-14,atol=1e-14)


@pytest.mark.parametrize('costs,flags',[
    ([[0.,1.]], [False]),
    ([[1.,2.]], [True]),
    ([[1.,float('nan')]], [False]),
    ([[1.,-1.]], [False]),
])
def test_invalid_or_zero_baselines_are_not_silently_repaired(costs,flags):
    with pytest.raises(ValueError):normalize_fitting_costs(costs,np.array(flags,bool))
