"""Read explicit development reports/frozen JSON only; no final roster or image access."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/joint_colour_qualification_plan_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    if sys.argv[1:]!=['--specify-only']:raise SystemExit('Explicit --specify-only required')
    if OUT.exists():raise FileExistsError('Preserve qualification plan')
    freeze=read(ROOT/'outputs/joint_colour_development_freeze_v1/freeze_PRIVATE.json')
    assert freeze['assessment']=='POSTHOC_REVIEW_ACCEPTABLE' and not freeze['model_adopted'] and not freeze['independent_validation']
    blue={};models={}
    for source,b in freeze['models'].items():
        path=ROOT/b['path'];assert sha(path)==b['sha256']
        tree=read(path);assert tree['feature_names']==freeze['feature_names'] and tree['target_names']==freeze['target_names']
        blue[source]=sorted({n['values'][2] for n in tree['nodes'] if n['kind']=='leaf'})
        assert blue[source]==[1.0];models[b['path']]=b['sha256']
    pages=read(ROOT/'outputs/proposal_scope_validation_20261103_v1/pages.json')
    page66=next(p['text'] for p in pages if p['pdf_page']==66)
    assert '01–03' in page66 and '04–07' in page66 and '08–10' in page66 and '10%' in page66
    scin=read(ROOT/'outputs/mst_retention_checkpoint_v1/summary.json')
    assert scin['case_count']==scin['label_row_count']==5033 and scin['head_neck_at_distance_cases']==368
    paths=['docs/joint-colour-qualification-plan-2026-11-13.md','scripts/specify_joint_colour_qualification.py',
        'docs/darker-skin-bias-priority-2026-11-13.md','docs/acceptable-small-change-policy-2026-11-13.md',
        'docs/joint-colour-acceptability-review-results-2026-11-13.md','docs/mst-calibration-evaluation-design.md',
        'docs/mst-method-retained.md','docs/existing-data-feasibility-results-2026-11-01.md',
        'docs/existing-dataset-correction-evidence-readiness-2026-11-11.md',
        'docs/consolidated-training-design-decision-2026-11-12.md','docs/android-integration-2026-10-31.md',
        'docs/android-consultation-update-2026-11-05.md','outputs/joint_colour_development_freeze_v1/freeze_PRIVATE.json',
        'outputs/proposal_scope_validation_20261103_v1/pages.json','outputs/mst_retention_checkpoint_v1/summary.json']
    bindings={**{n:sha(ROOT/n) for n in paths},**models}
    plan=dict(status='PLAN_ONLY_NOT_EXECUTABLE',development_acceptable=True,criterion_revision_posthoc=True,
        darker_skin_primary_motivation=True,paper_tone_groups=dict(light=[1,2,3],medium=[4,5,6,7],dark=[8,9,10]),
        grouping_source='cachedproposal PDFpage66',predicted_MST_is_not_independent_group_label=True,
        disparity=dict(paper_flag_percent=10,proposed_signed_formula='100*(D_light-D_dark)/D_light if D_light>0 else undefined',
            proposed_absolute_flag='abs(signed_gap)>10',formula_is_operationalization_not_verbatim=True,raw_values_and_direction_required=True,
            uncertainty='1000source-bootstrapresamples seed42 when estimable; singleton/missing NA'),
        current_blue_leaf_values=blue,trained_final_model_exists=False,independent_labelled_cohort_bound=False,
        source_processing_selected=False,final_fit_selected=False,locked_access_selected=False,android_deployment_selected=False,
        stages=[dict(id='freeze_evidence',status='COMPLETE'),dict(id='eligible_source_and_label_roles',status='UNBOUND'),
            dict(id='blue_severity_combined_coverage',status='UNSUPPORTED'),dict(id='one_final_predictor',status='NOT_SELECTED'),
            dict(id='prospective_evaluation',status='NOT_EXECUTABLE'),dict(id='generated281_parity',status='SPECIFICATION_NEXT'),
            dict(id='android_device_evidence',status='PENDING'),dict(id='expertMOS_and_paper',status='AFTER_MODEL_PER_USER')],
        historical_SCIN_metadata=dict(as_of='saved28Octcheckpoint;notnewavailabilityaudit',cases=5033,head_neck_pool=368,local_pool_images=9,
            both_annotators_preserved=True,agreement_only_admission=False),
        interpretation='Supporteddevelopmentrestoration;notvalidatedbiasreduction/fullblue/finalmodel',input_sha256=bindings,
        new_fits=0,new_predictions=0,image_arrays=0,final_or_older_locked_contents_read=False,runtime_changed=False,model_adopted=False)
    OUT.mkdir();write(OUT/'plan_PRIVATE.json',plan)
    assert all(sha(ROOT/n)==h for n,h in bindings.items())
    write(OUT/'verification_PRIVATE.json',dict(passed=True,cached_paper_groups_verified=True,frozen_fold_hashes_verified=11,
        blue_constant_all11=True,source_reports_unchanged=True,plan_sha256=sha(OUT/'plan_PRIVATE.json'),
        fits=0,predictions=0,image_arrays=0,locked_contents_read=False,executable=False))
    print('PASS plan/papergroups/11frozenmodels/constantblue/provenance;0fits/images/lockedaccess')
if __name__=='__main__':main()
