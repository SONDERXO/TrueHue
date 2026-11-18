"""One authorized fixed data-expansion comparison; no image or runtime work."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import hashlib
import json
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.ita_estimation.contextual_mst_experiment import FEATURES, _ridge, predict

DESIGN = ROOT / 'outputs/combined_reviewed_mst_design_v1'
OUT = ROOT / 'outputs/combined_reviewed_mst_validation_v1'
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
write = lambda p, d: Path(p).write_text(json.dumps(d, indent=2, allow_nan=False)+'\n')


def metrics(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[r['subject_id']].append(r)
    result = dict(attempts=len(rows), subjects=len(groups))
    for key in ('candidate', 'comparator', 'median'):
        result[key+'_MAE'] = statistics.mean(statistics.mean(r[key+'_error'] for r in group) for group in groups.values())
        result[key+'_maximum_error'] = max(r[key+'_error'] for r in rows)
    result['candidate_clips'] = sum(r['candidate_clipped'] for r in rows)
    result['candidate_within_subject_ranges'] = {s:max(r['candidate_score'] for r in group)-min(r['candidate_score'] for r in group) for s,group in groups.items()}
    return result


def main():
    if OUT.exists():
        raise FileExistsError('Preserve completed or partial validation')
    receipt = read(DESIGN/'review_PRIVATE.json')
    assert receipt['passed']
    bound = dict(receipt['input_sha256'])
    # Verify metadata/scalar files only. Preserve cached-image bindings without opening images.
    scalar_bound = {p:h for p,h in bound.items() if Path(p).suffix not in ('.png', '.npy', '.npz')}
    assert all(sha(p)==h for p,h in scalar_bound.items())
    rows = read(DESIGN/'rows_PRIVATE.json')
    folds = read(DESIGN/'folds_PRIVATE.json')
    plan = read(DESIGN/'proposed_validation_PRIVATE.json')
    assert len(rows)==60 and len(folds)==10 and plan['planned_fits']==10 and plan['alpha']==1.
    for path in (Path(__file__), ROOT/'src/ita_estimation/contextual_mst_experiment.py'):
        scalar_bound[str(path)] = sha(path)
    indexed = {r['case_id']:r for r in rows}
    assert len(indexed)==60 and all(r['training_admitted'] is False and r['calibration_admitted'] is False for r in rows)
    OUT.mkdir()
    write(OUT/'execution_plan_PRIVATE.json', dict(authorized_fits=10,candidate_predictions=60,unchanged_comparator_predictions=60,
         input_sha256=scalar_bound,preserved_cached_artifact_bindings=bound,new_image_reads=0,
         all_data_fit=False,PPR_prediction=False,tree_fit=False))
    fitted, predictions = [], []
    for fold in folds:
        held = fold['held_subject']
        training = [indexed[c] for c in fold['fitting_cases']]
        testing = [indexed[c] for c in fold['evaluation_cases']]
        assert len(training)==54 and len(testing)==6
        assert all(r['subject_id']!=held for r in training) and all(r['subject_id']==held for r in testing)
        assert len({r['subject_id'] for r in training})==9
        saved = fold['saved_600_only_comparator']
        assert set(saved['fitting_subjects'])=={r['subject_id'] for r in training}
        model = _ridge(training, FEATURES)
        assert set(model['training_subject_row_counts'].values())=={6}
        median = statistics.median({r['subject_id']:float(Decimal(r['source_mst_exact_decimal'])) for r in training}.values())
        fitted.append(dict(held_subject=held,model=model,median_baseline=median,definition=fold))
        lower = {f:min(r['features'][f] for r in training) for f in FEATURES}
        upper = {f:max(r['features'][f] for r in training) for f in FEATURES}
        for row in testing:
            candidate, comparator = predict(model,row['features']), predict(saved['model'],row['features'])
            reference = float(Decimal(row['source_mst_exact_decimal']))
            predictions.append(dict(case_id=row['case_id'],subject_id=held,condition=row['condition'],illumination=row['illumination'],
                source_mst_exact_decimal=row['source_mst_exact_decimal'],candidate_raw=candidate['raw'],candidate_score=candidate['score'],
                candidate_clipped=candidate['raw']!=candidate['score'],comparator_raw=comparator['raw'],comparator_score=comparator['score'],
                comparator_clipped=comparator['raw']!=comparator['score'],median_score=median,
                candidate_error=abs(candidate['score']-reference),comparator_error=abs(comparator['score']-reference),median_error=abs(median-reference),
                outside_fitting_marginals=[f for f in FEATURES if not lower[f]<=row['features'][f]<=upper[f]]))
    overall = metrics(predictions)
    conditions = {c:metrics([p for p in predictions if p['condition']==c]) for c in sorted({p['condition'] for p in predictions})}
    illumination = {c:metrics([p for p in predictions if p['illumination']==c]) for c in ('600','1200')}
    tolerance = plan['comparison_tolerance']
    checks = dict(full_coverage=len({p['case_id'] for p in predictions})==len(predictions)==60,
        overall_better_than_comparator=overall['candidate_MAE']<overall['comparator_MAE']-tolerance,
        overall_better_than_median=overall['candidate_MAE']<overall['median_MAE']-tolerance,
        new_1200_better_than_comparator=illumination['1200']['candidate_MAE']<illumination['1200']['comparator_MAE']-tolerance,
        each_old_condition_nonworse=all(conditions[c]['candidate_MAE']<=limit+tolerance for c,limit in plan['saved_600_condition_limits'].items()),
        combined_maximum_nonworse=overall['candidate_maximum_error']<=overall['comparator_maximum_error']+tolerance,
        old_maximum_nonworse=illumination['600']['candidate_maximum_error']<=plan['saved_600_maximum_error_limit']+tolerance)
    result = dict(mapping_fits=10,predictions=predictions,folds=fitted,metrics=overall,by_condition=conditions,by_illumination=illumination,
        by_subject={s:metrics([p for p in predictions if p['subject_id']==s]) for s in sorted({p['subject_id'] for p in predictions})},
        advancement_checks=checks,development_advancement_passed=all(checks.values()),calibration_admitted=False,training_admitted=False,
        PPR_application_qualified=False,runtime_adopted=False,all_data_fit=False,new_PPR_scores=0,correction_tree_fits=0)
    assert all(sha(p)==h for p,h in scalar_bound.items())
    write(OUT/'results_PRIVATE.json',result)
    print(json.dumps(dict(metrics=overall,illumination=illumination,checks=checks,passed=all(checks.values())),indent=2))


if __name__=='__main__':
    main()
