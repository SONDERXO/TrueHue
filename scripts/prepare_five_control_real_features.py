"""Single staged real feature preparation. No tree/target fitting entry point."""
from pathlib import Path
import sys
import json
import hashlib
import platform
import importlib.metadata
import cv2

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training.five_control_feature_preparation import BoundInputs,prepare,IdentityParityError

OUT=ROOT/'outputs/five_control_real_feature_preparation_v1'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def main():
    if sys.argv[1:]!=['--prepare-features-only']:raise SystemExit('Explicit --prepare-features-only required')
    if OUT.exists():raise FileExistsError('Preserve completed/partial real preparation')
    design_path=ROOT/'outputs/five_control_source_held_prediction_design_v1/plan_PRIVATE.json'
    plan=read(design_path);check=read(design_path.parent/'verification_PRIVATE.json')
    assert check['passed'] and sha(design_path)==check['plan_sha256']
    qa_path=ROOT/'outputs/five_control_prediction_engineering_v1/verification_PRIVATE.json';qa=read(qa_path)
    assert qa['passed'] and qa['actual_generated_tree_fits']==11 and qa['real_tree_fits']==0
    for p,h in qa['input_sha256'].items():assert sha(ROOT/p)==h
    for p,h in qa['artifact_sha256'].items():assert sha(qa_path.parent/p)==h
    versions=dict(Python=platform.python_version(),**{p:importlib.metadata.version(p)
        for p in ['numpy','scipy','scikit-learn','scikit-image','opencv-python']})
    assert versions==qa['versions']
    assert all(r['generated_fixture'] is False for r in plan['rows'])
    assert len(plan['rows'])==66 and len(plan['feature_sources'])==11
    mapping=read(ROOT/plan['mapper_path']);assert sha(ROOT/plan['mapper_path'])==plan['mapper_sha256']
    files=['scripts/prepare_five_control_real_features.py','scripts/verify_five_control_real_features.py',
        'src/model_training/five_control_feature_preparation.py','src/evaluation/five_control_feature_scalar.py',
        'tests/test_five_control_feature_preparation.py']
    bindings={p:sha(ROOT/p) for p in files};bindings.update(plan['input_sha256'])
    bindings[str(design_path.relative_to(ROOT))]=sha(design_path)
    bindings[str(qa_path.relative_to(ROOT))]=sha(qa_path)
    OUT.mkdir()
    write(OUT/'execution_plan_PRIVATE.json',dict(scope='real_feature_preparation_only',plan=plan,
        input_sha256=bindings,versions=versions,cv2_runtime=cv2.__version__,
        maximum_identity_extractions=11,maximum_nonidentity_extractions=55,tree_fits=0,target_fits=0,
        input_access='whole cached packs hashed; only input plus alpha/protected keys decoded; no reference/output key'))
    inputs=None;rows=[];events=[]
    def record(event,row):
        events.append(dict(event=event,case_id=row.get('case_id'),source_id=row.get('source_id')))
        if event in ['identity_pass','nonidentity_pass']:
            rows.append(row);write(OUT/'partial_rows_PRIVATE.json',rows)
        elif event=='identity_failure':write(OUT/'identity_failure_PRIVATE.json',row)
        write(OUT/'progress_PRIVATE.json',dict(events=events,identities_passed=sum(e['event']=='identity_pass' for e in events),
            nonidentities_prepared=sum(e['event']=='nonidentity_pass' for e in events),tree_fits=0))
        if event in ['identity_pass','all_identities_passed','identity_failure'] or len(rows)%6==0:
            print(f'{event}: {row.get("source_id",row.get("count",""))}; prepared {len(rows)}/66',flush=True)
    try:
        inputs=BoundInputs(ROOT,plan)
        result=prepare(plan,inputs,mapping,record=record)
        inputs.recheck()
        assert all(sha(ROOT/p)==h for p,h in bindings.items())
        write(OUT/'rows_PRIVATE.json',result)
        write(OUT/'status_PRIVATE.json',dict(status='PREPARED_PENDING_INDEPENDENT_VERIFICATION',
            identity_parities=11,nonidentity_vectors=55,rows=66,tree_fits=0,target_fits=0,predictions=0))
        print('Prepared66real input feature vectors; zero tree/target fits.',flush=True)
    except Exception as error:
        write(OUT/'status_PRIVATE.json',dict(status='BLOCKED_IDENTITY_FEATURE_PARITY' if isinstance(error,IdentityParityError) else 'FAILED_PRESERVED',
            error_type=type(error).__name__,error=str(error),completed_rows=len(rows),
            identity_parities=sum(e['event']=='identity_pass' for e in events),
            nonidentity_vectors=sum(e['event']=='nonidentity_pass' for e in events),tree_fits=0,target_fits=0,predictions=0))
        raise
    finally:
        if inputs is not None:write(OUT/'array_access_PRIVATE.json',inputs.access)


if __name__=='__main__':main()
