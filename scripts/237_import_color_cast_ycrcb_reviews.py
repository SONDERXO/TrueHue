"""Import exact paired candidate-mask judgments; no global policy promotion."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parent=ROOT/'outputs/color_cast_ycrcb_refinement_v1';out=ROOT/'outputs/color_cast_ycrcb_review_import_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    export=parent/'truehue_batch_ycrcb_color8_reviews.json'
    review=read(export);selection=read(parent/'review_selection.json')
    assert review['schema_version']=='truehue_training_review_v1' and review['batch']=='ycrcb_color8'
    assert review['review_scope']==selection['scope']=='candidate_reference_and_color_input_masks_only'
    assert review['manifest_sha256']==digest(parent/'plan.json')
    assert len(review['reviews'])==8 and set(review['reviews'])==set(selection['selected_ids'])
    for name,sha in read(parent/'verification.json')['evidence_sha256'].items():assert digest(parent/name)==sha
    attempts={r['image_id']:r for r in read(parent/'attempts.json')}
    followups={'75166':'Accepted with foreign-object inclusion; preserve concern before fitting.',
        '72595':'Accepted with minor holes; do not relabel as hole-free.',
        '68073':'Accepted with earrings selected; preserve explicit foreign-object concern.',
        '66413':'Accepted candidate-mask pair, but user reports blurry source; source suitability needs separate assessment.'}
    rows=[]
    for image_id in selection['selected_ids']:
        entry=review['reviews'][image_id];prior=attempts[image_id]
        assert entry['decision'] in {'accept','reject','uncertain'} and isinstance(entry['notes'],str)
        rows.append(dict(image_id=image_id,source_id=prior['source_id'],decision=entry['decision'],notes=entry['notes'],
            updated_at=entry.get('updated_at'),review_scope=review['review_scope'],
            accepted_with_notes=entry['decision']=='accept' and bool(entry['notes'].strip()),
            followup=followups.get(prior['source_id'],'') if entry['decision']=='accept' else '',
            candidate_reference_status=prior['frames']['reference']['status'],candidate_color_status=prior['frames']['color']['status'],
            reviewed_board_sha256=digest(parent/'boards'/f'{prior["source_id"]}.png'),
            exposure_variant_approval='not_reviewed',combined_variant_approval='not_reviewed',
            training_eligible=False,policy_promoted=False))
    summary=dict(status='paired_candidate_review_imported_no_promotion',sources=8,
        decisions=dict(Counter(r['decision'] for r in rows)),
        accepted_with_notes=sum(r['accepted_with_notes'] for r in rows),
        accepted_without_notes=[r['source_id'] for r in rows if r['decision']=='accept' and not r['notes'].strip()],
        rejected_without_notes=[r['source_id'] for r in rows if r['decision']=='reject' and not r['notes'].strip()],
        source_suitability_followup=['66413'],
        original_export_sha256=digest(export),review_scope=review['review_scope'],
        selection_bias='Purposive retention-gain/risk subset; not representative mask accuracy',
        training_admissions=0,policy_promoted=False,reserved_check_access=False,models_fitted=0)
    out.mkdir();(out/'original_user_export.json').write_bytes(export.read_bytes())
    for name,value in [('reconciled_reviews.json',rows),('summary.json',summary)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',exact_reviews_verified=8,
        paired_scope_and_board_hashes_match=True,
        evidence_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
