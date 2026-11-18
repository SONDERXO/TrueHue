"""Explicit real-fit stage, disabled until bound generated engineering passes."""
from pathlib import Path
import hashlib,json,platform,sys
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.joint_colour_training import join,run_once,SETTINGS

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def versions():return dict(python=platform.python_version(),numpy=version('numpy'),sklearn=version('scikit-learn'))

def main():
    if sys.argv[1:]!=['--execute-fixed-fitting-only']:raise SystemExit('Explicit --execute-fixed-fitting-only required')
    qa_path=ROOT/'outputs/joint_colour_runner_engineering_v1/verification_PRIVATE.json';qa=read(qa_path)
    assert qa['passed'] and qa['runtime_versions']==versions()
    for n,h in qa['input_sha256'].items():assert sha(ROOT/n)==h,n
    folder=ROOT/'outputs/joint_log_colour_training_design_v1';plan=read(folder/'plan_PRIVATE.json');checked=read(folder/'verification_PRIVATE.json')
    assert checked['passed'] and checked['plan_sha256']==sha(folder/'plan_PRIVATE.json') and plan['settings']==SETTINGS
    for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h,n
    out=ROOT/plan['output_directory'];assert out.resolve()==(ROOT/'outputs/joint_log_colour_training_feasibility_v1').resolve()
    if out.exists():raise FileExistsError('Preserve complete/partial real fit')
    base=read(ROOT/'outputs/histogram_gap_training_feasibility_v1/fitting_inputs_PRIVATE.json')
    rows=join(plan,base,read(ROOT/plan['audited_features_path']))
    assert rows==read(folder/'fitting_join_metadata_ONLY_PRIVATE.json') and len(rows)==40 and len({r['source'] for r in rows})==10
    receipt=dict(plan_sha256=sha(folder/'plan_PRIVATE.json'),engineering_sha256=sha(qa_path),
        input_sha256=plan['input_sha256'],code_sha256=qa['input_sha256'],runtime_versions=versions())
    run_once(out,rows,plan['feature_names'],read(ROOT/plan['baseline']['path']),receipt)
    for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h

if __name__=='__main__':main()
