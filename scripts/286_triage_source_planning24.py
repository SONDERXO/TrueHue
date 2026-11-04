"""Inspect existing training derivatives only; no mask or model changes."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.data_preparation.redesign_access import training_candidate
from src.data_preparation.color_reference_quality import assess_color_reference
from src.utilities.config import get_config

BASE = ROOT / get_config().OUTPUTS_ROOT
OUT = BASE / 'source_planning24_triage_v1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    hashes = {}

    def read(path):
        raw = path.read_bytes()
        hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    inventory = BASE / 'independent_source_inventory_v1'
    v = read(inventory / 'verification.json')
    for name, sha in v['output_sha256'].items():
        assert hashlib.sha256((inventory/name).read_bytes()).hexdigest() == sha
    selected = read(inventory / 'planning24.json')
    manifest = read(BASE / 'correction_data_redesign_v1/selection.json')
    policy = read(BASE / 'correction_data_redesign_v1/access_policy.json')
    preparation = BASE / 'correction_training_preparation_v1'
    verification = read(preparation / 'verification.json')
    attempts_path = preparation / 'attempts.jsonl'
    raw = attempts_path.read_bytes()
    hashes[attempts_path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
    assert hashes[attempts_path.relative_to(ROOT).as_posix()] == verification['evidence_sha256']['attempts.jsonl']
    attempts = {r['image_id']: r for r in map(json.loads, raw.decode().splitlines())}
    OUT.mkdir()
    rows, boards = [], []
    for item in selected:
        image_id = item['image_id']
        training_candidate(image_id, manifest, policy)
        assert item['duplicate_status'] == 'screen_clear_unreviewed'
        assert not item['in_current_26'] and not item['scoped_review_evidence']
        record = attempts[image_id]
        source_id = record['source_id']
        board_path = preparation / 'boards' / f'{source_id}.png'
        ref_path = preparation / 'images' / f'{source_id}_reference.png'
        with (OUT/'access_ledger.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(dict(image_id=image_id, role='train',
                phase='assistant_source_quality_triage_existing_derivatives',
                files=[p.relative_to(ROOT).as_posix() for p in (board_path, ref_path)],
                raw_source_opened=False, human_review_decision='not_requested'))+'\n')
        for path in (board_path, ref_path):
            key = path.relative_to(preparation).as_posix()
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            assert sha == verification['evidence_sha256'][key]
            hashes[path.relative_to(ROOT).as_posix()] = sha
        board, reference = cv2.imread(str(board_path)), cv2.imread(str(ref_path))
        assert board is not None and reference is not None
        boards.append(board)
        rows.append(dict(image_id=image_id, source_id=source_id,
            original_processing_status=record['status'],
            reference_check=assess_color_reference(reference),
            distorted_failure=record.get('input_measurement', {}).get('reason'),
            experimental_severity=record.get('assigned_severity'),
            clipping_fraction=record.get('clipping_fraction'),
            board_path=board_path.relative_to(ROOT).as_posix(),
            board_sha256=hashes[board_path.relative_to(ROOT).as_posix()],
            missing_judgments=['reference suitability', 'exact reference mask',
                'exact distorted mask if technically available'],
            assistant_visual_observation='pending', human_decision='not_requested',
            training_admitted=False))
    for i in range(6):
        sheet = np.vstack(boards[i*4:i*4+4])
        assert cv2.imwrite(str(OUT/f'sheet_{i+1}.png'), sheet)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in hashes.items())
    (OUT/'triage.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    summary = dict(status='technical_triage_visual_observations_pending', sources=len(rows),
        processing_status=dict(Counter(r['original_processing_status'] for r in rows)),
        reference_checks=dict(Counter(r['reference_check']['status'] for r in rows)),
        raw_images_opened=0, existing_derivative_files_decoded=48,
        reserved_role_pixel_access=0, new_training_admissions=0, model_fits=0,
        new_human_reviews_requested=0, input_sha256=hashes)
    (OUT/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__ == '__main__':
    main()
