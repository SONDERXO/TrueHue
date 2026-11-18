import json
import pytest
from src.demo.photographic_reference_review import sha, save_preference, latest_preferences, verify_bundle


def task(tmp_path):
    folder = tmp_path / 'generated_pair'
    folder.mkdir()
    (folder / 'source.png').write_bytes(b'generated_source_placeholder')
    (folder / 'target.png').write_bytes(b'generated_target_placeholder')
    (folder / 'task.json').write_text(json.dumps(dict(frame='generated_904', generated_fixture=True,
        correct_person_pair=False, historical_issue='wrong_person', calibration_admitted=False, training_admitted=False)))
    (folder / 'manifest.json').write_text(json.dumps(dict(files={p.name: dict(sha256=sha(p), bytes=p.stat().st_size)
        for p in folder.iterdir() if p.is_file()})))
    return folder


def test_style_acceptance_cannot_override_person_or_training_failure(tmp_path):
    folder = task(tmp_path)
    before = {p.name: sha(p) for p in folder.iterdir()}
    out = save_preference(folder, sha(folder / 'manifest.json'), 'suitable', 'appearance only', tmp_path / 'decisions')
    verify_bundle(out)
    record = json.loads((out / 'review.json').read_text())
    assert record['target_appearance_accepted'] and not record['task']['correct_person_pair']
    assert not record['training_admitted'] and not record['calibration_admitted']
    assert {p.name: sha(p) for p in folder.iterdir()} == before


def test_revisions_and_resumed_progress_count_pairs_not_saves(tmp_path):
    folder = task(tmp_path)
    identity = sha(folder / 'manifest.json')
    queue = [dict(manifest_sha256=identity)]
    parent = tmp_path / 'decisions'
    first = save_preference(folder, identity, 'too_bright', '', parent)
    second = save_preference(folder, identity, 'uncertain', 'review again', parent)
    assert first != second and (first / 'review.json').exists()
    latest = latest_preferences(queue, parent)
    assert len(latest) == 1 and latest[identity]['choice'] == 'uncertain'


@pytest.mark.parametrize('failure', ['missing_choice', 'wrong_task', 'changed_preview'])
def test_rejects_unbound_or_implicit_choices(tmp_path, failure):
    folder = task(tmp_path)
    identity = sha(folder / 'manifest.json')
    choice = 'suitable'
    if failure == 'missing_choice':
        choice = ''
    elif failure == 'wrong_task':
        identity = 'another_pair'
    else:
        (folder / 'target.png').write_bytes(b'changed')
    with pytest.raises(ValueError):
        save_preference(folder, identity, choice, '', tmp_path / 'decisions')
    assert not (tmp_path / 'decisions').exists()


def test_tampered_saved_preference_does_not_count_as_review(tmp_path):
    folder = task(tmp_path)
    identity = sha(folder / 'manifest.json')
    out = save_preference(folder, identity, 'too_dark', '', tmp_path / 'decisions')
    (out / 'review.json').write_text('{}')
    with pytest.raises(ValueError):
        latest_preferences([dict(manifest_sha256=identity)], tmp_path / 'decisions')
