"""One fixed developmental recipe; preserves scientific non-admission."""
from collections import Counter,defaultdict
from decimal import Decimal
import math
import statistics
from .contextual_mst_experiment import FEATURES,_ridge,predict


def evaluate(rows,folds,comparators,gates):
    indexed={r['case_id']:r for r in rows};baseline={r['case_id']:r for r in comparators}
    if len(indexed)!=len(rows) or set(indexed)!=set(baseline) or len(baseline)!=len(comparators):
        raise ValueError('Unique exactly matched reviewed/comparator cases required')
    cores={r['measurement_core_sha256'] for r in rows}
    if len(cores)!=1:raise ValueError('One shared measurement core required')
    subjects=defaultdict(list)
    for r in rows:
        if r.get('calibration_admitted') is not False or r.get('training_admitted') is not False or r.get('status')!='available' or r.get('user_review')!='reviewed_selection':
            raise ValueError('Explicit available reviewed developmental records with false admissions required')
        if set(r['features'])!=set(FEATURES) or any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) for v in r['features'].values()):
            raise ValueError('Four finite existing input features required')
        label=Decimal(r['source_mst_exact_decimal'])
        if not label.is_finite() or not 1<=label<=10:raise ValueError('Original decimal score required')
        p=baseline[r['case_id']]
        if any(p[k]!=r[k] for k in ['subject_id','condition','source_mst_exact_decimal']):raise ValueError('Comparator identity/label mismatch')
        subjects[r['subject_id']].append(r)
    if any(len({r['source_mst_exact_decimal'] for r in group})!=1 for group in subjects.values()):raise ValueError('Consistent subject scores required')
    if len(folds)!=len(subjects) or {f['held_subject'] for f in folds}!=set(subjects):raise ValueError('Exactly one held fold per subject required')
    for f in folds:
        held=f['held_subject'];train={r['case_id'] for r in rows if r['subject_id']!=held};test={r['case_id'] for r in subjects[held]}
        if set(f['fitting_cases'])!=train or len(f['fitting_cases'])!=len(train) or set(f['evaluation_cases'])!=test or len(f['evaluation_cases'])!=len(test):
            raise ValueError('Complete subject-disjoint folds required')
        if set(f['fitting_subjects'])!=set(subjects)-{held}:raise ValueError('Fitting subjects mismatch')
        if any(not math.isclose(f['fitting_weights'][c],1/len(subjects[indexed[c]['subject_id']]),abs_tol=1e-15) for c in train):
            raise ValueError('Equal subject total weights required')
    fitted=[];predictions=[]
    for f in folds:
        train=[indexed[c] for c in f['fitting_cases']]
        model=_ridge(train,FEATURES)  # Exactly one fixed alpha1 candidate per fold.
        fitted.append(dict(f,model=model))
        lower={n:min(r['features'][n] for r in train) for n in FEATURES};upper={n:max(r['features'][n] for r in train) for n in FEATURES}
        for case in f['evaluation_cases']:
            r=indexed[case];p=predict(model,r['features']);original=float(Decimal(r['source_mst_exact_decimal']));old=baseline[case]
            predictions.append(dict(case_id=case,subject_id=r['subject_id'],condition=r['condition'],source_mst_exact_decimal=r['source_mst_exact_decimal'],
                raw_mst_score=p['raw'],mst_score=p['score'],clipped=p['raw']!=p['score'],absolute_error=abs(p['score']-original),
                saved_isotonic_score=old['predicted_mst_score'],saved_isotonic_error=old['absolute_error'],
                saved_median_score=old['median_baseline'],saved_median_error=old['baseline_absolute_error'],
                outside_training_marginals=[n for n in FEATURES if not lower[n]<=r['features'][n]<=upper[n]]))
    def metrics(own):
        groups=defaultdict(list)
        for p in own:groups[p['subject_id']].append(p)
        return dict(attempts=len(own),available_predictions=len(own),unavailable_predictions=0,subjects=len(groups),
            image_MAE=statistics.mean(p['absolute_error'] for p in own),
            equal_subject_MAE=statistics.mean(statistics.mean(p['absolute_error'] for p in group) for group in groups.values()),
            saved_isotonic_MAE=statistics.mean(p['saved_isotonic_error'] for p in own),saved_median_MAE=statistics.mean(p['saved_median_error'] for p in own),
            maximum_absolute_error=max(p['absolute_error'] for p in own),clipped_predictions=sum(p['clipped'] for p in own),
            within_subject_prediction_ranges={s:max(p['mst_score'] for p in group)-min(p['mst_score'] for p in group) for s,group in groups.items()})
    overall=metrics(predictions);by_condition={c:metrics([p for p in predictions if p['condition']==c]) for c in sorted({p['condition'] for p in predictions})}
    tolerance=gates['comparison_tolerance']
    checks=dict(full_coverage=len(predictions)==len(rows) and len({p['case_id'] for p in predictions})==len(rows),
        overall_better_than_isotonic=overall['equal_subject_MAE']<gates['equal_subject_MAE_strictly_below']-tolerance,
        overall_better_than_median=overall['equal_subject_MAE']<gates['median_MAE_strictly_below']-tolerance,
        no_condition_worse=all(m['image_MAE']<=gates['condition_MAE_not_above'][c]+tolerance for c,m in by_condition.items()),
        maximum_error_not_worse=overall['maximum_absolute_error']<=gates['maximum_absolute_error_not_above']+tolerance)
    return dict(version='reviewed_contextual_MST_fixed_ridge1_validation_v1',features=list(FEATURES),alpha=1.,measurement_core_sha256=next(iter(cores)),
        mapping_fits=len(fitted),folds=fitted,predictions=predictions,metrics=overall,by_condition=by_condition,
        by_subject={s:metrics([p for p in predictions if p['subject_id']==s]) for s in sorted(subjects)},
        advancement_checks=checks,development_advancement_passed=all(checks.values()),
        calibration_admitted=False,training_admitted=False,PPR_application_qualified=False,runtime_adopted=False,
        all_data_fit=False,new_PPR_scores=0,correction_tree_fits=0)
