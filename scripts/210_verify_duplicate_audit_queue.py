"""Verify audit accounting and freeze a training-only queue after quarantine."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_preparation.redesign_access import training_candidate
from src.data_preparation.source_partition import connected_groups


def main():
    out = ROOT/'outputs/correction_duplicate_audit_v1'
    frozen = ROOT/'outputs/correction_data_redesign_v1'
    def read(path):
        return json.loads(path.read_text(encoding='utf-8'))
    target = out/'verified_training_queue.json'
    if target.exists() or (out/'verification.json').exists():
        raise FileExistsError('Refusing to overwrite audit verification')
    selection = read(frozen/'selection.json')
    policy = read(frozen/'access_policy.json')
    fingerprints = read(out/'fingerprints.json')
    failures = read(out/'failures.json')
    summary = read(out/'summary.json')
    for relative, digest in selection['input_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest
    assert hashlib.sha256((frozen/'selection.json').read_bytes()).hexdigest() == summary['selection_sha256']
    assert hashlib.sha256((ROOT/'docs/correction-duplicate-audit-protocol.md').read_bytes()).hexdigest() == summary['protocol_sha256']
    candidates = {r['image_id']:r for r in selection['selected']}
    historical = set(selection['excluded_ids'])
    all_ids = set(candidates)|historical
    decoded = {r['image_id'] for r in fingerprints}
    failed = {r['image_id'] for r in failures}
    assert len(decoded) == len(fingerprints) and not decoded & failed
    assert decoded | failed == all_ids
    links = []
    for index, a in enumerate(fingerprints):
        for b in fingerprints[index+1:]:
            distance = (int(a['dhash64'],16)^int(b['dhash64'],16)).bit_count()
            exact = a['decoded_sha256'] == b['decoded_sha256']
            if exact or distance <= 4:
                links.append(dict(image_a=a['image_id'],image_b=b['image_id'],decoded_exact=exact,dhash_distance=distance))
    assert links == read(out/'candidate_links.json')
    dispositions = {r['image_id']:r for r in read(out/'candidate_dispositions.json')}
    assert len(dispositions) == len(candidates) == 600
    for group in connected_groups(sorted(all_ids),[(r['image_a'],r['image_b']) for r in links]):
        roles = {candidates[i]['role'] for i in group if i in candidates}
        conflict = bool(historical & set(group)) or len(roles)>1
        for image_id in set(group)&set(candidates):
            row = dispositions[image_id]
            expected = 'quarantine_decode_failure' if image_id in failed else ('quarantine_overlap' if conflict else 'screen_clear_unreviewed')
            assert row['status']==expected and row['duplicate_group']==group[0]
            assert row['role']==candidates[image_id]['role'] and row['eligibility']=='not_admitted_for_fitting'
    ledger = read(out/'access_ledger.json')
    assert ledger['image_decode_attempts']==len(all_ids) and ledger['successful_decodes']==len(decoded)
    assert ledger['model_fits']==ledger['feature_extractions']==ledger['correction_predictions']==ledger['visual_reviews']==0
    queue = read(frozen/'training_queue.json')
    batches = []
    for batch in queue['batches']:
        retained, quarantined = [], []
        for image_id in batch['image_ids']:
            training_candidate(image_id, selection, policy)
            (retained if dispositions[image_id]['status']=='screen_clear_unreviewed' else quarantined).append(image_id)
        batches.append(dict(batch=batch['batch'],image_ids=retained,quarantined_ids=quarantined))
    assert sum(len(b['image_ids'])+len(b['quarantined_ids']) for b in batches)==420
    target.write_text(json.dumps(dict(status='training_preparation_only_not_fitting',batches=batches,
        prerequisites='Call training_candidate and check current audit disposition; no validation/test preparation or automatic suitability admission.'),indent=2),encoding='utf-8')
    evidence = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    (out/'verification.json').write_text(json.dumps(dict(status='pass',reconstructed_links=len(links),
        verified_candidate_dispositions=len(dispositions),historical_metadata_unchanged=True,
        retained_training_candidates=sum(len(b['image_ids']) for b in batches),
        quarantined_training_candidates=sum(len(b['quarantined_ids']) for b in batches),evidence_sha256=evidence),indent=2),encoding='utf-8')
    print('PASS: duplicate links/dispositions reconstructed; training queue frozen with quarantine and no replacement.')


if __name__=='__main__':
    main()
