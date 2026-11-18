"""Metadata-only281input fitting design; imports no optimizer and never fits."""
from pathlib import Path
import hashlib,json,math,struct,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/joint_log_colour_training_design_v1'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def f32(v):
    assert type(v) in (int,float) and math.isfinite(v)
    result=struct.unpack('!f',struct.pack('!f',v))[0];assert math.isfinite(result);return result
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main():
    if sys.argv[1:]!=['--specify-only']:raise SystemExit('Explicit --specify-only required')
    if OUT.exists():raise FileExistsError('Preserve prior complete/partial design')
    parent=read(ROOT/'outputs/histogram_gap_training_feasibility_design_v1/plan_PRIVATE.json')
    old=read(ROOT/'outputs/histogram_gap_training_feasibility_v1/fitting_inputs_PRIVATE.json')
    oldcheck=read(ROOT/'outputs/histogram_gap_training_feasibility_v1/verification_PRIVATE.json')
    baseline=read(ROOT/'outputs/histogram_gap_training_feasibility_v1/candidate_PRIVATE.json')
    assert oldcheck['passed'] and oldcheck['rows']==40 and baseline['feature_names']==parent['feature_names']
    assert [r['case_id'] for r in old]==[r['case_id'] for r in parent['fitting_records']]
    auditpath=ROOT/'outputs/joint_log_colour_exposed_audit_v1/features_PRIVATE.json'
    check=read(auditpath.parent/'verification_PRIVATE.json')
    assert check['passed'] and check['inputs']==44 and check['features_sha256']==sha(auditpath)
    for name,h in check['input_sha256'].items():assert sha(ROOT/name)==h,name
    generated=read(ROOT/'outputs/joint_log_colour_generated_v1/verification_PRIVATE.json')
    for name,h in generated['input_sha256'].items():assert sha(ROOT/name)==h,name
    newnames=['joint_colour_available','joint_colour_positive_fraction','joint_colour_clipped_fraction']+[
        f'joint_colour_u{i:02}_v{j:02}' for i in range(16) for j in range(16)]
    names=parent['feature_names']+newnames;assert len(names)==len(set(names))==281
    wanted={r['case_id'] for r in old};audited={}
    for record in read(auditpath):
        if record['case_id'] not in wanted:continue
        assert record['case_id'] not in audited;audited[record['case_id']]=record
    assert set(audited)==wanted
    snapshot=[]
    for r,binding in zip(old,parent['fitting_records']):
        a=audited[r['case_id']]
        assert a['generated_fixture'] is False and a['source']==r['source']==binding['source']!=parent['excluded_group']
        assert a['role']==r['role']==binding['role'] and a['available'] and len(a['features'])==259
        assert [f32(v) for v in a['old22']]==r['x']
        extra=[f32(v) for v in a['features']];assert len(extra)==259
        assert all(0<=v<=1 for v in extra) and extra[0]==1
        assert len(r['y'])==3 and all(v>0 and math.isfinite(v) for v in r['y'])
        snapshot.append(dict(case_id=r['case_id'],source=r['source'],role=r['role'],x=r['x']+extra,y=r['y']))
    assert len(snapshot)==40 and len({r['source'] for r in snapshot})==10
    assert all(len(r['x'])==281 for r in snapshot)
    sources={r['source'] for r in snapshot}
    assert all([r['role'] for r in snapshot if r['source']==s]==['identity','exposure_under','exposure_over','colour_cool'] for s in sources)
    settings=dict(criterion='squared_error',splitter='best',max_depth=4,random_state=42,min_samples_leaf=1,min_samples_split=2,
        min_weight_fraction_leaf=0.,max_features=None,max_leaf_nodes=None,min_impurity_decrease=0.,ccp_alpha=0.,monotonic_cst=None)
    assert parent['settings']==settings
    paths=['docs/joint-log-colour-training-feasibility-protocol-2026-11-13.md','scripts/specify_joint_log_colour_training_feasibility.py',
        'outputs/histogram_gap_training_feasibility_design_v1/plan_PRIVATE.json',
        'outputs/histogram_gap_training_feasibility_v1/fitting_inputs_PRIVATE.json',
        'outputs/histogram_gap_training_feasibility_v1/candidate_PRIVATE.json',
        'outputs/histogram_gap_training_feasibility_v1/verification_PRIVATE.json',
        'outputs/histogram_gap_training_feasibility_v1/training_replay_PRIVATE.json',
        'outputs/joint_log_colour_exposed_audit_v1/features_PRIVATE.json',
        'outputs/joint_log_colour_exposed_audit_v1/verification_PRIVATE.json',
        'outputs/joint_log_colour_exposed_audit_v1/metadata_crosscheck_PRIVATE.json',
        'outputs/joint_log_colour_generated_v1/verification_PRIVATE.json',
        'src/model_training/joint_log_colour.py','src/model_training/portable_tree.py']
    # Bind original row files by declared exact fitting records only, not broad data inventory.
    paths+=list(dict.fromkeys(r['record'] for r in parent['fitting_records']))
    bindings={p:sha(ROOT/p) for p in paths}
    OUT.mkdir()
    plan=dict(status='SPECIFIED_NONEXECUTABLE_PENDING_GENERATED_RUNNER_QA',fitting_records=parent['fitting_records'],
        excluded_group=parent['excluded_group'],feature_names=names,new_feature_names=newnames,old_prefix_width=22,
        target_names=['gamma','red_gain','blue_gain'],settings=settings,fit_calls=1,restarts=0,
        baseline=dict(path='outputs/histogram_gap_training_feasibility_v1/candidate_PRIVATE.json',refit=False,
            saved_fitting_SSE=oldcheck['candidate']['SSE']),audited_features_path=str(auditpath.relative_to(ROOT)),
        output_directory='outputs/joint_log_colour_training_feasibility_v1',input_sha256=bindings,
        max_nodes=31,max_splits=15,max_leaves=16,held_predictions_allowed=False,pixel_reads_allowed=False,
        sample_weights=False,scaling=False,source_role_inputs=False,reference_subtraction=False,feature_selection=False,
        strict_gain_formula='baselineSSE-candidateSSE > 1e-12*max(1,baselineSSE)',automatic_followup=False,
        generated_runner_verification_required=True,real_fits_executed=0,model_adopted=False)
    write(OUT/'plan_PRIVATE.json',plan)
    write(OUT/'fitting_join_metadata_ONLY_PRIVATE.json',snapshot)
    assert all(sha(ROOT/n)==h for n,h in bindings.items())
    write(OUT/'verification_PRIVATE.json',dict(passed=True,plan_sha256=sha(OUT/'plan_PRIVATE.json'),
        metadata_snapshot_sha256=sha(OUT/'fitting_join_metadata_ONLY_PRIVATE.json'),rows=40,sources=10,features=281,
        old22_exact=True,all259_added_in_frozen_order=True,excluded_source_absent=True,all_hashes_unchanged=True,
        fits=0,predictions=0,photo_arrays=0,executable=False))
    print('PASS fixed40row/281input metadata design;0fits/predictions/photoarrays;generated runner QA still required')

if __name__=='__main__':main()
