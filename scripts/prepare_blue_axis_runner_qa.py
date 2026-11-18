"""Artificial-only engineering receipt; no real preparation, fitting or inference."""
from pathlib import Path
import json,platform,subprocess,sys
from importlib.metadata import version
import cv2
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.blue_axis_preparation import read,sha,write

def main():
    out=ROOT/'outputs/blue_axis_runner_engineering_v1';out.mkdir()
    files=['src/model_training/'+n+'.py' for n in ['blue_axis_preparation','blue_axis_training','blue_axis_verification','gap_training_feasibility','joint_colour_verification','portable_tree','histogram_gap_features','joint_log_colour','whole_scene_features','green_distribution_features']]
    files+=['src/ita_estimation/compute_ita.py','src/ita_estimation/shared_core_mst.py','tests/test_blue_axis_feasibility.py','tests/test_portable_tree.py',
     'scripts/run_blue_axis_feasibility.py','scripts/verify_blue_axis_feasibility.py','scripts/prepare_blue_axis_runner_qa.py','scripts/check_joint_log_colour_generated.py',
     'docs/blue-axis-coverage-feasibility-protocol-2026-11-13.md','outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json','outputs/blue_axis_coverage_design_v1/verification_PRIVATE.json']
    hashes={n:sha(ROOT/n) for n in files};plan=read(ROOT/'outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json')
    assert all(sha(ROOT/n)==h for n,h in plan['input_sha256'].items())
    result=subprocess.run([sys.executable,'-m','pytest','tests/test_blue_axis_feasibility.py','tests/test_portable_tree.py','-q','-p','no:cacheprovider','--junitxml='+str(out/'generated_tests.xml')],cwd=ROOT,capture_output=True,text=True)
    (out/'generated_tests.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError('Artificial QA failed; evidence retained')
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    assert all(sha(ROOT/n)==h for n,h in plan['input_sha256'].items())
    assert not (ROOT/'outputs/blue_axis_preparation_v1').exists() and not (ROOT/'outputs/blue_axis_first_fit_v1').exists()
    write(out/'verification_PRIVATE.json',dict(passed=True,input_sha256=hashes,runtime_versions=dict(python=platform.python_version(),numpy=version('numpy'),sklearn=version('scikit-learn'),opencv=cv2.__version__),
     test_receipt_sha256=sha(out/'generated_tests.xml'),generated_only=True,artificial_preparation_records=66,artificial_first_fit_records=60,real_arrays_decoded=0,real_fits=0,held_predictions=0,model_adopted=False))
    print(result.stdout);print('Artificial QA passed; real preparation and fit absent')

if __name__=='__main__':main()
