"""Explicit future preparation/one-fit stages. No work on import."""
from pathlib import Path
import json,hashlib,platform,sys
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
from src.model_training.blue_axis_preparation import prepare_once,read,sha
from src.model_training.blue_axis_training import join60,fit_once

def versions():return dict(python=platform.python_version(),numpy=version('numpy'),sklearn=version('scikit-learn'),opencv=cv2.__version__)
def main():
    if sys.argv[1:] not in [['--execute-preparation'],['--execute-first-fitting-only']]:raise SystemExit('Explicit stage required')
    design=ROOT/'outputs/blue_axis_coverage_design_v1';plan=read(design/'plan_PRIVATE.json');check=read(design/'verification_PRIVATE.json')
    qa_path=ROOT/'outputs/blue_axis_runner_engineering_v1/verification_PRIVATE.json';qa=read(qa_path)
    assert qa['passed'] and qa['runtime_versions']==versions() and check['plan_sha256']==sha(design/'plan_PRIVATE.json')
    for table in [plan['input_sha256'],qa['input_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h,n
    receipt=dict(plan_sha256=sha(design/'plan_PRIVATE.json'),engineering_sha256=sha(qa_path),code_sha256=qa['input_sha256'],input_sha256=plan['input_sha256'],runtime_versions=versions())
    prep=ROOT/'outputs/blue_axis_preparation_v1'
    if sys.argv[1]=='--execute-preparation':prepare_once(ROOT,prep,plan,receipt)
    else:
        verified=read(prep/'verification_PRIVATE.json');assert verified['passed'] and verified['rows_sha256']==sha(prep/'rows_PRIVATE.json')
        rows=join60(plan,read(prep/'rows_PRIVATE.json'))
        receipt['preparation_verification_sha256']=sha(prep/'verification_PRIVATE.json');receipt['preparation_rows_sha256']=sha(prep/'rows_PRIVATE.json')
        fit_once(ROOT/'outputs/blue_axis_first_fit_v1',rows,plan['feature_names'],receipt)
    for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h
if __name__=='__main__':main()
