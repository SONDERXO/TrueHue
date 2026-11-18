"""Bind completed user reviews into input rows and subject-held roles; zero fits."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.demo.labelled_measurement import digest, verify, write

OUT = ROOT / 'outputs/refined_mst_grouped_design_v1'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve existing design')
    read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    audit_path = ROOT / 'outputs/labelled_annotation_audit_v2/audit_PRIVATE.json'
    audit = read(audit_path)
    assert audit['passed_integrity'] and audit['summary']['missing_cases'] == []
    assert audit['summary']['distinct_saved_cases'] == audit['summary']['valid_latest'] == 30
    bound = dict(audit['input_sha256'])
    for p, h in bound.items():
        assert digest(p) == h
    rows = []
    for entry in audit['coverage']:
        latest = entry['latest']
        folder = Path(latest['annotation'])
        verify(folder)
        assert digest(folder / 'manifest.json') == latest['manifest_sha256']
        report = read(folder / 'annotation.json')
        task = report['task']
        assert report['review'] == 'reviewed_selection' and report['statistics']['valid']
        assert not report['generated_fixture'] and not report['calibration_admitted'] and not report['training_admitted']
        score = Decimal(task['reference_mst_exact_decimal'])
        assert score.is_finite() and 1 <= score <= 10
        rows.append(dict(case_id=entry['case_id'], subject_id=entry['subject_id'], condition=entry['condition'],
            source_mst_exact_decimal=task['reference_mst_exact_decimal'],
            measurement_method_sha256=task['method_sha256'], source_sha256=task['source_sha256'],
            input_bridge=task['input_bridge'], task_manifest_sha256=report['task_manifest_sha256'],
            annotation_manifest_sha256=latest['manifest_sha256'], annotation_folder=str(folder),
            features={'input_' + k: report['statistics'][k] for k in ['mean_l_star', 'mean_a_star', 'mean_b_star', 'ita_degrees']},
            user_review='reviewed_selection', actual_skin_validity='user_reviewed_not_independent_pixel_truth',
            status='available', allocation=None, calibration_admitted=False, training_admitted=False,
            eligible_for='proposed_grouped_development_mapping_assessment_only'))
    subjects = defaultdict(list)
    for row in rows:
        subjects[row['subject_id']].append(row)
    assert len(subjects) == 10 and all(len(v) == 3 for v in subjects.values())
    assert len({r['measurement_method_sha256'] for r in rows}) == 1
    assert all(len({r['source_mst_exact_decimal'] for r in values}) == 1 for values in subjects.values())
    assert len({tuple(sorted(r['condition'] for r in values)) for values in subjects.values()}) == 1
    folds = []
    for held in sorted(subjects):
        train = [r for r in rows if r['subject_id'] != held]
        test = subjects[held]
        assert len(train) == 27 and len(test) == 3
        folds.append(dict(held_subject=held, fitting_subjects=sorted(set(subjects)-{held}),
            fitting_cases=[r['case_id'] for r in train], evaluation_cases=[r['case_id'] for r in test],
            fitting_weights={r['case_id']: 1/len(subjects[r['subject_id']]) for r in train}))
    conditions = sorted({r['condition'] for r in rows})
    summary = dict(records=30, subjects=10, conditions=conditions,
        by_condition={c: sum(r['condition'] == c for r in rows) for c in conditions},
        score_range=[str(min(Decimal(r['source_mst_exact_decimal']) for r in rows)), str(max(Decimal(r['source_mst_exact_decimal']) for r in rows))],
        method_sha256=rows[0]['measurement_method_sha256'], folds=10, calibration_fits=0, tree_fits=0,
        original_source_image_reads=0, model_calls=0, holdout_bytes_read=0,
        runtime_adopted=False, calibration_admitted=False, training_admitted=False)
    for path in [audit_path, Path(__file__), ROOT / 'docs/refined-mst-grouped-design-2026-11-10.md']:
        bound[str(path)] = digest(path)
    assert all(digest(p) == h for p, h in bound.items())
    OUT.mkdir()
    write(OUT / 'rows_PRIVATE.json', rows)
    write(OUT / 'folds_PRIVATE.json', folds)
    write(OUT / 'verification_PRIVATE.json', dict(passed=True, summary=summary, input_sha256=bound))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
