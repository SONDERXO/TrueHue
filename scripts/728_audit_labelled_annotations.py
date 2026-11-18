"""Audit actual saved annotations without opening source photos or fitting models."""
from pathlib import Path
from collections import defaultdict
import json
import math
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.demo.labelled_measurement import digest, verify, write
from src.demo.manual_brush import refine_masks
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

QUEUE = ROOT / 'outputs/labelled_measurement_queue_v1'
OUT = ROOT / 'outputs/labelled_annotation_audit_v1'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve completed or partial audit')
    read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    bound = {}
    def bind(p):
        bound[str(p)] = digest(p)
        return bound[str(p)]
    check = read(QUEUE / 'verification_PRIVATE.json')
    assert check['passed']
    # Verify preparation inputs. Do not hash any source-image path in task metadata.
    for p, h in check['input_sha256'].items():
        assert digest(p) == h
        bound[p] = h
    queue = read(QUEUE / 'queue.json')['tasks']
    tasks = {}
    for row in queue:
        folder = QUEUE / row['task_folder']
        manifest = verify(folder)
        assert bind(folder / 'manifest.json') == row['task_manifest_sha256']
        for name in manifest['files']:
            bind(folder / name)
        tasks[row['task_manifest_sha256']] = (row, folder, read(folder / 'task.json'))
    records = []
    groups = defaultdict(list)
    for path in sorted((ROOT / 'outputs/labelled_measurement_annotations_v1').glob('annotation_*/annotation.json')):
        manifest = verify(path.parent)
        for name in list(manifest['files']) + ['manifest.json']:
            bind(path.with_name(name))
        record = read(path)
        assert not record['generated_fixture']
        row, task_folder, task = tasks[record['task_manifest_sha256']]
        assert record['task'] == task and not task['generated_fixture']
        edits = read(path.with_name('edits.json'))
        assert edits['task_manifest_sha256'] == record['task_manifest_sha256']
        assert edits['review'] == record['review'] and edits.get('note', '') == record['note']
        image = cv2.imread(str(task_folder / 'image.png'))
        seed = cv2.imread(str(task_folder / 'seed.png'), 0)
        mask = cv2.imread(str(path.with_name('measurement_mask.png')), 0)
        assert mask.shape == seed.shape == (256, 256)
        empty = bytes(seed.size)
        _, replay, _ = refine_masks(empty, seed.tobytes(), empty, 256, 256, edits['strokes'])
        assert replay == mask.tobytes()
        stats = compute_masked_lab_statistics(image, mask, 1000)
        assert stats == record['statistics']
        if stats['valid']:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
            selected = mask > 0
            values = [lab[:, :, 0] * (100.0 / 255.0), lab[:, :, 1]-128.0, lab[:, :, 2]-128.0]
            means = [round(float(a[selected].mean()), 4) for a in values]
            assert means == [stats[k] for k in ['mean_l_star', 'mean_a_star', 'mean_b_star']]
            assert round(math.degrees(math.atan((means[0]-50)/means[2])), 4) == stats['ita_degrees']
        assert record['changed_pixels'] == int(np.count_nonzero(mask != seed))
        assert record['stroke_count'] == len(edits['strokes'])
        assert not record['training_admitted'] and not record['calibration_admitted'] and not record['old_lookup_compatible']
        assert record['model_calls'] == 0 and record['allocation'] is None
        expected = 'reviewed_measurement_pending_admission' if record['review'] == 'reviewed_selection' and stats['valid'] else 'unavailable'
        assert record['status'] == expected
        entry = dict(case_id=row['case_id'], annotation=str(path.parent), manifest_sha256=digest(path.with_name('manifest.json')),
            annotation_mtime_ns=path.stat().st_mtime_ns, task_manifest_sha256=record['task_manifest_sha256'],
            review=record['review'], status=record['status'], statistics=stats, stroke_count=record['stroke_count'],
            changed_pixels=record['changed_pixels'], note=record['note'])
        records.append(entry)
        groups[row['case_id']].append(entry)
    jobs = []
    for path in sorted((ROOT / 'outputs/labelled_measurement_jobs_v1').glob('*/edits.json')):
        edits = read(path)
        row, _, _ = tasks[edits['task_manifest_sha256']]
        bind(path)
        result = path.with_suffix('.result.json')
        saved = read(result)['annotation'] if result.exists() else None
        if result.exists():
            bind(result)
            assert any(str(Path(r['annotation']).resolve()) == str(Path(saved).resolve()) for r in records)
            assert edits == read(Path(saved) / 'edits.json')
        jobs.append(dict(case_id=row['case_id'], payload=str(path), annotation=saved,
                         status='saved' if result.exists() else 'missing_result_retained'))
    OUT.mkdir()
    latest = {}
    for case, revisions in groups.items():
        order = sorted(revisions, key=lambda r: r['annotation_mtime_ns'])
        assert len({r['annotation_mtime_ns'] for r in order}) == len(order), 'Ambiguous revision order'
        latest[case] = order[-1]
    coverage = []
    subjects = defaultdict(list)
    def overlay(image, mask):
        shown = image.copy()
        selected = mask > 0
        shown[selected] = np.rint(.65*shown[selected] + .35*np.array([0, 255, 0])).astype(np.uint8)
        return shown
    boards = []
    for row, task_folder, task in tasks.values():
        case = row['case_id']
        entry = latest.get(case)
        item = dict(case_id=case, subject_id=task['subject_id'], condition=task['condition'],
            reference_mst_exact_decimal=task['reference_mst_exact_decimal'], historical_status=task['historical_status'],
            review_saved=entry is not None, latest=entry, allocation=None, calibration_admitted=False,
            training_admitted=False, automatic_start=task['seed_origin'])
        coverage.append(item)
        subjects[task['subject_id']].append(item)
        image = cv2.imread(str(task_folder / 'image.png'))
        seed = cv2.imread(str(task_folder / 'seed.png'), 0)
        final = cv2.imread(str(Path(entry['annotation']) / 'measurement_mask.png'), 0) if entry else None
        panel = np.hstack([image, overlay(image, seed), overlay(image, final) if final is not None else np.full_like(image, 70)])
        header = np.full((32, 768, 3), 255, np.uint8)
        cv2.putText(header, case + (' SAVED' if entry else ' NO SAVED REVIEW') + ' | photo / automatic seed / manual selection',
                    (5, 21), cv2.FONT_HERSHEY_SIMPLEX, .46, (0, 0, 0), 1)
        board = np.vstack([header, panel])
        cv2.imwrite(str(OUT / (case + '.png')), board)
        boards.append(board)
    for start in range(0, len(boards), 5):
        cv2.imwrite(str(OUT / ('sheet_%02d.png' % (start//5))), np.vstack(boards[start:start+5]))
    summary = dict(saved_revisions=len(records), distinct_saved_cases=len(latest), total_cases=len(tasks),
        missing_cases=[r['case_id'] for r in coverage if not r['review_saved']],
        subjects_with_saved_review=sum(any(r['review_saved'] for r in rows) for rows in subjects.values()),
        subjects_all_three_saved=sum(all(r['review_saved'] for r in rows) for rows in subjects.values()),
        valid_latest=sum(r['statistics']['valid'] for r in latest.values()),
        reviewed_selection_latest=sum(r['review'] == 'reviewed_selection' for r in latest.values()),
        unjudgeable_latest=sum(r['review'] == 'unjudgeable' for r in latest.values()),
        failed_jobs=sum(r['status'] != 'saved' for r in jobs), jobs=len(jobs),
        calibration_ready=False, reason='incomplete_saved_review_coverage_and_support_review_pending',
        revision_selection='latest_annotation_json_mtime_ns_matching_UI_no_ties_all_revisions_retained',
        original_source_image_reads=0, model_calls=0, fits=0, holdout_bytes_read=0)
    for p in [Path(__file__), QUEUE / 'queue.json', QUEUE / 'method.json', QUEUE / 'verification_PRIVATE.json']:
        bind(p)
    assert all(digest(p) == h for p, h in bound.items())
    write(OUT / 'audit_PRIVATE.json', dict(summary=summary, coverage=coverage, revisions=records, jobs=jobs,
                                          input_sha256=bound, passed_integrity=True))
    write(OUT / 'artifact_sha256_PRIVATE.json', {p.name: digest(p) for p in OUT.iterdir() if p.is_file()})
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
