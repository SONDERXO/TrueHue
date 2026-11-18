"""Fixed30 cached development annotation tasks; no original-photo or model reads."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.demo.labelled_measurement import digest, write, seal, verify

OLD = ROOT / 'outputs/native_mst_measurement_readiness_v1'
OUT = ROOT / 'outputs/labelled_measurement_queue_v1'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve existing queue or partial preparation')
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    inventory = {k.replace('\\', '/'): v for k, v in read(OLD / 'artifact_sha256_PRIVATE.json').items()}
    bound = {}

    def historical(name):
        path = OLD / name
        expected = inventory[name]
        if digest(path) != expected:
            raise ValueError('Historical cached evidence changed: ' + name)
        bound[str(path)] = expected
        return path

    results = read(historical('results_PRIVATE.json'))
    plan = read(historical('plan_PRIVATE.json'))
    verification = read(OLD / 'verification_PRIVATE.json')
    assert verification['passed']
    for path in [OLD / 'verification_PRIVATE.json', OLD / 'artifact_sha256_PRIVATE.json',
                 ROOT / 'docs/labelled-manual-measurement-protocol-2026-11-10.md', Path(__file__),
                 ROOT / 'src/demo/labelled_measurement.py', ROOT / 'src/demo/manual_brush.py',
                 ROOT / 'src/ita_estimation/compute_ita.py']:
        bound[str(path)] = digest(path)
    rows = results['records']
    assert len(rows) == 30 and len({r['subject_id'] for r in rows}) == 10
    assert all(r['cohort'] == 'development' for r in rows)
    assert {r['source_case'] for r in rows} == {r['source_case'] for r in plan['sources']}
    method = dict(schema_version='truehue_native_manual_measurement_method_v1',
        upstream_contract=results['measurement_contract_sha256'],
        coordinates='cached_native_anchor_square_context_1p5_normalized_256_input_exact',
        workflow='human_review_or_annotation_from_empty_when_no_saved_measurement',
        region='visible_facial_skin_exclude_neck_hair_beard_brows_eyes_lips_mouth_objects',
        automatic_seed='exact_saved_mask_if_present_otherwise_explicit_empty',
        protection='full_manual_annotation_no_cached_protection_mask_available',
        minimum_pixels=1000, measurement='compute_masked_lab_statistics_BGR_uint8_OpenCV_Lab_float32_round4_ITA',
        implementation_sha256={k: v for k, v in bound.items() if k.endswith('.py')},
        opencv_version=cv2.__version__, numpy_version=np.__version__,
        desktop_method_compatible=False, old_lookup_compatible=False)
    method_id = hashlib.sha256(json.dumps(method, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    # Preflight all inputs before creating tasks. Never follow source_path.
    paths = {}
    for row in rows:
        case = row['source_case']
        assert case.startswith('case_') and '/' not in case and '\\' not in case
        image = historical(case + '/input.png')
        seed_name = case + '/measurement_mask.png'
        seed = historical(seed_name) if seed_name in inventory else None
        paths[case] = image, seed
    OUT.mkdir()
    write(OUT / 'method.json', dict(method=method, method_sha256=method_id))
    queue = []
    for row in rows:
        case = row['source_case']
        image, seed = paths[case]
        im = cv2.imread(str(image))
        assert im.shape == (256, 256, 3)
        mask = cv2.imread(str(seed), 0) if seed else np.zeros((256, 256), np.uint8)
        assert mask.shape == (256, 256) and set(np.unique(mask)) <= {0, 255}
        folder = OUT / case
        folder.mkdir()
        (folder / 'image.png').write_bytes(image.read_bytes())
        if seed:
            (folder / 'seed.png').write_bytes(seed.read_bytes())
        else:
            assert cv2.imwrite(str(folder / 'seed.png'), mask)
        task = dict(case_id=case, method_sha256=method_id, generated_fixture=False,
            source_sha256=row['source_sha256'], source_path_metadata_only=row['source_path'],
            subject_id=row['subject_id'], condition=row['condition'],
            reference_mst_exact_decimal=row['source_mst_exact_decimal'],
            historical_status=row['status'], historical_reason=row.get('reason'),
            seed_origin='historical_measurement_mask' if seed else 'empty_manual_annotation_start',
            cached_image_sha256=digest(image), input_bridge=row['input_bridge'],
            upstream_contract=results['measurement_contract_sha256'],
            allocation=None, calibration_admitted=False, training_admitted=False)
        write(folder / 'task.json', task)
        seal(folder)
        verify(folder)
        queue.append(dict(case_id=case, task_folder=case, task_manifest_sha256=digest(folder / 'manifest.json'),
                          historical_status=row['status'], seed_origin=task['seed_origin'], review='pending'))
    assert all(digest(p) == h for p, h in bound.items())
    write(OUT / 'queue.json', dict(schema_version='truehue_labelled_measurement_queue_v1', tasks=queue,
        method_sha256=method_id, annotations_directory='outputs/labelled_measurement_annotations_v1'))
    write(OUT / 'verification_PRIVATE.json', dict(passed=True, tasks=len(queue), subjects=10,
        historical_unavailable=sum(r['status'] != 'available' for r in rows),
        empty_starts=sum(r['seed_origin'] == 'empty_manual_annotation_start' for r in queue),
        original_image_reads=0, model_calls=0, fits=0, holdout_bytes_read=0,
        input_sha256=bound, tasks_sha256={r['case_id']: r['task_manifest_sha256'] for r in queue}))
    print(json.dumps(dict(tasks=len(queue), empty_starts=sum(r['seed_origin'] == 'empty_manual_annotation_start' for r in queue))))


if __name__ == '__main__':
    main()
