"""Generated rehearsal and frozen safeguards for the two-arm direct test."""
from pathlib import Path
import platform
import importlib.metadata
import numpy as np
from wb_feature_direct_workflow import ROOT,SETTINGS,fit_and_seal,score,select,predict,write,sha
from wb_feature_direct_verify import verify_run
from src.model_training.five_control_prediction_fixtures import build
from src.distortion_generation.camera_inspired_halfstop import generate,inverse

def versions():return dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scikit-learn','scikit-image','opencv-python','scipy']})

def main():
    out=ROOT/'outputs/wb_feature_direct_generated_v1'
    if out.exists():raise FileExistsError(out)
    out.mkdir()
    plan,cases,_=build([str(i) for i in range(314)],SETTINGS,side=16)
    plan['settings']=SETTINGS;rows=[]
    for i,c in enumerate(cases):
        c['image'],_=generate(c['reference'],c['role']);c['y']=inverse(c['role'])
        x=np.random.default_rng(89200+i).normal(0,.01,314).astype(np.float32)
        role=i%6;x[0]=[0,0,-1,1,-1,1][role];x[281]=[0,1,0,0,1,1][role]
        rows.append({k:c[k] for k in ['case_id','source_id','role','generated_fixture','y']}|dict(x281=x[:281].tolist(),x314=x.tolist()))
    class Poison(dict):
        def __getitem__(self,k):
            if k in ['x281','x314','y']:raise AssertionError('Held payload accessed')
            return super().__getitem__(k)
    f=plan['folds'][0]
    for arm in ['281','314']:
        assert len(select([Poison(r) if r['source_id']==f['held_source_id'] else r for r in rows],f,arm))==60
    bad=[dict(r,x314=r['x314'][:-1]) if i==0 else r for i,r in enumerate(rows)]
    try:fit_and_seal(plan,bad,out/'bad_width')
    except ValueError:pass
    else:raise AssertionError('bad width accepted')
    assert not (out/'bad_width').exists()
    try:predict(plan,[],out/'missing_certificate',{})
    except FileNotFoundError:pass
    else:raise AssertionError('Missing certificate accepted')
    run=out/'run';fit_and_seal(plan,rows,run)
    by_id={c['case_id']:c for c in cases}
    score(plan,rows,run,lambda r:by_id[r['case_id']])
    result=verify_run(run)
    try:fit_and_seal(plan,rows,run)
    except FileExistsError:pass
    else:raise AssertionError('Overwrite accepted')
    files=['scripts/wb_feature_direct_workflow.py','scripts/wb_feature_direct_verify.py','scripts/check_wb_feature_direct_generated.py',
           'scripts/run_wb_feature_direct_real.py','docs/wb-feature-direct-comparison-protocol-2026-11-15.md',
           'src/model_training/luminance_chroma_operator.py','src/evaluation/luminance_chroma_scalar.py',
           'src/evaluation/directional_recoverability.py']
    result.update(generated=True,poison_exclusion=True,width_failure_zero_fits=True,no_overwrite=True,missing_certificate_stop=True,
                  versions=versions(),input_sha256={p:sha(ROOT/p) for p in files})
    write(out/'verification.json',result);print(result)

if __name__=='__main__':main()
