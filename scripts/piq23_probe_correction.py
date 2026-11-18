"""One approved external PIQ23-head316 correction assessment; reuse verified seams."""
from pathlib import Path
import sys,math,copy
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from wb_feature_direct_workflow import SETTINGS,read,write,sha,select
from wb_feature_direct_verify import verify_fit,route,close
from synthetic_probe_correction_workflow import fit_all,validate,versions
from joint_cue_tree_workflow import score as score_pixels,ROLES
from src.model_training.exposure_quality_training import score
DESIGN=ROOT/'outputs/piq23_probe_correction_design_v1'
OUT=ROOT/'outputs/piq23_probe_correction_prediction_v1'
HEAD=ROOT/'outputs/piq23_actual_head_v1'
PROBE=ROOT/'outputs/synthetic_exposure_probe_v2'
WB=ROOT/'outputs/wb_feature_direct_prediction_v1'
FILES=['scripts/piq23_probe_correction.py','scripts/synthetic_probe_correction_workflow.py',
 'scripts/wb_feature_direct_workflow.py','scripts/wb_feature_direct_verify.py','scripts/joint_cue_tree_workflow.py',
 'src/model_training/exposure_quality_training.py','src/model_training/luminance_chroma_operator.py',
 'src/evaluation/luminance_chroma_scalar.py','src/evaluation/directional_recoverability.py',
 'docs/piq23-probe-correction-protocol-2026-11-18.md']
def scalar_score(h,x):return math.fsum(w*((float(v)-m)/s) for w,v,m,s in zip(h['weights'],x,h['mean'],h['scale']))
def current_cues(head,base,minus,plus):
    values=[score(head,v) for v in [base,minus,plus]];independent=[scalar_score(head,v) for v in [base,minus,plus]]
    for a,b in zip(values,independent):close(a,b)
    return np.asarray([values[1]-values[0],values[2]-values[0]],np.float32).astype(float).tolist(),values
