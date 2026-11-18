"""Trace four saved clean errors and outcome-selected successful comparators."""
from pathlib import Path
from collections import Counter
import hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/aligned_clean_error_trace_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def route(tree,features):
    x=np.asarray(features,dtype=np.float32);index=tree['root'];steps=[]
    while tree['nodes'][index]['kind']=='split':
        n=tree['nodes'][index];v=float(x[n['feature']]);left=v<=n['threshold']
        steps.append(dict(node=index,feature=tree['feature_names'][n['feature']],value=v,threshold=n['threshold'],branch='left' if left else 'right'))
        index=n['left'] if left else n['right']
    return index,steps,tree['nodes'][index]['values']

def main():
    if OUT.exists():raise FileExistsError('Preserve completed trace')
    bound={}
    def read(p):
        p=Path(p);bound[str(p)]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    models=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    evaluation=read(ROOT/'outputs/aligned_action_tree_comparison_v1/results_PRIVATE.json')['records']
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    preds={r['case_id']:r for r in models['predictions']};evals={r['case_id']:r for r in evaluation}
    fits={f['held_key']:f for f in models['folds']}
    def fitfor(r):return fits[r['subject_id']] if r['cohort']=='development' else models['full']
    focal=[r for r in evaluation if r['recipe']=='clean' and r['paths']['aligned_tree']['changed_channels']>0]
    assert len(focal)==4
    records=[]
    for r in focal:
        cid=r['case_id'];p=preds[cid];fit=fitfor(p);model=fit['model'];tree=model['tree']
        leaf,steps,controls=route(tree,p['features']);assert controls==p['parameters']
        trace=next(t for t in model['trace'] if t['node']==leaf);ids=trace['rows'];action=trace['action']
        members=[fit['training_cases'][i] for i in ids]
        clean=[c for c in members if prep[c]['recipe']=='clean']
        matrix=np.asarray(fit['training_features'],np.float32)[ids]
        bounds=[name for i,name in enumerate(models['feature_names']) if p['features'][i]<float(matrix[:,i].min()) or p['features'][i]>float(matrix[:,i].max())]
        candidates=[];cleans=[]
        for q in models['predictions']:
            if q['features'] is None or fitfor(q)['held_key']!=fit['held_key']:continue
            qleaf,_,qcontrols=route(tree,q['features']);assert qcontrols==q['parameters']
            e=evals[q['case_id']]
            if qleaf!=leaf:continue
            if e['recipe']=='clean':cleans.append(q['case_id'])
            if not e['reference_available']:continue
            benefit=e['input_region_metrics']['rgb8_mae_codes']-e['paths']['aligned_tree']['region_metrics']['rgb8_mae_codes']
            if benefit>0:candidates.append(dict(case_id=q['case_id'],benefit_rgb_mae=benefit,recipe=e['recipe'],features=dict(zip(models['feature_names'],q['features']))))
        candidates=sorted(candidates,key=lambda q:(-q['benefit_rgb_mae'],q['case_id']))[:2]
        source=prep[cid]['source_case'];siblings=[]
        for q in models['predictions']:
            if prep[q['case_id']]['source_case']!=source:continue
            e=evals[q['case_id']];siblings.append(dict(case_id=q['case_id'],parameters=q['parameters'],status=q['status'],
                region_error=e['paths']['aligned_tree']['region_metrics']['rgb8_mae_codes'] if e['reference_available'] else None,
                input_error=e['input_region_metrics']['rgb8_mae_codes'] if e['reference_available'] else None))
        records.append(dict(case_id=cid,cohort=r['cohort'],fit_key=fit['held_key'],leaf=leaf,action_index=action,parameters=controls,
            query_features=dict(zip(models['feature_names'],p['features'])),route=steps,
            clean_rgb_mae=r['paths']['aligned_tree']['region_metrics']['rgb8_mae_codes'],
            leaf_training_rows=len(ids),leaf_training_clean_cases=clean,
            training_recipes=dict(Counter(prep[c]['recipe'] for c in members)),
            training_leaf_action_cost=float(sum(model['costs'][i][action] for i in ids)),
            training_leaf_identity_cost=float(sum(model['costs'][i][0] for i in ids)),
            outside_training_leaf_axes=bounds,same_leaf_evaluation_clean=cleans,
            selected_successful_same_leaf=candidates,same_source_conditions=siblings))
    bound[str(Path(__file__))]=sha(Path(__file__))
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();result=dict(records=records,new_fits=0,new_inference=0,
        comparator_selection='Outcome-selected top two positive regional MAE benefits in same evaluation model/leaf, not independent evidence.',
        limitation='Tree routing is descriptive; no controlled background or mask causality established.')
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k not in ('same_source_conditions','query_features','selected_successful_same_leaf')} for r in records],indent=2))
    for r in records:print(r['case_id'],'successful comparators',[(q['case_id'],round(q['benefit_rgb_mae'],2)) for q in r['selected_successful_same_leaf']])

if __name__=='__main__':main()
