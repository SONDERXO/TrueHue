"""Fixed subject-balanced calibration and same-row comparison; no deployment."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from sklearn.isotonic import IsotonicRegression
from src.evaluation.mst_validation import evaluate_mst
from src.ita_estimation.semantic_measurement import contract


def main():
    out = ROOT / 'outputs/semantic_mst_calibration_v1'
    if out.exists():
        raise FileExistsError(out)
    source = ROOT / 'outputs/semantic_mst_measurement_v1/summary.json'
    oldpath = ROOT / 'outputs/mst_monotone_square256_v1/summary.json'
    oldmeasure = ROOT / 'outputs/mst_square256_measurement_v1/summary.json'
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    data = json.loads(source.read_text()); old = json.loads(oldpath.read_text())
    oldrows = {r['image_id']: r for r in json.loads(oldmeasure.read_text())['records']}
    rows = data['records']; byid = {r['image_id']: r for r in rows}
    assert set(byid) == set(oldrows)
    identity = contract(ROOT)[1]
    assert identity == data['measurement_contract_sha256']
    assert all(digest(Path(p)) == value for p, value in data['input_sha256'].items())
    hashes = {str(p): digest(p) for p in [source, oldpath, oldmeasure, Path(__file__),
        ROOT / 'src/evaluation/mst_validation.py', ROOT / 'docs/semantic-measurement-single-cycle-protocol.md']}
    subjects = sorted({r['subject_id'] for r in rows})
    folds = []; predictions = []; models = []
    attempts = [dict(image_id=r['image_id'], subject_id=r['subject_id'], mst=r['source_mst_label'],
                     lighting=r['lighting'], measured=r['status'] == 'success') for r in rows]
    out.mkdir()
    (out / 'plan.json').write_text(json.dumps(dict(status='fixed_before_fitting',
        held_subjects=subjects, recipe='same_decreasing_subject_balanced_isotonic_no_tuning',
        input_sha256=hashes, measurement_contract_sha256=identity,
        deployed=False, all_row_fit=False, correction_tree_fits=0), indent=2))
    for subject in subjects:
        training = [r for r in rows if r['status'] == 'success' and r['subject_id'] != subject]
        held = [r for r in rows if r['status'] == 'success' and r['subject_id'] == subject]
        counts = Counter(r['subject_id'] for r in training)
        labels = {r['subject_id']: r['source_mst_label'] for r in training}
        assert subject not in labels and labels
        weights = [1/counts[r['subject_id']] for r in training]
        folds.append(dict(held_subject=subject, fit_subject_labels=labels))
        model = IsotonicRegression(increasing=False, out_of_bounds='clip', y_min=1, y_max=10)
        model.fit([r['features']['input_ita_degrees'] for r in training],
                  [r['source_mst_label'] for r in training], sample_weight=weights)
        baseline = int(np.floor(np.median(list(labels.values())) + .5))
        for row in held:
            value = float(model.predict([row['features']['input_ita_degrees']])[0])
            assert abs(value-float(np.interp(row['features']['input_ita_degrees'], model.X_thresholds_, model.y_thresholds_))) < 1e-12
            predictions.append(dict(image_id=row['image_id'], continuous_prediction=value,
                                    prediction=int(np.floor(value+.5)), baseline=baseline))
        models.append(dict(held_subject=subject, fit_subjects=sorted(labels),
            fit_image_ids=[r['image_id'] for r in training], held_success_ids=[r['image_id'] for r in held],
            fit_image_weights=weights, x_knots=model.X_thresholds_.tolist(), y_knots=model.y_thresholds_.tolist()))
    metrics = evaluate_mst(attempts, predictions, folds)
    common = {r['image_id'] for r in predictions} & {r['image_id'] for r in old['predictions']}
    # Both models were fitted with their own technically successful memberships;
    # shared-row scoring controls the scoring denominator, not fit membership.
    def shared(reportpred, reportfold):
        return evaluate_mst([r for r in attempts if r['image_id'] in common],
                            [r for r in reportpred if r['image_id'] in common],
                            [f for f in reportfold if f['held_subject'] in {byid[i]['subject_id'] for i in common}])
    comparison = dict(common_rows=len(common), old=shared(old['predictions'], old['folds'])['overall'],
                      semantic=shared(predictions, folds)['overall'],
                      limitation='Common scoring rows; technical-success fitting memberships differ between mask contracts.')
    replayed = 0
    for row in rows:
        if row.get('mask_path'):
            p = source.parent / row['mask_path']; assert digest(p) == row['mask_sha256']
            replayed += 1
    assert contract(ROOT)[1] == identity
    assert all(digest(Path(p)) == value for p, value in hashes.items())
    report = dict(status='development_calibration_complete_not_validated_or_adopted',
        measurement_contract_sha256=identity, metrics=metrics, predictions=predictions,
        fold_models=models, folds=folds, shared_row_comparison=comparison,
        new_mapping_fits=len(models), correction_tree_fits=0, all_row_fit_performed=False,
        production_lookup_exported=False, new_mask_approvals=0, input_sha256=hashes,
        verification=dict(source_separation=True, independent_interpolation_replays=len(predictions),
                          saved_mask_hash_checks=replayed),
        limitations=['Previously exposed development subjects; no untouched final validation.',
            'New masks are not human-approved; parser errors/facial hair can alter measurements.',
            'Same-category independent-subject support remains limited.',
            'No causal claim that mask area explains any change in mapping error.',
            'Do not feed these measurements into the legacy lookup or correction tree.'])
    (out / 'summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(dict(status=report['status'], overall=metrics['overall'], shared_row_comparison=comparison), indent=2))


if __name__ == '__main__':
    main()
