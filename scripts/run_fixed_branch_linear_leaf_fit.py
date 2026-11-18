"""Explicit future one-attempt actual60 fitting entry; no work on import."""
from pathlib import Path
import hashlib,json,platform,sys
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.fixed_branch_linear_leaf_training import join_actual,fit_once
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def versions():return dict(python=platform.python_version(),numpy=version('numpy'))
def main():
    if sys.argv[1:]!=['--execute-first-fitting-only']:raise SystemExit('Explicit fitting-only flag required')
    design=ROOT/'outputs/fixed_branch_linear_leaf_design_v1';plan=read(design/'plan_PRIVATE.json');check=read(design/'verification_PRIVATE.json')
    qa_path=ROOT/'outputs/fixed_branch_linear_leaf_engineering_v1/verification_PRIVATE.json';qa=read(qa_path)
    assert qa['passed'] and qa['runtime_versions']==versions() and check['plan_sha256']==sha(design/'plan_PRIVATE.json')
    for table in [plan['input_sha256'],qa['input_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h,n
    first=ROOT/'outputs/blue_axis_first_fit_v1';records=read(ROOT/'outputs/blue_axis_preparation_v1/rows_PRIVATE.json');snapshot=read(first/'fitting_inputs_PRIVATE.json');bindings=read(design/'fitting_join_metadata_PRIVATE.json')
    rows=join_actual(plan,records,snapshot,bindings)
    out=ROOT/plan['output_directory'];assert out.resolve()==(ROOT/'outputs/fixed_branch_linear_leaf_first_fit_v1').resolve()
    receipt=dict(protocol=plan['protocol'],plan_sha256=sha(design/'plan_PRIVATE.json'),engineering_sha256=sha(qa_path),code_sha256=qa['input_sha256'],runtime_versions=versions())
    fit_once(out,plan,rows,read(first/'candidate_PRIVATE.json'),read(first/'training_replay_PRIVATE.json'),receipt)
    for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h
if __name__=='__main__':main()
