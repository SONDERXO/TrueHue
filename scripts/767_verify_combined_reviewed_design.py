"""Independent stdlib design checks, without fits or predictions."""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/combined_reviewed_mst_design_v1'
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest = OUT / 'verification_PRIVATE.json'
    if dest.exists():
        raise FileExistsError('Preserve prior verification')
    bindings = read(OUT / 'input_sha256_PRIVATE.json')
    assert all(sha(p) == h for p, h in bindings.items())
    rows, folds = read(OUT / 'rows_PRIVATE.json'), read(OUT / 'folds_PRIVATE.json')
    plan = read(OUT / 'proposed_validation_PRIVATE.json')
    subjects = {r['subject_id'] for r in rows}
    assert len(rows) == 60 and len(subjects) == len(folds) == 10
    assert len({r['case_id'] for r in rows}) == len({r['source_sha256'] for r in rows}) == 60
    assert set(Counter(r['subject_id'] for r in rows).values()) == {6}
    expected_conditions = {f'{family}_{level}' for family in ('F_cool', 'H_warm', 'L_warm') for level in (600, 1200)}
    assert {r['condition'] for r in rows} == expected_conditions
    prior = read(ROOT / 'outputs/reviewed_contextual_validation_v1/results_PRIVATE.json')
    saved = {f['held_subject']: f for f in prior['folds']}
    evaluated = []
    for fold in folds:
        subject = fold['held_subject']
        fit = [r for r in rows if r['subject_id'] != subject]
        held = [r for r in rows if r['subject_id'] == subject]
        assert set(fold['fitting_cases']) == {r['case_id'] for r in fit} and len(fold['fitting_cases']) == 54
        assert set(fold['evaluation_cases']) == {r['case_id'] for r in held} and len(fold['evaluation_cases']) == 6
        assert {r['condition'] for r in held} == expected_conditions
        assert len({Decimal(r['source_mst_exact_decimal']) for r in held}) == 1
        assert fold['saved_600_only_comparator'] == saved[subject]
        for s in subjects - {subject}:
            assert math.isclose(sum(fold['fitting_weights'][r['case_id']] for r in fit if r['subject_id'] == s), 1, abs_tol=1e-12)
        evaluated += fold['evaluation_cases']
    assert len(evaluated) == len(set(evaluated)) == 60
    assert all(r['training_admitted'] is False and r['calibration_admitted'] is False for r in rows)
    assert plan['planned_fits'] == 10 and plan['new_fits'] == plan['new_predictions'] == 0
    assert not any(plan[k] for k in ('all_data_fit', 'PPR_prediction', 'tree_fit', 'runtime_change', 'execution_authorized_by_this_preparation'))
    result = dict(passed=True, rows=60, subjects=10, conditions=6, folds=10, fitting_per_fold=54,
                  evaluated_per_fold=6, unique_evaluations=60, saved_comparator_models_exact=10,
                  bound_metadata_or_cached_artifacts_checked=len(bindings), equal_subject_weights=True,
                  new_fits=0, new_predictions=0, photo_bytes_read=0, holdout_reads=0,
                  design_sha256={p.name:sha(p) for p in OUT.iterdir() if p.is_file()}, verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS:60unique captures/10people/6conditions;10exact54/6 disjoint folds; weights and saved comparators unchanged.')


if __name__ == '__main__':
    main()
