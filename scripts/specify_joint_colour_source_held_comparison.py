"""Freeze metadata/support declarations only; zero fits or array decodes."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/joint_colour_source_held_design_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main():
    if sys.argv[1:]!=['--specify-only']:raise SystemExit('Explicit --specify-only required')
    if OUT.exists():raise FileExistsError('Preserve prior design')
    prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
    rows=read(prep/'rows_PRIVATE.json');folds=read(prep/'folds_PRIVATE.json');cases={r['case_id'] for r in rows}
    assert len(rows)==len(cases)==44 and len(folds)==11
    bycase={r['case_id']:r for r in rows}
    for fold in folds:
        assert len(fold['fitting_cases'])==40 and len(fold['evaluation_cases'])==4
        assert set(fold['fitting_cases'])==cases-set(fold['evaluation_cases'])
        assert {bycase[c]['publisher_group'] for c in fold['evaluation_cases']}=={fold['held_publisher_group']}
        assert fold['held_publisher_group'] not in {bycase[c]['publisher_group'] for c in fold['fitting_cases']}
    assert Counter(r['experimental_role'] for r in rows)==dict(identity=11,exposure_under=11,exposure_over=11,colour_cool=11)
    assert all(r['generated_fixture'] is False and r['status']=='available' and '29863' not in r['case_id'] for r in rows)
    for r in rows:assert Path(r['pixels_file']).resolve()==(prep/r['case_id']/'paired_pixels.npz').resolve()
    first=ROOT/'outputs/joint_log_colour_training_feasibility_v1';checked=read(first/'verification_PRIVATE.json')
    assert checked['passed'] and checked['classification']=='STRICT_FITTING_IMPROVEMENT'
    for n,h in checked['artifact_sha256'].items():assert sha(first/n)==h
    firstplan=read(ROOT/'outputs/joint_log_colour_training_design_v1/plan_PRIVATE.json')
    assert folds[0]['fitting_cases']==[r['case_id'] for r in firstplan['fitting_records']]
    assert folds[0]['held_publisher_group']==firstplan['excluded_group']=='ffhq_source_16061'
    assert sha(first/'candidate_PRIVATE.json')=='624347012a0211650dbceb8fc6005958da19e099c34d51437fc70f7f5a7fdc10'
    old=ROOT/'outputs/histogram_gap_source_held_comparison_v1';seal=read(old/'all_supports_sealed_PRIVATE.json');oldcheck=read(old/'verification_PRIVATE.json')
    assert seal['passed'] and oldcheck['passed']
    manual=ROOT/'outputs/approved_correction_support_59807_v1';approval=read(manual/'approval_PRIVATE.json')
    assert approval['source_id']=='59807' and approval['measurement_byte_unchanged'] and not approval['runtime_integrated']
    supports=[];manifest_paths=[]
    for item in seal['supports']:
        source=item['source'];ident=source.removeprefix('ffhq_source_');assert ident.isdigit() and ident!='29863'
        oldfolder=old/'supports'/ident;manifest=oldfolder/'manifest_PRIVATE.json'
        assert sha(manifest)==oldcheck['artifact_sha256'][f'supports/{ident}/manifest_PRIVATE.json'] and read(manifest)==item
        manifest_paths.append(str(manifest.relative_to(ROOT)))
        if ident=='59807':
            assert approval['files']['measurement_mask.png']==item['files']['measurement_mask.png']
            selected=dict(directory=str(manual.relative_to(ROOT)),receipt='approval_PRIVATE.json',receipt_sha256=sha(manual/'approval_PRIVATE.json'),
                files=approval['files'],alpha_filename='correction_alpha.npy',manual_assisted=True,
                provenance='user_approved_source_specific_forehead_neck_microphone')
        else:
            selected=dict(directory=str(oldfolder.relative_to(ROOT)),receipt='manifest_PRIVATE.json',receipt_sha256=sha(manifest),
                files=item['files'],alpha_filename='alpha.npy',manual_assisted=False,
                provenance='exact_saved_reviewed_support_plus_approved_ear_rule')
        assert len(selected['files'])==4
        supports.append(dict(source=source,source_id=ident,face_width=item['face_width'],selected=selected,
            old_support_directory=str(oldfolder.relative_to(ROOT)),old_files=item['files'],
            protection_rule='old_subset_new' if ident=='59807' else 'exact_old',measurement_unchanged=True))
    assert len(supports)==11 and {s['source'] for s in supports}=={r['publisher_group'] for r in rows}
    paths=['docs/joint-colour-source-held-comparison-protocol-2026-11-13.md','scripts/specify_joint_colour_source_held_comparison.py',
        'outputs/joint_log_colour_training_design_v1/plan_PRIVATE.json','outputs/joint_log_colour_training_design_v1/verification_PRIVATE.json',
        'outputs/joint_log_colour_training_feasibility_v1/candidate_PRIVATE.json','outputs/joint_log_colour_training_feasibility_v1/verification_PRIVATE.json',
        'outputs/joint_log_colour_training_feasibility_v1/fitting_inputs_PRIVATE.json','outputs/joint_log_colour_training_feasibility_v1/training_replay_PRIVATE.json',
        'outputs/joint_log_colour_exposed_audit_v1/features_PRIVATE.json','outputs/joint_log_colour_exposed_audit_v1/verification_PRIVATE.json',
        'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json','outputs/reviewed_ffhq_restoration_preparation_v1/folds_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/role_ledger_PRIVATE.json','outputs/reviewed_ffhq_restoration_preparation_v1/mapping_application_PRIVATE.json',
        'outputs/histogram_gap_source_held_comparison_v1/all_supports_sealed_PRIVATE.json','outputs/histogram_gap_source_held_comparison_v1/verification_PRIVATE.json',
        'outputs/approved_correction_support_59807_v1/approval_PRIVATE.json','outputs/correction_support_59807_preview_v1/preview_receipt_PRIVATE.json',
        'src/model_training/joint_colour_training.py','src/model_training/joint_colour_verification.py','src/model_training/portable_tree.py',
        'src/model_training/joint_log_colour.py','src/correction/seamless_blend.py',
        'docs/practical-model-evaluation-protocol-2026-11-12.md','src/demo/oblique_comparison_review.py','src/demo/oblique_comparison_review.html']+manifest_paths
    bindings={n:sha(ROOT/n) for n in paths}
    # Compare declarations only. No mask/alpha/photo byte hashing at specification.
    assert approval['preview_receipt_sha256']==sha(ROOT/'outputs/correction_support_59807_preview_v1/preview_receipt_PRIVATE.json')
    ordered=[c for f in folds for c in f['evaluation_cases']]
    review_order=[c for c in ordered if bycase[c]['experimental_role']=='identity']+[c for c in ordered if bycase[c]['experimental_role']!='identity']
    plan=dict(status='SPECIFIED_NONEXECUTABLE_PENDING_WORKFLOW_QA',protocol_id='truehue_jointcolour281_sourceheld_manual59807_2026_11_13_v1',
        stage='EXPOSED_DEVELOPMENT_NOT_FINAL',folds=folds,feature_names=firstplan['feature_names'],target_names=firstplan['target_names'],settings=firstplan['settings'],
        reuse=dict(fold=folds[0]['held_publisher_group'],path=str((first/'candidate_PRIVATE.json').relative_to(ROOT)),sha256=sha(first/'candidate_PRIVATE.json')),
        new_fits=10,reused_fits=1,held_controls=44,primary_renders=44,secondary_renders=0,attempted=48,available=44,excluded=4,
        support_sources=supports,declared_pixel_containers=[dict(case_id=r['case_id'],path=r['pixels_file'],sha256=r['pixels_sha256']) for r in rows],
        primary=dict(scoring_region='selected_alpha>0',baseline='same_input_same_reference_same_region',
            support_assistance='59807user_approved_manual_revision;others_exact_saved_ear_support',old_aggregate_effect_comparison_allowed=False),
        all_fits_verified_before_held=True,all_supports_sealed_before_scoring=True,families=['exposure_under','exposure_over','colour_cool'],
        metric_replay=dict(abs_tol=1e-10,rel_tol=1e-10,RGB8_exact=True),review_order=review_order,
        anonymous_id_case_order=ordered,review_identity_first=True,early_identity_rejection=True,partial_pass_allowed=False,
        incomplete_unblinding_allowed=False,all44_before_pass=True,scores_hidden_until_all_initial_saved=True,
        reviewer_role='User researcher development appraisal, not expertMOS',display_details='record afresh',
        numerical_failure_requires_visual_review=False,old_failures_reclassified=False,model_adopted=False,
        final_access=False,new_fits_executed=0,predictions=0,arrays_decoded=0,input_sha256=bindings,
        output_directory='outputs/joint_colour_source_held_comparison_v1')
    OUT.mkdir();write(OUT/'plan_PRIVATE.json',plan)
    assert all(sha(ROOT/n)==h for n,h in bindings.items())
    write(OUT/'verification_PRIVATE.json',dict(passed=True,folds=11,cases=44,supports=11,manual_source='59807',
        exact_first_reuse=True,identity_first_count=11,old_regions_not_pooled=True,executable=False,fits=0,predictions=0,arrays_decoded=0,
        plan_sha256=sha(OUT/'plan_PRIVATE.json')))
    print('PASS11folds/10newfits+exactreuse/10old+1manualsupport/44primary/identityfirst earlyreject;specification only')

if __name__=='__main__':main()
