"""Preserve initial trial and build a labelled, criterion-revised continuation."""
from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.demo.acceptability_review import validate,save,page
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    old=ROOT/'outputs/joint_colour_source_held_comparison_v1'
    out=ROOT/'outputs/joint_colour_acceptability_review_v2'
    if out.exists():raise FileExistsError('Preserve continuation')
    check=read(old/'verification_PRIVATE.json');public=read(old/'review_public.json')
    revision='b990942290a94e1dbbcf7ff42a1e6821.json';initial=read(old/'ratings'/revision)
    assert len(initial['ratings'])==9 and initial['ratings']['case-33']['identity']=='noticeable_change'
    assert check['passed']
    original_hashes={n:sha(old/n) for n in ['early_identity_failure_PRIVATE.json','final_development_assessment_PRIVATE.json','ratings/'+revision]}
    assets={c[k] for c in public['cases'] for k in ['A','B','R'] if c[k]}
    for rel in assets:assert sha(old/rel)==check['artifact_sha256'][rel]
    public['protocol_id']+='__acceptability_v2'
    public['preview_note']='Revised criterion: slight acceptable differences are allowed; unwanted changes are not. This is a post-hoc continuation, not a fresh independent test. Your first nine judgments and case33 clarification are carried forward. Continue at the first unanswered case.'
    seed=dict(protocol_id=public['protocol_id'],display=initial['display'],ratings={},
        carry_forward_provenance='Initial nine judgments preserved separately; case33 acceptability supplied explicitly in chat.')
    for case,rating in initial['ratings'].items():
        assert rating['identity']=='no_noticeable_change' or case=='case-33'
        seed['ratings'][case]=dict(identity='slight_acceptable_change' if case=='case-33' else 'no_unwanted_change',reason=rating.get('reason',''))
    assert not validate(public,seed)
    out.mkdir();(out/'review_assets').mkdir()
    for rel in assets:shutil.copyfile(old/rel,out/rel)
    (out/'original_initial_ratings_PRIVATE.json').write_bytes((old/'ratings'/revision).read_bytes())
    (out/'review_public.json').write_text(json.dumps(public,indent=2)+'\n',encoding='utf-8')
    provenance=dict(original_comparison=str(old),original_protocol=initial['protocol_id'],original_revision=revision,
        original_hashes=original_hashes,criterion='no unwanted change; slight acceptable differences allowed',
        user_confirmation='ok',case33_clarification='there wasnt anything wrong with it, it was just a very slight difference',
        mapping='8original no_noticeable_change -> no_unwanted_change; case33 -> slight_acceptable_change per explicit user clarification',
        original_assessment_not_reclassified=True,posthoc_continuation=True,model_adopted=False,scores_controls_unblinded=False)
    (out/'provenance_PRIVATE.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    result=save(out,public,seed)
    (out/'generated_page.html').write_bytes(page())
    assert all(sha(old/n)==h for n,h in original_hashes.items())
    receipt=dict(prepared=True,carried_forward=9,unanswered=35,seed_revision=result['revision'],old_records_unchanged=True,
        scores_controls_unblinded=False,fits=0,new_predictions=0,
        assets_sha256={rel:sha(out/rel) for rel in assets},public_sha256=sha(out/'review_public.json'))
    (out/'preparation_PRIVATE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('Prepared labelled continuation:9carried/35unanswered;original assessment untouched;no scores unblinded')
if __name__=='__main__':main()
