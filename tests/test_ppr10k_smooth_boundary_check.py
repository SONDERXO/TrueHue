import importlib.util
from pathlib import Path

import numpy as np

spec=importlib.util.spec_from_file_location('smooth',Path(__file__).resolve().parents[1]/'scripts/398_ppr10k_smooth_boundary_check.py')
candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)


def test_fixed_curve_is_monotone_symmetric_and_bounded():
    x=np.linspace(-.4,1.4,2001);y=candidate.soft_boundary(x)
    assert np.isfinite(y).all() and (y>=0).all() and (y<=1).all()
    assert (np.diff(y)>0).all()
    np.testing.assert_allclose(y+candidate.soft_boundary(1-x),1,atol=3e-16,rtol=0)
    assert candidate.soft_boundary(np.array([.5]))[0]==.5


def test_smooth_boundary_retains_some_variation_hard_clip_loses():
    raw=np.array([1.005,1.015])
    assert np.clip(raw,0,1)[0]==np.clip(raw,0,1)[1]
    soft=candidate.soft_boundary(raw)
    assert soft[0]<soft[1]<1
    assert np.rint(soft[0]*255)!=np.rint(soft[1]*255)


def test_flat_input_does_not_gain_detail():
    output=candidate.soft_boundary(np.full((5,5,3),1.02))
    assert np.unique(output).size==1
