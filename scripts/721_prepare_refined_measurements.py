"""Read-only export audit and research preparation; never invokes a model or source photo.

Only the three explicit manual-output roots are enumerated. Dataset metadata is
read for provenance/queue purposes; paths contained in it are never opened.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.demo.manual_refinement import verify_export
from src.demo.manual_brush import refine_masks
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

OUT = ROOT / 'outputs/refined_measurement_preparation_v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')


def main():
    if OUT.exists():
        raise FileExistsError('Preserve existing preparation, including partial attempts')
    OUT.mkdir()
    bound = {}

    def bind(path):
        path = Path(path)
        bound[str(path)] = sha(path)
        return bound[str(path)]

    implementation = {p: bind(ROOT / p) for p in (
        'src/demo/manual_brush.py', 'src/demo/manual_refinement.py',
        'src/demo/current_masking.py', 'src/ita_estimation/compute_ita.py')}
    method = dict(
        schema_version='truehue_manual_assisted_measurement_method_v1',
        status='research_preparation_not_calibration_admission',
        workflow='successful_current_desktop_automatic_start_then_explicit_human_refinement',
        coordinate_policy='desktop_square_256x256_INTER_LINEAR_from_decoded_original',
        upstream_contract='89c7a3963dcc72bfa8c7b73433789b058093131662c88a6d30a7f25d791823fd',
        measurement_region='visible_facial_skin_only_exclude_neck_hair_beard_brows_eyes_lips_mouth_objects',
        review_required=True, protection='locked_additions_unless_explicit_stroke_unlock',
        mask_selection='nonzero_uint8_pixels_no_weights', minimum_pixels=1000,
        colour='decoded_export_BGR_uint8_OpenCV_BGR2LAB_no_new_colour_management',
        lab='float32_L_times_100_over_255_a_minus_128_b_minus_128_mean_round4',
        ita='degrees_atan((rounded_mean_L_minus_50)/rounded_mean_b)_round4_abs_b_ge_1e-6',
        invalid_policy='retain_failure_no_imputation_no_old_lookup_fallback',
        correction_support='separate_not_used_for_facial_measurement',
        calibration='new_compatible_labelled_grouped_validation_required_no_old_coefficients',
        final_predictor='decision_tree_with_ITA_and_compatible_calibrated_MST',
        implementation_sha256=implementation,
        opencv_version=cv2.__version__, numpy_version=np.__version__)
    canonical = json.dumps(method, sort_keys=True, separators=(',', ':')).encode()
    method_id = hashlib.sha256(canonical).hexdigest()
    write('method.json', dict(method=method, method_sha256=method_id))

    folders = sorted((ROOT / 'outputs/manual_mask_refinement_v1').glob('*/manifest.json'))
    folders += sorted((ROOT / 'outputs/manual_editor_sessions').glob('*/manifest.json'))
    # Fixture base is needed only to verify its exclusion and history.
    folders += [ROOT / 'outputs/manual_refinement_gui_fixture_v1/truehue_demo_419251b92835/manifest.json']
    exports = {}
    for path in folders:
        manifest = verify_export(path.parent)
        identity = bind(path)
        for name in manifest['files']:
            bind(path.parent / name)
        exports[identity] = (path.parent, manifest, read(path.parent / 'report.json'))

    attempts = read(ROOT / 'outputs/ffhq_source_preparation_v1/attempts.json')
    bind(ROOT / 'outputs/ffhq_source_preparation_v1/attempts.json')
    records = []
    for identity, (folder, manifest, report) in exports.items():
        if 'manual_refinement' not in report:
            continue
        demo = report['demo']
        manual = report['manual_refinement']
        generated = demo['source_path'].startswith('generated:')
        row = dict(export=str(folder), manifest_sha256=identity, run_id=manifest['run_id'],
                   generated_fixture=generated, method_sha256=method_id,
                   historical_instance_contract=report['measurement_contract_sha256'],
                   source_path=demo['source_path'], source_sha256=demo['source_sha256'],
                   subject_id=None, group_id=None, mst_reference_label=None,
                   correction_reference=None, allocation=None, training_admitted=False,
                   calibration_admitted=False, human_support_review_approved=False)
        payload = read(folder / 'manual_edits.json')
        assert payload['strokes'] == manual['strokes']
        assert payload['base_manifest_sha256'] == manual['base_manifest_sha256']
        parent, _, parent_report = exports[manual['base_manifest_sha256']]
        assert sha(parent / 'report.json') == sha(folder / 'before_refinement_report.json')
        assert parent_report['demo']['run_id'] == manual['previous_run_id']
        for name in ['photo_used.png', 'measurement_mask.png', 'correction_mask.png',
                     'protected_mask.png', 'report.json', 'experimental_correction.png', 'correction_alpha.npy']:
            origin = parent / ('automatic_' + name)
            if not origin.exists():
                origin = parent / name
            assert sha(origin) == sha(folder / ('automatic_' + name))
        row['history_verified'] = True
        if generated:
            row['ineligibility_reasons'] = ['generated_fixture_not_annotation']
            records.append(row)
            continue
        assert report['automatic_measurement_contract_sha256'] == method['upstream_contract']
        images = lambda p: cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        base = [images(parent / name) for name in ('correction_mask.png', 'measurement_mask.png', 'protected_mask.png')]
        image = cv2.imread(str(folder / 'photo_used.png'))
        assert image.shape == (256, 256, 3)
        replay = refine_masks(*(a.tobytes() for a in base), 256, 256, payload['strokes'])
        masks = [images(folder / name) for name in ('correction_mask.png', 'measurement_mask.png', 'protected_mask.png')]
        assert all(a.tobytes() == b for a, b in zip(masks, replay))
        stats = compute_masked_lab_statistics(image, masks[1], 1000)
        assert stats == report['measurement']['statistics'] == manual['measurement_statistics']
        # Separate arithmetic replay, including rounding before the ITA ratio.
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
        lab[:, :, 0] *= 100.0 / 255.0
        lab[:, :, 1:] -= 128.0
        selected = lab[masks[1] > 0]
        means = [round(float(selected[:, k].mean()), 4) for k in range(3)]
        assert means == [stats[k] for k in ('mean_l_star', 'mean_a_star', 'mean_b_star')]
        assert round(math.degrees(math.atan((means[0] - 50) / means[2])), 4) == stats['ita_degrees']
        expected_instance = dict(version='explicit_manual_measurement_v1', image_sha256=sha(folder / 'photo_used.png'),
                                 mask_bytes_sha256=hashlib.sha256(masks[1].tobytes()).hexdigest(),
                                 automatic_contract=method['upstream_contract'])
        assert hashlib.sha256(json.dumps(expected_instance, sort_keys=True).encode()).hexdigest() == row['historical_instance_contract']
        assert report['renderer_parameters_direct_gamma'] == parent_report['renderer_parameters_direct_gamma']
        match = [a for a in attempts if a['access']['sha256'] == demo['source_sha256']]
        assert len(match) == 1
        row.update(source_metadata_id=match[0]['id'], source_metadata_hash_join=True,
                   photo_sha256=sha(folder / 'photo_used.png'), measurement_mask_sha256=sha(folder / 'measurement_mask.png'),
                   measurement_statistics=stats, stroke_count=len(payload['strokes']),
                   change_counts={k: v for k, v in manual.items() if k.endswith('_pixels')},
                   ineligibility_reasons=['support_review_pending', 'reference_MST_label_missing',
                       'verified_subject_group_missing', 'allocation_missing', 'correction_target_missing'])
        records.append(row)

    real = [r for r in records if not r['generated_fixture']]
    parents = {read(Path(r['export']) / 'report.json')['manual_refinement']['previous_run_id'] for r in real}
    for row in real:
        row['latest_available_revision'] = row['run_id'] not in parents
        row['deduplication_key'] = row['source_sha256']
    jobs = []
    for p in sorted((ROOT / 'outputs/manual_editor_jobs').glob('*/edits.json')):
        payload = read(p)
        bind(p)
        result = p.with_name('edits.result.json')
        jobs.append(dict(payload=str(p), base_manifest_sha256=payload['base_manifest_sha256'],
                         result=read(result) if result.exists() else None,
                         status='result_present' if result.exists() else 'missing_result_retained'))
        if result.exists():
            bind(result)
    # Metadata-only queue: retain ALL existing labelled development cases and failures.
    # Native cached geometry is deliberately not admitted into the desktop method.
    plan_path = ROOT / 'outputs/native_mst_measurement_readiness_v1/plan_PRIVATE.json'
    bind(plan_path)
    sources = read(plan_path)['sources']
    assert len(sources) == 30
    queue = [dict(source_metadata=s, status='blocked_coordinate_and_editor_ingestion_design',
                  proposed_role='labelled_development_refinement_candidate_not_admitted',
                  reason='native_cached_pipeline_is_not_desktop_square_method_no_automatic_transfer',
                  training_admitted=False, calibration_admitted=False) for s in sources]
    write('records_PRIVATE.json', records)
    write('jobs_PRIVATE.json', jobs)
    write('labelled_queue_PRIVATE.json', queue)
    for path, expected in bound.items():
        assert sha(path) == expected
    write('verification_PRIVATE.json', dict(passed=True, method_sha256=method_id,
        refined_exports=len(records), generated_excluded=sum(r['generated_fixture'] for r in records),
        photographic_revisions=len(real), unique_photographs=len({r['source_sha256'] for r in real}),
        admitted_records=0, labelled_queue=len(queue), jobs=len(jobs),
        source_original_bytes_read=0, model_calls=0, fits=0, holdout_bytes_read=0,
        scope='explicit_manual_export_roots_and_named_development_metadata_only', input_sha256=bound))
    print(json.dumps(dict(passed=True, photographic_revisions=len(real), unique_photographs=len({r['source_sha256'] for r in real}), admitted=0)))


if __name__ == '__main__':
    main()
