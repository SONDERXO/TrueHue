"""Full-width generated adapter rehearsal; no real correction fit/photo read."""
from pathlib import Path
import sys,json,platform,importlib.metadata
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training import reiqa_tree_workflow as work
from src.model_training.five_control_prediction_fixtures import build
from src.evaluation.reiqa_tree_pixel_verification import verify_run
OUT=ROOT/'outputs/reiqa_added_feature_engineering_v1'

def main():
    if OUT.exists():raise FileExistsError(OUT)
    design=work.read(ROOT/'outputs/reiqa_added_feature_design_v1/plan_PRIVATE.json')
    names=design['feature_names'];assert len(names)==4377
    plan,cases,_=build(names,design['settings'],side=16)
    rows=[]
    for i,c in enumerate(cases):
        x=np.random.default_rng(82200+i).normal(0,.01,4377).astype(np.float32)
        x[0]=i%6;x[281]=i%6;x[-1]=i//6
        rows.append({k:c[k] for k in ['case_id','source_id','role','generated_fixture','y']}|dict(x=x.tolist()))
    fold=plan['folds'][0]
    class Poison(dict):
        def __getitem__(self,k):
            if k in ['x','y']:raise AssertionError('Excluded payload accessed')
            return super().__getitem__(k)
    poison=[Poison(r) if r['source_id']==fold['held_source_id'] else r for r in rows]
    assert len(work.select_fitting(poison,fold,generated_fixture=True))==60
    OUT.mkdir()
    missing=[dict(r,x=r['x'][:-1]) if r['case_id']==fold['fitting_cases'][0] else r for r in rows]
    calls=[]
    def forbidden(**kwargs):calls.append(True);raise AssertionError('Fit factory reached')
    try:work.fit_all(plan,missing,OUT/'invalid_width_models',factory=forbidden)
    except ValueError:pass
    else:raise AssertionError('Missing-width case accepted')
    assert not calls and not (OUT/'invalid_width_models').exists()
    try:work.predict_held(plan,[],[],OUT/'missing_barrier')
    except (FileNotFoundError,ValueError):pass
    else:raise AssertionError('Missing allfits barrier accepted')
    # Failure-preservation path is generated only; no trained model before injected failure.
    def fail_factory(**kwargs):raise RuntimeError('injected generated failure')
    try:work.fit_all(plan,rows,OUT/'preserved_failure',factory=fail_factory)
    except RuntimeError:pass
    else:raise AssertionError('Injected failure swallowed')
    assert (OUT/'preserved_failure/failure.json').exists()
    run=OUT/'generated_run';run.mkdir()
    work.write(run/'execution_plan.json',plan);work.write(run/'prepared_rows.json',rows)
    models=work.fit_all(plan,rows,run/'models')
    inference=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x']} for r in rows]
    work.write(run/'inference_inputs.json',inference)
    predictions=work.predict_held(plan,inference,models,run/'models')
    work.score(plan,cases,predictions,run/'evaluation')
    result=verify_run(run)
    try:work.fit_all(plan,rows,run/'models',factory=forbidden)
    except FileExistsError:pass
    else:raise AssertionError('Overwrite accepted')
    assert not calls
    files=['src/model_training/reiqa_tree_workflow.py','src/model_training/reiqa_tree_verification.py',
        'src/evaluation/reiqa_tree_pixel_verification.py','src/model_training/five_control_prediction_workflow.py',
        'src/model_training/portable_five_control_tree.py','src/model_training/five_control_prediction_fixtures.py',
        'src/model_training/affine_prepower_targets.py','src/evaluation/affine_prepower_scalar.py',
        'src/evaluation/directional_recoverability.py','scripts/check_reiqa_added_feature_generated.py',
        'scripts/run_reiqa_added_feature_prediction.py','scripts/verify_reiqa_added_feature_prediction.py',
        'outputs/reiqa_added_feature_design_v1/plan_PRIVATE.json']
    result.update(scope='generated4377engineering_only',actual_generated_fits=11,real_fits=0,
        poison_excluded_pass=True,invalid_width_zero_fits=True,allfits_barrier_pass=True,
        no_overwrite_pass=True,failure_preservation_pass=True,
        versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn','scikit-image','opencv-python']}),
        input_sha256={p:work.sha(ROOT/p) for p in files},
        artifact_sha256={str(p.relative_to(OUT)):work.sha(p) for p in OUT.rglob('*') if p.is_file()})
    work.write(OUT/'verification_PRIVATE.json',result)
    print('PASS: full4377 generated adapter;11fits/660fit66held132render replay and failure guards.')
if __name__=='__main__':main()
