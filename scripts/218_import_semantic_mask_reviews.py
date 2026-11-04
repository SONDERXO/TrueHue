"""Preserve candidate-only reviews and paired baseline transitions."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parent=ROOT/'outputs/focused_semantic_mask_comparison_v1'
    export=ROOT/'outputs/focused_mask_review24_v1/truehue_batch_semantic24_reviews.json'
    out=ROOT/'outputs/focused_semantic_mask_review_import_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    review=read(export);plan=read(parent/'plan.json')
    assert review['schema_version']=='truehue_training_review_v1' and review['batch']=='semantic24'
    assert review['review_scope']=='semantic_reference_mask_candidate_only'
    assert review['manifest_sha256']==digest(parent/'plan.json')
    for name,sha in read(parent/'verification.json')['evidence_sha256'].items():assert digest(parent/name)==sha
    baseline={r['image_id']:r for r in read(ROOT/'outputs/focused_mask_review24_import_v1/reconciled_reviews.json')}
    attempts={r['image_id']:r for r in (json.loads(line) for line in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    assert set(review['reviews'])==set(plan['selected_ids'])==set(baseline)==set(attempts)
    assert len(review['reviews'])==24
    rows=[]
    for image_id in plan['selected_ids']:
        entry=review['reviews'][image_id];old=baseline[image_id];attempt=attempts[image_id]
        assert entry['decision'] in {'accept','reject','uncertain'} and isinstance(entry['notes'],str)
        rows.append(dict(image_id=image_id,source_id=attempt['source_id'],
            baseline_decision=old['decision'],baseline_exact_notes=old['notes'],
            candidate_decision=entry['decision'],candidate_exact_notes=entry['notes'],
            candidate_updated_at=entry.get('updated_at'),candidate_technical_status=attempt['status'],
            review_scope=review['review_scope'],
            transition=old['decision']+'_to_'+entry['decision'],training_eligible=False,
            reviewed_board_sha256=digest(parent/'boards'/f'{attempt["source_id"]}.png')))
    summary=dict(status='candidate_annotations_imported_no_promotion',sources=24,
        baseline_decisions=dict(Counter(r['baseline_decision'] for r in rows)),
        candidate_decisions=dict(Counter(r['candidate_decision'] for r in rows)),
        transitions=dict(Counter(r['transition'] for r in rows)),
        accepted_with_notes=sum(r['candidate_decision']=='accept' and bool(r['candidate_exact_notes'].strip()) for r in rows),
        accepted_to_rejected_ids=[r['source_id'] for r in rows if r['transition']=='accept_to_reject'],
        original_export_sha256=digest(export),models_fitted=0,training_admissions=0,
        reserved_training_check_opened=False,
        explicit_source_policy_note='55166 rejected; user requests rejecting black-and-white filtered photos. No invented automatic saturation threshold.')
    out.mkdir();(out/'original_user_export.json').write_bytes(export.read_bytes())
    (out/'reconciled_reviews.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',validated_reviews=24,
        scope_ids_and_board_hashes_verified=True,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
