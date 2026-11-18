"""Metadata-only exact60join/scaffold binding; never fit or decode images."""
from pathlib import Path
from collections import Counter
import json,hashlib,math,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    if sys.argv[1:]!=['--specify-only']:raise SystemExit('Explicit specification flag required')
    out=ROOT/'outputs/fixed_branch_linear_leaf_design_v1'
    if out.exists():raise FileExistsError('Preserve design')
    first=ROOT/'outputs/blue_axis_first_fit_v1';check=read(first/'verification_PRIVATE.json')
    assert check['passed'] and check['classification']=='BLUE_FITTING_FEASIBILITY_PASS'
    for n,h in check['artifact_sha256'].items():assert sha(first/n)==h
    scaffold=read(first/'candidate_PRIVATE.json');assert sha(first/'candidate_PRIVATE.json')=='f0177b7040e3bd89e8c035abfbaeeb66a866bef73539166780031b32f3caf370'
    rows=read(first/'fitting_inputs_PRIVATE.json');prep=ROOT/'outputs/blue_axis_preparation_v1';allrows={r['case_id']:r for r in read(prep/'rows_PRIVATE.json')}
    assert sha(prep/'rows_PRIVATE.json')==read(prep/'verification_PRIVATE.json')['rows_sha256']
    coverage=read(ROOT/'outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json');assert [r['case_id'] for r in rows]==coverage['first_fitting_cases']
    assert len(rows)==60 and len({r['source'] for r in rows})==10 and coverage['first_excluded_source']=='ffhq_source_16061'
    assert Counter(r['role'] for r in rows)=={r:10 for r in coverage['roles']}
    for r in rows:
        original=allrows[r['case_id']]
        assert r=={k:original[k] for k in ['case_id','source','role','x','y']}
        assert original['generated_fixture'] is False and original['status']=='available' and r['source']!='ffhq_source_16061' and '29863' not in r['case_id']
        assert len(r['x'])==281 and all(math.isfinite(v) and struct.unpack('!f',struct.pack('!f',v))[0]==v for v in r['x'])
        assert len(r['y'])==3 and all(math.isfinite(v) and v>0 for v in r['y'])
    names=scaffold['feature_names'];assert names==coverage['feature_names'] and names[5:7]==['scene_log_r_over_g','scene_log_b_over_g']
    topology=[{k:v for k,v in n.items() if k in ['kind','feature','threshold','left','right']} if n['kind']=='split' else dict(kind='linear_leaf') for n in scaffold['nodes']]
    assert len(topology)==11 and sum(n['kind']=='linear_leaf' for n in topology)==6
    files=['docs/linear-leaf-bounded-trial-decision-2026-11-14.md','scripts/specify_fixed_branch_linear_leaf_feasibility.py',
      'outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json','outputs/blue_axis_preparation_v1/rows_PRIVATE.json','outputs/blue_axis_preparation_v1/verification_PRIVATE.json',
      'outputs/blue_axis_first_fit_v1/candidate_PRIVATE.json','outputs/blue_axis_first_fit_v1/fitting_inputs_PRIVATE.json','outputs/blue_axis_first_fit_v1/training_replay_PRIVATE.json','outputs/blue_axis_first_fit_v1/verification_PRIVATE.json',
      'outputs/linear_leaf_generated_v1/results.json','outputs/linear_leaf_generated_v1/verification.json','src/model_training/linear_leaf_generated.py','src/model_training/portable_linear_leaf_tree.py','src/model_training/linear_leaf_scalar_check.py']
    bindings={n:sha(ROOT/n) for n in files}
    plan=dict(status='SPECIFIED_FITTING_ONLY_NONEXECUTABLE_PENDING_ACTUAL_ADAPTER_QA',protocol='fixed_branch_linear_leaf_first60_2026_11_14_v1',feature_names=names,target_names=['gamma','red_gain','blue_gain'],topology=topology,
      excluded_source='ffhq_source_16061',fitting_cases=[r['case_id'] for r in rows],source_ids=sorted({r['source'] for r in rows}),roles=coverage['roles'],leaf_coordinates=[5,6],lambda_fixed=.01,
      leaf_fit_attempts=1,direct_leaf_solves=6,branch_fits=0,coefficient_count=54,branch_scalar_count=15,generated_flags_may_be_changed=False,
      baseline='EXACT_SAVED_ORDINARY_FIRST60_NATIVE_FITTING_REPLAY_NO_REFIT',loss_tolerance=dict(abs_rel=1e-12),gate='red_blue_each_nonworse_strict_combined_gain_exposure_nominal_valid_predictions',
      held_predictions_allowed=False,photo_arrays_allowed=False,new_review_task=False,full_sourceheld_run_selected=False,output_directory='outputs/fixed_branch_linear_leaf_first_fit_v1',
      new_fits_executed=0,new_predictions=0,arrays_decoded=0,model_adopted=False,input_sha256=bindings)
    out.mkdir();write(out/'plan_PRIVATE.json',plan);write(out/'fitting_join_metadata_PRIVATE.json',[dict(case_id=r['case_id'],source=r['source'],role=r['role'],nominal=r['y']) for r in rows])
    assert all(sha(ROOT/n)==h for n,h in bindings.items())
    write(out/'verification_PRIVATE.json',dict(passed=True,plan_sha256=sha(out/'plan_PRIVATE.json'),cases=60,sources=10,excluded_source='ffhq_source_16061',copied_nodes=11,leaf_solves_planned=6,executed=False,arrays_decoded=0))
    print('PASS exact60fit10sources/immutable11node scaffold/6linearleafsolves planned; no fit or held inference')
if __name__=='__main__':main()
