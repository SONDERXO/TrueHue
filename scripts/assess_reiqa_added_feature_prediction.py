"""Matched saved-result assessment, not a refit or new correction proposal."""
from pathlib import Path
import sys,json,math,collections
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.model_training.reiqa_frozen_features import sha
RUN=ROOT/'outputs/reiqa_added_feature_prediction_v1'
BASE=ROOT/'outputs/five_control_source_held_prediction_v1'
OUT=ROOT/'outputs/reiqa_added_feature_assessment_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    if OUT.exists():raise FileExistsError(OUT)
    verified=read(RUN/'verification_PRIVATE.json');oldproof=read(BASE/'verification_PRIVATE.json')
    assert verified['passed'] and oldproof['passed']
    for proof in [verified,oldproof]:
        proof['artifact_sha256']={Path(k).as_posix():v for k,v in proof['artifact_sha256'].items()}
    # Exact declared run metadata only; no pixel containers need to be reopened.
    new_summary=read(RUN/'evaluation/summary.json');old_summary=read(BASE/'evaluation/summary.json')
    assert sha(BASE/'evaluation/summary.json')==oldproof['artifact_sha256']['evaluation/summary.json']
    assert sha(RUN/'evaluation/summary.json')==verified['artifact_sha256']['evaluation/summary.json']
    models=read(RUN/'models/all_fits_verified.json')['models'];details={};split_count=collections.Counter()
    for m in models:
        tree=read(m['tree_path']);fitted=read(m['fitting_rows_path']);native=read(m['replay_path'])
        usage=dict(learned=sum(n['kind']=='split' and n['feature']>=281 for n in tree['nodes']),
                   traditional=sum(n['kind']=='split' and n['feature']<281 for n in tree['nodes']))
        split_count.update(usage)
        details[m['held_source_id']]=dict(usage=usage,tree=tree,fitted=fitted,native=native)
    sealed=read(RUN/'models/held_controls_sealed.json');matched=[]
    for p in sealed:
        relative='evaluation/'+p['case_id']+'.json'
        assert sha(BASE/relative)==oldproof['artifact_sha256'][relative]
        assert sha(RUN/relative)==verified['artifact_sha256'][relative]
        old,new=read(BASE/relative),read(RUN/relative)
        assert all(new[k]==old[k] for k in ['case_id','source_id','role','generated_fixture','oracle_controls'])
        assert new['regions']['primary']['input']==old['regions']['primary']['input']
        assert new['regions']['primary']['constant']==old['regions']['primary']['constant']
        detail=details[p['source_id']]
        members=[r for r,l in zip(detail['fitted'],detail['native']['leaves']) if l==p['leaf']]
        roles=dict(collections.Counter(r['role'] for r in members))
        matched.append(dict(case_id=p['case_id'],source_id=p['source_id'],role=p['role'],
            input_metrics=new['regions']['primary']['input'],saved281_metrics=old['regions']['primary']['tree'],
            added4377_metrics=new['regions']['primary']['tree'],
            delta_vs_saved281={k:new['regions']['primary']['tree'][k]-old['regions']['primary']['tree'][k] for k in ['RGB','DE']},
            controls=p['controls'],oracle_controls=new['oracle_controls'],
            leaf=p['leaf'],fitting_leaf_roles=roles,identity_whole_RGB_change=new['identity_mean_RGB_change']))
    grouped={}
    for role in new_summary['by_role']:
        own=[r for r in matched if r['role']==role]
        grouped[role]=dict(input=new_summary['by_role'][role]['means']['input'],
            saved281=old_summary['by_role'][role]['means']['tree'],added4377=new_summary['by_role'][role]['means']['tree'],
            constant=new_summary['by_role'][role]['means']['constant'],
            regressions_vs_input={k:[r['case_id'] for r in own if r['added4377_metrics'][k]>r['input_metrics'][k]+1e-10] for k in ['RGB','DE']},
            regressions_vs_saved281={k:[r['case_id'] for r in own if r['delta_vs_saved281'][k]>1e-10] for k in ['RGB','DE']})
    neutral=[r for r in matched if r['role'] in ['identity','colour_only']]
    wrong_exposure=[r for r in neutral if all(k not in ['identity','colour_only'] for k in r['fitting_leaf_roles'])]
    result=dict(status=new_summary['status'],fixed_trial_closed=new_summary['status']=='NOT_ADVANCED',
        numeric_role_checks=new_summary['numeric_role_checks'],matched_cases=66,by_role=grouped,
        split_usage=dict(split_count),neutral_in_pure_exposure_leaves=[r['case_id'] for r in wrong_exposure],
        per_fold_split_usage={s:d['usage'] for s,d in details.items()},
        human_acceptability='not_assessed_no_new_ratings',new_fits=0,model_ready=False,
        next_experiment_selected=False,
        evidence_hashes={str(p.relative_to(ROOT)):sha(p) for p in [RUN/'verification_PRIVATE.json',BASE/'verification_PRIVATE.json',Path(__file__)]})
    OUT.mkdir();write(OUT/'matched_cases_PRIVATE.json',matched);write(OUT/'assessment_PRIVATE.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['by_role','evidence_hashes']},indent=2))
if __name__=='__main__':main()
