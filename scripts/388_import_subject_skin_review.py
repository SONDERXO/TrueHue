"""Import exact complete human answers; preserve failed/prior cases, never fit."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/mst_subject_skin_study_v1'
TARGET = ROOT / 'outputs/mst_subject_skin_study_import_v1'
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def validate(payload, manifest, manifest_hash, verify_files=True):
    assert payload['schema'] == manifest['schema']
    assert payload['manifest_sha256'] == manifest_hash
    assert payload['complete'] is True, 'Partial progress cannot be imported'
    expected = [r for r in manifest['rows'] if r['status'] == 'ready_for_human_review']
    assert len(payload['rows']) == len(expected)
    assert len({r['case_id'] for r in payload['rows']}) == len(expected)
    for answer, saved in zip(payload['rows'], expected):
        assert answer['case_id'] == f'case_{saved["case_index"]}'
        assert answer['image_id'] == saved['image_id']
        assert answer['input_sha256'] == saved['file_sha256']['input.png']
        assert answer['mask_sha256'] == saved['file_sha256']['candidate_mask.png']
        assert set(answer['decisions']) == {'non_skin', 'skin_loss', 'judgeable'}
        assert all(v in {'yes', 'no', 'unsure'} for v in answer['decisions'].values())
        assert isinstance(answer['notes'], str)
    if verify_files:
        assert digest(OUT / 'plan.json') == manifest['plan_sha256']
        assert all(digest(p) == h for p, h in manifest['input_sha256'].items())
        for row in manifest['rows']:
            folder = OUT / f'case_{row["case_index"]}'
            assert all(digest(folder / name) == h for name, h in row['file_sha256'].items())
    return expected


def main(path):
    if TARGET.exists(): raise FileExistsError(TARGET)
    manifest_path = OUT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    payload = json.loads(path.read_text(encoding='utf-8-sig'))
    validate(payload, manifest, digest(manifest_path))
    byid = {r['image_id']: r for r in payload['rows']}
    records = []
    for row in manifest['rows']:
        result = dict(image_id=row['image_id'], subject_id=row['subject_id'], official_mst=row['official_mst'],
                      calibration_admitted=False, training_admitted=False, technical_status=row['status'])
        if row['status'] == 'prior_review_complete':
            result.update(decisions=row['human_decisions'], notes=row['human_notes'], review_origin='preserved_prior_actual_export')
        elif row['status'] == 'ready_for_human_review':
            result.update(decisions=byid[row['image_id']]['decisions'], notes=byid[row['image_id']]['notes'], review_origin='new_actual_export')
        else:
            result.update(visual_status='technical_failure_no_judgment', reason=row.get('reason', row.get('candidate_report', {}).get('reason')))
        if 'decisions' in result:
            result['visual_status'] = 'favourable_exact_image_visual_evidence' if result['decisions'] == dict(non_skin='no', skin_loss='no', judgeable='yes') else 'concern_or_uncertainty_hold'
        records.append(result)
    assert len(records) == 19 and len({r['subject_id'] for r in records}) == 19
    summary = dict(attempts=19, records=records, original_export_sha256=digest(path),
                   scope='exact-image qualitative evidence only; no automatic calibration or training', fits=0)
    TARGET.mkdir()
    (TARGET / 'original_export.json').write_bytes(path.read_bytes())
    (TARGET / 'decisions.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(TARGET)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('export', type=Path)
    main(parser.parse_args().export)
