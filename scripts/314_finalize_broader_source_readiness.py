"""Resolve the predeclared comparison membership; no decoding or tree fitting."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data_preparation.redesign_access import training_candidate


def main():
    out=ROOT/'outputs/broader_source_comparison_readiness_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):
        hashes[p.relative_to(ROOT).as_posix()]=digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    base=ROOT/'outputs'
    design=read(base/'broader_source_comparison_design_v1/design.json')
    dv=read(base/'broader_source_comparison_design_v1/verification.json')
    assert dv['status']=='pass' and digest(base/'broader_source_comparison_design_v1/design.json')==dv['design_sha256']
    for p,sha in design['input_sha256'].items():assert digest(ROOT/p)==sha,p
    imported=base/'additional_six_source_mask_import_v2'
    iv=read(imported/'verification.json');assert iv['status']=='pass'
    for name,sha in iv['evidence_sha256'].items():assert digest(imported/name)==sha,name
    for p,sha in iv['input_sha256'].items():assert digest(Path(p))==sha,p
    accepted=read(imported/'accepted_primary_rows.json')
    reviews=read(imported/'reconciled_reviews.json')
    assert Counter(r['decision'] for r in reviews)=={'accept':4,'reject':11}
    export=read(imported/'original_user_export.json')
    assert all({k:r[k] for k in ['decision','notes']}=={k:export['reviews'][r['pair_id']][k] for k in ['decision','notes']} for r in reviews)
    registry=read(base/'reviewed_source_evidence32_v1/registry.json')
    rv=read(base/'reviewed_source_evidence32_v1/verification.json')
    assert digest(base/'reviewed_source_evidence32_v1/registry.json')==rv['evidence_sha256']['registry.json']
    allocation=read(base/'correction_data_redesign_v1/selection.json')
    policy=read(base/'correction_data_redesign_v1/access_policy.json')
    historical=read(base/'reviewed_primary_comparison_v1/plan.json')
    historical_verification=read(base/'reviewed_primary_comparison_v1/verification.json')
    assert digest(base/'reviewed_primary_comparison_v1/plan.json')==historical_verification['evidence_sha256']['plan.json']
    historical_rows={r['pair_id']:r for r in historical['rows']}
    rows=list(registry['rows']);keys=registry['features']
    for r in accepted:
        assert r['exact_input_mask_review']=='accept' and not r['training_eligible']
        rows.append(dict(pair_id=r['pair_id'],source_image_id=r['source_image_id'],duplicate_group_id=r['duplicate_group_id'],
            stratum='primary',evidence_origin='additional_six_source_mask_import_v2',variant=r['variant'],
            features=[r['features'][k] for k in keys],target_direct_gamma_red_blue=r['paper_target'],
            exact_review_notes=r['exact_review_notes'],review_updated_at=r['review_updated_at'],
            input_path=r['input_path'],input_sha256=r['input_sha256'],
            input_mask_path=r['input_mask_path'],input_mask_sha256=r['input_mask_sha256'],new_fitting_admitted=False))
    by_id={r['pair_id']:r for r in rows};assert len(rows)==len(by_id)==121
    for r in rows:
        if r['pair_id'] in historical_rows:
            # Historical development cohort predates the separate600-source allocation.
            old=historical_rows[r['pair_id']]
            assert r['evidence_origin']=='completed_primary_comparison'
            assert (r['source_image_id'],r['duplicate_group_id'])==(old['source_image_id'],old['duplicate_group_id'])
            assert r['target_direct_gamma_red_blue']==old['paper_target']
            assert r['input_sha256']==old['input_sha256'] and r['input_mask_sha256']==old['input_mask_sha256']
        else:training_candidate(r['source_image_id'],allocation,policy)
        for path,sha in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256')]:
            assert digest(ROOT/r[path])==r[sha],r['pair_id']
    admitted={r['pair_id'] for r in accepted}
    c=design['C_ordered_definite_fit_candidates']+[p for p in design['C_ordered_conditional_fit_candidates'] if p in admitted]
    assert len(c)==94 and all(by_id[p]['stratum']!='clipped_stress' for p in c)
    folds=[]
    for f in design['folds']:
        group=f['held_group'];source=f['held_source']
        held=[r['pair_id'] for r in rows if r['duplicate_group_id']==group]
        train=[p for p in c if by_id[p]['duplicate_group_id']!=group]
        assert not set(train)&set(held)
        assert all(by_id[p]['source_image_id']!=source for p in train)
        folds.append(dict(fold_id=f['fold_id'],held_group=group,held_source=source,
            evaluation_pair_ids=held,C_ordered_training_pair_ids=train,A_B_strategy=f['A_B_strategy']))
    assert len(folds)==32 and Counter(p for f in folds for p in f['evaluation_pair_ids'])==Counter(by_id.keys())
    for r in design['historical_reusable_trees']:
        assert digest(ROOT/r['tree_path'])==r['tree_sha256']
    prediction=design['historical_predictions_to_reuse']
    assert digest(ROOT/prediction['path'])==prediction['sha256']
    summary=dict(status='ready_for_predeclared_comparison_no_fitting_run',
        review_decisions=dict(Counter(r['decision'] for r in reviews)),
        evaluation_cases=len(rows),source_groups=32,strata=dict(Counter(r['stratum'] for r in rows)),
        C_fit_candidate_cases=len(c),C_controls=32,C_primary_cases=62,
        newly_accepted_primary_cases=4,newly_accepted_primary_sources=2,
        retained_historical_trees=52,retained_historical_predictions=210,planned_new_tree_fits=34,
        reference_quality_and_tone_truth_validated=False,lookup_status='experimental_not_validated',
        execution_started=False,model_fits=0,raw_image_decodes=0,reserved_pixel_access=0,
        semantic_parser_and_beard_work='on_hold_pending_adviser_discussion',demo_changed=False,
        limitations=['Only two added sources supply accepted primary variants; six added controls do not establish broad distortion coverage.',
            'All groups are development-exposed; source groups are not verified distinct people.',
            'Mask acceptance does not validate reference illumination or true skin tone.',
            'Zero clean changes and all predeclared gates remain required; no tuning after failure.'])
    plan=dict(summary,features=keys,settings=design['settings'],measurement_contract_sha256=registry['measurement_contract_sha256'],
        lookup_sha256=registry['lookup_sha256'],rows=rows,folds=folds,
        A_ordered_fit_candidates=design['A_ordered_fit_candidates'],B_ordered_fit_candidates=design['B_ordered_fit_candidates'],
        C_ordered_fit_candidates=c,historical_reusable_trees=design['historical_reusable_trees'],
        historical_predictions_to_reuse=prediction,protocol='docs/broader-source-comparison-predeclaration.md')
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=digest(Path(__file__))
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
    out.mkdir()
    for name,payload in [('plan.json',plan),('summary.json',summary)]:
        (out/name).write_text(json.dumps(payload,indent=2),encoding='utf-8')
    verification=dict(status='pass',exact_review_notes_preserved=True,source_separated_folds=32,
        all_input_image_and_mask_hashes_checked=242,imported_export_complete=True,
        historical_tree_hashes_checked=52,input_sha256=hashes,
        evidence_sha256={p.name:digest(p) for p in out.iterdir()})
    (out/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
