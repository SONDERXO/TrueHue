"""Fixed subject-held developmental assessment; no release calibration export."""
from collections import Counter, defaultdict
from decimal import Decimal
import math
import statistics

from sklearn.isotonic import IsotonicRegression


def assess(rows, folds):
    by_case = {r['case_id']: r for r in rows}
    if len(by_case) != len(rows) or not rows:
        raise ValueError('Unique nonempty cases required')
    contracts = {r['measurement_method_sha256'] for r in rows}
    if len(contracts) != 1:
        raise ValueError('One measurement method required')
    subjects = defaultdict(list)
    for r in rows:
        if r['status'] != 'available' or r['user_review'] != 'reviewed_selection':
            raise ValueError('This frozen complete cohort requires reviewed available rows')
        if r['calibration_admitted'] or r['training_admitted']:
            raise ValueError('This assessment must retain unadmitted status')
        x = r['features']['input_ita_degrees']
        score = Decimal(r['source_mst_exact_decimal'])
        if isinstance(x, bool) or not math.isfinite(x) or not -90 <= x <= 90 or not score.is_finite() or not 1 <= score <= 10:
            raise ValueError('Finite ITA and original decimal score required')
        subjects[r['subject_id']].append(r)
    if any(len({r['source_mst_exact_decimal'] for r in group}) != 1 for group in subjects.values()):
        raise ValueError('Consistent publisher score per subject required')
    if len(folds) != len(subjects) or {f['held_subject'] for f in folds} != set(subjects):
        raise ValueError('Exactly one fold per subject required')
    # Validate every allocation before any fit.
    for f in folds:
        expected_train = {r['case_id'] for r in rows if r['subject_id'] != f['held_subject']}
        expected_test = {r['case_id'] for r in subjects[f['held_subject']]}
        if set(f['fitting_cases']) != expected_train or set(f['evaluation_cases']) != expected_test:
            raise ValueError('Subject-separated allocation required')
        if len(f['fitting_cases']) != len(expected_train) or len(f['evaluation_cases']) != len(expected_test):
            raise ValueError('Repeated case in a fold')
        if set(f['fitting_subjects']) != set(subjects)-{f['held_subject']}:
            raise ValueError('Fitting subject declaration mismatch')
        for case in f['fitting_cases']:
            expected_weight = 1 / len(subjects[by_case[case]['subject_id']])
            if not math.isclose(f['fitting_weights'][case], expected_weight, abs_tol=1e-15):
                raise ValueError('Equal subject weights required')
    predictions = []
    fitted = []
    for f in folds:
        train = [by_case[c] for c in f['fitting_cases']]
        x = [r['features']['input_ita_degrees'] for r in train]
        y = [float(Decimal(r['source_mst_exact_decimal'])) for r in train]
        weights = [f['fitting_weights'][r['case_id']] for r in train]
        estimator = IsotonicRegression(increasing=False, out_of_bounds='clip')
        estimator.fit(x, y, sample_weight=weights)
        baseline = statistics.median([float(Decimal(subjects[s][0]['source_mst_exact_decimal'])) for s in f['fitting_subjects']])
        fitted.append(dict(f, ita_knots=estimator.X_thresholds_.tolist(), mst_knots=estimator.y_thresholds_.tolist(),
                           median_baseline=baseline, decreasing=True, outside_range='clip'))
        for case in f['evaluation_cases']:
            r = by_case[case]
            value = r['features']['input_ita_degrees']
            predicted = float(estimator.predict([value])[0])
            target = float(Decimal(r['source_mst_exact_decimal']))
            predictions.append(dict(case_id=case, subject_id=r['subject_id'], condition=r['condition'],
                source_mst_exact_decimal=r['source_mst_exact_decimal'], input_ita_degrees=value,
                predicted_mst_score=predicted, median_baseline=baseline,
                absolute_error=abs(predicted-target), baseline_absolute_error=abs(baseline-target),
                outside_fitting_support=value < min(x) or value > max(x),
                endpoint_clipped=value < min(x) or value > max(x),
                fitting_support=[min(x), max(x)]))
    def metrics(records):
        grouped = defaultdict(list)
        for r in records:
            grouped[r['subject_id']].append(r)
        return dict(attempts=len(records), available_predictions=len(records), unavailable_predictions=0,
            subjects=len(grouped), image_MAE=statistics.mean(r['absolute_error'] for r in records),
            baseline_image_MAE=statistics.mean(r['baseline_absolute_error'] for r in records),
            equal_subject_MAE=statistics.mean(statistics.mean(r['absolute_error'] for r in group) for group in grouped.values()),
            baseline_equal_subject_MAE=statistics.mean(statistics.mean(r['baseline_absolute_error'] for r in group) for group in grouped.values()),
            outside_support=sum(r['outside_fitting_support'] for r in records),
            better_cases=sum(r['absolute_error'] < r['baseline_absolute_error'] for r in records),
            worse_cases=sum(r['absolute_error'] > r['baseline_absolute_error'] for r in records),
            equal_cases=sum(r['absolute_error'] == r['baseline_absolute_error'] for r in records))
    return dict(version='refined_manual_ita_isotonic_loso_v1', method_sha256=next(iter(contracts)),
        calibration_fits=len(folds), correction_tree_fits=0, all_data_fit=False,
        calibration_admitted=False, training_admitted=False, runtime_adopted=False,
        folds=fitted, predictions=predictions, metrics=metrics(predictions),
        by_condition={c: metrics([r for r in predictions if r['condition'] == c]) for c in sorted({r['condition'] for r in predictions})},
        by_subject={s: dict(metrics([r for r in predictions if r['subject_id'] == s]),
                            prediction_range=max(r['predicted_mst_score'] for r in predictions if r['subject_id'] == s)-min(r['predicted_mst_score'] for r in predictions if r['subject_id'] == s)) for s in sorted(subjects)})
