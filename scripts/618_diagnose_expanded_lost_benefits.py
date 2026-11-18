"""Describe frozen lost-benefit decisions; no fitting, rendering or source-image reads."""
from pathlib import Path
from collections import Counter
import hashlib,json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/expanded_lost_benefit_diagnosis_v1'

def route(tree, features):
    x=np.asarray(features,np.float32);i=tree['root'];steps=[]
    while tree['nodes'][i]['kind']=='split':
        n=tree['nodes'][i];left=bool(x[n['feature']]<=n['threshold'])
        steps.append(dict(feature=tree['feature_names'][n['feature']],value=float(x[n['feature']]),threshold=n['threshold'],left=left))
        i=n['left'] if left else n['right']
    return i,steps,tree['nodes'][i]['values']

def main():
    if OUT.exists():raise FileExistsError('Preserve completed diagnosis')
    bound={}
    def read(name):
        p=ROOT/name;b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
    old=read('outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    new=read('outputs/expanded_correction_models_v1/models_PRIVATE.json')
    ev=read('outputs/expanded_correction_comparison_v1/results_PRIVATE.json')
    assert read('outputs/expanded_correction_models_v1/verification_PRIVATE.json')['passed']
    assert read('outputs/expanded_correction_comparison_v1/verification_PRIVATE.json')['passed']
    predictions=[{p['case_id']:p for p in m['predictions']} for m in (old,new)]
    fits=[{f['held_key']:f for f in m['folds']+[m['full']]} for m in (old,new)]
    records=[];summaries={};routed=0
    for r in ev['records']:
        if not r['reference_available'] or r['layer']=='clean':continue
        inp=r['input_region_metrics']['rgb8_mae_codes']
        pe=r['parent']['region_metrics']['rgb8_mae_codes'];ce=r['candidate']['region_metrics']['rgb8_mae_codes']
        if not (pe<inp and ce>=inp):continue
        cid=r['case_id'];p,q=[d[cid] for d in predictions]
        assert p['features']==q['features'] and p['features'] is not None
        key=p['subject_id'] if p['cohort']=='development' else 'full'
        a,b=[d[key] for d in fits];assert a['model']['actions']==b['model']['actions']
        li,steps,controls=route(b['model']['tree'],q['features'])
        _,parent_steps,pc=route(a['model']['tree'],p['features'])
        assert controls==q['parameters'] and pc==p['parameters'];routed+=2
        m=b['model'];t=next(t for t in m['trace'] if t['node']==li)
        ids=t['rows'];pa=m['actions'].index(pc);ca=m['actions'].index(controls)
        costs=np.asarray(m['costs']);clean=np.asarray(m['clean']);cleanids=[i for i in ids if clean[i]]
        feasible=[j for j in range(len(m['actions'])) if all(costs[i,j]==0 for i in cleanids)]
        totals=costs[ids].sum(axis=0)
        assert ca==min(feasible,key=lambda j:totals[j])
        blockers=[b['training_cases'][i] for i in cleanids if costs[i,pa]>0]
        category='identity_with_clean_blockers' if ca==0 and blockers else ('identity_without_parent_action_clean_blockers' if ca==0 else 'different_nonidentity_action')
        records.append(dict(case_id=cid,cohort=r['cohort'],layer=r['layer'],recipe=r['recipe'],category=category,
            input_error=inp,parent_error=pe,candidate_error=ce,lost_benefit=inp-pe,
            parent_action=pa,candidate_action=ca,parent_controls=pc,candidate_controls=controls,
            parent_route=parent_steps,candidate_route=steps,leaf=li,depth=t['depth'],leaf_rows=len(ids),
            leaf_old_rows=sum(i<b['parent_rows'] for i in ids),leaf_new_rows=sum(i>=b['parent_rows'] for i in ids),
            leaf_clean_rows=len(cleanids),parent_action_clean_blockers=blockers,
            feasible_actions=feasible,identity_total_cost=float(totals[0]),parent_action_total_cost=float(totals[pa]),
            selected_total_cost=float(totals[ca]),unconstrained_best_action=int(np.argmin(totals))))
    for cohort in ('development','later'):
        for layer in ('core','composite_stress_design'):
            rr=[r for r in ev['records'] if r['cohort']==cohort and r['layer']==layer and r['reference_available']]
            status=Counter()
            for r in rr:
                x=r['input_region_metrics']['rgb8_mae_codes'];p=r['parent']['region_metrics']['rgb8_mae_codes']<x;c=r['candidate']['region_metrics']['rgb8_mae_codes']<x
                status[('both_beneficial' if p and c else 'lost' if p else 'gained' if c else 'neither_beneficial')]+=1
            detail=[r for r in records if r['cohort']==cohort and r['layer']==layer]
            assert status['lost']==len(detail)
            summaries[cohort+'_'+layer]=dict(transitions=dict(status),categories=dict(Counter(r['category'] for r in detail)),
                identity_unconstrained_best=sum(r['unconstrained_best_action']==0 for r in detail),
                only_identity_feasible=sum(r['feasible_actions']==[0] for r in detail),
                maximum_depth=sum(r['depth']==3 for r in detail),
                lost_by_recipe=dict(Counter(r['recipe'] for r in detail)),leaves=dict(Counter(str(r['leaf']) for r in detail)))
    for p,h in bound.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    bound[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(summary=summaries,records=records,verified_routes=routed,input_sha256=bound,new_fits=0,new_inference=0,holdout_image_reads=0,
        limitation='Descriptive frozen routing and training-leaf constraints, not proof that a deeper tree or any changed feature would generalise safely.')
    OUT.mkdir();(OUT/'diagnosis_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(summary=summaries,records=len(records),verified_routes=routed),indent=2))

if __name__=='__main__':main()
