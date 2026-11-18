"""Isolated research annotation of cached labelled measurements. No predictors."""
from pathlib import Path
import hashlib
import json
import uuid

import cv2
import numpy as np

from src.demo.manual_brush import refine_masks
from src.ita_estimation.compute_ita import compute_masked_lab_statistics


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')


def seal(folder):
    folder = Path(folder)
    write(folder / 'manifest.json', dict(schema_version='truehue_labelled_measurement_bundle_v1',
        files={p.name: dict(sha256=digest(p), bytes=p.stat().st_size)
               for p in folder.iterdir() if p.is_file() and p.name != 'manifest.json'}))


def verify(folder):
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 'truehue_labelled_measurement_bundle_v1':
        raise ValueError('Known research bundle required')
    if {p.name for p in folder.iterdir()} != set(manifest['files']) | {'manifest.json'}:
        raise ValueError('Bundle membership changed')
    for name, item in manifest['files'].items():
        if Path(name).name != name or '/' in name or '\\' in name:
            raise ValueError('Local bundle filenames required')
        path = folder / name
        if path.is_symlink() or not path.is_file() or digest(path) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('Bundle evidence changed: ' + name)
    return manifest


def save_annotation(task_folder, payload, output_parent):
    task_folder = Path(task_folder)
    verify(task_folder)
    task_hash = digest(task_folder / 'manifest.json')
    if payload.get('schema_version') != 'truehue_labelled_measurement_edits_v1' or payload.get('task_manifest_sha256') != task_hash:
        raise ValueError('Edits must bind the research task')
    review = payload.get('review')
    if review not in ('reviewed_selection', 'unjudgeable'):
        raise ValueError('Explicit selection review or unjudgeable decision required')
    if not isinstance(payload.get('note', ''), str):
        raise ValueError('Review note must be text')
    task = json.loads((task_folder / 'task.json').read_text(encoding='utf-8'))
    image = cv2.imread(str(task_folder / 'image.png'))
    seed = cv2.imread(str(task_folder / 'seed.png'), 0)
    if image is None or seed is None or image.shape != (256, 256, 3) or seed.shape != (256, 256):
        raise ValueError('Matching normalized research image and seed required')
    strokes = payload.get('strokes')
    if not isinstance(strokes, list) or any(s.get('target') != 'measurement' or s.get('unlock', False) for s in strokes if isinstance(s, dict)):
        raise ValueError('Measurement-only annotation strokes required')
    empty = bytes(seed.size)
    _, mask_bytes, _ = refine_masks(empty, seed.tobytes(), empty, 256, 256, strokes)
    mask = np.frombuffer(mask_bytes, np.uint8).reshape(256, 256)
    stats = compute_masked_lab_statistics(image, mask, 1000)
    status = 'reviewed_measurement_pending_admission' if review == 'reviewed_selection' and stats['valid'] else 'unavailable'
    report = dict(schema_version='truehue_labelled_manual_measurement_v1',
        task=task, task_manifest_sha256=task_hash, review=review, note=payload.get('note', ''),
        status=status, reason=('user_unjudgeable' if review == 'unjudgeable' else stats['reason']),
        statistics=stats, changed_pixels=int(np.count_nonzero(mask != seed)),
        stroke_count=len(strokes), calibration_admitted=False, training_admitted=False,
        old_lookup_compatible=False, model_calls=0, allocation=None,
        generated_fixture=task.get('generated_fixture', False))
    verify(task_folder)
    if digest(task_folder / 'manifest.json') != task_hash:
        raise ValueError('Task changed during review')
    folder = Path(output_parent) / ('annotation_' + uuid.uuid4().hex)
    folder.mkdir(parents=True, exist_ok=False)
    write(folder / 'annotation.json', report)
    write(folder / 'edits.json', payload)
    if not cv2.imwrite(str(folder / 'measurement_mask.png'), mask):
        raise OSError('Cannot save measurement mask')
    seal(folder)
    verify(folder)
    return folder
