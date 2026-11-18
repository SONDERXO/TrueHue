"""Freeze metadata-only plan after generated engineering passes; never fits real data."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

CODE=[
 'src/model_training/portable_bagged_tree.py','src/model_training/source_bagged_training.py',
 'src/model_training/source_bagged_verification.py','src/model_training/portable_tree.py',
 'src/model_training/gap_training_feasibility.py','src/model_training/gap_source_held_workflow.py',
 'src/skin_masking/approved_ear_support.py','src/skin_masking/face_neck_support.py','src/correction/seamless_blend.py',
 'scripts/prepare_source_bagged_design.py','scripts/run_source_bagged_development.py',
 'scripts/verify_source_bagged_development.py','scripts/867_verify_gap_source_held_comparison.py',
 'scripts/review_source_bagged_development.py','src/demo/oblique_comparison_review.py',
 'src/demo/oblique_comparison_review.html','scripts/850_assess_saved_oblique_review.py',
 'review_source_bagged_comparison.cmd',
 'tests/test_source_bagged_tree.py','docs/bagged-tree-fixed-protocol-2026-11-13.md',
 'docs/practical-model-evaluation-protocol-2026-11-12.md',
 'docs/paper-input-reference-alignment-2026-11-13.md']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def versions():return dict(python=platform.python_version(),numpy=version('numpy'),sklearn=version('scikit-learn'),opencv=version('opencv-python'),skimage=version('scikit-image'))

def main():
    if sys.argv[1:]!=['--prepare-design']:raise SystemExit('Explicit --prepare-design required')
    out=ROOT/'outputs/source_bagged_design_v1';out.mkdir()
    result=subprocess.run([sys.executable,'-m','pytest','tests/test_source_bagged_tree.py','tests/test_portable_tree.py',
                           'tests/test_gap_source_held_workflow.py','-q','-p','no:cacheprovider',
                           '--junitxml='+str(out/'generated_tests.xml')],cwd=ROOT,capture_output=True,text=True)
    (out/'generated_tests.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError('Generated engineering failed; preserve output')
    parent_path=ROOT/'outputs/histogram_gap_source_held_design_v1/plan_PRIVATE.json'
    parent=read(parent_path)
    parent_verified=read(parent_path.parent/'verification_PRIVATE.json')
    assert parent_verified['passed'] and parent_verified['plan_sha256']==sha(parent_path)
    metadata={k:v for k,v in parent['input_sha256'].items() if k.endswith('.json')}
    # Existing parent bindings are restricted metadata/code, not photo inventory.
    for name,digest in metadata.items():assert sha(ROOT/name)==digest,name
    assert len(parent['folds'])==11 and len(parent['feature_names'])==22
    prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
    rows=read(prep/'rows_PRIVATE.json');bycase={r['case_id']:r for r in rows}
    gaps=read(ROOT/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')
    assert len(bycase)==44 and {c for f in parent['folds'] for c in f['evaluation_cases']}==set(bycase)
    for f in parent['folds']:
        assert len(f['fitting_cases'])==40 and len(set(f['fitting_cases']))==40 and len(f['evaluation_cases'])==4
        assert set(f['fitting_cases']).isdisjoint(f['evaluation_cases'])
        assert set(f['fitting_cases'])|set(f['evaluation_cases'])==set(bycase)
        assert {bycase[c]['publisher_group'] for c in f['evaluation_cases']}=={f['held_publisher_group']}
        assert f['held_publisher_group'] not in {bycase[c]['publisher_group'] for c in f['fitting_cases']}
    for r in rows:
        assert r['generated_fixture'] is False and '29863' not in r['case_id']
        assert Path(r['pixels_file']).resolve()==(prep/r['case_id']/'paired_pixels.npz').resolve()
    old=ROOT/'outputs/histogram_gap_source_held_comparison_v1'
    oldcheck=read(old/'verification_PRIVATE.json');assert oldcheck['passed']
    supports=read(old/'all_supports_sealed_PRIVATE.json');assert supports['passed'] and len(supports['supports'])==11
    support_bindings=[]
    for entry in supports['supports']:
        source=entry['source'];source_id=source.removeprefix('ffhq_source_')
        assert source_id.isdigit() and source_id!='29863'
        rel=f'outputs/histogram_gap_source_held_comparison_v1/supports/{source_id}'
        manifest=ROOT/rel/'manifest_PRIVATE.json'
        assert sha(manifest)==oldcheck['artifact_sha256'][f'supports/{source_id}/manifest_PRIVATE.json']
        assert read(manifest)==entry
        assert set(entry['files'])=={'alpha.npy','correction_mask.png','measurement_mask.png','protected_mask.png'}
        for name,digest in entry['files'].items():
            assert digest==oldcheck['artifact_sha256'][f'supports/{source_id}/{name}']
        support_bindings.append(dict(source=source,directory=rel,manifest_sha256=sha(manifest),files=entry['files'],face_width=entry['face_width']))
    assert {s['source'] for s in support_bindings}=={r['publisher_group'] for r in rows}
    extra=['outputs/histogram_gap_source_held_design_v1/plan_PRIVATE.json',
           'outputs/histogram_gap_source_held_design_v1/verification_PRIVATE.json',
           'outputs/histogram_gap_source_held_comparison_v1/verification_PRIVATE.json',
           'outputs/histogram_gap_source_held_comparison_v1/all_supports_sealed_PRIVATE.json',
           'outputs/histogram_gap_source_held_comparison_v1/summary_PRIVATE.json',
           'outputs/histogram_gap_source_held_comparison_v1/predictions_PRIVATE.json',
           'outputs/reviewed_ffhq_restoration_preparation_v1/role_ledger_PRIVATE.json']
    bindings={**metadata,**{n:sha(ROOT/n) for n in CODE+extra}}
    plan=dict(protocol_id='truehue_source_bagged64_gap22_2026_11_13_v1',user_authorized=True,
        method_change='single_tree_to_fixed_source_bagged_mean',paper_primary='synthetic_to_original_photographic_restoration',
        stage='EXPOSED_DEVELOPMENT_NOT_FINAL',folds=parent['folds'],feature_names=parent['feature_names'],
        target_names=['gamma','red_gain','blue_gain'],members=64,seed=42,rng='sha256_u32_bigendian_rejection_v1',
        input_sha256=bindings,runtime_versions=versions(),supports=support_bindings,
        pixel_containers=parent['declared_pixel_containers'],families=parent['families'],
        first_output='outputs/source_bagged_first_fit_v1',comparison_output='outputs/source_bagged_source_held_v1',
        max_real_member_fits=704,all_fits_before_held=True,final_access=False,model_adopted=False)
    write(out/'plan_PRIVATE.json',plan)
    write(out/'engineering_PRIVATE.json',dict(passed=True,generated_tests_returncode=0,
        plan_sha256=sha(out/'plan_PRIVATE.json'),generated_test_sha256=sha(out/'generated_tests.xml'),runtime_versions=versions(),
        code_sha256={n:sha(ROOT/n) for n in CODE},real_fits=0,arrays_decoded=0))
    print('PASS generated engineering; fixed11fold plan sealed; 0real fits/arrays')

if __name__=='__main__':main()
