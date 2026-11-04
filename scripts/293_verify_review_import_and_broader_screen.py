"""Independent metadata replay; no model fitting or image decoding."""
import copy
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    base=ROOT/'outputs'
    imported=base/'additional_source_reference_review3_import_v1'
    screen=base/'broader_source_screen61_v1'
    destination=screen/'independent_verification.json'
    if destination.exists():raise FileExistsError(destination)
    for folder in [imported,screen]:
        verification=read(folder/'verification.json')
        assert verification['status']=='pass'
        for name,sha in verification['evidence_sha256'].items():assert digest(folder/name)==sha
    original=read(imported/'original_user_export.json')
    reconciled=read(imported/'reconciled_reviews.json')
    assert {r['image_id']:r['judgments'] for r in reconciled}==original['reviews']
    assert len(original['reviews'])==3
    assert Counter(j['decision'] for scopes in original['reviews'].values() for j in scopes.values())=={'accept':9}
    spec=read(base/'additional_source_reference_review3_v1/spec.json')
    module_spec=importlib.util.spec_from_file_location('import_review',ROOT/'scripts/290_import_source_reference_review3.py')
    module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    module.validate(original,spec)
    bad=[]
    v=copy.deepcopy(original);v['spec_sha256']='wrong';bad.append(v)
    v=copy.deepcopy(original);v['reviews']['unexpected']={};bad.append(v)
    v=copy.deepcopy(original);del v['reviews'][next(iter(v['reviews']))]['reference_mask'];bad.append(v)
    v=copy.deepcopy(original);v['reviews'][next(iter(v['reviews']))]['reference_mask']['decision']='automatic';bad.append(v)
    v=copy.deepcopy(original);v['reviews'][next(iter(v['reviews']))]['reference_mask']['notes']=None;bad.append(v)
    for value in bad:
        try:module.validate(value,spec)
        except ValueError:pass
        else:raise AssertionError('Invalid review accepted')
    inventory=read(base/'independent_source_inventory_v1/fairface_inventory.json')
    pool=[r for r in inventory if r['additional_source_group'] and r['reference_status']=='success' and not r['scoped_review_evidence']]
    pool.sort(key=lambda r:hashlib.sha256(('truehue_inventory24_v1/'+r['image_id']).encode()).hexdigest())
    expected=[r['image_id'] for r in pool[:60]]+['fairface__train/70911.jpg']
    plan=read(screen/'plan.json');rows=read(screen/'assistant_observations.json')
    assert expected==plan['source_ids']==[r['image_id'] for r in rows]
    assert len(set(expected))==61
    prior={r['image_id']:r for r in read(base/'source_planning24_triage_v1/assistant_observations.json')}
    ledger=[json.loads(line) for line in (screen/'access_ledger.jsonl').read_text().splitlines()]
    assert len(ledger)==37 and {r['image_id'] for r in ledger}==set(expected)-set(prior)
    assert all(r['role']=='train' and r['raw_source_opened'] is False for r in ledger)
    accepted={r['image_id']:r['judgments'] for r in reconciled}
    for row in rows:
        if row['image_id'] in prior:
            assert row['assistant_observation']==prior[row['image_id']]['assistant_visual_observation']
        assert row['exact_user_judgments']==accepted.get(row['image_id'])
        assert row['training_admitted'] is False
        assert digest(ROOT/row['board_path'])==row['board_sha256']
    result=dict(status='pass',exact_user_judgments_preserved=9,invalid_review_payloads_rejected=5,
        candidate_membership_reproduced=61,prior_observations_reused=24,new_exposure_records=37,
        board_hashes_verified=61,training_admissions=0,raw_image_decodes=0,
        evidence_sha256={str(p.relative_to(ROOT)):digest(p) for p in [imported/'verification.json',screen/'verification.json',Path(__file__)]})
    destination.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
