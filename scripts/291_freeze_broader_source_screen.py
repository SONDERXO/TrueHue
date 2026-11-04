"""Extend the existing hash-prefix inventory once, retaining prior failures."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.data_preparation.redesign_access import training_candidate


def main():
    base=ROOT/get_config().OUTPUTS_ROOT
    out=base/'broader_source_screen61_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def read(p):
        raw=p.read_bytes();hashes[p.relative_to(ROOT).as_posix()]=hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    inventory=read(base/'independent_source_inventory_v1/fairface_inventory.json')
    first24=read(base/'independent_source_inventory_v1/planning24.json')
    previous=read(base/'source_planning24_triage_v1/assistant_observations.json')
    imported=read(base/'additional_source_reference_review3_import_v1/reconciled_reviews.json')
    manifest=read(base/'correction_data_redesign_v1/selection.json')
    policy=read(base/'correction_data_redesign_v1/access_policy.json')
    saved=read(base/'correction_training_preparation_v1/verification.json')['evidence_sha256']
    pool=[r for r in inventory if r['additional_source_group'] and r['reference_status']=='success' and not r['scoped_review_evidence']]
    pool.sort(key=lambda r:hashlib.sha256(('truehue_inventory24_v1/'+r['image_id']).encode()).hexdigest())
    assert [r['image_id'] for r in pool[:24]]==[r['image_id'] for r in first24]
    # One declared 60-source metadata prefix, not replacements until 60 succeed.
    chosen=pool[:60]
    dark=[r for r in pool if r['experimental_severity']=='dark']
    assert len(dark)==1
    if dark[0]['image_id'] not in {r['image_id'] for r in chosen}:chosen=chosen+dark
    assert len(chosen)==61
    previous_by={r['image_id']:r for r in previous}
    imported_by={r['image_id']:r for r in imported}
    for r in chosen:
        training_candidate(r['image_id'],manifest,policy)
        assert r['duplicate_status']=='screen_clear_unreviewed' and not r['in_current_26']
    assert len({r['duplicate_group'] for r in chosen})==61
    out.mkdir()
    plan=dict(status='frozen_before_additional_derivative_inspection',
        selection='Existing salt hash-prefix first60 from the original269 pool; append unreviewed dark-proxy source70911',
        selection_bias='Reference-success/no-collected-review gate; dark-proxy supplement is purposive, not representative or calibrated MST',
        no_failure_replacements=True,original24_retained=True,
        source_ids=[r['image_id'] for r in chosen],newly_inspected_ids=[r['image_id'] for r in chosen if r['image_id'] not in previous_by],
        reserved_roles_locked=['development_validation','final_test'],
        mask_method_changes=0,augmentation_runs=0,model_fits_authorized=False,automatic_admission=False)
    (out/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    evidence=[];boards=[]
    for index,r in enumerate(chosen):
        source_id=Path(r['image_id']).stem
        board=base/'correction_training_preparation_v1/boards'/f'{source_id}.png'
        key=board.relative_to(base/'correction_training_preparation_v1').as_posix()
        row=dict(r,source_id=source_id,selection_role='hash_prefix60' if index<60 else 'dark_proxy_coverage_supplement',
            board_path=board.relative_to(ROOT).as_posix(),board_sha256=saved[key],
            previous_assistant_observation=previous_by.get(r['image_id'],{}).get('assistant_visual_observation'),
            exact_user_judgments=imported_by.get(r['image_id'],{}).get('judgments'),training_admitted=False)
        if r['image_id'] not in previous_by:
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(dict(image_id=r['image_id'],role='train',file=row['board_path'],
                    phase='assistant_broader_source_triage_existing_saved_board',raw_source_opened=False))+'\n')
            raw=board.read_bytes();assert hashlib.sha256(raw).hexdigest()==saved[key]
            hashes[row['board_path']]=saved[key]
            image=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
            assert image is not None
            boards.append(image)
        evidence.append(row)
    assert len(boards)==37
    for start in range(0,len(boards),4):
        assert cv2.imwrite(str(out/f'new_sources_sheet_{start//4+1}.png'),np.vstack(boards[start:start+4]))
    summary=dict(status='frozen_membership_additional_visual_observations_pending',candidate_sources=61,
        prior_assistant_triage_reused=24,new_saved_boards_decoded=37,
        new_user_reviewed_sources=3,processing_status=dict(Counter(r['processing_status'] for r in evidence)),
        experimental_severity=dict(Counter(r['experimental_severity'] for r in evidence)),
        raw_source_decodes=0,reserved_pixel_access=0,training_admissions=0,model_fits=0,
        no_claim_of_person_independence=True,no_claim_of_validated_mst_coverage=True,input_sha256=hashes)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    for name,value in [('sources.json',evidence),('summary.json',summary)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':main()
