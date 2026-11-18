"""Stdlib-only, immutable user preference records for photographic references."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import uuid

CHOICES = ('suitable', 'too_bright', 'too_dark', 'other_concern', 'uncertain')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_bundle(folder):
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if {p.name for p in folder.iterdir()} != set(manifest['files']) | {'manifest.json'}:
        raise ValueError('Review bundle membership changed')
    for name, item in manifest['files'].items():
        if Path(name).name != name or '/' in name or '\\' in name:
            raise ValueError('Local review files required')
        path = folder / name
        if path.is_symlink() or not path.is_file() or sha(path) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('Review evidence changed: ' + name)
    return manifest


def save_preference(folder, expected_manifest, choice, note, output_parent):
    folder = Path(folder)
    verify_bundle(folder)
    if sha(folder / 'manifest.json') != expected_manifest:
        raise ValueError('Review belongs to another photographic pair')
    if choice not in CHOICES or not isinstance(note, str):
        raise ValueError('Explicit reference appearance choice and text note required')
    task = json.loads((folder / 'task.json').read_text(encoding='utf-8'))
    record = dict(schema_version='truehue_photographic_reference_preference_v1',
        saved_utc=datetime.now(timezone.utc).isoformat(), frame=task['frame'],
        task_manifest_sha256=expected_manifest, task=task, choice=choice, note=note,
        target_appearance_accepted=choice == 'suitable',
        scope='reference_appearance_preference_only_not_mask_or_registration_approval',
        calibration_admitted=False, training_admitted=False, model_calls=0)
    dest = Path(output_parent) / ('review_' + uuid.uuid4().hex)
    dest.mkdir(parents=True, exist_ok=False)
    (dest / 'review.json').write_text(json.dumps(record, indent=2, allow_nan=False), encoding='utf-8')
    path = dest / 'review.json'
    (dest / 'manifest.json').write_text(json.dumps(dict(files={'review.json': dict(sha256=sha(path), bytes=path.stat().st_size)}), indent=2), encoding='utf-8')
    verify_bundle(dest)
    return dest


def latest_preferences(queue, output_parent):
    known = {r['manifest_sha256'] for r in queue}
    latest = {}
    for path in Path(output_parent).glob('review_*/review.json'):
        verify_bundle(path.parent)
        row = json.loads(path.read_text(encoding='utf-8'))
        key = row['task_manifest_sha256']
        if key in known:
            if key not in latest or row['saved_utc'] > latest[key]['saved_utc']:
                latest[key] = row
    return latest
