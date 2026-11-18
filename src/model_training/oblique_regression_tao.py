"""Bounded single-tree regression TAO-inspired engineering implementation.

Own L2 branch surrogate + canonical raw-SSE safeguards, not author-code parity.
No real-data access or initialization fitting; caller provides one initial tree.
"""
from collections import Counter, deque
from copy import deepcopy
import math
import time

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

from src.model_training.portable_oblique_tree import PortableObliqueTree, score, float32


def fold_scaling(weights, intercept, mean, scale):
    w = np.asarray(weights, float)/np.asarray(scale, float)
    b = math.fsum([float(intercept)] + [-float(a)*float(m) for a, m in zip(w, mean)])
    if not np.isfinite(w).all() or not math.isfinite(b):
        raise ValueError('Nonfinite folded coefficients')
    return w.tolist(), b


def logistic_objective(theta, x, labels, weights, l2=.01):
    z = x @ theta[:-1]+theta[-1]
    value = float(np.sum(weights*(np.logaddexp(0., z)-labels*z)) + .5*l2*np.dot(theta[:-1], theta[:-1]))
    residual = weights*(expit(z)-labels)
    gradient = np.r_[x.T @ residual+l2*theta[:-1], residual.sum()]
    return value, gradient


def raw_sse(model, x, y):
    tree = PortableObliqueTree(model)
    try:
        value = math.fsum((float(v)-float(t))**2 for row, target in zip(x, y)
                         for v, t in zip(tree.predict_one(row), target))
    except (OverflowError, ValueError) as exc:
        raise ValueError('Nonfinite fitting SSE') from exc
    if not math.isfinite(value):
        raise ValueError('Nonfinite fitting SSE')
    return value


def leaf_members(model, x):
    tree = PortableObliqueTree(model)
    result = {}
    for i, row in enumerate(x):
        result.setdefault(tree.leaf_id(row), []).append(i)
    return result


def refresh_leaves(model, x, y):
    candidate = deepcopy(model)
    for leaf, indices in leaf_members(model, x).items():
        candidate['nodes'][leaf]['values'] = [math.fsum(float(y[i, j]) for i in indices)/len(indices)
                                             for j in range(3)]
    # Empty leaves intentionally retain their existing positive values.
    return candidate


def guarded_update(model, node_index, weights, intercept, x, y, tolerance):
    """Return current model on every invalid, empty-child or worse proposal."""
    candidate = deepcopy(model)
    node = candidate['nodes'][node_index]
    if node['kind'] != 'split':
        raise ValueError('Branch required')
    node['weights'] = list(weights);node['intercept'] = intercept
    try:
        PortableObliqueTree(candidate)
        reduced = reduced_rows(model, node_index, x)
        outcomes = [score(node, row) > 0 for row in x[reduced]]
        if not outcomes or all(outcomes) or not any(outcomes):
            return model, 'empty_child', None
        before, after = raw_sse(model, x, y), raw_sse(candidate, x, y)
    except (ValueError, OverflowError):
        return model, 'nonfinite_or_invalid', None
    if after < before-tolerance:
        return candidate, 'accepted', after
    return model, 'no_strict_raw_SSE_gain', after


def reduced_rows(model, node_index, x):
    nodes = model['nodes'];result = []
    for row_index, row in enumerate(x):
        i = 0
        while True:
            if i == node_index:
                result.append(row_index);break
            n = nodes[i]
            if n['kind'] == 'leaf':
                break
            i = n['right'] if score(n, row) > 0 else n['left']
    return result


class _TimeCap(Exception):
    pass


