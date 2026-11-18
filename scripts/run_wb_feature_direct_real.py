"""Exact real adapter, two fixed arms. All targets are existing analytic labels."""
from pathlib import Path
import numpy as np
from wb_feature_direct_workflow import ROOT,SETTINGS,read,write,sha,fit_and_seal,score
from wb_feature_direct_verify import verify_run
from check_wb_feature_direct_generated import versions

def main():
    out=ROOT/'outputs/wb_feature_direct_prediction_v1'
    if out.exists():raise FileExistsError(out)
    qa_path=ROOT/'outputs/wb_feature_direct_generated_v1/verification.json';qa=read(qa_path)
    assert qa['passed'] and qa['fits_replayed']==22 and qa['scalar_render_metric_replays']==198
    assert versions()==qa['versions']
    for p,h in qa['input_sha256'].items():assert sha(ROOT/p)==h,p
    data=ROOT/'outputs/camera_halfstop_data_v1';done=read(data/'completion_PRIVATE.json')
    assert done['passed'] and sha(data/'plan_PRIVATE.json')==done['plan_sha256'] and sha(data/'rows281_PRIVATE.json')==done['rows281_sha256']
    plan=read(data/'plan_PRIVATE.json');base=read(data/'rows281_PRIVATE.json');plan['settings']=SETTINGS;plan['generated_fixture']=False
    wb=ROOT/'outputs/wb_cue_portrait_assessment_v2';seal=read(wb/'feature_seal.json')
    assert sha(wb/'sealed_features.json')==seal['sha256'] and read(wb/'independent_verification.json')['passed']
    for p,h in read(wb/'bindings.json').items():assert sha(ROOT/p)==h,p
    # Existing camera independent feature/generation verification, not re-extraction.
    prior=ROOT/'outputs/camera_halfstop_prediction_v1/verification_PRIVATE.json'
    previous=read(prior);assert previous['passed'] and previous['scalar_feature_values']==18546
    cues={r['case_id']:r for r in read(wb/'sealed_features.json')}
    assert len(cues)==66 and len(base)==66 and set(cues)=={r['case_id'] for r in base}
    original={r['case_id']:r for r in plan['rows']};rows=[]
    bindings=dict(qa['input_sha256'])
    files=[qa_path,prior,data/'plan_PRIVATE.json',data/'rows281_PRIVATE.json',data/'completion_PRIVATE.json',wb/'sealed_features.json',wb/'feature_seal.json',wb/'independent_verification.json']
    for p in files:bindings[str(p.relative_to(ROOT))]=sha(p)
    bindings.update(read(wb/'bindings.json'))
    for b in base:
        c=cues[b['case_id']];d=original[b['case_id']]
        assert c['source_id']==b['source_id']==d['source_id'] and c['role']==b['role']==d['role'] and b['y']==d['y']
        assert b['generated_fixture'] is False and b['parent_training_admitted'] is False
        assert len(b['x'])==281 and len(c['coefficients'])==33
        assert b['input_pack']==d['input_pack'] and b['input_pack_sha256']==d['input_pack_sha256']
        path=ROOT/d['input_pack'];assert path.resolve().parent==(data/'cases').resolve()
        bindings[d['input_pack']]=d['input_pack_sha256']
        x=np.asarray(b['x']+c['coefficients'],dtype=np.float32).astype(float).tolist()
        assert x[:281]==b['x'] and np.isfinite(x).all()
        rows.append({k:b[k] for k in ['case_id','source_id','role','generated_fixture','y']}|dict(x281=b['x'],x314=x))
    for p,h in bindings.items():assert sha(ROOT/p)==h,p
    access=[]
    try:
        fit_and_seal(plan,rows,out)
        write(out/'bindings.json',dict(input_sha256=bindings,versions=versions(),features_recomputed=0,target_fits=0,execution_role='authorized_exposed_development_not_final_admission'))
        def loader(r):
            d=original[r['case_id']]
            with np.load(ROOT/d['input_pack'],allow_pickle=False) as pack:a={k:pack[k].copy() for k in ['input','reference','alpha','protected']}
            access.append(dict(case_id=r['case_id'],path=d['input_pack'],keys=['input','reference','alpha','protected'],stage='after_22fits_verified_and_132controls_sealed'))
            return dict(image=a['input'],reference=a['reference'],alpha=a['alpha'],protected=a['protected'])
        result=score(plan,rows,out,loader)
        write(out/'access.json',access)
        proof=verify_run(out)
        for p,h in bindings.items():assert sha(ROOT/p)==h,p
        proof.update(real_tree_fits=22,constant_renders=66,tree_renders=132,feature_recomputations=0,target_fits=0,
                     independent_real_joins=66,artifacts={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()})
        write(out/'verification.json',proof)
        print(result);print(proof)
    except Exception as exc:
        if out.exists():write(out/'execution_failure.json',dict(error=str(exc),scoring_access=access))
        raise

if __name__=='__main__':main()
