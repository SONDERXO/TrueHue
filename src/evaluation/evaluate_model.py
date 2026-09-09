"""
Model evaluation helpers.

Computes MAE, CIEDE2000 ΔE, and timing metrics.
"""

from __future__ import annotations

import time
from typing import Callable, Dict

import numpy as np


def measure_inference_time(fn: Callable, *args, n_runs: int = 50, **kwargs) -> float:
    """Return average wall-clock time (ms) for *fn* over *n_runs*."""
    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        times.append((time.perf_counter() - t0) * 1000)
    return float(np.mean(times))


def compute_mae(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Element-wise mean absolute error."""
    return np.mean(np.abs(y_true - y_pred), axis=0)
