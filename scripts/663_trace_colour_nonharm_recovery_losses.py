"""Exact six lost core benefits, old/new branch and constraint attribution; zero fits."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/colour_nonharm_loss_trace_v1'
def route(f,x,names):
    x=np.asarray(x,np.float32);tree=f['model']['tree'];node=0;steps=[]
    while tree['nodes'][node]['kind']=='split':
        n=tree['nodes'][node];left=bool(x[n['feature']]<=n['threshold']);t=f['pre_veto_model']['trace'][node]
        steps.append(dict(node=node,feature=names[n['feature']],threshold=n['threshold'],value=float(x[n['feature']]),left=left,training_rows=t['rows']))
        node=n['left'] if left else n['right']
    assert PortableTree(tree).leaf_id(x)==node
    return node,steps
def main():
    if OUT.exists():raise FileExistsError('Preserve trace')
    bound={}
    def read(name):
        p=ROOT/name;b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
    old=read('outputs/facial_veto_exception_models_v1/models_PRIVATE.json');new=read('outputs/colour_nonharm_models_v1/models_PRIVATE.json')
    assert read('outputs/colour_nonharm_models_v1/verification_PRIVATE.json')['passed']
    a={r['case_id']:r for r in read('outputs/facial_veto_exception_comparison_v1/results_PRIVATE.json')['records']}
    ev=read('outputs/colour_nonharm_comparison_v1/results_PRIVATE.json');assert read('outputs/colour_nonharm_comparison_v1/verification_PRIVATE.json')['passed']
    ff=[{f['held_key']:f for f in m['folds']+[m['full']]} for m in (old,new)];pp=[{p['case_id']:p for p in m['predictions']} for m in (old,new)]
    selected=[r for r in ev['records'] if r['layer']=='core' and r['reference_available'] and a[r['case_id']]['candidate']['region_metrics']['rgb8_mae_codes']<r['input_region_metrics']['rgb8_mae_codes'] and r['candidate']['region_metrics']['rgb8_mae_codes']>=r['input_region_metrics']['rgb8_mae_codes']]
    assert len(selected)==6;records=[]
    for r in selected:
        cid=r['case_id'];p,q=[d[cid] for d in pp];assert p['features']==q['features'];key=p['subject_id'] if p['cohort']=='development' else 'full';f,g=[d[key] for d in ff]
        for k in ('training_cases','training_features'):assert f[k]==g[k]
        li,steps=route(f,p['features'],new['feature_names']);lj,steps2=route(g,q['features'],new['feature_names'])
        divergence=next((i for i,(s,t) in enumerate(zip(steps,steps2)) if (s['feature'],s['threshold'],s['left'])!=(t['feature'],t['threshold'],t['left'])),None)
        model=g['pre_veto_model'];ids=model['trace'][lj]['rows'];cost=np.asarray(model['costs']);prior=model['actions'].index(p['parameters']);current=model['actions'].index(q['parameters'])
        clean=[g['training_cases'][i] for i in ids if model['clean'][i] and cost[i,prior]>0]
        colour=[g['training_cases'][i] for i in ids if model['nonharm'][i] and cost[i,prior]>cost[i,0]]
        oldids=f['pre_veto_model']['trace'][li]['rows'];oldcolour=[g['training_cases'][i] for i in oldids if model['nonharm'][i] and cost[i,prior]>cost[i,0]]
        records.append(dict(case_id=cid,fit_key=key,old_leaf=li,new_leaf=lj,old_route=steps,new_route=steps2,first_changed_split_depth=divergence,
            old_controls=p['parameters'],new_controls=q['parameters'],new_pre_veto_controls=model['tree']['nodes'][lj]['values'],new_leaf_vetoed=str(lj) in g['vetoed_leaves'],
            old_leaf_rows=len(oldids),new_leaf_rows=len(ids),new_leaf_clean_count=sum(model['clean'][i] for i in ids),new_leaf_colour_count=sum(model['nonharm'][i] for i in ids),
            prior_action_clean_blockers=clean,prior_action_colour_blockers=colour,prior_action_colour_blockers_in_old_leaf=oldcolour,
            new_leaf_recipes=dict(Counter(g['training_cases'][i].split('__',1)[1] for i in ids)),
            new_leaf_identity_cost=float(cost[ids,0].sum()),new_leaf_prior_action_cost=float(cost[ids,prior].sum()),
            old_error=a[cid]['candidate']['region_metrics']['rgb8_mae_codes'],new_error=r['candidate']['region_metrics']['rgb8_mae_codes']))
    for p,h in bound.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    bound[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    OUT.mkdir();(OUT/'trace_PRIVATE.json').write_text(json.dumps(dict(records=records,input_sha256=bound,new_fits=0,new_inference=0,new_predictions=0,holdout_image_reads=0),indent=2))
    print(json.dumps([{k:v for k,v in r.items() if k not in ('old_route','new_route','prior_action_clean_blockers','prior_action_colour_blockers','prior_action_colour_blockers_in_old_leaf')} for r in records],indent=2))
if __name__=='__main__':main()
