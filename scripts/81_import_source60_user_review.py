"""Reconcile user review with immutable75-attempt exclusions; never fit/admit."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = Path(sys.argv[1]) if len(sys.argv)>1 else Path('C:/Users/NYTHAN/OneDrive/Documents/truehue_source60_variant_review.json')
    parent = ROOT/'data/manifests/training_source60_variants_v1'
    tables = ROOT/'data/manifests/source60_user_review_v1'
    output = ROOT/'outputs/source60_user_review_v1'
    if tables.exists() or output.exists():
        raise FileExistsError('Review import exists')
    disposition_path = parent/'pair_dispositions.json'
    original = json.loads(disposition_path.read_text(encoding='utf-8'))
    review = json.loads(source.read_text(encoding='utf-8-sig'))
    assert review['version']=='training_source60_variants_v1'
    assert review['status']=='user_review_export_not_training_admission'
    expected = {r['pair_id']:r for r in original['pairs'] if r['status']=='pending_human_visual_review'}
    entries = review['pairs']
    assert len(entries)==len({r['pair_id'] for r in entries})==len(expected)==48
    assert {r['pair_id'] for r in entries}==set(expected)
    decisions = {}
    for r in entries:
        base = expected[r['pair_id']]
        assert set(r)==set(base)
        assert all(r[k]==base[k] for k in base if k not in ['human_decision','human_notes'])
        assert r['human_decision'] in ['accept','reject','uncertain','pending']
        assert isinstance(r['human_notes'],str)
        decisions[r['pair_id']]=r
    tracked = [source,disposition_path,parent/'human_review_template.json',
        ROOT/'data/manifests/development_exposure_additions.jsonl',
        ROOT/'data/manifests/controlled_development_v1/source_audit.csv',
        ROOT/'data/manifests/controlled_expansion39_v1/staged_train.csv',
        ROOT/'outputs/brightness_feature_audit_v1/feature_schema.json',
        ROOT/'models/correction_prototype_v1/decision_tree.joblib']
    hashes = {str(p):digest(p) for p in tracked}
    # These follow-ups record explicit accepted-review concerns, not altered labels.
    concerns = {
        '31154': 'User accepted with hair included near neck; separate desired same-person neck skin from hair before fitting.',
        '60162': 'User accepted dark/color with incomplete background exclusion but rejected both controls; inspect residual non-skin measurement/support and retain rejected controls.',
        '63870': 'User notes hijab in baseline measurement despite cleaner correction support; inspect feature contamination before fitting.'}
    merged = []
    for prior in original['pairs']:
        row = dict(prior)
        decision = decisions.get(row['pair_id'])
        row['technical_followup'] = ''
        if decision is not None:
            row['human_decision']=decision['human_decision']
            row['human_notes']=decision['human_notes']
            row['reconciled_status']='user_'+decision['human_decision']
            ident=Path(row['image_id']).stem
            if row['human_decision']=='accept' and ident in concerns:
                row['technical_followup']=concerns[ident]
        else:
            assert row['status']!='pending_human_visual_review'
            row['reconciled_status']=row['status']
        row['training_eligible']=False
        merged.append(row)
    accepted=[r for r in merged if r['human_decision']=='accept']
    assert len(merged)==75 and len(accepted)==35
    assert all(r['status']=='pending_human_visual_review' and not r['clipped_pixels'] for r in accepted)
    assert hashes=={str(p):digest(p) for p in tracked}
    tables.mkdir();output.mkdir()
    (tables/'original_user_export.json').write_bytes(source.read_bytes())
    (tables/'reconciled_pairs.json').write_text(json.dumps(dict(status='review_imported_not_training_admission',pairs=merged),indent=2),encoding='utf-8')
    counts=dict(Counter(r['human_decision'] for r in entries))
    summary=dict(status='complete_no_fitting',review_decisions=counts,total_attempts=75,
        immutable_prior_exclusions=27,accepted_pairs=len(accepted),accepted_sources=len({r['image_id'] for r in accepted}),
        accepted_by_planned_fold=dict(Counter(r['planned_development_fold'] for r in accepted)),
        accepted_by_variant=dict(Counter(r['variant'] for r in accepted)),
        complete_five_accepted_sources=[s for s in sorted({r['image_id'] for r in accepted}) if sum(r['image_id']==s for r in accepted)==5],
        accepted_pairs_needing_note_followup=sum(bool(r['technical_followup']) for r in accepted),
        unresolved_pairs=[r['pair_id'] for r in entries if r['human_decision'] in ['uncertain','pending']],
        input_sha256=hashes,exported_at=review.get('exported_at'),models_fitted=0,
        limitation='User acceptance is preserved separately from source/reference and numerical eligibility. No original master labels, source allocations, existing manifests, runtime models or exclusions were changed.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    assert (tables/'original_user_export.json').read_bytes()==source.read_bytes()
    assert hashes=={str(p):digest(p) for p in tracked}
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':
    main()
