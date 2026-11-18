"""Metadata-only coverage review; never opens photographs or fits models."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/labelled_brightness_coverage_review_v1'


def main():
    OUT.mkdir(exist_ok=False)
    bindings = {}

    def read(relative):
        data = (ROOT / relative).read_bytes()
        bindings[relative] = hashlib.sha256(data).hexdigest()
        return json.loads(data)

    calibration = read('outputs/reviewed_feature_control_contract_v1/calibration_rows_PRIVATE.json')
    photographic = read('outputs/shared_core_mst_features_v1/complete_development_rows_PRIVATE.json')
    fitting = read('outputs/fitting_green_features_v1/features_PRIVATE.json')['records']
    subjects = read('outputs/stellenbosch_received_data_v1/subjects_PRIVATE.json')
    files = read('outputs/stellenbosch_received_data_v1/files_PRIVATE.json')
    inventory = read('outputs/stellenbosch_received_data_v1/protocol.json')
    groups = read('outputs/group_diversity_candidates_v1/plan_PRIVATE.json')['groups']
    known = {r['subject_id'] for r in calibration}
    locked = {r['subject_key'] for r in groups if r['role'] == 'closed_holdout_candidate'}
    assert len(known) == 10 and len(locked) == 8 and known.isdisjoint(locked)
    labels = {r['subject_key']: r for r in subjects if r['subject_key'] in known}
    by_path = {r['path']: r for r in files}
    candidates = []
    source_root = Path(inventory['dataset_location'])
    for subject in sorted(known):
        label = labels[subject]
        original_labels = {r['source_mst_exact_decimal'] for r in calibration if r['subject_id'] == subject}
        assert original_labels == {label['exact_decimal']}
        for condition in ('F_cool_1200', 'H_warm_1200', 'L_warm_1200'):
            relative = f"{label['publisher_folder']}/front-facing/{condition}.jpeg"
            record = by_path[relative]
            assert record['subject_key'] == subject and record['dimensions'] == [224, 224]
            path = source_root / relative
            assert path.is_file() and path.stat().st_size == record['bytes']
            candidates.append(dict(record, condition=condition, source_mst_exact_decimal=label['exact_decimal'],
                                   source_path=str(path), current_size_matches=True,
                                   measurement_available=False, training_admitted=False, calibration_admitted=False))
    clean = [r for r in fitting if r['role'] == 'fitting' and r['recipe'] == 'clean']
    def span(rows, key):
        values = [r[key]['input_mean_l_star'] for r in rows]
        return [min(values), max(values)]
    current_range = span(calibration, 'features')
    clean_range = span(clean, 'raw_features')
    ppr_range = span(photographic, 'features')
    outside = lambda bounds: sum(not bounds[0] <= r['features']['input_mean_l_star'] <= bounds[1] for r in photographic)
    assert len(clean) == 82 and len(candidates) == 30 and len(photographic) == 14
    summary = dict(current_reviewed_rows=30, current_subjects=10, current_l_star_range=current_range,
                   historical_real_clean_fitting_rows=len(clean), historical_clean_l_star_range=clean_range,
                   photographic_rows=14, photographic_l_star_range=ppr_range,
                   photographic_outside_current_range=outside(current_range),
                   photographic_outside_historical_clean_range=outside(clean_range),
                   candidate_rows=30, candidate_subjects=10, candidate_conditions=3,
                   final_holdout_groups_disjoint=True, photo_bytes_read=0, model_calls=0, fits=0,
                   synthetic_variants_excluded=True, reserved_fitting_rows_excluded=True,
                   candidate_illumination_name_is_not_measured_brightness=True,
                   training_admitted=False, calibration_admitted=False, runtime_adopted=False)
    plan = dict(status='prepared_not_executed', roster='candidate_roster_PRIVATE.json',
                question='Do these real matched 1200 captures provide brighter valid facial measurements?',
                all_30_attempts_required=True, replacement_or_success_only_selection=False,
                first_step='Verify exact 30 inherited image hashes before decoding/inference.',
                pipeline='Existing fixed native YuNet 0.85, native square context 1.5, parser and FaceOcc; retain all failures.',
                restrictions=['No borrowing 600-image masks, strokes or face boxes.',
                              'No threshold, crop, parser or guard rescue; no fits or MST predictions.',
                              'Review actual support and measured Lab/ITA before proposing annotation or calibration admission.',
                              'No other subjects, poses, conditions or locked photos.'],
                user_annotation_required_now=False)
    for name, value in [('summary_PRIVATE.json', summary), ('candidate_roster_PRIVATE.json', candidates),
                        ('proposed_screen_PRIVATE.json', plan), ('metadata_bindings_PRIVATE.json', bindings)]:
        (OUT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
