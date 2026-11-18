"""Experimental ranking/probe math only; no image loader or training entry point."""
import math
import numpy as np


def ranking_pairs(rows):
    names = [r['id'] for r in rows]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate image id')
    for r in rows:
        if not all(math.isfinite(float(r[k])) for k in ('low', 'score', 'high')):
            raise ValueError('Nonfinite annotation')
        if not r['low'] <= r['score'] <= r['high']:
            raise ValueError('Invalid score interval')
    pairs = []
    for i, a in enumerate(rows):
        for j in range(i):
            b = rows[j]
            if (a['scene'], a['partition']) != (b['scene'], b['partition']):
                continue
            if a['low'] > b['high']:
                pairs.append((i, j))
            elif b['low'] > a['high']:
                pairs.append((j, i))
    return pairs


def fit_scaler(x, fit_indices):
    x = np.asarray(x, dtype=np.float64)
    ids = list(fit_indices)
    if x.ndim != 2 or not ids or len(set(ids)) != len(ids):
        raise ValueError('Unique nonempty fitting rows required')
    fitting = x[ids]
    if not np.isfinite(fitting).all():
        raise ValueError('Nonfinite fitting features')
    mean, scale = fitting.mean(axis=0), fitting.std(axis=0)
    scale[scale == 0] = 1
    return mean, scale


def rank_objective(weights, differences, pair_weights, regularization=0.001):
    w = np.asarray(weights, dtype=np.float64)
    d = np.asarray(differences, dtype=np.float64)
    a = np.asarray(pair_weights, dtype=np.float64)
    if d.ndim != 2 or w.shape != (d.shape[1],) or a.shape != (len(d),) or not len(d):
        raise ValueError('Nonempty aligned ranking arrays required')
    if not all(np.isfinite(v).all() for v in (w, d, a)) or np.any(a < 0) or a.sum() <= 0:
        raise ValueError('Finite positive total pair weight required')
    if not math.isfinite(regularization) or regularization < 0:
        raise ValueError('Invalid regularization')
    a = a / a.sum()
    margin = d @ w
    loss = a @ np.logaddexp(0, -margin) + regularization / 2 * (w @ w)
    gradient = -(d.T @ (a * np.exp(-np.logaddexp(0, margin)))) + regularization * w
    return float(loss), gradient


def exposure_probe(rgb, ev):
    x = np.asarray(rgb)
    if x.dtype != np.uint8 or x.ndim != 3 or x.shape[-1] != 3:
        raise ValueError('RGB8 image required')
    if ev not in (-0.5, 0.5):
        raise ValueError('Only the two fixed exposure probes are allowed')
    encoded = x.astype(np.float64) / 255
    linear = np.where(encoded <= 0.04045, encoded / 12.92, ((encoded + 0.055) / 1.055) ** 2.4)
    shifted = np.clip(linear * 2 ** ev, 0, 1)
    result = np.where(shifted <= 0.0031308, 12.92 * shifted, 1.055 * shifted ** (1 / 2.4) - 0.055)
    return np.rint(np.clip(result, 0, 1) * 255).astype(np.uint8)
