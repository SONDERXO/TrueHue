"""Validate and preserve reference-only annotations without training admission."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parent=ROOT/'outputs/focused_mask_review24_v1'
    out=ROOT/'outputs/focused_mask_review24_import_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    export=parent/'truehue_batch_focused24_reviews.json'
    review=read(export);selection=read(parent/'selection.json');verification=read(parent/'verification.json')
    assert review['schema_version']=='truehue_training_review_v1' and review['batch']=='focused24'
    assert review['review_scope']==selection['binding']['review_scope']=='reference_photo_and_reference_mask_only'
    identity=hashlib.sha256(json.dumps(selection['binding'],sort_keys=True).encode()).hexdigest()
    assert review['manifest_sha256']==verification['manifest_sha256']==identity
    for name,sha in verification['evidence_sha256'].items():assert digest(parent/name)==sha
    source=ROOT/'outputs/correction_training_preparation_v1'
    assert digest(source/'attempts.jsonl')==selection['binding']['source_attempts_sha256']
    attempts={r['image_id']:r for r in (json.loads(line) for line in (source/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    entries=review['reviews']
    assert isinstance(entries,dict) and set(entries)==set(selection['binding']['selected_ids']) and len(entries)==24
    old=read(source/'verification.json')['evidence_sha256']
    reconciled=[]
    for selected in selection['selected']:
        image_id=selected['image_id'];entry=entries[image_id];prior=attempts[image_id]
        assert entry['decision'] in {'accept','reject','uncertain'}
        assert isinstance(entry['notes'],str)
        board=f'boards/{prior["source_id"]}.png'
        assert digest(source/board)==old[board]
        reconciled.append(dict(image_id=image_id,source_id=prior['source_id'],
            decision=entry['decision'],notes=entry['notes'],updated_at=entry.get('updated_at'),
            selection_reason=selected['selection_reason'],review_scope=review['review_scope'],
            original_processing_status=prior['status'],reference_processing_status=prior['reference_measurement']['status'],
            reference_failure_reason=prior['reference_measurement'].get('reason'),
            accepted_with_concern=entry['decision']=='accept' and bool(entry['notes'].strip()),
            training_eligible=False,distorted_variant_approval='not_reviewed_in_this_export',
            reviewed_board_sha256=digest(source/board)))
    summary=dict(status='validated_reference_mask_annotations_not_training_admission',reviewed_sources=24,
        decisions=dict(Counter(r['decision'] for r in reconciled)),
        accepted_with_concerns=sum(r['accepted_with_concern'] for r in reconciled),
        accepted_with_reference_processing_failure=[r['source_id'] for r in reconciled if r['decision']=='accept' and r['reference_processing_status']!='success'],
        rejected_without_notes=[r['source_id'] for r in reconciled if r['decision']=='reject' and not r['notes'].strip()],
        review_scope=review['review_scope'],original_export_sha256=digest(export),manifest_sha256=identity,
        new_training_admissions=0,models_fitted=0,mask_changes=0)
    out.mkdir()
    (out/'original_user_export.json').write_bytes(export.read_bytes())
    (out/'reconciled_reviews.json').write_text(json.dumps(reconciled,indent=2),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',verified_reviews=24,
        exact_image_ids_and_scope=True,reviewed_board_hashes_unchanged=True,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
