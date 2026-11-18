"""One fixed source-held paired-reference model assessment on unchanged saved data."""
from pathlib import Path
import sys,json,platform,importlib.metadata
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training import paired_reference_prototype as work
SOURCE=ROOT/'outputs/camera_halfstop_prediction_v1'
OUT=ROOT/'outputs/paired_reference_calibration_prediction_v1'
QA=ROOT/'outputs/paired_reference_calibration_engineering_v1/verification_PRIVATE.json'
def main():
    if sys.argv[1:]!=['--execute-fixed-calibration']:raise SystemExit('Explicit fixed-calibration switch required')
    if OUT.exists():raise FileExistsError(OUT)
    qa=work.read(QA);assert qa['passed'] and qa['actual_generated_models']==11 and qa['stress_failure_retained']
    for p,h in qa['input_sha256'].items():assert work.sha(ROOT/p)==h
    for p,h in qa['artifact_sha256'].items():assert work.sha(QA.parent/p)==h
    v=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn','scikit-image','opencv-python']})
    assert v==qa['versions']
    prior=work.read(SOURCE/'verification_PRIVATE.json');assert prior['passed'] and prior['numeric_status']=='NOT_ADVANCED'
    expected={Path(k).as_posix():h for k,h in prior['artifact_sha256'].items()}
    for name in ['execution_plan.json','prepared_rows.json']:assert work.sha(SOURCE/name)==expected[name]
    plan=work.read(SOURCE/'execution_plan.json');rows=work.read(SOURCE/'prepared_rows.json')
    assert len(rows)==66 and len(plan['feature_names'])==4377
    assert all(r['generated_fixture'] is False and r['parent_training_admitted'] is False for r in rows)
    declared={r['case_id']:r for r in plan['rows']}
    for r in rows:assert r['y']==declared[r['case_id']]['y'] and work.sha(ROOT/r['input_pack'])==r['input_pack_sha256']
    plan=dict(plan,predictor='paired_reference_projection_six_prototypes',settings=dict(blocks=[[0,281],[281,4377]],
        scale='fitting_only_centered_total_block_energy',nuisance='all_numerical_clean_reference_rowspace',tie='lexical_role'))
    bindings={str(p.relative_to(ROOT)):work.sha(p) for p in [QA,SOURCE/'verification_PRIVATE.json',SOURCE/'prepared_rows.json',SOURCE/'execution_plan.json']}
    bindings.update(qa['input_sha256'])
    OUT.mkdir();work.write(OUT/'execution_plan.json',plan);work.write(OUT/'prepared_rows.json',rows);work.write(OUT/'bindings_PRIVATE.json',bindings)
    try:
        models=work.fit_all(plan,rows,OUT/'models')
        inference=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x']} for r in rows]
        work.write(OUT/'inference_inputs.json',inference)
        predicted=work.predict_held(plan,inference,models,OUT/'models')
        cases=[];access=[]
        for r in rows:
            with np.load(ROOT/r['input_pack'],allow_pickle=False) as pack:a={k:pack[k].copy() for k in ['input','reference','alpha','protected']}
            cases.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture','y']}|dict(image=a.pop('input'),**a))
            access.append(dict(case_id=r['case_id'],keys=['input','reference','alpha','protected'],stage='after_all11models_and66sealedcontrols'))
        work.score(plan,cases,predicted,OUT/'evaluation');work.write(OUT/'scoring_access_PRIVATE.json',access)
        for p,h in bindings.items():assert work.sha(ROOT/p)==h
        for r in rows:assert work.sha(ROOT/r['input_pack'])==r['input_pack_sha256']
        work.write(OUT/'completion_PRIVATE.json',dict(calibration_models=11,role_prototypes=66,held_predictions=66,renders=132,
            target_optimizer_calls=0,tree_encoder_mapper_baseline_fits=0,model_ready=False,human_review_launched=False))
        print('Fixed11paired calibration models complete; independent verification pending.',flush=True)
    except Exception as e:
        work.write(OUT/'failure_PRIVATE.json',dict(error_type=type(e).__name__,error=str(e)));raise
if __name__=='__main__':main()
