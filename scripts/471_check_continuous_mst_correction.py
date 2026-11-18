"""Generated continuous-score interface and portable-control replay, no real data."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from src.correction.continuous_mst_candidate import continuous_model_features, CONTINUOUS_FEATURES, VERSION
from src.ita_estimation.contextual_mst_experiment import predict, FEATURES
from src.model_training.target_scaled_tree import fit_target_scaled_tree
from src.model_training.portable_tree import PortableTree

OUT = ROOT/'outputs/continuous_mst_correction_generated_v1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    paths = ['src/correction/continuous_mst_candidate.py', 'tests/test_continuous_mst_candidate.py',
        'scripts/471_check_continuous_mst_correction.py', 'src/ita_estimation/mst_lookup.py',
        'src/ita_estimation/threshold_calibration.py', 'src/ita_estimation/contextual_mst_experiment.py',
        'src/model_training/target_scaled_tree.py', 'src/model_training/portable_tree.py',
        'docs/continuous-mst-correction-protocol-2026-11-06.md']
    bindings = {p: sha(ROOT/p) for p in paths}
    # Explicit arithmetic coefficients, not a fitted or validated MST estimator.
    model = dict(features=list(FEATURES), mean=[0.]*4, scale=[1.]*4,
                 coefficient=[.1, 0., 0., 0.], intercept=4.37)
    rows = []
    for i in range(12):
        features = dict(zip(FEATURES, [-80.+15*i, 30.+4*i, 5.+i, 12.]))
        prediction = predict(model, features)
        full = continuous_model_features(features, prediction, measurement_contract_sha256='a'*64,
            estimator_measurement_contract_sha256='a'*64)
        rows.append(dict(case_id=f'fictional_{i}', input_features=features, prediction=prediction,
            features=full, targets=[.8+.04*i, 1.+.01*i, 1.2-.02*i]))
    train, held = rows[:8], rows[8:]
    x = lambda rr: [[r['features'][f] for f in CONTINUOUS_FEATURES] for r in rr]
    payload, fitted, meta = fit_target_scaled_tree(x(train), [r['targets'] for r in train],
        CONTINUOUS_FEATURES, dict(fixture_only=True, version=VERSION))
    tree = PortableTree(json.loads(json.dumps(payload)))
    expected = fitted.predict(x(rows))*meta['applied_scale']+meta['fitting_target_mean']
    np.testing.assert_allclose(tree.predict(x(rows)), expected, atol=1e-12, rtol=0)
    assert tree.feature_names == CONTINUOUS_FEATURES and 'input_mst_index' not in tree.feature_names
    assert any(1 < r['prediction']['score'] < 10 and not r['prediction']['score'].is_integer() for r in rows)
    assert any(r['prediction']['raw'] < 1 for r in rows) and any(r['prediction']['raw'] > 10 for r in rows)
    summary = dict(fixture_only=True, arithmetic_rows=12, fitting_rows=8, held_arithmetic_rows=4,
        generated_correction_tree_fits=1, generated_mst_fits=0, portable_control_replays=12,
        explicit_clipping_and_fraction_preservation=True, feature_names=list(CONTINUOUS_FEATURES),
        real_images=0, real_mst_fits=0, photographic_tree_fits=0, admissions=0,
        limitation='Interface and tree replay only; no person-held, nested calibration, renderer or accuracy evidence.')
    assert all(sha(ROOT/p)==h for p,h in bindings.items())
    OUT.mkdir(parents=True)
    for name, value in [('fixtures.json', rows), ('tree.json', payload), ('normalization.json', meta),
        ('verification.json', summary), ('input_sha256.json', bindings)]:
        (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()}, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
