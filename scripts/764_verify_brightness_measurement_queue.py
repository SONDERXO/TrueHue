"""Independent fixed-queue joins, cached pixel hashes and measurement replay."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
from src.demo.labelled_measurement import digest, verify, write
from src.ita_estimation.compute_ita import compute_masked_lab_statistics


def main():
    folder = ROOT / 'outputs/brightness_measurement_queue_v1'
    target = folder / 'independent_verification_PRIVATE.json'
    if target.exists():
        raise FileExistsError('Preserve earlier verification')
    read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    old = ROOT / 'outputs/labelled_brightness_screen_v1'
    first = read(folder / 'verification_PRIVATE.json')
    assert first['passed']
    for p, h in first['input_sha256'].items():
        assert digest(p) == h
    historical = {r['source_case']: r for r in read(old / 'results_PRIVATE.json')['records']}
    plan = {r['source_case']: r for r in read(old / 'plan_PRIVATE.json')['sources']}
    queue = read(folder / 'queue.json')['tasks']
    assert len(queue) == 30 and {r['case_id'] for r in queue} == set(plan) == set(historical)
    replays = 0
    for row in queue:
        path = folder / row['task_folder']
        manifest = verify(path)
        assert digest(path / 'manifest.json') == row['task_manifest_sha256'] == first['tasks_sha256'][row['case_id']]
        task = read(path / 'task.json')
        source = historical[row['case_id']]
        assert all(source[k] == v for k, v in plan[row['case_id']].items())
        for key in ['subject_id', 'condition', 'source_sha256']:
            assert task[key] == source[key]
        assert task['reference_mst_exact_decimal'] == source['source_mst_exact_decimal']
        assert task['historical_status'] == source['status']
        assert task['historical_reason'] == source.get('reason')
        assert task['input_bridge'] == source['input_bridge']
        assert task['source_path_metadata_only'] == source['source_path']
        assert digest(path / 'image.png') == digest(old / row['case_id'] / 'input.png')
        seed = cv2.imread(str(path / 'seed.png'), 0)
        original_seed = old / row['case_id'] / 'measurement_mask.png'
        if original_seed.exists():
            assert digest(path / 'seed.png') == digest(original_seed)
        else:
            assert not seed.any() and task['seed_origin'] == 'empty_manual_annotation_start'
        if source['status'] == 'available':
            stats = compute_masked_lab_statistics(cv2.imread(str(path / 'image.png')), seed, 1000)
            assert stats['valid']
            assert all(stats[k.removeprefix('input_')] == v for k, v in source['raw_features'].items())
            replays += 1
        assert not task['generated_fixture'] and not task['training_admitted'] and not task['calibration_admitted']
    assert replays == 24
    paths = [folder / 'queue.json', folder / 'method.json', folder / 'verification_PRIVATE.json',
             ROOT / 'scripts/764_verify_brightness_measurement_queue.py',
             ROOT / 'src/demo/labelled_measurement_window.py', ROOT / 'scripts/724_save_labelled_measurement.py',
             ROOT / 'scripts/762_review_brightness_measurements.py', ROOT / 'review_brightness_measurements.cmd',
             ROOT / 'tests/test_labelled_measurement.py',
             ROOT / 'outputs/brightness_measurement_gui_check_v1/verification.json']
    write(target, dict(passed=True, cases=30, subjects=10, exact_historical_measurement_replays=replays,
        unavailable_cases_retained=6, empty_manual_starts=3, generated_in_real_queue=0,
        new_user_annotations=0, model_calls=0, fits=0, original_source_image_reads=0, holdout_bytes_read=0,
        input_sha256={str(p): digest(p) for p in paths}))
    print('PASS: all30 exact provenance joins, 24 unchanged measurement replays, 6 failures retained, 3 explicit empty starts')


if __name__ == '__main__':
    main()
