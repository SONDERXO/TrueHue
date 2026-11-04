"""Operator/solver safeguards for the isolated, unadopted contrast experiment."""
import importlib.util
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from src.distortion_generation.generate_distortions import transform_rgb

spec = importlib.util.spec_from_file_location(
    'contrast_diagnostic', Path(__file__).resolve().parents[1] /
    'scripts/394_ppr10k_contrast_diagnostic.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


def test_neutral_contrast_preserves_existing_operator():
    image = np.random.default_rng(394).uniform(0, 1, (31, 29, 3))
    for parameters in [(1.,1.,1.), (1.7,1.1,1.03), (.8,.9,1.5)]:
        np.testing.assert_allclose(candidate.transform(image,*parameters,1.),
                                   transform_rgb(image,*parameters),atol=3e-16,rtol=0)


def test_contrast_clipping_and_midpoint_with_hand_computed_values():
    image = np.array([[[0.,.5,1.],[.25,.5,.75]]])
    np.testing.assert_array_equal(candidate.transform(image,1.,1.,1.,2.),
        np.array([[[0.,.5,1.],[0.,.5,1.]]]))
    np.testing.assert_array_equal(candidate.transform(image,1.,1.,1.,2.,clip=False),
        np.array([[[-.5,.5,1.5],[0.,.5,1.]]]))


def test_single_start_solver_recovers_known_four_control_target():
    source = np.random.default_rng(395).uniform(.12,.75,(600,1,3))
    truth = [1.4,1.03,.97,1.25]
    target = candidate.transform(source,*truth)
    fit = least_squares(lambda p:(candidate.transform(source,*p)-target).ravel(),
        [1.,1.,1.,1.],bounds=([.25,.25,.25,.5],[4.,4.,4.,2.]),
        xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=2000)
    assert fit.success
    np.testing.assert_allclose(fit.x,truth,atol=1e-7,rtol=0)
