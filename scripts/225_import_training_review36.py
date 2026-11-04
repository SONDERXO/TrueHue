"""Validate 36 original-mask annotations and reconcile the 60-source budget."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parent=ROOT/'outputs/training_review36_v1';out=ROOT/'outputs/training_review36_import_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    export=parent/'truehue_batch_training36_reviews.json'
    review=read(export);selection=read(parent/'selection.json');verification=read(parent/'verification.json')
    assert review['schema_version']=='truehue_training_review_v1' and review['batch']=='training36'
    assert review['review_scope']==selection['binding']['review_scope']=='original_rule_based_reference_and_mask_only'
    identity=hashlib.sha256(json.dumps(selection['binding'],sort_keys=True).encode()).hexdigest()
    assert review['manifest_sha256']==verification['manifest_sha256']==identity
    for name,sha in verification['evidence_sha256'].items():assert digest(parent/name)==sha
    for name,sha in selection['binding']['input_sha256'].items():assert digest(ROOT/name)==sha
    assert len(review['reviews'])==36 and set(review['reviews'])==set(selection['binding']['selected_ids'])
    source=ROOT/'outputs/correction_training_preparation_v1'
    attempts={r['image_id']:r for r in (json.loads(x) for x in (source/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    old_hashes=read(source/'verification.json')['evidence_sha256']
    rows=[]
    for image_id in selection['binding']['selected_ids']:
        entry=review['reviews'][image_id];prior=attempts[image_id]
        assert entry['decision'] in {'accept','reject','uncertain'} and isinstance(entry['notes'],str)
        board=f'boards/{prior["source_id"]}.png';assert digest(source/board)==old_hashes[board]
        rows.append(dict(image_id=image_id,source_id=prior['source_id'],decision=entry['decision'],notes=entry['notes'],
            updated_at=entry.get('updated_at'),review_scope=review['review_scope'],
            original_processing_status=prior['status'],reference_processing_status=prior['reference_measurement']['status'],
            accepted_with_notes=entry['decision']=='accept' and bool(entry['notes'].strip()),
            assigned_severity=prior['assigned_severity'],clipped_pixels=prior['clipping']['clipped_pixels'],
            duplicate_group_id=prior['duplicate_group_id'],distorted_variant_approval='not_reviewed',training_eligible=False,
            explicit_followup='Accepted with too much hair coverage; preserve acceptance but hold for contamination assessment.' if prior['source_id']=='16033' and entry['decision']=='accept' else '',
            reviewed_board_sha256=digest(source/board)))
    earlier=read(ROOT/'outputs/focused_mask_review24_import_v1/reconciled_reviews.json')
    assert len(earlier)==24 and not {r['image_id'] for r in earlier}&{r['image_id'] for r in rows}
    all_rows=earlier+rows
    summary=dict(status='reviews_imported_no_training_admission',new_reviewed_sources=36,
        new_decisions=dict(Counter(r['decision'] for r in rows)),
        new_accepted_with_notes=sum(r['accepted_with_notes'] for r in rows),
        combined_original_mask_reviewed_sources=60,combined_original_mask_decisions=dict(Counter(r['decision'] for r in all_rows)),
        new_accepted_ids=[r['source_id'] for r in rows if r['decision']=='accept'],
        new_accepted_without_notes=sum(r['decision']=='accept' and not r['notes'].strip() for r in rows),
        all_new_associated_distortions_clipped=all(r['clipped_pixels']>0 for r in rows),
        training_admissions=0,models_fitted=0,original_export_sha256=digest(export),manifest_sha256=identity)
    out.mkdir();(out/'original_user_export.json').write_bytes(export.read_bytes())
    for name,value in [('reconciled_reviews.json',rows),('combined_original_mask_reviews60.json',all_rows),('summary.json',summary)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',verified_new_reviews=36,combined_unique_sources=60,
        scope_and_images_verified=True,evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
