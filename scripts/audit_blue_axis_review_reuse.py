"""Exact development-panel/support audit; no fits, rendering or rating invention."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.blue_axis_preparation import read,write,sha
from src.demo.blue_axis_review_policy import carry_forward

def image_hash(path):
    a=cv2.imread(str(path),cv2.IMREAD_COLOR)
    if a is None:raise ValueError('Missing panel')
    a=np.ascontiguousarray(a[:,:,::-1]);return hashlib.sha256(str((a.shape,a.dtype.str)).encode()+a.tobytes()).hexdigest()
def main():
    if sys.argv[1:]!=['--same-viewing-setup-confirmed']:raise SystemExit('Explicit user viewing attestation required')
    old=ROOT/'outputs/joint_colour_source_held_comparison_v1';new=ROOT/'outputs/blue_axis_source_held_comparison_v1'
    out=ROOT/'outputs/blue_axis_review_reuse_audit_v1'
    if out.exists():raise FileExistsError('Preserve audit')
    ov=read(old/'verification_PRIVATE.json');nv=read(new/'verification_PRIVATE.json');assert ov['passed'] and nv['passed'] and nv['numeric_families_pass']
    freeze=read(ROOT/'outputs/joint_colour_development_freeze_v1/freeze_PRIVATE.json')
    revision=ROOT/'outputs/joint_colour_acceptability_review_v2/ratings'/freeze['review_revision']
    assert sha(revision)==freeze['review_sha256'];saved=read(revision)
    op={p['case_id']:p for p in read(old/'predictions_PRIVATE.json')};npred=read(new/'predictions_PRIVATE.json')
    evidence=[];eligible=[];sources=read(ROOT/'outputs/blue_axis_source_held_design_v1/plan_PRIVATE.json')['support_sources']
    ids={s['source']:s['source_id'] for s in sources}
    def signature(folder,p,check):
        output=p['output_panel'];ident=p['review_id'];result={}
        for key,panel in [('input_RGB8_sha256','B' if output=='A' else 'A'),('output_RGB8_sha256',output),('reference_RGB8_sha256','R')]:
            rel=f'review_assets/{ident}_{panel}.png';assert sha(folder/rel)==check['artifact_sha256'][rel];result[key]=image_hash(folder/rel)
        for key,name in [('correction_sha256','correction_mask.png'),('measurement_sha256','measurement_mask.png'),('protection_sha256','protected_mask.png'),('alpha_sha256','alpha.npy')]:
            rel=f'supports/{ids[p["source"]]}/{name}';assert sha(folder/rel)==check['artifact_sha256'][rel];result[key]=sha(folder/rel)
        result['viewing_contract']=dict(display=saved['display'],same_computer_display_zoom_scaling_colour=True,presentation='existing_shared_page_same_panel_dimensions_native_button')
        result['question_semantics']='no_unwanted_allow_slight_acceptable' if p['role']=='identity' else 'usefully_closer_to_R_and_unwanted_artifact'
        return result
    for p in npred:
        c=p['case_id'];a=signature(new,p,nv);item=dict(case_id=c,review_id=p['review_id'],existing_case=c in op,eligible=False)
        if c in op:
            prior=op[c];b=signature(old,prior,ov);provenance=dict(revision_sha256=sha(revision),revision_path=str(revision.relative_to(ROOT)),case_id=c,prior_review_id=prior['review_id'],same_viewing_setup_user_confirmation='Yes, the same viewing setup')
            assert prior['source']==p['source'] and prior['role']==p['role']
            carried=carry_forward(b,a,saved['ratings'][prior['review_id']],provenance,prior['output_panel'],p['output_panel'],a['viewing_contract'])
            item.update(exact_fields={k:a[k]==b[k] for k in a},new_evidence=a,old_evidence=b)
            if carried is not None:item.update(eligible=True,carry_forward=carried);eligible.append(p['review_id'])
        evidence.append(item)
    out.mkdir();write(out/'audit_PRIVATE.json',dict(passed=True,user_viewing_setup_confirmation='Yes, the same viewing setup',prior_revision_sha256=sha(revision),prior_display=saved['display'],cases=evidence,eligible_ids=eligible,eligible_count=len(eligible),fresh_count=66-len(eligible),new_review_ratings_written=0,fits=0,new_predictions=0))
    write(out/'verification_PRIVATE.json',dict(passed=True,audit_sha256=sha(out/'audit_PRIVATE.json'),source_verification_sha256=sha(new/'verification_PRIVATE.json'),old_verification_sha256=sha(old/'verification_PRIVATE.json'),prior_revision_sha256=sha(revision),eligible_count=len(eligible),fresh_count=66-len(eligible)))
    print(f'Exact reuse audit PASS: {len(eligible)}eligible/{66-len(eligible)}fresh; no new judgments invented')
if __name__=='__main__':main()
