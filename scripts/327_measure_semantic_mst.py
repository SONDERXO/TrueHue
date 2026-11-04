"""One fixed semantic measurement pass on the already exposed MST-E cohort."""
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys
from collections import Counter
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.semantic_measurement import contract, measure
from src.ita_estimation.square_measurement import contract as old_contract
from src.skin_masking.face_parsing_experiment import DenseFaceParser


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out = ROOT / 'outputs/semantic_mst_measurement_v1'
    if out.exists():
        raise FileExistsError(out)
    table = ROOT / 'data/manifests/mst_mapping_feasibility_v1/reviewed_included_rows.csv'
    with table.open(encoding='utf-8-sig', newline='') as stream:
        rows = sorted(csv.DictReader(stream), key=lambda r: r['image_id'])
    assert len(rows) == len({r['image_id'] for r in rows}) == 418
    assert all(r['historical_ita_use'].strip() == 'include' and r['metadata_matches'] == '1'
               and r['historical_quality_review'] in ('good', 'acceptable') for r in rows)
    previous = json.loads((ROOT / 'outputs/mst_square256_measurement_v1/summary.json').read_text())
    assert {r['image_id'] for r in rows} == {r['image_id'] for r in previous['records']}
    spec, identity = contract(ROOT)
    legacy_identity = old_contract(ROOT)[1]
    tracked = [Path(__file__), table, ROOT / 'docs/semantic-measurement-single-cycle-protocol.md',
               ROOT / 'src/demo/service.py', ROOT / 'outputs/mst_monotone_square256_v1/development_lookup.json']
    tracked += [Path(r['image_path']) for r in rows]
    hashes = {str(p): digest(p) for p in tracked}
    out.mkdir(); (out / 'masks').mkdir()
    plan = dict(status='frozen_before_measurement', contract=spec, measurement_contract_sha256=identity,
                legacy_measurement_contract_sha256=legacy_identity, input_sha256=hashes,
                image_ids=[r['image_id'] for r in rows], role='previously_exposed_mapping_development',
                reserved_correction_evaluation_access=False, approvals_transferred=False,
                correction_tree_fits=0, beard_models_enabled=False)
    (out / 'plan.json').write_text(json.dumps(plan, indent=2), encoding='utf-8')
    prepare = importlib.import_module('11_prepare_training_manifests')
    config = get_config()
    detector = lambda image: prepare._detect_face_boxes(image, ROOT / config.FACE_MODEL_PATH, .85)
    def landmarks(image, box):
        points, _, _ = prepare.detect_landmarks_with_margin(image, box, ROOT / config.FACE_LANDMARKER_MODEL_PATH)
        return None if points is None else points + np.array(box[:2])
    parser = DenseFaceParser(ROOT / config.MODELS_ROOT / 'face_parser_experimental_v1/resnet18.onnx')
    records = []
    for index, row in enumerate(rows, 1):
        with (out / 'access_ledger.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(dict(image_id=row['image_id'], subject_id=row['subject_id'],
                role='previously_exposed_mapping_development', phase='semantic_contract_remeasurement')) + '\n')
        result = measure(cv2.imread(row['image_path'], cv2.IMREAD_COLOR), detector, landmarks, parser)
        record = dict(image_id=row['image_id'], subject_id=row['subject_id'],
                      source_mst_label=int(row['source_mst_label']), lighting=row['source_lighting'],
                      source_path=row['image_path'], source_sha256=hashes[str(Path(row['image_path']))],
                      measurement_contract_sha256=identity, **result.report)
        if result.mask is not None:
            path = out / 'masks' / (row['image_id'].replace('/', '_') + '.png')
            assert cv2.imwrite(str(path), result.mask)
            record.update(mask_path=path.relative_to(out).as_posix(), mask_sha256=digest(path))
        records.append(record)
        with (out / 'records.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(record) + '\n')
        if index % 20 == 0 or index == len(rows):
            print(f'{index}/{len(rows)} attempts; {sum(r["status"] == "success" for r in records)} measured', flush=True)
    assert all(digest(Path(p)) == value for p, value in hashes.items())
    assert contract(ROOT)[1] == identity and old_contract(ROOT)[1] == legacy_identity
    summary = dict(status='complete_unreviewed_development_measurements', records=records,
                   attempts=len(records), successes=sum(r['status'] == 'success' for r in records),
                   failure_stages=dict(Counter(r['stage'] for r in records if r['status'] != 'success')),
                   measurement_contract_sha256=identity, input_sha256=hashes,
                   new_source_exposures=0, new_mask_approvals=0, correction_tree_fits=0,
                   deployed=False, prior_contract_unchanged=True)
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('records', 'input_sha256')}, indent=2))


if __name__ == '__main__':
    main()
