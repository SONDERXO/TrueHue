"""Bind exact66condition/first60fit coverage design. No arrays or optimizer imports."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/blue_axis_coverage_design_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    if sys.argv[1:]!=['--specify-only']:raise SystemExit('Explicit --specify-only required')
    if OUT.exists():raise FileExistsError('Preserve prior design')
    current=read(ROOT/'outputs/joint_colour_source_held_design_v1/plan_PRIVATE.json')
    freeze=read(ROOT/'outputs/joint_colour_development_freeze_v1/freeze_PRIVATE.json')
    check=read(ROOT/'outputs/qualification_eligibility_blue_check_v1/verification_PRIVATE.json');assert check['passed']
    for n,h in check['input_sha256'].items():assert sha(ROOT/n)==h
    prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1';rows=read(prep/'rows_PRIVATE.json')
    identities=[r for r in rows if r['experimental_role']=='identity'];assert len(rows)==44 and len(identities)==11
    expected='54632 39568 29617 16061 52445 32685 53146 48879 49131 59807 46795'.split()
    assert [r['case_id'].split('__')[0].removeprefix('ffhq_') for r in identities]==expected
    assert current['feature_names']==freeze['feature_names'] and len(current['feature_names'])==281 and current['settings']==freeze['settings']
    roles=['identity','exposure_under','exposure_over','colour_cool','blue_decrease','blue_increase']
    operations=dict(blue_decrease=dict(gamma=1.,red_gain=1.,blue_gain=245/255,nominal_controls=[1.,1.,255/245]),
        blue_increase=dict(gamma=1.,red_gain=1.,blue_gain=255/245,nominal_controls=[1.,1.,245/255]))
    allcases=[];old_by_source={}
    for r in rows:old_by_source.setdefault(r['publisher_group'],[]).append(r)
    bases=[]
    for ident,r in zip(expected,identities):
        path=Path(r['pixels_file']);assert path.resolve()==(prep/r['case_id']/'paired_pixels.npz').resolve()
        assert r['generated_fixture'] is False and r['status']=='available' and r['provided_mst_label'] is None
        bases.append(dict(source=r['publisher_group'],source_id=ident,identity_case=r['case_id'],identity_container=r['pixels_file'],identity_sha256=r['pixels_sha256'],
            allowed_key='input_rgb8',official_tone_label=None,reference_role='alreadyreviewedexposedphotographicreference'))
        old=old_by_source[r['publisher_group']];assert [a['experimental_role'] for a in old]==roles[:4]
        for a in old:
            allcases.append(dict(case_id=a['case_id'],source=a['publisher_group'],role=a['experimental_role'],kind='EXACT_OLD_RECORD_REUSE',
                existing_container=a['pixels_file'],existing_container_sha256=a['pixels_sha256'],nominal_controls=a['nominal_controls']))
        for role in roles[4:]:allcases.append(dict(case_id=f'ffhq_{ident}__{role}',source=r['publisher_group'],role=role,kind='PLANNED_NEW_NOT_GENERATED',nominal_controls=operations[role]['nominal_controls']))
    folds=[]
    for f in current['folds']:
        held=f['held_publisher_group'];folds.append(dict(held_publisher_group=held,
            fitting_cases=[r['case_id'] for r in allcases if r['source']!=held],evaluation_cases=[r['case_id'] for r in allcases if r['source']==held]))
    assert len(allcases)==len({r['case_id'] for r in allcases})==66
    assert Counter(r['role'] for r in allcases)=={r:11 for r in roles}
    assert all(len(f['fitting_cases'])==60 and len(f['evaluation_cases'])==6 and set(f['fitting_cases']).isdisjoint(f['evaluation_cases']) for f in folds)
    assert folds[0]['held_publisher_group']=='ffhq_source_16061'
    paths=['docs/blue-axis-coverage-feasibility-protocol-2026-11-13.md','scripts/specify_blue_axis_coverage.py',
        'outputs/joint_colour_source_held_design_v1/plan_PRIVATE.json','outputs/joint_colour_development_freeze_v1/freeze_PRIVATE.json',
        'outputs/qualification_eligibility_blue_check_v1/verification_PRIVATE.json','outputs/qualification_eligibility_blue_check_v1/summary_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json','outputs/reviewed_ffhq_restoration_preparation_v1/mapping_application_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/verification_PRIVATE.json',
        'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json','outputs/joint_log_colour_exposed_audit_v1/features_PRIVATE.json',
        'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json','src/ita_estimation/compute_ita.py','src/ita_estimation/shared_core_mst.py',
        'src/model_training/whole_scene_features.py','src/model_training/green_distribution_features.py','src/model_training/histogram_gap_features.py',
        'src/model_training/joint_log_colour.py','src/model_training/portable_tree.py','src/distortion_generation/paper_gamma.py',
        'outputs/joint_log_colour_training_feasibility_v1/verification_PRIVATE.json']
    bindings={n:sha(ROOT/n) for n in paths}
    plan=dict(status='SPECIFIED_NONEXECUTABLE_PENDING_GENERATED_PREPARATION_AND_FIT_QA',protocol_id='truehue_fixed_blue_axis_extension_2026_11_13_v1',
        stage='EXPOSED_DEVELOPMENT_COVERAGE_NOT_FINAL',source_references=bases,roles=roles,operations=operations,cases=allcases,folds=folds,
        original_records_reused=44,new_records_planned=22,available_planned=66,attempts_planned=72,
        excluded_cases=[f'ffhq_29863__{role}' for role in roles],feature_names=current['feature_names'],target_names=current['target_names'],settings=current['settings'],
        support_sources=current['support_sources'],same_geometry_manual_assistance_disclosed=True,clip_exclusion_allowed=False,
        preparation_input_keys=['input_rgb8'],recompute_all281_for_new_inputs=True,original44_features_exact=True,new_mapping_fit_allowed=False,
        first_fitting_cases=folds[0]['fitting_cases'],first_excluded_source=folds[0]['held_publisher_group'],first_fit_calls=1,restarts=0,
        blue_fitting_checks=dict(nonconstant_range_gt=1e-12,baseline='best_constant_training_blue_mean',
            strict_SSE_gain='constantBlueSSE-newBlueSSE > 1e-12*max(1,constantBlueSSE)',decrease_role_mean='>1+1e-12',increase_role_mean='<1-1e-12'),
        automatic_full_comparison=False,held_predictions_allowed=False,new_review_task=False,final_model_selected=False,
        real_conditions_generated=0,fits_executed=0,arrays_decoded=0,final_locked_access=False,input_sha256=bindings)
    OUT.mkdir();write(OUT/'plan_PRIVATE.json',plan)
    assert all(sha(ROOT/n)==h for n,h in bindings.items())
    write(OUT/'verification_PRIVATE.json',dict(passed=True,sources=11,old_records=44,new_records_planned=22,folds=11,first_fit_rows=60,first_held_rows=6,
        source_separation=True,immutable_recipe_retained=True,input_hashes_unchanged=True,photos=0,fits=0,predictions=0,executable=False,
        plan_sha256=sha(OUT/'plan_PRIVATE.json')))
    print('PASS11reviewedrefs/44reuse+22plannedblue/66conditions/60fit6held/fixedsettings+bluechecks;specification only')
if __name__=='__main__':main()
