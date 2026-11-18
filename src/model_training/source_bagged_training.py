"""Fixed source bootstrap; no fitting or dataset IO on import."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from .gap_training_feasibility import SETTINGS, TARGETS, f32
from .portable_tree import export_tree, PortableTree
from .portable_bagged_tree import SCHEMA, MEMBERS, PortableBaggedTree

ROLES = ('identity', 'exposure_under', 'exposure_over', 'colour_cool')


def source_draws(n, member):
    if type(n) is not int or n < 1 or type(member) is not int or not 0 <= member < MEMBERS:
        raise ValueError('Positive source count and valid member index required')
    result = []
    limit = (2 ** 32 // n) * n
    for draw in range(n):
        attempt = 0
        while True:
            word = f'42:{member}:{draw}:{attempt}'.encode('utf-8')
            value = int.from_bytes(hashlib.sha256(word).digest()[:4], 'big')
            if value < limit:
                result.append(value % n)
                break
            attempt += 1
    return result


def validate_rows(rows, names, excluded):
    if not rows or len(names) != 22 or len(set(names)) != 22:
        raise ValueError('Nonempty 22-input fitting roster required')
    if len({r['case_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate canonical fitting cases')
    sources = list(dict.fromkeys(r['source'] for r in rows))
    if excluded in sources:
        raise ValueError('Held source in fitting inputs')
    for r in rows:
        if len(r['x']) != 22 or any(f32(v) != v for v in r['x']):
            raise ValueError('Exact finite float32 inputs required')
        if len(r['y']) != 3 or any(isinstance(v, bool) or not math.isfinite(v) or v <= 0 for v in r['y']):
            raise ValueError('Positive raw three-control targets required')
    for source in sources:
        if [r['role'] for r in rows if r['source'] == source] != list(ROLES):
            raise ValueError('Each source must retain its four ordered roles')
    return sources


def fit_ensemble(rows, names, excluded, *, factory=DecisionTreeRegressor):
    sources = validate_rows(rows, names, excluded)
    x = np.array([r['x'] for r in rows], dtype=np.float32)
    members, replays = [], []
    start = time.monotonic()
    for member in range(MEMBERS):
        draws = source_draws(len(sources), member)
        indices = [i for s in draws for i, r in enumerate(rows) if r['source'] == sources[s]]
        settings = dict(SETTINGS, random_state=42 + member)
        estimator = factory(**settings)
        estimator.fit(x[indices], np.array([rows[i]['y'] for i in indices], dtype=float))
        tree = export_tree(estimator, names, TARGETS, dict(member=member, generated_or_real='bound_by_run'))
        native = estimator.predict(x).tolist()
        leaves = estimator.apply(x).tolist()
        portable = PortableTree(tree)
        if native != portable.predict(x) or leaves != [portable.leaf_id(r) for r in x.tolist()]:
            raise ValueError('Member export mismatch')
        members.append(tree)
        replays.append(dict(member=member, settings=estimator.get_params(deep=False), source_indices=draws,
                            occurrence_cases=[rows[i]['case_id'] for i in indices],
                            predictions=native, leaves=leaves))
    payload = dict(schema_version=SCHEMA, aggregation='math.fsum_divide_64',
                   feature_names=list(names), target_names=TARGETS, members=members)
    predictions = [[math.fsum(r['predictions'][i][c] for r in replays) / MEMBERS
                    for c in range(3)] for i in range(len(rows))]
    if PortableBaggedTree(json.loads(json.dumps(payload))).predict(x) != predictions:
        raise ValueError('Ensemble serialization/mean mismatch')
    return payload, dict(fit_calls=MEMBERS, canonical_sources=sources, members=replays,
                         mean_predictions=predictions, elapsed_seconds=time.monotonic()-start)


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def run_once(out, rows, names, excluded, receipt):
    out = Path(out)
    out.mkdir()  # Never overwrite successful or failed attempts.
    write(out/'execution_plan_PRIVATE.json', receipt)
    write(out/'fitting_inputs_PRIVATE.json', rows)
    try:
        before = deepcopy(rows)
        candidate, replay = fit_ensemble(rows, names, excluded)
        if before != rows:
            raise ValueError('Fitting inputs changed')
        write(out/'candidate_PRIVATE.json', candidate)
        write(out/'training_replay_PRIVATE.json', replay)
        write(out/'status_PRIVATE.json', dict(status='FITTED_PENDING_VERIFICATION', fit_calls=64))
        return candidate, replay
    except BaseException as error:
        write(out/'status_PRIVATE.json', dict(status='FAILED_PRESERVED_NO_RETRY', error=repr(error)))
        raise
