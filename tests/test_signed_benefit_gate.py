import numpy as np
import pytest
from src.model_training.signed_benefit_gate import fit_signed_benefit,signed_benefit_decision

def test_weighted_ridge_equation_and_key_class_masses():
    x=np.array([[0.,7.],[1.,7.],[2.,7.],[3.,7.],[4.,7.],[5.,7.]])
    y=np.array([-1.,2.,4.,-2.,1.,5.]);keys=['a','a','a','b','b','b'];p=fit_signed_benefit(x,y,keys);w=np.array(p['weights']);z=(x-p['mean'])/p['scale'];b=np.array(p['coefficient'])
    assert p['scale'][1]==1 and p['coefficient'][1]==0
    np.testing.assert_allclose((z.T@(w[:,None]*z)+np.eye(2))@b,z.T@(w*(y-p['intercept'])),atol=1e-12)
    for k in ['a','b']:
        for label in [False,True]:assert np.isclose(sum(w[i] for i in range(6) if keys[i]==k and (y[i]>0)==label),1.5)

def test_signed_magnitude_changes_prediction_with_same_binary_labels():
    x=[[0.],[1.],[2.],[3.]];keys=['a']*4
    a=fit_signed_benefit(x,[-1.,-1.,1.,1.],keys);b=fit_signed_benefit(x,[-1.,-1.,20.,20.],keys)
    assert signed_benefit_decision(a,[2.])['predicted_rgb_mae_gain']!=signed_benefit_decision(b,[2.])['predicted_rgb_mae_gain']
    zero=dict(mean=[0.],scale=[1.],coefficient=[0.],intercept=0.)
    assert not signed_benefit_decision(zero,[1.])['apply_correction']

def test_invalid_features_and_missing_sign_class_rejected():
    with pytest.raises(ValueError):fit_signed_benefit([[0.],[1.]],[1.,2.],['a','a'])
    with pytest.raises(ValueError):fit_signed_benefit([[0.],[float('nan')]],[-1.,2.],['a','a'])
    with pytest.raises(ValueError):signed_benefit_decision(dict(mean=[0.],scale=[1.],coefficient=[1.],intercept=0.),[1.,2.])