def prepare():
    if DESIGN.exists():raise FileExistsError(DESIGN)
    qa_path=ROOT/'outputs/synthetic_probe_correction_engineering_v3/verification.json';qa=read(qa_path)
    assert qa['passed'] and qa['versions']==versions()
    for p,h in qa['code_sha256'].items():assert sha(ROOT/p)==h
    hv=read(HEAD/'verification.json');ha=read(HEAD/'independent_audit.json');assert hv['passed'] and ha['passed'] and hv['real_head_fits']==1
    for p,h in hv['artifacts'].items():assert sha(HEAD/p)==h
    head=read(HEAD/'head.json');assert not head['generated_fixture'] and sha(HEAD/'head.json')=='fb5b1609d3933c2280844e5e2a19b0255db215b7969ba4ce1e4af9a8528fc9b6'
    assert head['bias']==0 and len(head['training_ids'])==3630 and len(head['scene_pair_counts'])==35
    pv=read(PROBE/'verification.json');assert pv['passed'] and sha(PROBE/'features.npz')==pv['features_sha256']
    for p,h in read(PROBE/'execution_bindings.json')['sha256'].items():assert sha(ROOT/p)==h
    original=read(WB/'rows.json');parent=read(WB/'verification.json');assert parent['passed']
    known={p.replace('\\','/'):h for p,h in parent['artifacts'].items()}
    bound={p:sha(ROOT/p) for p in FILES};bound.update(read(PROBE/'execution_bindings.json')['sha256'])
    for p in [qa_path,PROBE/'verification.json',PROBE/'features.npz',PROBE/'execution_bindings.json',HEAD/'head.json',HEAD/'verification.json',HEAD/'independent_audit.json']:
        bound[p.relative_to(ROOT).as_posix()]=sha(p)
    for name in ['rows.json','plan.json','records.json','summary.json','held_controls_sealed.json']:
        assert sha(WB/name)==known[name];bound[(WB/name).relative_to(ROOT).as_posix()]=known[name]
    assert not set(head['training_ids'])&{r['case_id'] for r in original}
    original_plan=read(WB/'plan.json');assert original_plan['settings']==SETTINGS
    plan=dict(folds=original_plan['folds'],settings=SETTINGS,generated_fixture=False,
       head_training_sources={f['held_source_id']:['PIQ23:'+s for s in head['scene_pair_counts']] for f in original_plan['folds']},
       external_head_sha256=sha(HEAD/'head.json'),person_overlap='UNKNOWN_NOT_CERTIFIED',head_scope='one_fixed_external_PIQ23_head_for_all_folds')
    rows=[];cue_records=[]
    with np.load(ROOT/'outputs/camera_halfstop_neural_v1/features.npz',allow_pickle=False) as base,np.load(PROBE/'features.npz',allow_pickle=False) as probes:
        assert set(base.files)=={r['case_id'] for r in original}
        assert set(probes.files)=={r['case_id']+suffix for r in original for suffix in ['__minus','__plus']}
        for r in original:
            case=r['case_id'];cue,values=current_cues(head,base[case],probes[case+'__minus'],probes[case+'__plus'])
            x=r['x314']+cue;assert len(x)==316 and np.isfinite(x).all() and x[:314]==r['x314']
            rows.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture','y']}|dict(x316=x))
            cue_records.append(dict(case_id=case,scores=values,cues=cue))
            p=WB/'evaluation'/(case+'.npz');assert sha(p)==known['evaluation/'+case+'.npz'];bound[p.relative_to(ROOT).as_posix()]=sha(p)
    fold_rows={f['held_source_id']:[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x316']}|
        dict(outer_head_source=f['held_source_id'])|(dict(y=r['y']) if r['source_id']!=f['held_source_id'] else {}) for r in rows] for f in plan['folds']}
    validate(plan,fold_rows)
    # New assembly risk: all folds use one external head and held targets stay absent.
    for source,rr in fold_rows.items():
        for r in rr:
            assert ('y' in r)==(r['source_id']!=source) and r['x316']==next(a['x316'] for a in rows if a['case_id']==r['case_id'])
    class Poison(dict):
        def __getitem__(self,key):
            if key in ('x316','y'):raise AssertionError('Held fitting payload read')
            return super().__getitem__(key)
    f=plan['folds'][0];rr=fold_rows[f['held_source_id']]
    assert len(select([Poison(r) if r['source_id']==f['held_source_id'] else r for r in rr],f,'316'))==60
    # Width/nonfinite validation must fail before the reused fitter constructs any tree.
    for kind in ['width','nonfinite']:
        bad=copy.deepcopy(fold_rows)
        if kind=='width':bad[f['held_source_id']][0]['x316'].pop()
        else:bad[f['held_source_id']][0]['x316'][0]=float('nan')
        try:validate(plan,bad)
        except ValueError:pass
        else:raise AssertionError('Invalid current assembly accepted')
    for p,h in bound.items():assert sha(ROOT/p)==h
    DESIGN.mkdir();write(DESIGN/'plan.json',plan);write(DESIGN/'rows.json',rows);write(DESIGN/'fold_rows.json',fold_rows)
    write(DESIGN/'cues.json',cue_records);write(DESIGN/'bindings.json',bound)
    write(DESIGN/'authorization.json',dict(exact_reply="okay lets do that, just make sure we're not going in circles again. I want real progress. I want ot finish the correction model fast.",
        scope='one frozen external PIQ23head316-feature/11tree comparison; prior loss failure unchanged; no repeatheadtraining'))
    write(DESIGN/'verification.json',dict(passed=True,versions=versions(),reused_generated_full_workflow=True,new_generated_fits=0,
        new_head_fits=0,new_encoder_calls=0,new_input_decodes=0,scalar_scores=198,raw_cues=132,prefix_values=20724,
        held_targets_absent=True,one_external_head_all_rows=True,invalid_width_nonfinite_poison=True,
        output_sha256={n:sha(DESIGN/n) for n in ['plan.json','rows.json','fold_rows.json','cues.json','bindings.json','authorization.json']}))
    print('PASS currentPIQhead198scalar scores/132cues/20724prefix/reused316QA;0headfits/encodercalls/pixelreads.',flush=True)

