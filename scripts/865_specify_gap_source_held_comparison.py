"""Bind metadata for a fixed source-held comparison; zero arrays or fitting."""
from pathlib import Path
from collections import Counter
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/histogram_gap_source_held_design_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    if OUT.exists():raise FileExistsError('Preserve specification')
    prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
    rows=read(prep/'rows_PRIVATE.json');folds=read(prep/'folds_PRIVATE.json')
    parent=ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1';models=read(parent/'models_PRIVATE.json')
    first=ROOT/'outputs/histogram_gap_training_feasibility_v1'
    verification=read(first/'verification_PRIVATE.json');assert verification['passed'] and verification['classification']=='STRICT_FITTING_IMPROVEMENT'
    firstplan=read(ROOT/'outputs/histogram_gap_training_feasibility_design_v1/plan_PRIVATE.json')
    assert len(rows)==44 and len(folds)==len(models)==11
    cases={r['case_id'] for r in rows};assert len(cases)==44
    for fold,old in zip(folds,models):
        assert fold==old['definition'] and len(fold['fitting_cases'])==40 and len(fold['evaluation_cases'])==4
        assert set(fold['fitting_cases'])==cases-set(fold['evaluation_cases'])
    assert folds[0]['fitting_cases']==[r['case_id'] for r in firstplan['fitting_records']]
    assert folds[0]['held_publisher_group']==firstplan['excluded_group']
    assert Counter(r['experimental_role'] for r in rows)==dict(identity=11,exposure_under=11,exposure_over=11,colour_cool=11)
    inventory=read(ROOT/'outputs/ffhq_mask_support_v1/sha256.json')
    bindings={};supports=[]
    for r in rows:
        assert r['generated_fixture'] is False and r['status']=='available' and '29863' not in r['case_id']
        if r['experimental_role']!='identity':continue
        folder=Path(r['annotation']);manifest=read(folder/'manifest.json');report=read(folder/'report.json')
        assert sha(folder/'manifest.json')==r['annotation_manifest_sha256']
        ident=r['case_id'].split('__')[0].removeprefix('ffhq_')
        required=['correction_mask.png','measurement_mask.png','protected_mask.png','automatic_correction_mask.png','correction_alpha.npy']
        supports.append(dict(source=r['publisher_group'],source_id=ident,annotation=str(folder),face_width=report['face_width'],
            manifest_sha256=r['annotation_manifest_sha256'],declared_files={n:manifest['files'][n] for n in required},
            categories_path=f'outputs/ffhq_mask_support_v1/{ident}/categories.png',categories_sha256=inventory[ident+'/categories.png'],
            already_approved_exact_preview=ident in ['16061','29617','54632']))
        for path in [folder/'manifest.json',folder/'report.json']:bindings[path.relative_to(ROOT).as_posix()]=sha(path)
    assert len(supports)==11
    files=['docs/histogram-gap-source-held-comparison-protocol-2026-11-12.md',
        'scripts/865_specify_gap_source_held_comparison.py','src/model_training/gap_training_feasibility.py',
        'src/model_training/histogram_gap_features.py','src/model_training/portable_tree.py',
        'src/skin_masking/approved_ear_support.py','src/skin_masking/correction_ear_preview.py',
        'src/correction/seamless_blend.py','docs/practical-model-evaluation-protocol-2026-11-12.md',
        'docs/practical-model-completion-contract-2026-11-12.md',
        'outputs/histogram_gap_training_feasibility_design_v1/plan_PRIVATE.json',
        'outputs/histogram_gap_training_feasibility_v1/candidate_PRIVATE.json',
        'outputs/histogram_gap_training_feasibility_v1/verification_PRIVATE.json',
        'outputs/histogram_gap_training_feasibility_v1/training_replay_PRIVATE.json',
        'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json',
        'outputs/histogram_gap_exposed_input_audit_v1/verification_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/folds_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/verification_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/mapping_application_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_comparison_v1/predictions_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_comparison_v1/summary_PRIVATE.json',
        'outputs/ffhq_mask_support_v1/sha256.json']
    for ident in ['16061','29617','54632']:files.append(f'outputs/approved_ear_support_integration_v1/{ident}/manifest_PRIVATE.json')
    bindings.update({p:sha(ROOT/p) for p in files})
    plan=dict(status='SPECIFIED_NOT_EXECUTABLE',protocol_id='truehue_gap22_approved_ears_source_held_2026_11_12_v1',
        stage='EXPOSED_DEVELOPMENT_NOT_FINAL',folds=folds,feature_names=firstplan['feature_names'],target_names=firstplan['target_names'],
        settings=firstplan['settings'],planned_new_fits=10,reused_fit_count=1,held_control_vectors=44,
        planned_primary_renders=44,planned_fixed_support_diagnostic_renders=44,attempted=48,available=44,excluded=4,
        reuse=dict(fold=folds[0]['held_publisher_group'],path='outputs/histogram_gap_training_feasibility_v1/candidate_PRIVATE.json',sha256=sha(first/'candidate_PRIVATE.json')),
        support_revision='associated_ear_correction_support_v1',support_sources=supports,
        declared_pixel_containers=[dict(case_id=r['case_id'],path=r['pixels_file'],sha256=r['pixels_sha256']) for r in rows],
        primary=dict(alpha='new sealed approved-ear revision',scoring_region='new alpha>0',baseline='uncorrected actual input on same region',visual_cases=44),
        fixed_diagnostic=dict(alpha='original frozen cached alpha',scoring_region='original scoring_mask',
            model_controls='identical to primary',comparison='saved ordinary16parent metrics descriptive only on compatible region',visual_cases=0,can_rescue_primary_failure=False),
        all_fits_verified_before_held_inference=True,all_supports_sealed_before_scoring=True,
        metric_replay=dict(abs_tol=1e-10,rel_tol=1e-10,output_RGB8_exact=True),
        families=['exposure_under','exposure_over','colour_cool'],identity_visual_policy='no noticeable change',
        reviewer=dict(identity='User',role='researcher development reviewer',device='usual computer',display_details='capture afresh before ratings'),
        presentation=dict(pair_rule='SHA256(UTF8(protocol_id+case_id)) last-byte lowbit;0=inputA/1=inputB',
            scores_and_labels_hidden_until_all_saved=True,diagnostic_outputs_hidden=True,css_long_edge_max=512,no_upscale=True,
            native='cached256image100percent not originaldetail',durable_save_reload_download_required=True),
        failed_or_unresolved_required_check='NOTREADY',old_failures_reclassified=False,threshold_grid=False,
        requirements_before_execution=['Generated one-shot runner/22input fold joins/export parity','Generated dual-context renders/metrics and sealed ear-veto checks',
            'Independent fitting/held-route/mask/scoring/source-equal replay','Hash/version-bound readiness receipt'],
        new_fits_executed=0,predictions=0,arrays_decoded=0,final_locked_access=False,input_sha256=bindings)
    OUT.mkdir()
    (OUT/'plan_PRIVATE.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/p)==h for p,h in bindings.items())
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,folds=11,available_cases=44,declared_supports=11,
        generated_cases=0,exact_first_candidate_reuse_bound=True,source_hashes_unchanged=True,planned_new_fits=10,
        primary_review_cases=44,total_render_contexts=2,executable=False,new_fits=0,predictions=0,arrays_decoded=0,
        plan_sha256=sha(OUT/'plan_PRIVATE.json')),indent=2)+'\n',encoding='utf-8')
    print('PASS: 11folds / 10newfits+exactreuse / 44primaryear-reviewedcases / explicit fixed-support diagnostic; specification only')

if __name__=='__main__':main()
