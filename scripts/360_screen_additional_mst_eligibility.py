"""Frozen small stratified additional-subject screen; no calibration/fitting."""
import csv
import hashlib
import importlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.nostril_measurement import contract, measure
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.full_face_support import nostril_guard


def main():
    out = ROOT / 'outputs/additional_mst_eligibility_v1'
    if out.exists():
        raise FileExistsError(out)
    digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    table = ROOT / 'data/raw/mst-e_data/mst-e_image_details.csv'
    protocol = ROOT / 'docs/additional-mst-eligibility-protocol-2026-11-01.md'
    with table.open(encoding='utf-8-sig', newline='') as f:
        official = list(csv.DictReader(f))
    groups = defaultdict(list)
    for r in official:
        if r['subject_name'] in {'subject_1', 'subject_9', 'subject_11', 'subject_10'}:
            groups[(r['subject_name'], r['image_ID'])].append(r)
    assert len(groups) == 337
    strata = defaultdict(list)
    for key, entries in sorted(groups.items()):
        assert all(len({r[f] for r in entries}) == 1 for f in ['MST', 'lighting'])
        r = entries[0]
        r = dict(r, mask='|'.join(sorted({e['mask'] for e in entries})), image_id='mst_e__' + key[0] + '/' + key[1], metadata_rows=entries)
        strata[(r['subject_name'], r['lighting'], r['mask'])].append(r)
    selected = []
    for key, rows in sorted(strata.items()):
        selected.extend(sorted(rows, key=lambda r: hashlib.sha256(('additional-mst-eligibility-v1/' + r['image_id']).encode()).hexdigest())[:2])
    spec, identity = contract(ROOT)
    assert identity == '1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7'
    hashes = {str(p): digest(p) for p in [table, protocol, Path(__file__)]}
    out.mkdir()
    (out / 'plan.json').write_text(json.dumps(dict(status='frozen_before_pixel_reads',
        selected=selected, universe=[dict(subject_id=k[0], image_name=k[1], metadata_rows=v) for k,v in groups.items()],
        input_sha256=hashes, contract=spec, measurement_contract_sha256=identity,
        fits=0, reserved_pixels=0, no_replacement=True), indent=2))
    prepare = importlib.import_module('11_prepare_training_manifests'); config = get_config(); cache = {}
    detector = lambda im: prepare._detect_face_boxes(im, ROOT / config.FACE_MODEL_PATH, .85)
    def landmarks(im, box):
        points, _, _ = prepare.detect_landmarks_with_margin(im, box, ROOT / config.FACE_LANDMARKER_MODEL_PATH)
        cache['points'] = None if points is None else points + np.array(box[:2])
        return cache['points']
    class Parser:
        def __init__(self):
            self.net = DenseFaceParser(ROOT / config.MODELS_ROOT / 'face_parser_experimental_v1/resnet18.onnx')
            self.last = None
        def categories_bgr(self, im):
            self.last = self.net.categories_bgr(im)
            return self.last
    parser = Parser(); records = []; cards = []
    for index, row in enumerate(selected, 1):
        cache.clear(); parser.last = None
        path = ROOT / 'data/raw/mst-e_data' / row['subject_name'] / row['image_ID']
        with (out / 'access_ledger.jsonl').open('a') as f:
            f.write(json.dumps(dict(image_id=row['image_id'], role='historically_exposed_additional_subject_eligibility_only')) + '\n')
        source_hash = digest(path)
        result = measure(cv2.imread(str(path)), detector, landmarks, parser)
        folder = out / ('case_' + str(index)); folder.mkdir()
        rec = dict(image_id=row['image_id'], subject_id=row['subject_name'], official_mst=int(row['MST']),
            lighting=row['lighting'], recorded_mask=row['mask'], source_sha256=source_hash,
            source_path=str(path), **result.report, admitted=False, visual_review='pending')
        if result.report['status'] == 'success':
            replay = build_semantic_face_coverage(result.image, cache['points'], parser.last).mask
            replay[nostril_guard(replay.shape, cache['points'])] = 0
            assert np.array_equal(replay, result.mask)
            assert not result.mask[~np.isin(parser.last, [1, 10])].any()
            overlay = result.image.copy(); chosen = result.mask > 0
            overlay[chosen] = np.rint(.5 * overlay[chosen] + .5 * np.array([0,255,0])).astype(np.uint8)
            board = np.hstack((result.image, overlay, cv2.cvtColor(result.mask, cv2.COLOR_GRAY2BGR)))
            for name, array in [('input.png', result.image), ('mask.png', result.mask), ('categories.png', parser.last), ('board.png', board)]:
                assert cv2.imwrite(str(folder / name), array)
            np.save(folder / 'landmarks.npy', cache['points'])
            rec['board_path'] = (folder / 'board.png').relative_to(out).as_posix()
            rec['reconstruction_passed'] = True
            rec['saved_sha256'] = {p.name: digest(p) for p in folder.iterdir()}
            cards.append('<h2>' + row['image_id'] + '</h2><img src="' + rec['board_path'] + '">')
        else:
            cards.append('<h2>' + row['image_id'] + '</h2><p>Failed: ' + str(rec.get('reason')) + '</p>')
        assert digest(path) == source_hash
        records.append(rec)
        with (out / 'records.jsonl').open('a') as f:
            f.write(json.dumps(rec) + '\n')
        print(str(index) + '/' + str(len(selected)) + ': ' + rec['status'], flush=True)
    assert contract(ROOT)[1] == identity and all(digest(p) == h for p,h in hashes.items())
    summary = dict(status='screen_complete_not_admitted', records=records, universe=337,
        attempts=len(selected), successes=sum(r['status']=='success' for r in records),
        not_assessed=337-len(selected), failures=dict(Counter(r['stage'] for r in records if r['status']!='success')),
        measurement_contract_sha256=identity, fits=0, approvals=0)
    (out / 'summary.json').write_text(json.dumps(summary, indent=2))
    (out / 'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Additional MST eligibility screen</title><style>body{font:18px system-ui;max-width:1000px;margin:auto;padding:20px}img{width:100%}</style><h1>Additional MST-E eligibility screen</h1><p>Original; selected measurement skin; binary mask. No correction, calibration or admission. Exclusions are programmed checks, not actual-skin ground truth.</p>' + ''.join(cards), encoding='utf-8')


if __name__ == '__main__':
    main()