def run():
    if OUT.exists():raise FileExistsError('Existing real comparison attempt')
    v=read(DESIGN/'verification.json');assert v['passed'] and v['versions']==versions()
    for p,h in v['output_sha256'].items():assert sha(DESIGN/p)==h
    bound=read(DESIGN/'bindings.json')
    for p,h in bound.items():assert sha(ROOT/p)==h
    plan=read(DESIGN/'plan.json');rows=read(DESIGN/'rows.json');fold_rows=read(DESIGN/'fold_rows.json')
    fit_all(plan,fold_rows,OUT);write(OUT/'bindings.json',bound)
    previous={r['case_id']:r for r in read(WB/'records.json')};old={r['case_id']:r for r in read(WB/'held_controls_sealed.json')};access=[]
    try:
        def loader(row,p):
            assert read(OUT/'prediction_seal.json')['predictions']==66 and read(OUT/'all_fits_verified.json')['verified_fits']==11
            for a,b in zip(p['constant'],old[row['case_id']]['constant']):close(a,b,1e-12)
            with np.load(WB/'evaluation'/(row['case_id']+'.npz'),allow_pickle=False) as pack:
                arrays={k:pack[k].copy() for k in ['input','reference','alpha','protected','314','constant']}
            access.append(dict(case_id=row['case_id'],stage='after11fitproofs_and66sealed_controls',keys=list(arrays)))
            arrays['saved314']=arrays.pop('314');arrays['parent_scores']=previous[row['case_id']]['regions'];return arrays
        result=score_pixels(rows,OUT,loader);write(OUT/'access.json',access)
        for p,h in bound.items():assert sha(ROOT/p)==h
        write(OUT/'verification.json',dict(passed=True,real_control_fits=11,head_refits=0,new_encoder_calls=0,
            fitting_routes=660,held_controls=66,scalar_render_metric_checks=66,all_fits_before_held=True,
            controls_sealed_before_reference_pixels=True,numerical_eligible=result['numerical_eligible'],model_ready=False,
            candidate_alias='joint_means_PIQ23_external316_here',versions=versions(),
            artifact_sha256={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
        print('COMPLETE externalPIQ316/numerical_eligible='+str(result['numerical_eligible']),flush=True)
    except Exception as exc:write(OUT/'scoring_failure.json',dict(error=repr(exc),completed_case_access=len(access)));raise

def audit():
    dest=OUT/'independent_audit.json'
    if dest.exists():raise FileExistsError(dest)
    v=read(OUT/'verification.json');assert v['passed'] and v['real_control_fits']==11
    for p,h in v['artifact_sha256'].items():assert sha(OUT/p)==h
    for p,h in read(OUT/'bindings.json').items():assert sha(ROOT/p)==h
    plan=read(OUT/'plan.json');folds=read(OUT/'fold_rows.json');controls={r['case_id']:r for r in read(OUT/'held_controls_sealed.json')}
    old={r['case_id']:r for r in read(WB/'rows.json')};head=read(HEAD/'head.json');assert sha(HEAD/'head.json')==plan['external_head_sha256']
    fit_count=held_count=cue_count=prefix_count=0;splits=0;used=[]
    with np.load(ROOT/'outputs/camera_halfstop_neural_v1/features.npz',allow_pickle=False) as base,np.load(PROBE/'features.npz',allow_pickle=False) as probes:
        expected={}
        for case in old:
            val=[scalar_score(head,x) for x in [base[case],probes[case+'__minus'],probes[case+'__plus']]]
            expected[case]=np.asarray([val[1]-val[0],val[2]-val[0]],np.float32).astype(float).tolist()
        for f in plan['folds']:
            s=f['held_source_id'];rr=folds[s];model=read(OUT/'models'/(s+'.json'));assert model['dimensions']==316
            verify_fit(model,select(rr,f,'316'),f,SETTINGS);fit_count+=60
            for r in rr:
                case=r['case_id'];assert r['x316'][:314]==old[case]['x314'];prefix_count+=314
                for a,b in zip(r['x316'][314:],expected[case]):close(a,b);cue_count+=1
                if r['source_id']==s:
                    assert 'y' not in r
                    leaf,p=route(model,r['x316']);assert p==controls[case]['controls'] and leaf==controls[case]['leaf'];held_count+=1
            n=sum(x['kind']=='split' and x['feature']>=314 for x in model['nodes']);splits+=n
            if n:used.append(s)
    records=read(OUT/'records.json');summary=read(OUT/'summary.json');count=0
    for role in ROLES:
        for label in ['input','constant','saved314','joint']:
            for m in ['RGB','DE']:
                mean=math.fsum(r['regions']['primary'][label][m] for r in records if r['role']==role)/11
                close(mean,summary['by_role'][role][label][m]);count+=1
    means=summary['by_role'];gates={r:all(means[r]['joint'][m]<means[r][b][m]-1e-10 for m in ['RGB','DE'] for b in ['input','constant']) for r in ROLES[1:]}
    under=all(means['exposure_under']['joint'][m]<means['exposure_under']['saved314'][m]-1e-10 for m in ['RGB','DE'])
    colour=all(means['colour_only']['joint'][m]<=means['colour_only']['saved314'][m]+1e-10 for m in ['RGB','DE'])
    assert summary['role_gates']==gates and summary['under_improvement']==under and summary['colour_nonworse']==colour
    assert summary['numerical_eligible']==v['numerical_eligible']==(all(gates.values()) and under and colour)
    write(dest,dict(passed=True,artifact_hashes=len(v['artifact_sha256']),fitting_routes=fit_count,held_routes=held_count,
        prefix_values=prefix_count,cue_values=cue_count,mean_checks=count,cue_splits=splits,models_using_cues=used,
        numerical_eligible=summary['numerical_eligible'],new_fits=0,new_pixel_reads=0,model_ready=False))
    print(read(dest),flush=True)
if __name__=='__main__':{'prepare':prepare,'run':run,'audit':audit}[sys.argv[1]]()
