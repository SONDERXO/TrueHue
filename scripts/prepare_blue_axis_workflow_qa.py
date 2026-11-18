"""Generated-only comparison QA and bindings; never execute the real workflow."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.run_blue_axis_source_held import versions
from src.model_training.blue_axis_preparation import read,write,sha

def main():
    out=ROOT/'outputs/blue_axis_workflow_engineering_v1';out.mkdir()
    design=ROOT/'outputs/blue_axis_source_held_design_v1';plan=read(design/'plan_PRIVATE.json')
    assert read(design/'verification_PRIVATE.json')['plan_sha256']==sha(design/'plan_PRIVATE.json')
    for table in [plan['input_sha256'],plan['inherited_input_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h
    files=['src/model_training/'+n+'.py' for n in ['blue_axis_workflow','blue_axis_preparation','blue_axis_training','blue_axis_verification','joint_colour_verification','joint_colour_workflow','joint_colour_training','gap_training_feasibility','gap_source_held_workflow','portable_tree']]
    files+=['src/demo/blue_axis_review_policy.py','src/demo/acceptability_review.py','src/correction/seamless_blend.py','src/distortion_generation/paper_gamma.py',
      'scripts/run_blue_axis_source_held.py','scripts/verify_blue_axis_source_held.py','scripts/prepare_blue_axis_workflow_qa.py','scripts/867_verify_gap_source_held_comparison.py',
      'tests/test_blue_axis_workflow.py','tests/test_blue_axis_feasibility.py','tests/test_joint_colour_workflow.py','tests/test_joint_colour_training.py','tests/test_portable_tree.py',
      'outputs/blue_axis_source_held_design_v1/plan_PRIVATE.json','outputs/blue_axis_source_held_design_v1/verification_PRIVATE.json','outputs/blue_axis_source_held_design_v1/independent_metadata_check_PRIVATE.json']
    manual_veto=[]
    for s in plan['support_sources']:
        old=read(ROOT/s['old_support_directory']/'manifest_PRIVATE.json');annotation=Path(old['source_annotation']);manifest=read(annotation/'manifest.json')
        files.append((annotation/'manifest.json').relative_to(ROOT).as_posix())
        for n in ['automatic_correction_mask.png','correction_mask.png']:manual_veto.append(dict(path=(annotation/n).relative_to(ROOT).as_posix(),sha256=manifest['files'][n]['sha256']))
    hashes={n:sha(ROOT/n) for n in files}
    targets=['tests/test_blue_axis_workflow.py','tests/test_portable_tree.py',
      'tests/test_joint_colour_workflow.py::test_new_protection_superset_measurement_removal_and_exact_seal',
      'tests/test_joint_colour_workflow.py::test_bad_support_rejected']
    result=subprocess.run([sys.executable,'-m','pytest',*targets,'-q','-p','no:cacheprovider','--junitxml='+str(out/'generated_tests.xml')],cwd=ROOT,capture_output=True,text=True)
    (out/'generated_tests.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError('Generated QA failed; evidence retained')
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    for table in [plan['input_sha256'],plan['inherited_input_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h
    assert not (ROOT/'outputs/blue_axis_source_held_comparison_v1').exists()
    write(out/'verification_PRIVATE.json',dict(passed=True,input_sha256=hashes,runtime_versions=versions(),generated_full11fold66case_replay=True,
      fitting_routes=660,held_routes=66,render_metric_replays=66,support_replays=11,all_fits_barrier=True,exact_first_reuse=True,
      generated_five_family_gate=True,generated_review_policy_helpers=True,actual_review_launcher_created=False,carry_forward_requires_later_case_evidence_audit=True,
      manual_veto_declarations=manual_veto,real_fits=0,real_predictions=0,real_photo_mask_arrays=0,real_output_absent=True,
      live_browser_qa_claimed=False,test_receipt_sha256=sha(out/'generated_tests.xml')))
    print(result.stdout);print('Generated workflow QA bound; real comparison absent')
if __name__=='__main__':main()
