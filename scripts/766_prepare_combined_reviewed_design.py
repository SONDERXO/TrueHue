"""Prepare a fixed sixty-row subject-held design; no model imports or fits."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.demo.labelled_measurement import verify

OUT = ROOT / 'outputs/combined_reviewed_mst_design_v1'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve prior or partial design')
    bound = {}

    def read(path):
        path = Path(path)
        raw = path.read_bytes()
        bound[str(path)] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    def write(name, value):
        (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')

    methods = [read(ROOT / 'outputs' / q / 'method.json') for q in
               ('labelled_measurement_queue_v1', 'brightness_measurement_queue_v1')]
    ignored = {'upstream_contract', 'implementation_sha256'}
    assert {k: v for k, v in methods[0]['method'].items() if k not in ignored} == {
        k: v for k, v in methods[1]['method'].items() if k not in ignored}
    for relative in ('src/demo/labelled_measurement.py', 'src/demo/manual_brush.py', 'src/ita_estimation/compute_ita.py'):
        path = ROOT / relative
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert all(m['method']['implementation_sha256'][str(path)] == digest for m in methods)
        bound[str(path)] = digest
    core = read(ROOT / 'outputs/reviewed_feature_control_contract_v1/execution_plan_PRIVATE.json')
    for relative, expected in core['core']['implementation_sha256'].items():
        path = ROOT / relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        bound[str(path)] = expected
    rows = read(ROOT / 'outputs/reviewed_feature_control_contract_v1/calibration_rows_PRIVATE.json')
    audits = [read(ROOT / 'outputs' / p / 'audit_PRIVATE.json') for p in
              ('labelled_annotation_audit_v2', 'brightness_annotation_audit_v1')]
    for audit in audits:
        assert audit['passed_integrity'] and not audit['summary']['missing_cases']
    old_by_case = {r['case_id']: r for r in rows}
    fresh = []
    for index, audit in enumerate(audits):
        for item in audit['coverage']:
            latest = item['latest']
            folder = Path(latest['annotation'])
            verify(folder)
            record = read(folder / 'annotation.json')
            task = record['task']
            queue = 'labelled_measurement_queue_v1' if index == 0 else 'brightness_measurement_queue_v1'
            task_folder = ROOT / 'outputs' / queue / item['case_id']
            verify(task_folder)
            assert read(task_folder / 'task.json') == task
            assert hashlib.sha256((folder / 'manifest.json').read_bytes()).hexdigest() == latest['manifest_sha256']
            assert hashlib.sha256((task_folder / 'manifest.json').read_bytes()).hexdigest() == record['task_manifest_sha256']
            assert record['review'] == 'reviewed_selection' and record['statistics']['valid']
            im_path, mask_path = task_folder / 'image.png', folder / 'measurement_mask.png'
            for path in (im_path, mask_path, folder / 'manifest.json', task_folder / 'manifest.json'):
                bound[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
            im, mask = cv2.imread(str(im_path)), cv2.imread(str(mask_path), 0)
            lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
            lab[:, :, 0] *= 100 / 255
            lab[:, :, 1:] -= 128
            selected = lab[mask > 0]
            means = [round(float(selected[:, i].mean()), 4) for i in range(3)]
            values = dict(zip(('mean_l_star', 'mean_a_star', 'mean_b_star'), means))
            values['ita_degrees'] = round(math.degrees(math.atan((means[0] - 50) / means[2])), 4)
            assert all(record['statistics'][k] == v for k, v in values.items()) and len(selected) >= 1000
            features = {'input_' + k: v for k, v in values.items()}
            row = dict(case_id=task['case_id'], subject_id=task['subject_id'], condition=task['condition'],
                       source_mst_exact_decimal=task['reference_mst_exact_decimal'], source_sha256=task['source_sha256'],
                       measurement_method_sha256=task['method_sha256'], measurement_core_sha256=core['core_sha256'],
                       annotation_manifest_sha256=latest['manifest_sha256'], task_manifest_sha256=record['task_manifest_sha256'],
                       annotation_folder=str(folder), features=features, status='available', user_review='reviewed_selection',
                       input_bridge=task['input_bridge'], training_admitted=False, calibration_admitted=False,
                       shared_core_scope='computation_only_not_empirical_transfer', illumination='600' if index == 0 else '1200')
            if index == 0:
                original = old_by_case[row['case_id']]
                for k in ('subject_id', 'condition', 'source_sha256', 'source_mst_exact_decimal', 'features', 'annotation_manifest_sha256'):
                    assert row[k] == original[k]
            fresh.append(row)
    assert len(fresh) == len({r['case_id'] for r in fresh}) == len({r['source_sha256'] for r in fresh}) == 60
    subjects = sorted({r['subject_id'] for r in fresh})
    assert len(subjects) == 10 and set(Counter(r['condition'] for r in fresh).values()) == {10}
    locked = {r['subject_key'] for r in read(ROOT / 'outputs/group_diversity_candidates_v1/plan_PRIVATE.json')['groups']
              if r['role'] == 'closed_holdout_candidate'}
    assert set(subjects).isdisjoint(locked)
    prior = read(ROOT / 'outputs/reviewed_contextual_validation_v1/results_PRIVATE.json')
    old_folds = {f['held_subject']: f for f in prior['folds']}
    folds = []
    for subject in subjects:
        held = [r for r in fresh if r['subject_id'] == subject]
        fitting = [r for r in fresh if r['subject_id'] != subject]
        assert len(held) == 6 and len(fitting) == 54
        assert len({r['source_mst_exact_decimal'] for r in held}) == 1
        comparator = old_folds[subject]
        assert set(comparator['fitting_subjects']) == set(subjects) - {subject}
        assert len(comparator['fitting_cases']) == 27
        folds.append(dict(held_subject=subject, fitting_subjects=sorted(set(subjects)-{subject}),
                          fitting_cases=[r['case_id'] for r in fitting], evaluation_cases=[r['case_id'] for r in held],
                          fitting_weights={r['case_id']: 1/6 for r in fitting},
                          saved_600_only_comparator=comparator))
    plan = dict(status='prepared_not_executed', candidate='fixed_ITA_L_a_b_subject_weighted_standardized_ridge_alpha1',
                features=['input_ita_degrees', 'input_mean_l_star', 'input_mean_a_star', 'input_mean_b_star'],
                alpha=1., planned_fits=10, planned_candidate_predictions=60, planned_saved_model_predictions=60,
                comparator='Saved matching-subject-held 600-only models, unchanged; no comparator refits.',
                baseline='Median of nine fitting-subject decimal scores, no held labels.',
                training_scaling='Fitting rows only; each subject total weight1; row weight1/6.',
                clipping='Retain raw prediction; clip to [1,10] without category rounding.',
                prospective_checks=['All60 predictions/all10 subjects/all6 conditions.',
                    'Combined60 equal-subject MAE strictly below both frozen-model comparator and fitting-subject median.',
                    'New1200 equal-subject MAE strictly below the frozen600-model comparator on those same30 rows.',
                    'Each old600 condition MAE no worse than its saved contextual value.',
                    'Combined60 maximum absolute error no worse than frozen-model comparator on same60.',
                    'Old600 maximum absolute error no worse than its saved contextual value.'],
                comparison_tolerance=1e-12, saved_600_condition_limits={k:v['image_MAE'] for k,v in prior['by_condition'].items()},
                saved_600_maximum_error_limit=prior['metrics']['maximum_absolute_error'],
                report=['Allraw/clipped/errors; six conditions; two illumination levels; subjects; clips; within-subject ranges; fitting marginal support.'],
                all_data_fit=False, PPR_prediction=False, tree_fit=False, runtime_change=False,
                execution_authorized_by_this_preparation=False, new_fits=0, new_predictions=0,
                upper_photographic_brightness_transfer_established=False)
    OUT.mkdir()
    write('rows_PRIVATE.json', fresh)
    write('folds_PRIVATE.json', folds)
    write('proposed_validation_PRIVATE.json', plan)
    write('measurement_compatibility_PRIVATE.json', dict(shared_core_sha256=core['core_sha256'],
         original_methods=[m['method_sha256'] for m in methods], method_identities_preserved=True,
         upstream_contracts_differ=True, exact_computational_replays=60, empirical_transfer_proven=False,
         photograph_bytes_read=0, cached_annotated_images_read=60, model_calls=0, fits=0))
    write('input_sha256_PRIVATE.json', bound)
    print('Prepared60 exact reviewed rows,10 subject-held54/6 folds; zero fits/predictions.')


if __name__ == '__main__':
    main()
