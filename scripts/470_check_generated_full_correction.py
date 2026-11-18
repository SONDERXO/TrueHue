"""Fictional full-schema correction-tree check; no photograph or MST estimation."""
import hashlib
import json
import math
from numbers import Real
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.target_scaled_tree import fit_target_scaled_tree
from src.model_training.portable_tree import PortableTree
from src.model_training.development_build import SETTINGS

OUT = ROOT / 'outputs/generated_full_correction_v1'


def vector(features):
    if not isinstance(features, dict) or set(features) != set(MST_FEATURES):
        raise ValueError('Exact full feature schema required')
    values = [features[k] for k in MST_FEATURES]
    if any(isinstance(v, bool) or not isinstance(v, Real) or not math.isfinite(v) for v in values):
        raise ValueError('Finite numeric features required; no unavailable MST fallback')
    mst = features['input_mst_index']
    if not isinstance(mst, int) or not 0 <= mst <= 9:
        raise ValueError('Fictional integer MST index required')
    return values


def fit_fold(rows, held):
    ids = [r['case_id'] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate case')
    sources = {}
    for r in rows:
        vector(r['features'])
        if sources.setdefault(r['source_id'], r['group_id']) != r['group_id']:
            raise ValueError('Source descendants cross groups')
    train = [r for r in rows if r['group_id'] != held]
    test = [r for r in rows if r['group_id'] == held]
    if not train or not test:
        raise ValueError('Nonempty fitting and held groups required')
    payload, model, meta = fit_target_scaled_tree(
        [vector(r['features']) for r in train], [r['targets'] for r in train], MST_FEATURES,
        dict(fixture_only=True, held_group=held))
    return payload, model, meta, train, test


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    paths = ['src/ita_estimation/mst_lookup.py', 'src/ita_estimation/threshold_calibration.py',
             'src/model_training/target_scaled_tree.py', 'src/model_training/portable_tree.py',
             'src/model_training/development_build.py', 'scripts/470_check_generated_full_correction.py',
             'docs/controlled-correction-experiment-plan-2026-11-06.md']
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    bindings = {p: sha(ROOT / p) for p in paths}
    rows = []
    for group in range(6):
        for variant in range(3):
            rows.append(dict(case_id=f'fictional_{group}_{variant}', source_id=f'fictional_source_{group}',
                group_id=f'fictional_group_{group}', features=dict(zip(MST_FEATURES,
                [25. + 7*group + variant, 2. + group, 8. + variant, -30. + 12*group, group])),
                targets=[.8 + .08*group + .03*variant, 1. + .02*variant, .9 + .03*group]))
    original = json.dumps(rows, sort_keys=True)
    folds = []
    replays = 0
    for held in sorted({r['group_id'] for r in rows}):
        payload, model, meta, train, test = fit_fold(rows, held)
        assert held not in {r['group_id'] for r in train}
        y = np.array([r['targets'] for r in train])
        np.testing.assert_allclose(meta['fitting_target_mean'], y.mean(axis=0), rtol=0, atol=1e-15)
        np.testing.assert_allclose(meta['fitting_population_std'], y.std(axis=0), rtol=0, atol=1e-15)
        # Held target changes must not alter normalization, splits or exported leaves.
        changed = json.loads(original)
        for r in changed:
            if r['group_id'] == held:
                r['targets'] = [100., 200., 300.]
        other, _, other_meta, _, _ = fit_fold(changed, held)
        assert other == payload and other_meta == meta
        tree = PortableTree(json.loads(json.dumps(payload)))
        x = [vector(r['features']) for r in rows]
        expected = model.predict(x)*meta['applied_scale'] + meta['fitting_target_mean']
        np.testing.assert_allclose(tree.predict(x), expected, rtol=0, atol=1e-12)
        for r in rows:
            assert tree.predict_one(dict(reversed(list(r['features'].items())))) == tree.predict_one(vector(r['features']))
        replays += len(rows)
        folds.append(dict(held_group=held, fitting_cases=[r['case_id'] for r in train],
            evaluation_cases=[r['case_id'] for r in test], model=payload, normalization=meta,
            predictions=[dict(case_id=r['case_id'], controls=tree.predict_one(r['features'])) for r in test]))
    bad = []
    for value in [None, '', float('nan'), True, -1, 10, 3.5]:
        features = dict(rows[0]['features']); features['input_mst_index'] = value
        bad.append(features)
    missing = dict(rows[0]['features']); missing.pop('input_mst_index'); bad.append(missing)
    extra = dict(rows[0]['features']); extra['reference_mst'] = 4; bad.append(extra)
    rejected = 0
    for features in bad:
        try:
            vector(features)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError('Invalid full-schema input accepted')
    leaking = json.loads(original); leaking[0]['group_id'] = leaking[3]['group_id']
    try:
        fit_fold(leaking, 'fictional_group_2')
    except ValueError:
        pass
    else:
        raise AssertionError('Source leakage accepted')
    assert json.dumps(rows, sort_keys=True) == original
    assert all(sha(ROOT/p) == h for p, h in bindings.items())
    summary = dict(fixture_only=True, fictional_groups=6, rows=18, features=list(MST_FEATURES),
        targets=list(TARGETS), settings=SETTINGS, generated_tree_fits=12,
        outer_folds=6, held_target_mutation_checks=6, normalization_checks=6,
        portable_prediction_replays=replays, named_order_checks=replays,
        invalid_feature_vectors_rejected=rejected, cross_group_source_rejected=True,
        real_images_loaded=0, real_mst_fits=0, photographic_tree_fits=0, admissions=0,
        limitation='Software plumbing only; fictional MST is neither estimated nor validated; no renderer/image-quality check.')
    OUT.mkdir(parents=True)
    for name, value in [('fixtures.json', rows), ('folds.json', folds), ('verification.json', summary), ('input_sha256.json', bindings)]:
        (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name: sha(p) for p in OUT.iterdir()}, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
