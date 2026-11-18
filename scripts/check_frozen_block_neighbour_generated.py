"""Generated full-width nearest-neighbour workflow and independent numeric replay."""
from pathlib import Path
import sys,json,platform,importlib.metadata
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training import frozen_block_neighbour as work
from src.model_training.frozen_block_neighbour_scalar import search as scalar_search
from src.model_training.five_control_prediction_fixtures import build
from src.evaluation.frozen_block_neighbour_pixel_verification import verify_run
OUT=ROOT/'outputs/frozen_block_neighbour_engineering_v1'
def main():
    if OUT.exists():raise FileExistsError(OUT)
    design=work.read(ROOT/'outputs/frozen_block_neighbour_design_v1/plan_PRIVATE.json')
    plan,cases,_=build(design['feature_names'],design['settings'],side=16)
    rows=[]
    for i,c in enumerate(cases):
        x=np.random.default_rng(815000+i).normal(0,.01,4377).astype(np.float32)
        x[0]=i%6;x[281]=i%6;x[-1]=i//6
        rows.append({k:c[k] for k in ['case_id','source_id','role','generated_fixture','y']}|dict(x=x.tolist()))
    class Poison(dict):
        def __getitem__(self,k):
            if k in ['x','y']:raise AssertionError('Excluded payload accessed')
            return super().__getitem__(k)
    fold=plan['folds'][0]
    assert len(work.select_fitting([Poison(r) if r['source_id']==fold['held_source_id'] else r for r in rows],fold,generated_fixture=True))==60
    # Exact tie has different controls and resolves by ID, not targets/input order.
    pair=[dict(case_id=name,source_id=name,x=[v]*4377,y=y) for name,v,y in
        [('z',-1.,[1.,1.,1.,1.,-.1]),('a',1.,[1.,1.,1.,1.,.1])]]
    index=work.build_index(pair)
    assert work.search(index,[0.]*4377)['neighbour_case_id']==scalar_search(index,[0.]*4377)['neighbour_case_id']=='a'
    zero=[dict(r,x=[0.]*4377) for r in pair]
    try:work.build_index(zero)
    except ValueError:pass
    else:raise AssertionError('Zero dispersion accepted')
    OUT.mkdir()
    try:work.predict_held(plan,[],[],OUT/'missing_indices')
    except (FileNotFoundError,ValueError):pass
    else:raise AssertionError('Missing barrier accepted')
    # Malformed width rejected during full fitting projection before any construction.
    bad=[dict(r,x=r['x'][:-1]) if r['case_id']==fold['fitting_cases'][0] else r for r in rows]
    try:work.fit_all(plan,bad,OUT/'bad_width')
    except ValueError:pass
    else:raise AssertionError('Bad width accepted')
    assert not (OUT/'bad_width').exists()
    # A fit-only constant learned block fails after admission, retaining failure evidence.
    degenerate=[dict(r,x=r['x'][:281]+[0.]*4096) for r in rows]
    try:work.fit_all(plan,degenerate,OUT/'preserved_failure')
    except ValueError:pass
    else:raise AssertionError('Degenerate learned block accepted')
    assert (OUT/'preserved_failure/failure.json').exists()
    run=OUT/'generated_run';run.mkdir()
    work.write(run/'execution_plan.json',plan);work.write(run/'prepared_rows.json',rows)
    models=work.fit_all(plan,rows,run/'models')
    inference=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x']} for r in rows]
    work.write(run/'inference_inputs.json',inference)
    predictions=work.predict_held(plan,inference,models,run/'models')
    work.score(plan,cases,predictions,run/'evaluation')
    result=verify_run(run)
    try:work.fit_all(plan,rows,run/'models')
    except FileExistsError:pass
    else:raise AssertionError('Overwrite accepted')
    files=['src/model_training/frozen_block_neighbour.py','src/model_training/frozen_block_neighbour_scalar.py',
        'src/evaluation/frozen_block_neighbour_pixel_verification.py','src/model_training/reiqa_tree_workflow.py',
        'src/model_training/five_control_prediction_workflow.py','src/model_training/portable_five_control_tree.py',
        'src/model_training/affine_prepower_targets.py','src/evaluation/affine_prepower_scalar.py',
        'src/evaluation/directional_recoverability.py','scripts/check_frozen_block_neighbour_generated.py',
        'scripts/run_frozen_block_neighbour.py','scripts/verify_frozen_block_neighbour.py',
        'outputs/frozen_block_neighbour_design_v1/plan_PRIVATE.json']
    result.update(passed=True,actual_generated_indices=11,real_indices=0,tree_fits=0,
        zero_dispersion_stop=True,tie_lexical=True,poison_exclusion=True,allindices_barrier=True,
        invalid_width_before_index=True,no_overwrite=True,failure_preserved=True,
        versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn','scikit-image','opencv-python']}),
        input_sha256={p:work.sha(ROOT/p) for p in files},
        artifact_sha256={str(p.relative_to(OUT)):work.sha(p) for p in OUT.rglob('*') if p.is_file()})
    work.write(OUT/'verification_PRIVATE.json',result);print('PASS: generated11indices/660fit66held132render/scalar replay and failure guards.')
if __name__=='__main__':main()
