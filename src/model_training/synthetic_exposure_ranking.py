"""Explicit synthetic-restoration pairs; no JOD, image, or encoder API."""
import hashlib
import math
from collections import Counter
import numpy as np
from .exposure_quality_training import SETTINGS, batch_objective, adam_update
from .portrait_exposure_quality import fit_scaler

ROLES = ('identity', 'colour_only', 'exposure_under', 'exposure_over',
         'combined_under', 'combined_over')
PREFERENCES = (('identity', 'exposure_under'), ('identity', 'exposure_over'),
               ('colour_only', 'combined_under'), ('colour_only', 'combined_over'))
SCHEMA = 'truehue_synthetic_exposure_rank_diagnostic_v1'


def metadata(rows, generated_fixture):
    if not isinstance(generated_fixture, bool) or not rows:
        raise ValueError('Explicit provenance and nonempty roster required')
    result = []
    seen = set()
    groups = {}
    for row in rows:
        r = {k: row[k] for k in ('case_id', 'source_id', 'role', 'generated_fixture')}
        if (not isinstance(r['case_id'], str) or not isinstance(r['source_id'], str)
                or r['role'] not in ROLES or r['case_id'] in seen
                or r['generated_fixture'] is not generated_fixture):
            raise ValueError('Invalid ID/role/provenance or duplicate record')
        seen.add(r['case_id'])
        by_role = groups.setdefault(r['source_id'], {})
        if r['role'] in by_role:
            raise ValueError('Duplicate source role')
        by_role[r['role']] = r['case_id']
        result.append(r)
    if any(set(g) != set(ROLES) for g in groups.values()):
        raise ValueError('Each source must have all six roles')
    return sorted(result, key=lambda r: r['case_id'])


def fitting_records(rows, held_source, generated_fixture):
    rows = metadata(rows, generated_fixture)
    sources = {r['source_id'] for r in rows}
    if held_source not in sources or len(sources) < 2:
        raise ValueError('Declared held source and fitting sources required')
    return [r | {'partition': 'Train'} for r in rows if r['source_id'] != held_source]


def pair_ids(records):
    groups = {}
    for r in records:
        groups.setdefault(r['source_id'], {})[r['role']] = r['case_id']
    return sorted((g[a], g[b]) for g in groups.values() for a, b in PREFERENCES)


def prepare(records, provider, held_source, generated_fixture, explicit_pairs=None):
    # Validate exclusion BEFORE consulting the feature provider.
    if any(r['source_id'] == held_source or r.get('partition') != 'Train' for r in records):
        raise ValueError('Held/Test record cannot enter fitting')
    rows = metadata(records, generated_fixture)
    expected = pair_ids(rows)
    pairs_ids = expected if explicit_pairs is None else [tuple(p) for p in explicit_pairs]
    if sorted(pairs_ids) != expected or len(set(pairs_ids)) != len(expected):
        raise ValueError('Exactly the four declared within-source preferences required')
    pairs_ids = sorted(pairs_ids)
    raw = []
    for r in rows:
        v = np.asarray(provider(r['case_id']))
        if v.shape != (4096,) or v.dtype != np.float32 or not np.isfinite(v).all():
            raise ValueError('Finite 4096 float32 cached vector required')
        raw.append(v.copy())
    x = np.asarray(raw, dtype=np.float64)
    means, scales = fit_scaler(x, range(len(x)))
    z = (x - means) / scales
    if not np.isfinite(z).all():
        raise ValueError('Nonfinite standardized features')
    index = {r['case_id']: i for i, r in enumerate(rows)}
    pairs = np.asarray([(index[a], index[b]) for a, b in pairs_ids], dtype=np.int64)
    counts = Counter(rows[a]['source_id'] for a, _ in pairs)
    weights = np.asarray([1 / (len(counts) * counts[rows[a]['source_id']])
                          for a, _ in pairs], dtype=np.float64)
    return dict(rows=rows, x=x, z=z, mean=means, scale=scales, pairs=pairs,
                pair_ids=pairs_ids, pair_weights=weights, source_pair_counts=dict(counts))


def fit(records, provider, held_source, generated_fixture, observer=None):
    data = prepare(records, provider, held_source, generated_fixture)
    rng = np.random.default_rng(SETTINGS['seed'])
    w = np.zeros(4096); m = w.copy(); v = w.copy()
    traces = []; ws = []; ms = []; vs = []; step = 0
    for epoch in range(SETTINGS['epochs']):
        order = rng.permutation(len(data['pairs']))
        for start in range(0, len(order), SETTINGS['batch_size']):
            ids = order[start:start + SETTINGS['batch_size']]
            loss, g = batch_objective(w, data['z'], data['pairs'], data['pair_weights'], ids)
            step += 1
            w, m, v = adam_update(w, m, v, g, step)
            if not all(np.isfinite(a).all() for a in (w, m, v)) or not math.isfinite(loss):
                raise ValueError('Nonfinite optimizer state')
            ws.append(w.copy()); ms.append(m.copy()); vs.append(v.copy())
            traces.append(dict(step=step, epoch=epoch, loss=loss,
                               batch_indices=ids.tolist(), batch_size=len(ids)))
            if observer is not None:
                observer(step, w.copy(), m.copy(), v.copy())
    expected_steps = SETTINGS['epochs'] * math.ceil(len(data['pairs']) / SETTINGS['batch_size'])
    assert step == expected_steps
    head = dict(schema=SCHEMA, generated_fixture=generated_fixture,
                scientific_status='SYNTHETIC_RANK_DIAGNOSTIC_NOT_ADOPTED',
                held_source=held_source, settings=dict(SETTINGS), bias=0.,
                training_ids=[r['case_id'] for r in data['rows']],
                training_sources=sorted(data['source_pair_counts']),
                explicit_pair_ids=data['pair_ids'],
                source_pair_counts=data['source_pair_counts'],
                mean=data['mean'].tolist(), scale=data['scale'].tolist(),
                weights=w.tolist(), optimizer_updates=step,
                immutable_input_sha256=hashlib.sha256(data['x'].tobytes()).hexdigest())
    return head, traces, dict(weights=np.stack(ws), first_moment=np.stack(ms),
                              second_moment=np.stack(vs))


def score(head, vector):
    if head['schema'] != SCHEMA or head['bias'] != 0.:
        raise ValueError('Wrong synthetic ranking schema')
    arrays = [np.asarray(head[k], dtype=np.float64) for k in ('weights', 'mean', 'scale')]
    x = np.asarray(vector, dtype=np.float64)
    if any(a.shape != (4096,) or not np.isfinite(a).all() for a in arrays + [x]):
        raise ValueError('Finite full-width scoring input/state required')
    w, mean, scale = arrays
    if np.any(scale <= 0):
        raise ValueError('Positive scales required')
    return float(w @ ((x - mean) / scale))
