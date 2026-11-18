"""Create a separate review, preserving comparison and prior ratings."""
from pathlib import Path
import shutil,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.blue_axis_preparation import read,write,sha
from src.demo.blue_axis_review import save,page

def main():
    source=ROOT/'outputs/blue_axis_source_held_comparison_v1';out=ROOT/'outputs/blue_axis_review_v1'
    if out.exists():raise FileExistsError('Preserve review')
    checked=read(source/'verification_PRIVATE.json');assert checked['passed'] and checked['numeric_families_pass']
    auditfolder=ROOT/'outputs/blue_axis_review_reuse_audit_v1';audit=read(auditfolder/'audit_PRIVATE.json');av=read(auditfolder/'verification_PRIVATE.json')
    assert av['audit_sha256']==sha(auditfolder/'audit_PRIVATE.json') and av['source_verification_sha256']==sha(source/'verification_PRIVATE.json')
    public=read(source/'review_draft_PRIVATE.json');public['protocol_id']+='__exact_reuse_review_v1'
    public['carried_ids']=audit['eligible_ids']
    public['preview_note']=f"{audit['eligible_count']} exact prior judgments retained; {audit['fresh_count']} cases need your review. Next/Previous skip retained cases. Start with unchanged-photo cases. Slight acceptable differences are allowed; save an unwanted change to stop early. Keep the confirmed viewing setup. Save regularly, then Download saved JSON."
    assets={c[k] for c in public['cases'] for k in ['A','B','R'] if c[k]}
    assert sha(source/'review_draft_PRIVATE.json')==checked['artifact_sha256']['review_draft_PRIVATE.json']
    for rel in assets:assert sha(source/rel)==checked['artifact_sha256'][rel]
    seed=dict(protocol_id=public['protocol_id'],display=audit['prior_display'],ratings={r['review_id']:r['carry_forward']['rating'] for r in audit['cases'] if r['eligible']})
    assert set(seed['ratings'])==set(public['carried_ids']) and len(seed['ratings'])==22
    out.mkdir();(out/'review_assets').mkdir()
    for rel in assets:shutil.copyfile(source/rel,out/rel)
    write(out/'review_public.json',public);write(out/'carry_forward_seed_PRIVATE.json',seed)
    write(out/'provenance_PRIVATE.json',dict(comparison=str(source),comparison_verification_sha256=sha(source/'verification_PRIVATE.json'),reuse_audit_sha256=sha(auditfolder/'audit_PRIVATE.json'),prior_revision_sha256=audit['prior_revision_sha256'],same_viewing_setup_user_confirmation=audit['user_viewing_setup_confirmation'],carried_forward=22,fresh=44,posthoc_oldcriterion_revised_preserved=True,independent_validation=False,model_adopted=False))
    result=save(out,public,seed);(out/'generated_page.html').write_bytes(page(public))
    write(out/'preparation_PRIVATE.json',dict(prepared=True,carried_forward=22,unanswered=44,seed_revision=result['revision'],public_sha256=sha(out/'review_public.json'),assets_sha256={rel:sha(out/rel) for rel in assets},source_verification_sha256=sha(source/'verification_PRIVATE.json'),scores_unblinded=False,new_fits=0,new_predictions=0))
    print('Review prepared:22exact carried/44fresh, identities first; no scores unblinded')
if __name__=='__main__':main()
