"""Aggregate-only candidate freeze/readiness package. No inference or fitting."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.utilities.config import get_config
BASE=ROOT/get_config().OUTPUTS_ROOT
OUT=BASE/'correction_training_readiness_plan_v1'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError('Use a new version; frozen package exists')
    parents=['ppr10k_inspection_v1','ppr10k_operator_diagnostic_v1',
        'ppr10k_residual_diagnosis_v1','ppr10k_contrast_diagnostic_v1',
        'ppr10k_new_group_comparison_v1','ppr10k_clipping_detail_check_v1','ppr10k_detail_repair_v1']
    for name in parents:
        p=BASE/name
        for file,digest in json.loads((p/'sha256.json').read_text()).items():assert sha(p/file)==digest
    OUT.mkdir()
    sources=['scripts/394_ppr10k_contrast_diagnostic.py','scripts/398_ppr10k_smooth_boundary_check.py',
        'src/distortion_generation/generate_distortions.py','src/ita_estimation/faceocc_development.py',
        'docs/correction-training-readiness-plan-2026-11-02.md',
        'docs/ppr10k-smooth-boundary-results-2026-11-02.md',
        'docs/mst-subject-skin-study-results-2026-11-02.md']
    hashes={name:sha(ROOT/name) for name in sources}
    payload=dict(version='experimental_gamma_rb_contrast_soft_boundary_v1',
        status='Frozen experimental reference for planning; not runtime adoption or calibrated correction model',
        input_space='Encoded sRGB normalized[0,1], RGB order',
        parameter_order=['gamma','red_gain','blue_gain','contrast'],
        raw_formula='(0.5+contrast*(x**(1/gamma)-0.5))*[red_gain,1,blue_gain]',
        boundary_formula='s*log(1+exp(raw/s))-s*log(1+exp((raw-1)/s))',
        boundary_width=.02,stable_evaluation='scripts/398:soft_boundary, symmetric softplus difference',
        experimental_bounds=[[.25,.25,.25,.5],[4.,4.,4.,2.]],
        spatial_smoothing=False,exact_neutral_identity=False,analytic_old_inverse_valid=False,
        deployed_output_schema_changed=False,
        measurement_candidate_contract='89c7a3963dcc72bfa8c7b73433789b058093131662c88a6d30a7f25d791823fd',
        measurement_admitted=False,mst_available=False,
        correction_support='Future adopted wholeface+visible-neck/protected pixels/continuity/inward alpha; not validated by face-only diagnostics',
        operator_source_hashes={k:v for k,v in hashes.items() if k.endswith('.py')})
    canonical=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    contract=dict(payload=payload,canonical_payload_sha256=hashlib.sha256(canonical).hexdigest())
    readiness=dict(training_ready=False,operator_frozen_for_planning=True,
        blockers=['reference_support_admission','identity_and_exposure_grouping','matching_MST_skin_admission_and_validation',
            'smooth_blended_target_and_clean_image_policy','complete_feature_schema_and_predeclared_adequacy_acceptance'],
        targets_generated=0,new_calibration_fits=0,new_tree_fits=0,new_inference=0,
        review_batch_activated=False,contacts_sent=False,runtime_adopted=False,
        final_split=None,adequate_cohort_size=None,acceptance_thresholds=None,
        retained_method='ITA+calibratedMST+facialstatistics -> decisiontree correction',
        next_trigger='Substantive new admission/access evidence addresses a named blocker; then justify one bounded protocol, no automatic fits')
    frames=[]
    for folder in ['ppr10k_inspection_v1','ppr10k_new_group_comparison_v1']:
        plan=json.loads((BASE/folder/'frozen_sample.json').read_text())
        for frame in plan['frames']:
            frames.append(dict(frame=frame,group=frame.split('_')[0],editor='a',truehue_role='development_exposed_diagnostic_only',
                publisher_role='training' if int(frame.split('_')[0])<1356 else 'validation',
                training_admitted=False,unseen_final_eligible=False,person_identity_verified=False))
    assert len(frames)==len({r['frame'] for r in frames})==14
    outputs={'candidate_contract.json':contract,'readiness.json':readiness,'development_exposure.json':frames,
        'source_hashes.json':hashes,'parent_manifest_hashes.json':{name:sha(BASE/name/'sha256.json') for name in parents}}
    for name,value in outputs.items():(OUT/name).write_text(json.dumps(value,indent=2),encoding='utf8')
    (OUT/'README.txt').write_text('Planning only: no training-ready cohort or reliable MST.\nRead docs/correction-training-readiness-plan-2026-11-02.md.\nNo photographs, model weights or deployed lookup included.\nFrozen contract is experimental, not adopted runtime.\n',encoding='utf8')
    reread=json.loads((OUT/'candidate_contract.json').read_text())
    assert hashlib.sha256(json.dumps(reread['payload'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==reread['canonical_payload_sha256']
    for name,value in hashes.items():assert sha(ROOT/name)==value
    for name in outputs:assert json.loads((OUT/name).read_text())==outputs[name]
    (OUT/'verification.json').write_text(json.dumps(dict(contract_hash_verified=True,source_hashes_verified=len(hashes),
        parent_manifests_verified=7,json_roundtrip=True,exposed_frames=14,raw_photos_embedded=0,model_weights_embedded=0,
        no_new_fits_or_inference=True),indent=2),encoding='utf8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf8')
    print('Verified planning freeze:',contract['canonical_payload_sha256'],';14exposed diagnostic frames; training_ready=false')


if __name__=='__main__':main()
