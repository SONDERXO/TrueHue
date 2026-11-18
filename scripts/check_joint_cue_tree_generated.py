"""Full fixed generated workflow; no real image/encoder/control fit."""
import copy
import platform
import importlib.metadata
import math
import numpy as np
from joint_cue_tree_workflow import ROOT,SETTINGS,ROLES,read,write,sha,select,fit_and_seal,score
from src.distortion_generation.camera_inspired_halfstop import generate,inverse
from src.model_training.luminance_chroma_operator import render_rgb8


def versions():
    return dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn','scikit-image']})


def main():
    out=ROOT/'outputs/joint_cue_tree_generated_v1'
    if out.exists():raise FileExistsError(out)
    rows=[];images={};rng=np.random.default_rng(42)
    for s in range(11):
        ref=rng.integers(20,210,(12,13,3),dtype=np.uint8)
        alpha=np.ones((12,13));alpha[0,:]=0;alpha[-1,:]=.5
        protected=np.zeros(alpha.shape,bool);protected[0,:]=True
        for j,role in enumerate(ROLES):
            image,_=generate(ref,role);y=list(inverse(role))
            x=rng.normal(0,.001,4410).astype(np.float32);x[0]=j;x[281]=j;x[314]=j;x[-1]=s
            case=str(s)+'_'+role
            rows.append(dict(case_id=case,source_id=str(s),role=role,generated_fixture=True,x=x.astype(float).tolist(),y=y))
            images[case]=dict(input=image,reference=ref,alpha=alpha,protected=protected,saved314=image.copy())
    folds=[dict(held_source_id=str(s),fitting_cases=[r['case_id'] for r in rows if r['source_id']!=str(s)],evaluation_cases=[r['case_id'] for r in rows if r['source_id']==str(s)]) for s in range(11)]
    plan=dict(folds=folds,generated_fixture=True,settings=SETTINGS)
    class Poison(dict):
        def __getitem__(self,k):
            if k in ['x','y']:raise AssertionError('Held payload accessed')
            return super().__getitem__(k)
    assert len(select([Poison(r) if r['source_id']=='0' else r for r in rows],folds[0]))==60
    out.mkdir()
    calls=[]
    def forbidden(**kwargs):calls.append(True);raise AssertionError('Unexpected model construction')
    bad=copy.deepcopy(rows);bad[6]['x']=bad[6]['x'][:-1]
    try:fit_and_seal(plan,bad,out/'invalid_width',factory=forbidden)
    except ValueError:pass
    else:raise AssertionError('Invalid width accepted')
    assert not calls and not (out/'invalid_width').exists()
    bad=copy.deepcopy(rows);bad[6]['x'][0]=float('nan')
    try:fit_and_seal(plan,bad,out/'nonfinite',factory=forbidden)
    except ValueError:pass
    else:raise AssertionError('Nonfinite accepted')
    assert not calls and not (out/'nonfinite').exists()
    def failure(**kwargs):raise RuntimeError('generated injected prefit failure')
    try:fit_and_seal(plan,rows,out/'preserved_failure',factory=failure)
    except RuntimeError:pass
    else:raise AssertionError('Failure swallowed')
    assert (out/'preserved_failure/failure.json').exists()
    run=out/'run';before=copy.deepcopy(rows);fit_and_seal(plan,rows,run)
    assert rows==before
    accesses=[]
    def loader(row,p):
        assert (run/'all_fits_verified.json').exists() and (run/'prediction_seal.json').exists()
        a=dict(images[row['case_id']]);a['constant']=render_rgb8(a['input'],a['alpha'],a['protected'],p['constant'])
        accesses.append(row['case_id']);return a
    result=score(rows,run,loader);assert len(accesses)==66
    try:fit_and_seal(plan,rows,run,factory=forbidden)
    except FileExistsError:pass
    else:raise AssertionError('Overwrite accepted')
    assert not calls
    files=['scripts/joint_cue_tree_workflow.py','scripts/check_joint_cue_tree_generated.py','scripts/run_joint_cue_tree.py',
           'scripts/wb_feature_direct_verify.py','scripts/wb_feature_direct_workflow.py','src/model_training/luminance_chroma_operator.py',
           'src/evaluation/luminance_chroma_scalar.py','src/evaluation/directional_recoverability.py','src/distortion_generation/camera_inspired_halfstop.py',
           'docs/joint-cue-tree-protocol-2026-11-16.md']
    report=dict(passed=True,fits=11,fitting_routes=660,held_routes=66,scalar_pixel_checks=66,
                excluded_payload_poison='PASS',invalid_width_zero_fits='PASS',nonfinite_zero_fits='PASS',
                no_overwrite='PASS',failure_preserved='PASS',pixel_reads_after_seal=True,real_fits=0,real_portraits=0,
                generated_numeric_eligible=result['numerical_eligible'],versions=versions(),code_sha256={p:sha(ROOT/p) for p in files})
    write(out/'verification.json',report);print(report)


if __name__=='__main__':main()
