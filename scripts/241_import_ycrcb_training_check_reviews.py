"""Preserve partial check annotations, blank decisions and conflicting notes."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parent=ROOT/'outputs/ycrcb_training_check20_v1';out=ROOT/'outputs/ycrcb_training_check_review_import_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    export=parent/'truehue_batch_ycrcb_check20_reviews.json'
    review=read(export);plan=read(parent/'plan.json')
    assert review['schema_version']=='truehue_training_review_v1' and review['batch']=='ycrcb_check20'
    assert review['manifest_sha256']==digest(parent/'plan.json')
    assert review['review_scope']=='frozen_candidate_reference_and_global_color_check_only'
    for name,sha in read(parent/'verification.json')['evidence_sha256'].items():assert digest(parent/name)==sha
    expected=[r['image_id'] for r in plan['selected']]
    assert set(review['reviews'])==set(expected) and len(review['reviews'])==20
    attempts={r['image_id']:r for r in (json.loads(x) for x in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    rows=[]
    for image_id in expected:
        entry=review['reviews'][image_id];prior=attempts[image_id];name=prior['source_id']
        assert entry['decision'] in {'','accept','reject','uncertain'} and isinstance(entry['notes'],str)
        issues=[]
        if entry['decision']=='':issues.append('blank_explicit_decision')
        failures=[f for f in ['reference','color'] if prior['frames'][f]['candidate']['status']!='success']
        if entry['decision']=='accept' and failures:issues.append('acceptance_with_candidate_pipeline_failure')
        # Explicit, case-specific discrepancy in this exact exported check.
        if name=='37974' and entry['decision']=='accept':issues.append('accepted_but_note_reports_significant_color_mask_holes')
        rows.append(dict(image_id=image_id,source_id=name,decision=entry['decision'],notes=entry['notes'],
            updated_at=entry.get('updated_at'),decision_completion='pending' if entry['decision']=='' else 'selected',
            review_scope=review['review_scope'],clarification_issues=issues,candidate_pipeline_failed_frames=failures,
            accepted_with_notes=entry['decision']=='accept' and bool(entry['notes'].strip()),
            reviewed_board_sha256=digest(parent/'boards'/f'{name}.png'),
            training_eligible=False,policy_promoted=False))
    counts=Counter(r['decision'] if r['decision'] else 'pending' for r in rows)
    summary=dict(status='imported_pending_five_clarifications',exported_entries=20,
        selected_decisions=sum(r['decision_completion']=='selected' for r in rows),decision_counts=dict(counts),
        blank_decision_ids=[r['source_id'] for r in rows if not r['decision']],
        acceptance_clarification_ids=[r['source_id'] for r in rows if r['decision']=='accept' and r['clarification_issues']],
        accepted_with_notes=sum(r['accepted_with_notes'] for r in rows),
        original_export_sha256=digest(export),candidate_contract_sha256=plan['candidate_contract_sha256'],
        mask_policy_changed=False,check_outcomes_used_for_tuning=False,training_admissions=0,
        mst_lookup_calls=0,models_fitted=0,
        conclusion='Check does not currently support global promotion; preserve explicit contamination/coverage rejections and pending decisions.')
    out.mkdir();(out/'original_user_export.json').write_bytes(export.read_bytes())
    for name,value in [('reconciled_reviews.json',rows),('summary.json',summary)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',exact_export_entries_verified=20,
        blank_decisions_not_inferred=True,conflicting_acceptances_not_overwritten=True,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
