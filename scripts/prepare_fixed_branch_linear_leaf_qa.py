"""Artificial adapter/portable QA and readiness binding. No scientific fitting."""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.run_fixed_branch_linear_leaf_fit import versions
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'outputs/fixed_branch_linear_leaf_engineering_v1';out.mkdir()
    design=ROOT/'outputs/fixed_branch_linear_leaf_design_v1';plan=read(design/'plan_PRIVATE.json')
    assert read(design/'verification_PRIVATE.json')['plan_sha256']==sha(design/'plan_PRIVATE.json')
    for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h
    files=['src/model_training/'+n+'.py' for n in ['fixed_branch_linear_leaf_training','fixed_branch_linear_leaf_verification','linear_leaf_generated','linear_leaf_scalar_check','portable_linear_leaf_tree','linear_leaf_fixtures']]
    files+=['tests/test_fixed_branch_linear_leaf.py','tests/test_linear_leaf_generated.py','scripts/run_fixed_branch_linear_leaf_fit.py','scripts/verify_fixed_branch_linear_leaf_fit.py','scripts/prepare_fixed_branch_linear_leaf_qa.py',
        'outputs/fixed_branch_linear_leaf_design_v1/plan_PRIVATE.json','outputs/fixed_branch_linear_leaf_design_v1/verification_PRIVATE.json','outputs/fixed_branch_linear_leaf_design_v1/independent_metadata_check_PRIVATE.json','outputs/fixed_branch_linear_leaf_design_v1/fitting_join_metadata_PRIVATE.json']
    hashes={n:sha(ROOT/n) for n in files}
    test=subprocess.run([sys.executable,'-m','pytest','tests/test_fixed_branch_linear_leaf.py','tests/test_linear_leaf_generated.py','-q','-p','no:cacheprovider','--junitxml='+str(out/'generated_tests.xml')],cwd=ROOT,capture_output=True,text=True)
    (out/'generated_tests.txt').write_text(test.stdout+test.stderr,encoding='utf-8')
    if test.returncode:raise RuntimeError('Generated QA failed; preserve evidence')
    guard="import sys;import scripts.verify_fixed_branch_linear_leaf_fit;assert 'numpy' not in sys.modules;assert 'sklearn' not in sys.modules"
    assert subprocess.run([sys.executable,'-c',guard],cwd=ROOT,capture_output=True).returncode==0
    for table in [hashes,plan['input_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h
    assert not (ROOT/plan['output_directory']).exists()
    report=dict(passed=True,input_sha256=hashes,runtime_versions=versions(),generated_test_receipt_sha256=sha(out/'generated_tests.xml'),artificial_60row_six_leaf_fit_scalar_replayed=True,
        no_signal_stop_tested=True,actual_provenance_unchanged_contract_tested=True,held_filter_before_payload_tested=True,verifier_optimizer_import_guard=True,
        real_output_absent=True,real_fits=0,real_leaf_solves=0,held_predictions=0,photo_arrays=0)
    (out/'verification_PRIVATE.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(test.stdout);print('Generated adapter QA bound; actual60 fitting output absent')
if __name__=='__main__':main()
