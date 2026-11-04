"""Import actual pending-mask decisions; no inferred choices or model fitting."""
import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data_preparation.redesign_access import training_candidate


def validate(review,manifest,manifest_sha256):
    if review.get('schema_version')!='truehue_primary_mask_review_v1' or review.get('manifest_sha256')!=manifest_sha256:
        raise ValueError('Wrong review manifest')
    if review.get('review_scope')!='exact_new_primary_candidate_input_masks_only':raise ValueError('Wrong review scope')
    decisions=review.get('reviews');expected={r['pair_id'] for r in manifest['rows']}
    if not isinstance(decisions,dict) or set(decisions)!=expected:raise ValueError('Exact mask membership required')
    for entry in decisions.values():
        if not isinstance(entry,dict) or entry.get('decision') not in {'accept','reject','uncertain',''} or not isinstance(entry.get('notes'),str):
            raise ValueError('Invalid mask judgment')
    return decisions


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--export',type=Path)
    parser.add_argument('--output-dir',type=Path,help='New versioned import directory; existing evidence is never overwritten')
    args=parser.parse_args()
    folder=ROOT/'outputs/additional_six_source_mask_review_v1'
    export=args.export or folder/'truehue_additional_six_source_mask_decisions.json'
    if not export.is_file():
        print(json.dumps(dict(status='pending_actual_user_export',expected_path=str(export),decisions_inferred=0)))
        return
    out=args.output_dir or ROOT/'outputs/additional_six_source_mask_import_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):
        hashes[str(p)]=digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    manifest=read(folder/'manifest.json');payload=read(export)
    decisions=validate(payload,manifest,digest(folder/'manifest.json'))
    for name,sha in read(folder/'verification.json')['evidence_sha256'].items():assert digest(folder/name)==sha
    parent=ROOT/'outputs/additional_six_source_pairs_v1'
    pv=read(parent/'verification.json');assert pv['status']=='pass'
    for name,sha in pv['evidence_sha256'].items():assert digest(parent/name)==sha
    plan=read(parent/'plan.json');prepared={r['pair_id']:r for r in read(parent/'attempts.json')}
    registry=read(ROOT/'outputs/reviewed_source_evidence32_v1/registry.json')
    controls={r['source_image_id']:r for r in registry['rows'] if r['stratum']=='original_control'}
    allocation=read(ROOT/'outputs/correction_data_redesign_v1/selection.json')
    policy=read(ROOT/'outputs/correction_data_redesign_v1/access_policy.json')
    assert plan['measurement_contract_sha256']==manifest['measurement_contract_sha256']==registry['measurement_contract_sha256']
    accepted=[];reconciled=[]
    for item in manifest['rows']:
        pair=item['pair_id'];entry=decisions[pair];r=prepared[pair]
        training_candidate(r['source_image_id'],allocation,policy)
        for path,sha in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256')]:
            assert digest(ROOT/r[path])==r[sha]==item[sha]
        reconciled.append(dict(pair_id=pair,source_image_id=r['source_image_id'],variant=r['variant'],**entry))
        if entry['decision']!='accept':continue
        control=controls[r['source_image_id']]
        assert r['lane']=='primary_pending_exact_mask_review' and r['measurement']['status']=='success'
        assert r['clipping']['clipped_pixels']==0 and r['support_screen']['screen_pass']
        assert control['duplicate_group_id']==r['duplicate_group_id']
        assert digest(ROOT/r['reference_path'])==control['input_sha256']
        assert digest(ROOT/r['reference_mask_path'])==control['input_mask_sha256']
        assert set(r['features'])==set(registry['features'])
        assert all(math.isfinite(v) for v in r['features'].values())
        assert len(r['paper_target'])==3 and all(math.isfinite(v) and v>0 for v in r['paper_target'])
        accepted.append(dict(r,exact_input_mask_review='accept',exact_review_notes=entry['notes'],
            review_updated_at=entry.get('updated_at'),data_review_eligible=True,training_eligible=False))
    assert all(digest(Path(p))==sha for p,sha in hashes.items())
    out.mkdir();(out/'original_user_export.json').write_bytes(export.read_bytes())
    summary=dict(status='annotations_imported_pending_fitting_specification',decisions=dict(Counter(r['decision'] or 'pending' for r in reconciled)),
        accepted_primary_cases=len(accepted),accepted_sources=len({r['source_image_id'] for r in accepted}),
        accepted_variants=dict(Counter(r['variant'] for r in accepted)),new_fitting_admissions=0,model_fits=0)
    for name,value in [('reconciled_reviews.json',reconciled),('accepted_primary_rows.json',accepted),('summary.json',summary)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    hashes[str(Path(__file__))]=digest(Path(__file__))
    (out/'verification.json').write_text(json.dumps(dict(status='pass',exact_notes_preserved=True,
        verified_preparation_reused_without_image_replay=True,input_sha256=hashes,
        evidence_sha256={p.name:digest(p) for p in out.iterdir()}),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