def train_oblique(initial, x, y, *, max_passes=20, max_proposals=300,
                  max_seconds=60., clock=time.monotonic):
    """Fit only caller-supplied arrays; no file access, restart or all-data policy."""
    PortableObliqueTree(initial)
    x = np.asarray(x)
    y = np.asarray(y, dtype=float)
    width = len(initial['feature_names'])
    if x.ndim != 2 or not len(x) or x.shape[1] != width or y.shape != (len(x), 3):
        raise ValueError('Nonempty fitting X and exactly three targets required')
    try:
        x = np.array([[float32(v) for v in row] for row in x], dtype=float)
    except (ValueError, OverflowError, TypeError) as exc:
        raise ValueError('Invalid fitting input') from exc
    if not np.isfinite(y).all() or np.min(y) <= 0:
        raise ValueError('Finite positive targets required')
    if (type(max_passes) is not int or not 0 <= max_passes <= 20 or
        type(max_proposals) is not int or not 0 <= max_proposals <= 300 or
        not math.isfinite(max_seconds) or not 0 <= max_seconds <= 60):
        raise ValueError('Budget must stay within frozen caps')
    started = clock()
    def check_time():
        if clock()-started >= max_seconds:
            raise _TimeCap()
    current = deepcopy(initial)
    mean = x.mean(axis=0);scale = x.std(axis=0)
    scale[scale == 0] = 1.
    normalized = (x-mean)/scale
    initial_sse = raw_sse(current, x, y)
    tolerance = 1e-12*max(1., initial_sse)
    history = [dict(event='initial', SSE=initial_sse)]
    attempts = 0;passes = 0;reasons = Counter();solver_status = []
    order = [];q = deque([0])
    while q:
        i = q.popleft();n = current['nodes'][i]
        if n['kind'] == 'split':
            order.append(i);q.extend([n['left'], n['right']])
    status = 'pass_cap'
    try:
        for iteration in range(max_passes):
            check_time();start_sse = raw_sse(current, x, y)
            for i in order:
                check_time()
                if attempts >= max_proposals:
                    status = 'proposal_cap';raise StopIteration()
                n = current['nodes'][i]
                ids = reduced_rows(current, i, x)
                if not ids:
                    reasons['empty_reduced_set'] += 1;continue
                tree = PortableObliqueTree(current)
                left = np.array([tree.predict_one(x[k], n['left']) for k in ids])
                right = np.array([tree.predict_one(x[k], n['right']) for k in ids])
                left_loss = ((left-y[ids])**2).sum(axis=1)
                right_loss = ((right-y[ids])**2).sum(axis=1)
                weights = np.abs(left_loss-right_loss)
                active = weights > 0
                labels = (right_loss < left_loss).astype(float)
                if not active.any():
                    reasons['zero_routing_loss_weights'] += 1;continue
                if len(set(labels[active])) < 2:
                    reasons['single_routing_label'] += 1;continue
                ids = np.asarray(ids)[active];weights = weights[active];weights /= weights.sum()
                labels = labels[active]
                raw_w = np.asarray(n['weights'])
                theta0 = np.r_[raw_w*scale, math.fsum([n['intercept']]+list(raw_w*mean))]
                attempts += 1
                def objective(theta):
                    check_time()
                    return logistic_objective(theta, normalized[ids], labels, weights)
                result = minimize(objective, theta0, method='L-BFGS-B', jac=True,
                    options=dict(maxiter=100, maxfun=1000, maxls=20, ftol=1e-10,
                                 gtol=1e-8, maxcor=10))
                solver_status.append(dict(node=i, pass_index=iteration,
                    success=bool(result.success), status=int(result.status),
                    iterations=int(result.nit), function_evaluations=int(result.nfev)))
                check_time()
                if not result.success:
                    reasons['solver_unsuccessful'] += 1;continue
                try:
                    w, b = fold_scaling(result.x[:-1], result.x[-1], mean, scale)
                    updated, reason, proposed_sse = guarded_update(current, i, w, b, x, y, tolerance)
                except (ValueError, OverflowError):
                    reasons['nonfinite_or_invalid'] += 1;continue
                reasons[reason] += 1
                if reason == 'accepted':
                    current = updated;history.append(dict(event='branch', node=i, SSE=proposed_sse))
            check_time()
            updated = refresh_leaves(current, x, y)
            before, after = raw_sse(current, x, y), raw_sse(updated, x, y)
            if after <= before:
                current = updated;history.append(dict(event='leaf_means', SSE=after))
            else:
                reasons['leaf_rounding_increase_rejected'] += 1
            passes += 1
            if start_sse-raw_sse(current, x, y) <= tolerance:
                status = 'no_strict_gain';break
    except _TimeCap:
        status = 'time_cap'
    except StopIteration:
        pass
    final_sse = raw_sse(current, x, y)
    assert final_sse <= initial_sse and all(b['SSE'] <= a['SSE'] for a, b in zip(history, history[1:]))
    current['provenance'] = dict(current.get('provenance') or {},
        trainer='truehue_regression_TAO_inspired_L2_v1',
        normalization_folded_into_branches=True, correction_runtime_adopted=False)
    return current, dict(status=status, completed_passes=passes, solver_attempts=attempts,
        reasons=dict(reasons), solver_status=solver_status, initial_SSE=initial_sse,
        final_SSE=final_sse, SSE_history=history, fitting_mean=mean.tolist(),
        fitting_scale=scale.tolist(), elapsed_seconds=clock()-started,
        global_optimality_claim=False, cap_seconds=max_seconds,
        cap_passes=max_passes, cap_proposals=max_proposals)
