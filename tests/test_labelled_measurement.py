import json

import cv2
import numpy as np
import pytest

from src.demo.labelled_measurement import digest, write, seal, verify, save_annotation
from src.demo.labelled_measurement_progress import saved_reviews, first_unsaved


def task(tmp_path, empty=False):
    folder = tmp_path / 'generated_task'
    folder.mkdir()
    image = np.full((256, 256, 3), [90, 120, 160], np.uint8)
    seed = np.zeros((256, 256), np.uint8)
    if not empty:
        seed[50:150, 50:150] = 255
    assert cv2.imwrite(str(folder / 'image.png'), image)
    assert cv2.imwrite(str(folder / 'seed.png'), seed)
    write(folder / 'task.json', dict(case_id='generated_only', generated_fixture=True,
        subject_id='generated_group', reference_mst_exact_decimal='4.2', method_sha256='generated_method'))
    seal(folder)
    return folder


def payload(folder, review='reviewed_selection', strokes=None):
    return dict(schema_version='truehue_labelled_measurement_edits_v1',
        task_manifest_sha256=digest(folder / 'manifest.json'), review=review,
        strokes=[] if strokes is None else strokes, note='generated test')


def test_explicit_unchanged_review_preserves_task_and_never_admits(tmp_path):
    folder = task(tmp_path)
    before = {p.name: p.read_bytes() for p in folder.iterdir()}
    result = save_annotation(folder, payload(folder), tmp_path / 'annotations')
    verify(result)
    record = json.loads((result / 'annotation.json').read_text())
    assert record['status'] == 'reviewed_measurement_pending_admission'
    assert record['generated_fixture'] and record['statistics']['skin_pixels'] == 10000
    assert record['task']['subject_id'] == 'generated_group'
    assert record['task']['reference_mst_exact_decimal'] == '4.2'
    assert not record['calibration_admitted'] and not record['training_admitted']
    assert not record['old_lookup_compatible'] and record['model_calls'] == 0
    assert {p.name: p.read_bytes() for p in folder.iterdir()} == before
    again = save_annotation(folder, payload(folder), tmp_path / 'annotations')
    assert again != result and (result / 'annotation.json').exists()


def test_empty_and_unjudgeable_are_saved_failures(tmp_path):
    folder = task(tmp_path, empty=True)
    for review in ['reviewed_selection', 'unjudgeable']:
        result = save_annotation(folder, payload(folder, review), tmp_path / 'annotations')
        record = json.loads((result / 'annotation.json').read_text())
        assert record['status'] == 'unavailable' and not record['statistics']['valid']
        assert not record['calibration_admitted']
        if review == 'unjudgeable':
            assert record['reason'] == 'user_unjudgeable'


def test_manually_added_skin_from_empty_is_not_automatic_success(tmp_path):
    folder = task(tmp_path, empty=True)
    strokes = [dict(target='measurement', mode='add', radius=24, unlock=False, points=[[100, 100]])]
    result = save_annotation(folder, payload(folder, strokes=strokes), tmp_path / 'annotations')
    record = json.loads((result / 'annotation.json').read_text())
    assert record['statistics']['skin_pixels'] > 1000
    assert record['changed_pixels'] == record['statistics']['skin_pixels']
    assert record['stroke_count'] == 1 and not record['training_admitted']


@pytest.mark.parametrize('change', ['tamper', 'injected_member', 'wrong_task', 'no_review', 'correction_stroke'])
def test_integrity_and_scoped_review_rejections(tmp_path, change):
    folder = task(tmp_path)
    edits = payload(folder)
    if change == 'tamper':
        (folder / 'seed.png').write_bytes(b'changed')
    elif change == 'injected_member':
        (folder / 'injected.json').write_text('{}')
    elif change == 'wrong_task':
        edits['task_manifest_sha256'] = 'another_task'
    elif change == 'no_review':
        edits.pop('review')
    else:
        edits['strokes'] = [dict(target='correction', mode='add', radius=4, points=[[100, 100]])]
    with pytest.raises(ValueError):
        save_annotation(folder, edits, tmp_path / 'annotations')
    assert not (tmp_path / 'annotations').exists()


def test_progress_counts_reviews_not_revisions_and_resumes_first_missing(tmp_path):
    folder = task(tmp_path)
    actual_hash = digest(folder / 'manifest.json')
    queue = [dict(task_manifest_sha256=actual_hash), dict(task_manifest_sha256='missing')]
    parent = tmp_path / 'annotations'
    assert first_unsaved(queue, saved_reviews(queue, parent)) == 0
    save_annotation(folder, payload(folder), parent)
    save_annotation(folder, payload(folder), parent)
    saved = saved_reviews(queue, parent)
    assert saved == {actual_hash} and first_unsaved(queue, saved) == 1


def test_unjudgeable_is_completed_review_but_tampered_review_is_rejected(tmp_path):
    folder = task(tmp_path, empty=True)
    queue = [dict(task_manifest_sha256=digest(folder / 'manifest.json'))]
    parent = tmp_path / 'annotations'
    result = save_annotation(folder, payload(folder, 'unjudgeable'), parent)
    assert len(saved_reviews(queue, parent)) == 1
    (result / 'measurement_mask.png').write_bytes(b'changed')
    with pytest.raises(ValueError):
        saved_reviews(queue, parent)
