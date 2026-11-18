"""Explicit one-shot real-data entry point; importing never fits."""
from pathlib import Path
import hashlib,json,sys
import platform
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.gap_training_feasibility import join_inputs,run_once,SETTINGS
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if sys.argv[1:]!=['--execute-fixed-fitting-only']:raise SystemExit('Explicit --execute-fixed-fitting-only required')
    qa_path=ROOT/'outputs/histogram_gap_runner_engineering_v1/verification_PRIVATE.json';qa=read(qa_path)
    assert qa['passed']
    assert qa['runtime_versions']==dict(python=platform.python_version(),numpy=version('numpy'),sklearn=version('scikit-learn'))
    for name,digest in qa['input_sha256'].items():assert sha(ROOT/name)==digest
    design=ROOT/'outputs/histogram_gap_training_feasibility_design_v1';plan=read(design/'plan_PRIVATE.json');verified=read(design/'verification_PRIVATE.json')
    assert verified['passed'] and sha(design/'plan_PRIVATE.json')==verified['plan_sha256']
    assert plan['settings']==SETTINGS and plan['fit_calls']==1 and plan['restarts']==0
    for name,digest in plan['input_sha256'].items():assert sha(ROOT/name)==digest
    out=ROOT/plan['output_directory']
    assert out.resolve()==(ROOT/'outputs/histogram_gap_training_feasibility_v1').resolve()
    if out.exists():raise FileExistsError('Preserve prior complete/partial run; no restart')
    records={r['case_id']:read(ROOT/r['record']) for r in plan['fitting_records']}
    # Other rows are already exposed metadata; join_inputs touches only fitting
    # descriptors and writes a fitting-only snapshot, never held values.
    snapshot=join_inputs(plan,records,read(ROOT/plan['audited_features_path']))
    assert len(snapshot)==40 and len({r['source'] for r in snapshot})==10
    modelpath=ROOT/plan['baseline']['path'];text=modelpath.read_text(encoding='utf-8').lstrip()
    first,_=json.JSONDecoder().raw_decode(text[1:].lstrip())
    assert first['definition']['fitting_cases']==[r['case_id'] for r in snapshot]
    assert first['definition']['held_publisher_group']==plan['excluded_group']
    receipt=dict(plan_sha256=sha(design/'plan_PRIVATE.json'),engineering_receipt_sha256=sha(qa_path),
        input_sha256=plan['input_sha256'],code_sha256=qa['input_sha256'],excluded_group=plan['excluded_group'],
        feature_names=plan['feature_names'],target_names=plan['target_names'])
    run_once(out,snapshot,plan['feature_names'],first['tree'],receipt)
    for name,digest in plan['input_sha256'].items():assert sha(ROOT/name)==digest

if __name__=='__main__':main()
