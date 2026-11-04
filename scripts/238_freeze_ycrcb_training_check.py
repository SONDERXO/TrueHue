"""Metadata-only role/group selection and candidate contract freeze."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.ita_estimation.ycrcb_measurement import contract
from src.data_preparation.redesign_access import training_candidate


def main():
    out=ROOT/'outputs/ycrcb_training_check20_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    frozen=ROOT/'outputs/correction_data_redesign_v1';manifest,policy=read(frozen/'selection.json'),read(frozen/'access_policy.json')
    dispositions=read(ROOT/'outputs/correction_duplicate_audit_v1/candidate_dispositions.json')
    groups={r['image_id']:r['duplicate_group'] for r in dispositions}
    checked=read(ROOT/'outputs/focused_mask_review24_v1/reserved_training_check.json')['sources']
    previous=read(ROOT/'outputs/training_review36_import_v1/combined_original_mask_reviews60.json')
    reviewed={r['image_id'] for r in previous};reserved={r['image_id'] for r in checked}
    blocked_groups={groups[i] for i in reviewed|reserved}
    pool=[r for r in dispositions if r['role']=='train' and r['status']=='screen_clear_unreviewed'
          and r['image_id'] not in reviewed|reserved and r['duplicate_group'] not in blocked_groups]
    extra=[];seen=set(blocked_groups)
    for row in sorted(pool,key=lambda r:(hashlib.sha256(('ycrcb_check20_extra8_v1/'+r['image_id']).encode()).hexdigest(),r['image_id'])):
        if row['duplicate_group'] in seen:continue
        extra.append(row);seen.add(row['duplicate_group'])
        if len(extra)==8:break
    ids=[r['image_id'] for r in checked]+[r['image_id'] for r in extra]
    assert len(ids)==len(set(ids))==len({groups[i] for i in ids})==20 and not set(ids)&reviewed
    records=[dict(training_candidate(i,manifest,policy),duplicate_group_id=groups[i],
        check_origin='original_reserved12' if i in reserved else 'additional_fixed_hash8') for i in ids]
    definition,identity=contract(ROOT)
    out.mkdir()
    (out/'candidate_measurement_contract.json').write_text(json.dumps(dict(definition=definition,sha256=identity),indent=2),encoding='utf-8')
    plan=dict(status='frozen_before_check_outcomes',selected=records,candidate_contract_sha256=identity,
        prior_review_excluded=60,reserved12_retained=True,extra_sources=8,
        check_shift='global fixed medium color-only diagnostic, not a source MST label',
        protocol_sha256=digest(ROOT/'docs/ycrcb-training-check-protocol.md'),
        input_sha256={str(p.relative_to(ROOT)):digest(p) for p in [Path(__file__),frozen/'selection.json',frozen/'access_policy.json',
          ROOT/'outputs/correction_duplicate_audit_v1/candidate_dispositions.json',
          ROOT/'outputs/focused_mask_review24_v1/reserved_training_check.json',
          ROOT/'outputs/training_review36_import_v1/combined_original_mask_reviews60.json']})
    (out/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    print('Frozen20training-check IDs and distinct candidate measurement contract; no check image opened.')


if __name__=='__main__':main()
