"""Generated-only test receipt bound to exact design/code/versions; never real fits."""
from pathlib import Path
import hashlib,json,platform,subprocess,sys
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/joint_colour_runner_engineering_v1'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    OUT.mkdir()
    files=['src/model_training/joint_colour_training.py','src/model_training/joint_colour_verification.py',
        'src/model_training/joint_log_colour.py','src/model_training/portable_tree.py','src/model_training/gap_training_feasibility.py',
        'tests/test_joint_colour_training.py','tests/test_portable_tree.py','scripts/run_joint_colour_fitting_only.py',
        'scripts/verify_joint_colour_fitting_only.py','scripts/prepare_joint_colour_runner_qa.py',
        'outputs/joint_log_colour_training_design_v1/plan_PRIVATE.json','outputs/joint_log_colour_training_design_v1/verification_PRIVATE.json',
        'outputs/joint_log_colour_training_design_v1/fitting_join_metadata_ONLY_PRIVATE.json']
    hashes={n:sha(ROOT/n) for n in files}
    result=subprocess.run([sys.executable,'-m','pytest','tests/test_joint_colour_training.py','tests/test_portable_tree.py',
        '-q','-p','no:cacheprovider','--junitxml='+str(OUT/'generated_tests.xml')],cwd=ROOT,capture_output=True,text=True)
    (OUT/'generated_tests.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError('Generated engineering failed; evidence preserved')
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    assert not (ROOT/'outputs/joint_log_colour_training_feasibility_v1').exists()
    receipt=dict(passed=True,input_sha256=hashes,runtime_versions=dict(python=platform.python_version(),numpy=version('numpy'),sklearn=version('scikit-learn')),
        generated_test_returncode=0,test_receipt_sha256=sha(OUT/'generated_tests.xml'),real_fits=0,real_predictions=0,pixel_arrays=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(result.stdout);print('Generated QA bound; realfit output absent')

if __name__=='__main__':main()
