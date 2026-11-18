"""Reconcile the exact reviewed60 metadata; never load pixels or locked records."""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/stellenbosch_correction_eligibility_metadata_v1'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve completed or partial evidence')
    bound = {}

    def read(path):
        path = Path(path)
        raw = path.read_bytes()
        bound[str(path)] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    rows = read(ROOT / 'outputs/combined_reviewed_mst_design_v1/rows_PRIVATE.json')
    assert len(rows) == 60
    assert len({r['case_id'] for r in rows}) == 60
    subjects = Counter(r['subject_id'] for r in rows)
    assert len(subjects) == 10 and set(subjects.values()) == {6}
    conditions = Counter(r['condition'] for r in rows)
    assert len(conditions) == 6 and set(conditions.values()) == {10}
    subject_scores = {}
    ledger = []
    for row in rows:
        folder = Path(row['annotation_folder']).resolve()
        assert folder.is_relative_to((ROOT / 'outputs').resolve())
        annotation = read(folder / 'annotation.json')
        manifest_path = folder / 'manifest.json'
        raw = manifest_path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        bound[str(manifest_path)] = digest
        assert digest == row['annotation_manifest_sha256']
        task = annotation['task']
        assert task['subject_id'] == row['subject_id']
        assert task['case_id'] == row['case_id']
        assert task['source_sha256'] == row['source_sha256']
        assert task['reference_mst_exact_decimal'] == row['source_mst_exact_decimal']
        assert annotation['review'] == row['user_review'] == 'reviewed_selection'
        assert not annotation['generated_fixture']
        assert not row['training_admitted'] and not row['calibration_admitted']
        assert not annotation['training_admitted'] and not annotation['calibration_admitted']
        subject = row['subject_id']
        exact = row['source_mst_exact_decimal']
        assert subject not in subject_scores or subject_scores[subject] == exact
        subject_scores[subject] = exact
        bridge = row['input_bridge']
        assert bridge['source_shape'] == [224, 224, 3]
        ledger.append(dict(case_id=row['case_id'], subject_id=subject,
            condition=row['condition'], supplied_mst_exact_decimal=exact,
            historical_role='already_exposed_reviewed_development',
            source_sha256=row['source_sha256'],
            annotation_manifest_sha256=digest,
            native_face_width=bridge['native_face_box'][2],
            native_face_height=bridge['native_face_box'][3],
            native_context_side=bridge['native_side'],
            measurement_review='user_reviewed_selection',
            note=annotation.get('note', ''),
            accepted_correction_reference='not_established_by_measurement_review',
            correction_application_alpha='not_bound_for_this_correction_test',
            correction_protection='not_bound_for_this_correction_test',
            current_281_feature_compatibility='not_established_by_four_feature_measurement_parity',
            supplied_label_is_correction_target=False,
            correction_training_admitted=False,
            recoverability_execution_admitted=False))
    def limits(key):
        values = [r[key] for r in ledger]
        return [min(values), max(values)]
    scores = [Decimal(v) for v in subject_scores.values()]
    result = dict(status='RELEVANT_EXISTING_DATA_NOT_CORRECTION_TEST_READY',
        reviewed_captures=60, publisher_subjects=10, conditions=dict(conditions),
        source_pixel_dimensions=[224, 224], native_face_width_range=limits('native_face_width'),
        native_face_height_range=limits('native_face_height'),
        native_context_side_range=limits('native_context_side'),
        supplied_subject_scores=sorted(subject_scores.values(), key=Decimal),
        fractional_subject_scores=sum(v != v.to_integral_value() for v in scores),
        source_scores_at_least_8_descriptive_not_paper_group=sum(v >= 8 for v in scores),
        correction_references_accepted_by_these_records=0,
        correction_application_supports_bound=0,
        admitted_recoverability_rows=0, new_target_or_calibration_or_tree_fits=0,
        image_or_mask_or_npz_arrays_read=0, locked_records_or_manifests_read=0,
        distinct_use_hypothesis='Reference-aware three-control recoverability, not MST-score prediction; unexecuted.',
        previous_calibration_failure_reclassified=False,
        next_execution_roster_selected=False)
    OUT.mkdir()
    for name, value in [('ledger_PRIVATE.json', ledger), ('decision_PRIVATE.json', result),
                        ('input_sha256_PRIVATE.json', bound)]:
        (OUT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in bound.items())
    (OUT / 'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,
        all60_annotations_and_subject_condition_source_bindings_checked=True,
        original_metadata_unchanged=True, pixels_read=0, fits=0), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
