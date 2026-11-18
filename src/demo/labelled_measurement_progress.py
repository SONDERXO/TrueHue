"""Stdlib-only saved-review progress; counts tasks, never annotation revisions."""
from pathlib import Path
import hashlib
import json


def saved_reviews(queue, annotations_parent):
    known = {r['task_manifest_sha256'] for r in queue}
    saved = set()
    for path in Path(annotations_parent).glob('annotation_*/annotation.json'):
        record = json.loads(path.read_text(encoding='utf-8'))
        task = record.get('task_manifest_sha256')
        if task not in known:
            continue
        manifest = json.loads(path.with_name('manifest.json').read_text(encoding='utf-8'))
        for name in ('annotation.json', 'edits.json', 'measurement_mask.png'):
            evidence = path.with_name(name)
            item = manifest['files'][name]
            if evidence.is_symlink() or hashlib.sha256(evidence.read_bytes()).hexdigest() != item['sha256'] or evidence.stat().st_size != item['bytes']:
                raise ValueError('Saved review evidence changed: ' + str(evidence))
        if record.get('review') in ('reviewed_selection', 'unjudgeable'):
            saved.add(task)
    return saved


def first_unsaved(queue, saved):
    return next((i for i, row in enumerate(queue) if row['task_manifest_sha256'] not in saved), 0)
