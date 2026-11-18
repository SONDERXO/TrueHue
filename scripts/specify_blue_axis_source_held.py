"""Metadata-only source-held design. No array libraries, trainer or image IO."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    if sys.argv[1:]!=['--specify-only']:raise SystemExit('Explicit specification flag required')
    out=ROOT/'outputs/blue_axis_source_held_design_v1'
    if out.exists():raise FileExistsError('Preserve existing design')
    original=read(ROOT/'outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json')
    prep=ROOT/'outputs/blue_axis_preparation_v1';first=ROOT/'outputs/blue_axis_first_fit_v1'
    pv=read(prep/'verification_PRIVATE.json');fv=read(first/'verification_PRIVATE.json')
    assert pv['passed'] and fv['passed'] and fv['classification']=='BLUE_FITTING_FEASIBILITY_PASS'
    # Own-stage JSON metadata/artifacts only; never hash declared photo/mask paths.
    for folder,v in [(prep,pv),(first,fv)]:
        for n,h in v['artifact_sha256'].items():
            if Path(n).suffix=='.json':assert sha(folder/n)==h
    assert pv['rows_sha256']==sha(prep/'rows_PRIVATE.json')
    for n,h in original['input_sha256'].items():assert sha(ROOT/n)==h
    rows=read(prep/'rows_PRIVATE.json');by={r['case_id']:r for r in rows};assert len(by)==len(rows)==66
    roles=original['roles'];assert Counter(r['role'] for r in rows)=={r:11 for r in roles}
    folds=original['folds'];assert len(folds)==11
    for f in folds:
        fit=f['fitting_cases'];held=f['evaluation_cases'];s=f['held_publisher_group']
        assert len(fit)==len(set(fit))==60 and len(held)==len(set(held))==6
        assert set(fit)==set(by)-set(held) and {by[c]['source'] for c in held}=={s}
        assert s not in {by[c]['source'] for c in fit}
        assert Counter(by[c]['role'] for c in fit)=={r:10 for r in roles}
    snapshot=read(first/'fitting_inputs_PRIVATE.json')
    assert folds[0]['fitting_cases']==[r['case_id'] for r in snapshot]==original['first_fitting_cases']
    for r in snapshot:assert r=={k:by[r['case_id']][k] for k in ['case_id','source','role','x','y']}
    expected='f0177b7040e3bd89e8c035abfbaeeb66a866bef73539166780031b32f3caf370'
    assert sha(first/'candidate_PRIVATE.json')==expected
    assert len(original['support_sources'])==11 and sum(s['selected']['manual_assisted'] for s in original['support_sources'])==1
    paths=['docs/blue-axis-source-held-comparison-protocol-2026-11-13.md','scripts/specify_blue_axis_source_held.py',
      'outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json','outputs/blue_axis_preparation_v1/rows_PRIVATE.json',
      'outputs/blue_axis_preparation_v1/verification_PRIVATE.json','outputs/blue_axis_first_fit_v1/candidate_PRIVATE.json',
      'outputs/blue_axis_first_fit_v1/fitting_inputs_PRIVATE.json','outputs/blue_axis_first_fit_v1/training_replay_PRIVATE.json',
      'outputs/blue_axis_first_fit_v1/verification_PRIVATE.json','outputs/joint_colour_development_freeze_v1/freeze_PRIVATE.json',
      'docs/acceptable-small-change-policy-2026-11-13.md','src/model_training/blue_axis_training.py',
      'src/model_training/blue_axis_verification.py','src/model_training/portable_tree.py','src/correction/seamless_blend.py']
    bindings={n:sha(ROOT/n) for n in paths}
    order=[c for f in folds for c in f['evaluation_cases']]
    plan=dict(status='SPECIFIED_NONEXECUTABLE_PENDING_GENERATED_WORKFLOW_QA',protocol_id='truehue_blueaxis66_sourceheld_2026_11_13_v1',
      stage='EXPOSED_DEVELOPMENT_NOT_FINAL',folds=folds,feature_names=original['feature_names'],target_names=original['target_names'],settings=original['settings'],
      reuse=dict(path=str((first/'candidate_PRIVATE.json').relative_to(ROOT)),sha256=expected,held_source=folds[0]['held_publisher_group']),
      new_fits=10,reused_fits=1,fitting_routes=660,held_controls=66,primary_renders=66,secondary_renders=0,attempted=72,available=66,excluded_cases=original['excluded_cases'],
      support_sources=original['support_sources'],declared_pixel_containers=[dict(case_id=r['case_id'],path=r['pixels_file'],sha256=r['pixels_sha256'],new_blue_pack=not r['old_record_reused']) for r in rows],
      all_fits_verified_before_held=True,all_supports_sealed_before_scoring=True,primary_region='selected_alpha>0',baseline='uncorrected_input_same_reference_same_region',
      numerical_gate=dict(families=roles[1:],metric='source_equal_mean_inputDE_minus_outputDE',each_strictly_positive=True,RGB_secondary_only=True,failure_before_visual=True),
      metric_replay=dict(abs_tol=1e-10,rel_tol=1e-10,RGB8_exact=True),
      review_order=[c for c in order if by[c]['role']=='identity']+[c for c in order if by[c]['role']!='identity'],anonymous_case_order=order,
      identity_rule='no_unwanted_change_slight_acceptable_permitted',early_stop='unwanted_change',cannot_judge='unresolved',
      review_maximum=66,current_review_task=False,carry_forward='only_exact_arrays_support_viewing_question_semantics_with_provenance',incomplete_unblinding=False,
      scores_hidden_until_all_initial_saved=True,reviewer_role='researcher_not_expertMOS',old_model_rescoring=False,model_adopted=False,
      new_fits_executed=0,predictions=0,arrays_decoded=0,final_locked_access=False,input_sha256=bindings,inherited_input_sha256=original['input_sha256'])
    out.mkdir();write(out/'plan_PRIVATE.json',plan)
    assert all(sha(ROOT/n)==h for n,h in bindings.items())
    write(out/'verification_PRIVATE.json',dict(passed=True,plan_sha256=sha(out/'plan_PRIVATE.json'),folds=11,fit_per_fold=60,held_per_fold=6,exact_first_reuse=True,
      five_family_gate=True,identity_policy_preserved=True,executable=False,fits=0,predictions=0,arrays_decoded=0))
    print('PASS metadata:11folds/60fit6held/10new+exactreuse/5familygate; no execution')
if __name__=='__main__':main()
