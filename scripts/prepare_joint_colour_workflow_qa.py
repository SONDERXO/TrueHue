"""Generated workflow receipt; reads only explicit saved JSON/code, never real arrays."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.run_joint_colour_source_held import versions
OUT=ROOT/'outputs/joint_colour_workflow_engineering_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if (OUT/'verification_PRIVATE.json').exists():raise FileExistsError('Preserve completed engineering receipt')
    OUT.mkdir(exist_ok=True)  # Initial generated failure evidence already exists.
    design=ROOT/'outputs/joint_colour_source_held_design_v1';plan=read(design/'plan_PRIVATE.json');checked=read(design/'verification_PRIVATE.json')
    assert checked['passed'] and checked['plan_sha256']==sha(design/'plan_PRIVATE.json')
    for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h
    files=['src/model_training/joint_colour_workflow.py','src/model_training/joint_colour_training.py',
        'src/model_training/joint_colour_verification.py','src/model_training/portable_tree.py','src/model_training/gap_training_feasibility.py',
        'src/model_training/gap_source_held_workflow.py','src/correction/seamless_blend.py','src/distortion_generation/paper_gamma.py',
        'src/demo/joint_colour_review.py','src/demo/joint_colour_review_status.js','src/demo/oblique_comparison_review.py','src/demo/oblique_comparison_review.html',
        'scripts/run_joint_colour_source_held.py','scripts/verify_joint_colour_source_held.py','scripts/review_joint_colour_source_held.py',
        'scripts/prepare_joint_colour_workflow_qa.py','scripts/867_verify_gap_source_held_comparison.py','scripts/850_assess_saved_oblique_review.py',
        'tests/test_joint_colour_workflow.py','tests/test_joint_colour_training.py','tests/test_portable_tree.py','review_joint_colour_comparison.cmd',
        'outputs/joint_colour_source_held_design_v1/plan_PRIVATE.json','outputs/joint_colour_source_held_design_v1/verification_PRIVATE.json',
        'outputs/joint_colour_source_held_design_v1/independent_metadata_check_PRIVATE.json',
        'outputs/histogram_gap_source_held_comparison_v1/models_PRIVATE.json']
    old=ROOT/'outputs/histogram_gap_source_held_comparison_v1'
    assert sha(old/'models_PRIVATE.json')==read(old/'verification_PRIVATE.json')['artifact_sha256']['models_PRIVATE.json']
    manual_veto_declarations=[]
    for s in plan['support_sources']:
        oldreceipt=read(ROOT/s['old_support_directory']/'manifest_PRIVATE.json')
        annotation=Path(oldreceipt['source_annotation']);manifest=read(annotation/'manifest.json')
        rel=(annotation/'manifest.json').relative_to(ROOT).as_posix();files.append(rel)
        for n in ['automatic_correction_mask.png','correction_mask.png']:
            manual_veto_declarations.append(dict(path=(annotation/n).relative_to(ROOT).as_posix(),sha256=manifest['files'][n]['sha256']))
    hashes={n:sha(ROOT/n) for n in files}
    result=subprocess.run([sys.executable,'-m','pytest','tests/test_joint_colour_workflow.py','tests/test_joint_colour_training.py','tests/test_portable_tree.py',
        '-q','-p','no:cacheprovider','--junitxml='+str(OUT/'generated_tests.xml')],cwd=ROOT,capture_output=True,text=True)
    (OUT/'generated_tests.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError('Generated QA failed; evidence preserved')
    js=subprocess.run(['node','--check','src/demo/joint_colour_review_status.js'],cwd=ROOT,capture_output=True,text=True)
    (OUT/'javascript_syntax.txt').write_text(js.stdout+js.stderr,encoding='utf-8')
    if js.returncode:raise RuntimeError('Review script syntax failed')
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    assert not (ROOT/plan['output_directory']).exists()
    receipt=dict(passed=True,input_sha256=hashes,runtime_versions=versions(),
        declared_manual_veto_inputs=manual_veto_declarations,generated_full11fold44case_independent_replay=True,
        generated_exact_reuse_fit_barrier=True,generated_new_protection_superset=True,
        generated_http_save_reload_private_denial_earlyclose=True,incomplete_pass_or_unblinding_refused=True,
        javascript_syntax_passed=True,live_browser_visual_qa_claimed=False,
        real_comparison_output_absent=True,real_fits=0,real_predictions=0,real_photo_mask_arrays=0,
        generated_test_receipt_sha256=sha(OUT/'generated_tests.xml'))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(result.stdout);print('PASS bound workflow engineering; real comparison output absent')

if __name__=='__main__':main()
