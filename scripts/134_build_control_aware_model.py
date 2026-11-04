"""Build one reproducible development candidate; never replace the active model."""
import argparse
import csv
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import numpy as np
import sklearn
from sklearn.tree import DecisionTreeRegressor
from src.utilities.config import get_config
from src.data_preparation.controlled_training_table import FEATURES, TARGETS
from src.model_training.development_build import SETTINGS, validate_build_rows, activation_gate
from src.model_training.control_recipe_comparison import plan_control_folds
from src.model_training.train_model import save_model, load_model
from src.model_training.portable_tree import PortableTree, export_tree
from src.evaluation.correction_prototype import model_arrays
from src.correction.correct_image import ESTIMATION_VERSION, LEGACY_POLICY


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(); out = args.output_dir.resolve()
    config = get_config()
    if not out.is_relative_to((ROOT / config.OUTPUTS_ROOT).resolve()):
        raise ValueError('Build outputs must stay under configured outputs root')
    if out.exists():
        raise FileExistsError('Refusing to overwrite a prior build')
    comparison_dir = ROOT / config.OUTPUTS_ROOT / 'core_control_comparison_v1'
    summary_path = comparison_dir / 'summary.json'
    verification_path = comparison_dir / 'verification.json'
    comparison = json.loads(summary_path.read_text())
    verification = json.loads(verification_path.read_text())
    if verification['status'] != 'pass' or digest(summary_path) != verification['summary_sha256']:
        raise ValueError('Prior source-held-out evidence changed or unverified')
    if not all(digest(ROOT / p) == h for p, h in comparison['input_sha256'].items()):
        raise ValueError('Prior comparison inputs changed')
    core_path = ROOT / config.OUTPUTS_ROOT / 'core_pipeline_check_v1/summary.json'
    core = {r['pair_id']: r for r in json.loads(core_path.read_text())['records']}
    table = ROOT / config.DATA_ROOT / 'manifests/controlled_training_v2/train.csv'
    with table.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if row['mask_version'] != ESTIMATION_VERSION or not core[row['pair_id']]['features_match_saved']:
            raise ValueError('Current-core feature/mask provenance mismatch')
        row.update(core[row['pair_id']]['features'])
    eligible, held = comparison['eligible_ids'], comparison['held_ids']
    fitting = validate_build_rows(rows, eligible, held)
    folds = plan_control_folds(rows, eligible, held)
    if folds != comparison['folds']:
        raise ValueError('Saved evaluation folds do not match this fitting recipe')
    evaluated = {r['pair_id']: r for r in comparison['predictions'] if r['method'] == 'with_controls'}
    for row in rows:
        x, y = model_arrays([row]); prior = evaluated[row['pair_id']]
        if x[0].tolist() != prior['features'] or y[0].tolist() != prior['target_parameters']:
            raise ValueError('Evaluation and build feature/target vectors differ')
    gate = activation_gate(comparison['aggregate'])
    tracked = [Path(__file__), table, core_path, summary_path, verification_path,
               ROOT / 'src/model_training/development_build.py', ROOT / 'src/model_training/portable_tree.py',
               ROOT / 'scripts/113_verify_core_tree_portability.py',
               ROOT / 'docs/control-aware-model-build-protocol.md',
               ROOT / config.CORRECTION_PROTOTYPE_MODEL_PATH,
               ROOT / 'android-app/app/src/main/assets/decision_tree.json']
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in tracked}
    out.mkdir(parents=True)
    (out / 'run_status.json').write_text('{"status":"running"}')
    manifest = dict(status='frozen_before_fit', fitting_pair_ids=[r['pair_id'] for r in fitting],
                    held_diagnostic_ids=held, settings=SETTINGS, sample_weight=None,
                    feature_columns=list(FEATURES), target_columns=list(TARGETS),
                    rows=fitting, evaluation_summary_sha256=digest(summary_path),
                    quality_gate=gate, final_dataset_admission=False)
    (out / 'fit_manifest.json').write_text(json.dumps(manifest, indent=2))
    x, y = model_arrays(fitting)
    model = DecisionTreeRegressor(**SETTINGS)
    model.fit(x, y)  # Exactly one full-data development fit; no CV refits/search.
    joblib_path = out / 'decision_tree.joblib'; save_model(model, str(joblib_path))
    reloaded = load_model(str(joblib_path))
    metadata = dict(feature_columns=list(FEATURES), target_columns=list(TARGETS),
        mask_version=ESTIMATION_VERSION, mask_policy=LEGACY_POLICY,
        transform_version='encoded_rgb_gamma_then_gain_v1', settings=SETTINGS,
        fit_pairs=len(fitting), fit_sources=sorted({r['source_image_id'] for r in fitting}),
        in_sample_parameter_mae=np.mean(np.abs(model.predict(x)-y), axis=0).tolist(),
        training_error_is_not_generalization=True, source_model_sha256=digest(joblib_path),
        activation_status=gate['status'], mst_status='unavailable', proposal_complete=False,
        sklearn_version=sklearn.__version__, final_thesis_model=False)
    payload = export_tree(model, FEATURES, TARGETS, dict(source_model_sha256=digest(joblib_path),
        source_metadata=metadata, status='Control-aware development candidate; held from runtime activation'))
    tree_path = out / 'decision_tree.json'; tree_path.write_text(json.dumps(payload, indent=2))
    portable = PortableTree(json.loads(tree_path.read_text()))
    vectors, _ = model_arrays(rows)
    boundaries = importlib.import_module('113_verify_core_tree_portability').boundary_cases(model, x[0])
    checks = vectors.tolist() + [r['features'] for r in boundaries]
    expected = model.predict(checks); leaves = model.apply(checks)
    np.testing.assert_array_equal(reloaded.predict(checks), expected)
    np.testing.assert_array_equal(portable.predict(checks), expected)
    assert [portable.leaf_id(v) for v in checks] == leaves.tolist()
    sample = out / 'sample_features.json'; sample.write_text(json.dumps(dict(zip(FEATURES, x[0].tolist())), indent=2))
    standalone = subprocess.run([sys.executable, '-I', '-S', str(ROOT / 'scripts/114_predict_portable_tree.py'),
                                '--tree', str(tree_path), '--features-file', str(sample)],
                               cwd=ROOT, check=True, capture_output=True, text=True)
    standalone_result = json.loads(standalone.stdout)
    assert list(standalone_result['parameters'].values()) == model.predict(x[:1])[0].tolist()
    (out / 'standalone_prediction.json').write_text(standalone.stdout)
    (out / 'metadata.json').write_text(json.dumps(metadata, indent=2))
    assert all(digest(ROOT / p) == h for p, h in hashes.items())
    report = dict(status='built_development_candidate_' + gate['status'], quality_gate=gate,
        fitting_pairs=len(fitting), fitting_sources=len(metadata['fit_sources']), held_pairs_never_fitted=len(held),
        all_probe_prediction_parity=len(vectors), split_boundary_parity=len(boundaries),
        new_model_fits=1, cv_refits=0, training_pairs_regenerated=0,
        runtime_model_replaced=False, android_asset_replaced=False, proposal_complete=False,
        mst_status='unavailable', input_sha256=hashes,
        artifact_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file() and p.name != 'run_status.json'},
        limitations='Selected exposed development IDs; inherited screen gate is not final cohort/mask approval. Original photos are reconstruction references, not calibrated complexion truth. Recipe fails source-held-out quality gate.')
    (out / 'build_report.json').write_text(json.dumps(report, indent=2))
    (out / 'run_status.json').write_text('{"status":"complete"}')
    print(json.dumps({k: v for k, v in report.items() if k not in ('input_sha256', 'artifact_sha256', 'quality_gate')}, indent=2))


if __name__ == '__main__':
    main()
