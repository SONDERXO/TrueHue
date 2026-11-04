"""
Model training (decision-tree regression).

Trains a scikit-learn DecisionTreeRegressor to predict
gamma, red_gain, and blue_gain from caller-supplied image features.
The controlled prototype uses continuous ITA and mean Lab, with no MST label.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
from sklearn.tree import DecisionTreeRegressor


def train(
    X: np.ndarray,
    y: np.ndarray,
    max_depth: int | None = 10,
) -> Tuple[DecisionTreeRegressor, dict]:
    """Train a decision-tree regressor.

    Parameters
    ----------
    X : np.ndarray
        Feature matrix (N, n_features).
    y : np.ndarray
        Target matrix (N, 3) – [gamma, red_gain, blue_gain].
    max_depth : int or None
        Maximum tree depth.

    Returns
    -------
    model : DecisionTreeRegressor
    metrics : dict
        Training MAE per target.
    """
    model = DecisionTreeRegressor(max_depth=max_depth, random_state=42)
    model.fit(X, y)

    preds = model.predict(X)
    mae = np.mean(np.abs(preds - y), axis=0)
    metrics = {"mae_gamma": mae[0], "mae_red": mae[1], "mae_blue": mae[2]}
    return model, metrics


def save_model(model: DecisionTreeRegressor, path: str) -> None:
    """Persist a trained model to disk with joblib."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path: str) -> DecisionTreeRegressor:
    """Load a previously saved model."""
    return joblib.load(path)
