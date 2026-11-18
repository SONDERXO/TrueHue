"""Full generated rehearsal, no actual portrait or real model fits."""
import copy
import hashlib
import platform
import importlib.metadata
import numpy as np
from fivefold_tree_workflow import ROOT,SETTINGS,DEPTHS,ROLES,read,write,sha,take,validate,choose_depth,run_nested
from fivefold_tree_verify import route,verify_outer
from joint_cue_tree_workflow import score
from src.distortion_generation.camera_inspired_halfstop import generate,inverse
from src.model_training.luminance_chroma_operator import render_rgb8


def versions():return dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn','scikit-image']})


def main():
    out=ROOT/'outputs/fivefold_tree_selection_generated_v1'
    if out.exists():raise FileExistsError(out)
    rows=[];images={};rng=np.random.default_rng(42)
    for s in range(11):
        ref=rng.integers(20,210,(12,13,3),dtype=np.uint8)
        alpha=np.ones((12,13));alpha[0,:]=0;alpha[-1,:]=.5
        protected=np.zeros(alpha.shape,bool);protected[0,:]=True
        for j,role in enumerate(ROLES):
            image,_=generate(ref,role);x=rng.normal(0,.001,4410).astype(np.float32)
            x[0]=j;x[281]=j;x[314]=j;x[-1]=s
            case=f'{s}_{role}'
            rows.append(dict(case_id=case,source_id=str(s),role=role,generated_fixture=True,x=x.astype(float).tolist(),y=list(inverse(role))))
            images[case]=dict(input=image,reference=ref,alpha=alpha,protected=protected,saved314=image.copy())
    outer_folds=[]
    for s in range(11):
        fit=[r for r in rows if r['source_id']!=str(s)]
        sources=sorted({r['source_id'] for r in fit},key=lambda q:(hashlib.sha256(('truehue-tree-cv-v1|'+q).encode()).hexdigest(),q))
        inners=[]
        for i in range(5):
            val=set(sources[2*i:2*i+2])
            inners.append(dict(index=i,fitting_cases=[r['case_id'] for r in fit if r['source_id'] not in val],validation_cases=[r['case_id'] for r in fit if r['source_id'] in val]))
        outer_folds.append(dict(held_source_id=str(s),outer_fitting_cases=[r['case_id'] for r in fit],outer_evaluation_cases=[r['case_id'] for r in rows if r['source_id']==str(s)],inner_folds=inners))
    allocation=dict(depths=DEPTHS,outer_folds=outer_folds)
    class Poison(dict):
        def __getitem__(self,k):
            if k in ['x','y']:raise AssertionError('Excluded payload read')
            return super().__getitem__(k)
    outer=outer_folds[0]
    allowed=take([Poison(r) if r['source_id']=='0' else r for r in rows],outer['outer_fitting_cases'],{'0'})
    inner=outer['inner_folds'][0];bad_ids=set(inner['validation_cases'])
    assert len(take([Poison(r) if r['case_id'] in bad_ids else r for r in allowed],inner['fitting_cases'],{'0'}))==48
    assert choose_depth([1.,1.,1.,1.])==0
    assert choose_depth([.1,.1+5e-13,.05,.05+4e-13])==2
    # Explicit six-deep comb tree proves the new scalar route supports >4levels.
    nodes=[]
    for d in range(6):
        nodes.extend([dict(kind='split',feature=0,threshold=float(d),left=2*d+1,right=2*d+2),dict(kind='leaf',values=[1.]*5)])
    nodes.append(dict(kind='leaf',values=[1.]*5))
    model=dict(dimensions=4410,settings=dict(max_depth=6),nodes=nodes)
    x=[0.]*4410;x[0]=7
    assert route(model,x)[0]==12
    cycle=copy.deepcopy(model);cycle['nodes'][0]['right']=0
    try:route(cycle,x)
    except AssertionError:pass
    else:raise AssertionError('Cycle accepted')
    out.mkdir();calls=[]
    def forbidden(**kwargs):calls.append(True);raise AssertionError('Fit reached')
    for name,mutate in [('width',lambda r:r[6]['x'].pop()),('finite',lambda r:r[6]['x'].__setitem__(0,float('nan'))),('roster',lambda r:r.pop())]:
        bad=copy.deepcopy(rows);mutate(bad)
        try:run_nested(allocation,bad,out/name,factory=forbidden)
        except (ValueError,AssertionError):pass
        else:raise AssertionError('Invalid input accepted')
        assert not calls and not (out/name).exists()
    def fail(**kwargs):raise RuntimeError('injected generated failure')
    try:run_nested(allocation,rows,out/'preserved_failure',factory=fail)
    except RuntimeError:pass
    else:raise AssertionError('Failure swallowed')
    assert (out/'preserved_failure/failure.json').exists()
    run=out/'run';before=copy.deepcopy(rows);run_nested(allocation,rows,run)
    assert rows==before
    outer_proof=verify_outer(run,rows,allocation);write(run/'outer_verification.json',outer_proof)
    access=[]
    def loader(row,p):
        assert (run/'selection_verified.json').exists() and (run/'outer_verification.json').exists() and (run/'prediction_seal.json').exists()
        a=dict(images[row['case_id']]);a['constant']=render_rgb8(a['input'],a['alpha'],a['protected'],p['constant'])
        access.append(row['case_id']);return a
    summary=score(rows,run,loader);assert len(access)==66
    try:run_nested(allocation,rows,run,factory=forbidden)
    except FileExistsError:pass
    else:raise AssertionError('Overwrite accepted')
    assert not calls
    files=['scripts/fivefold_tree_workflow.py','scripts/fivefold_tree_verify.py','scripts/check_fivefold_tree_selection_generated.py','scripts/run_fivefold_tree_selection.py',
           'scripts/joint_cue_tree_workflow.py','scripts/wb_feature_direct_workflow.py','scripts/wb_feature_direct_verify.py',
           'src/model_training/luminance_chroma_operator.py','src/evaluation/luminance_chroma_scalar.py','src/evaluation/directional_recoverability.py',
           'src/distortion_generation/camera_inspired_halfstop.py','docs/fivefold-tree-selection-proposal-2026-11-16.md','docs/fivefold-tree-selection-execution-protocol-2026-11-16.md']
    report=dict(passed=True,fits=231,inner_fit_routes=10560,inner_validation_routes=2640,outer_fit_routes=660,outer_held_routes=66,
        scalar_pixel_checks=66,outer_and_inner_exclusion_poison='PASS',tie_handling='PASS',depth6_route_and_cycle_guard='PASS',
        invalid_width_finite_roster_zero_fits='PASS',failure_preserved='PASS',no_overwrite='PASS',
        real_portraits=0,real_fits=0,generated_numeric_eligible=summary['numerical_eligible'],versions=versions(),code_sha256={p:sha(ROOT/p) for p in files})
    write(out/'verification.json',report);print(report)


if __name__=='__main__':main()
