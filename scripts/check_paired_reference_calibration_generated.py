"""Generated proof of paired calibration mechanism AND its counterexamples."""
from pathlib import Path
import sys,json,platform,importlib.metadata
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training import paired_reference_prototype as work
from src.model_training.paired_reference_prototype_scalar import search as scalar_search
from src.model_training.five_control_prediction_fixtures import build
from src.distortion_generation.camera_inspired_halfstop import generate,inverse,settings
from src.evaluation.paired_reference_prototype_pixel_verification import verify_run
OUT=ROOT/'outputs/paired_reference_calibration_engineering_v1'
def make_vector(source,role,collapse=False):
    ev,r,b=settings(role);e=ev/.5;c=float(r!=1.)
    x=np.zeros(4377,np.float32)
    if collapse:
        x[0]=x[281]=source+e;x[1]=x[282]=source**2+c
    else:
        x[0]=source;x[1]=source**2*.1;x[281]=np.sin(source);x[282]=np.cos(source)
        x[10]=x[291]=e;x[11]=x[292]=c
    return x.tolist()
def main():
    if OUT.exists():raise FileExistsError(OUT)
    names=work.read(ROOT/'outputs/camera_halfstop_data_v1/plan_PRIVATE.json')['feature_names']
    plan,cases,_=build(names,dict(nuisance='fit_clean_rowspace',tie='lexical_role'),side=16)
    rows=[]
    for i,c in enumerate(cases):
        c['image'],_=generate(c['reference'],c['role']);c['y']=inverse(c['role'])
        rows.append({k:c[k] for k in ['case_id','source_id','role','generated_fixture','y']}|
            dict(x=make_vector(i//6,c['role'])))
    fold=plan['folds'][0]
    class Poison(dict):
        def __getitem__(self,k):
            if k in ['x','y']:raise AssertionError('Held payload accessed')
            return super().__getitem__(k)
    assert len(work.select_fitting([Poison(r) if r['source_id']==fold['held_source_id'] else r for r in rows],fold,generated_fixture=True))==60
    try:work.block_energy(np.zeros((60,4377)))
    except ValueError:pass
    else:raise AssertionError('Zero energy accepted')
    OUT.mkdir()
    try:work.predict_held(plan,[],[],OUT/'missing_barrier')
    except (FileNotFoundError,ValueError):pass
    else:raise AssertionError('Missing model barrier accepted')
    bad=[dict(r,x=r['x'][:-1]) if r['case_id']==fold['fitting_cases'][0] else r for r in rows]
    try:work.fit_all(plan,bad,OUT/'bad_width')
    except ValueError:pass
    else:raise AssertionError('Bad width accepted')
    assert not (OUT/'bad_width').exists()
    collapsed=[dict(r,x=make_vector(i//6,r['role'],collapse=True)) for i,r in enumerate(rows)]
    try:work.fit_all(plan,collapsed,OUT/'preserved_signal_failure')
    except ValueError as exc:assert 'contrast unavailable' in str(exc)
    else:raise AssertionError('Signal destroyed by nuisance projection was not rejected')
    assert (OUT/'preserved_signal_failure/failure.json').exists()
    run=OUT/'generated_run';run.mkdir();work.write(run/'execution_plan.json',plan);work.write(run/'prepared_rows.json',rows)
    models=work.fit_all(plan,rows,run/'models')
    inference=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x']} for r in rows]
    work.write(run/'inference_inputs.json',inference)
    predictions=work.predict_held(plan,inference,models,run/'models')
    assert all(p['prototype_role']==p['role'] for p in predictions)
    work.score(plan,cases,predictions,run/'evaluation');result=verify_run(run)
    # New acceptable-source variation aligned with edit direction can still fool model.
    index=work.read(models[0]['index_path']);stress=make_vector(0,'identity');stress[11]+=2.;stress[292]+=2.
    outcome=work.search(index,stress);assert outcome['prototype_role']!='identity'
    assert outcome['prototype_role']==scalar_search(index,stress)['prototype_role']
    work.write(OUT/'unseen_nuisance_counterexample.json',dict(expected_true_role='identity',predicted=outcome,
        meaning='new nuisance aligned with edit is not solved; generated ideal mechanism is not portrait-transfer proof'))
    fake=dict(block_energy=[1.,1.],clean_mean=[0.]*4377,nuisance_rank=0,nuisance_basis=[],centres=[])
    for role,value in [('identity',1.),('colour_only',-1.)]:
        vector=[0.]*4377;vector[10]=value;fake['centres'].append(dict(role=role,projected_mean=vector,controls=inverse(role)))
    assert work.search(fake,[0.]*4377)['prototype_role']==scalar_search(fake,[0.]*4377)['prototype_role']=='colour_only'
    try:work.fit_all(plan,rows,run/'models')
    except FileExistsError:pass
    else:raise AssertionError('Overwrite accepted')
    files=['src/model_training/paired_reference_prototype.py','src/model_training/paired_reference_prototype_scalar.py',
        'src/evaluation/paired_reference_prototype_pixel_verification.py','src/model_training/camera_halfstop_neighbour.py',
        'src/model_training/luminance_chroma_operator.py','src/evaluation/luminance_chroma_scalar.py',
        'scripts/check_paired_reference_calibration_generated.py','scripts/run_paired_reference_calibration.py',
        'scripts/verify_paired_reference_calibration.py','docs/paired-reference-calibration-protocol-2026-11-15.md',
        'outputs/camera_halfstop_prediction_v1/verification_PRIVATE.json','outputs/camera_halfstop_prediction_v1/prepared_rows.json']
    result.update(actual_generated_models=11,deliberately_unavailable_generated_constructions=1,real_models=0,stress_failure_retained=True,
        collapsed_signal_stop=True,zero_energy_stop=True,poison_exclusion=True,allmodels_barrier=True,no_overwrite=True,
        fitting_reference_only=True,generated_held_role_matches=66,
        versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn','scikit-image','opencv-python']}),
        input_sha256={p:work.sha(ROOT/p) for p in files},
        artifact_sha256={str(p.relative_to(OUT)):work.sha(p) for p in OUT.rglob('*') if p.is_file()})
    work.write(OUT/'verification_PRIVATE.json',result);print('PASS: paired prototype generated11models660fit66held132render plus signal-loss/unseen-nuisance limits.',flush=True)
if __name__=='__main__':main()
