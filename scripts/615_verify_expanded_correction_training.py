"""Independent frozen-role/feature/cost/greedy-tree verification, without refitting."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/expanded_correction_models_v1';P=ROOT/'outputs/expanded_correction_inputs_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    d=read(OUT/'models_PRIVATE.json');old=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    rows={r['case_id']:r for r in read(P/'results_PRIVATE.json')['records']};ids=d['new_fitting_cases']
    plan=read(ROOT/'outputs/expanded_correction_training_plan_v1/plan_PRIVATE.json')
    assert d['calibrations']==old['calibrations'] and d['new_matching_MST_fits']==0 and len(ids)==890
    assert all(sha(p)==h for p,h in d['input_sha256'].items());cache={}
    for cid in ids:
        r=rows[cid];assert r['status']=='available' and r['subject_id'] not in plan['closed_holdout_keys']
        mask=cv2.imread(r['scoring_path'],0)>0
        cache[cid]=(rgb(r['scene_path'])[mask].astype(float)/255.,rgb(r['reference_path'])[mask].astype(float),np.load(r['alpha_path'],allow_pickle=False)[mask,None])
    counts=dict(fits=0,new_features=0,new_action_costs=0,clean_constraints=0,nodes=0,split_options=0,predictions=0)
    for fit,parent in zip(d['folds']+[d['full']],old['folds']+[old['full']],strict=True):
        offset=len(parent['training_cases']);assert fit['training_cases']==parent['training_cases']+ids
        assert fit['training_features'][:offset]==parent['training_features'] and fit['training_trace'][:offset]==parent['training_trace']
        m=fit['model'];pm=parent['model'];assert m['actions']==pm['actions'] and m['costs'][:offset]==pm['costs'] and m['clean'][:offset]==pm['clean']
        ex=[] if fit['held_key']=='full' else [fit['held_key']];mapping=d['calibrations']['|'.join(ex)];cal=mapping['model']
        assert not set(mapping['training_keys'])&set(d['new_publisher_groups'])
        actions=np.asarray(m['actions']);factors=np.column_stack([actions[:,1],np.ones(len(actions)),actions[:,2]])
        for j,cid in enumerate(ids,offset):
            r=rows[cid];t=fit['training_trace'][j];x=fit['training_features'][j]
            assert t['excluded_keys']==ex and r['subject_id'] not in mapping['training_keys'] and r['subject_id']!=fit['held_key']
            raw=float(((np.array([r['raw_features'][n] for n in cal['features']])-cal['mean'])/cal['scale'])@cal['coefficient']+cal['intercept'])
            score=float(np.clip(raw,1,10));values=dict(r['raw_features'],input_mst_score=score,**r['scene_features'])
            np.testing.assert_allclose(x,[values[n] for n in d['feature_names']],atol=1e-12,rtol=0);counts['new_features']+=1
            unit,ref,a=cache[cid]
            corrected=np.clip(unit[None]**actions[:,0,None,None]*factors[:,None,:],0,1)
            output=np.rint((unit[None]*(1-a)[None]+corrected*a[None])*255)
            expected=np.abs(output-ref[None]).mean(axis=(1,2))
            np.testing.assert_array_equal(expected,np.asarray(m['costs'][j]));counts['new_action_costs']+=len(actions)
            assert m['clean'][j]==(r['recipe']=='clean')
        x=np.asarray(fit['training_features'],np.float32);cost=np.asarray(m['costs']);flags=np.asarray(m['clean']);tree=m['tree'];portable=PortableTree(tree)
        def best(ix):
            sums=cost[ix].sum(axis=0);sums[np.any((cost[ix]>0)&flags[ix,None],axis=0)]=np.inf;return int(np.argmin(sums)),float(np.min(sums))
        def walk(node,ix,depth):
            t=m['trace'][node];n=tree['nodes'][node];action,value=best(ix);assert set(t['rows'])==set(ix.tolist()) and t['action']==action and abs(t['cost']-value)<1e-8;counts['nodes']+=1
            minimum=value;chosen=None
            if depth<3:
                for f in range(x.shape[1]):
                    vals=np.unique(x[ix,f])
                    for lo,hi in zip(vals[:-1],vals[1:]):
                        threshold=(float(lo)+float(hi))/2.;left=ix[x[ix,f]<=threshold];right=ix[x[ix,f]>threshold];v=best(left)[1]+best(right)[1];minimum=min(minimum,v);counts['split_options']+=1
                        if n['kind']=='split' and n['feature']==f and n['threshold']==threshold:chosen=v
            tol=1e-12*max(1.,abs(value))
            if n['kind']=='leaf':assert n['values']==m['actions'][action] and minimum>=value-2*tol;return
            assert chosen is not None and chosen<value-tol and chosen<=minimum+2*tol
            f=n['feature'];walk(n['left'],ix[x[ix,f]<=n['threshold']],depth+1);walk(n['right'],ix[x[ix,f]>n['threshold']],depth+1)
        walk(0,np.arange(len(x)),0)
        for j in np.flatnonzero(flags):assert cost[j,m['trace'][portable.leaf_id(x[j])]['action']]==0;counts['clean_constraints']+=1
        counts['fits']+=1;print('Verified expanded fit',fit['held_key'],flush=True)
    bykey={f['held_key']:f for f in d['folds']}
    for p,q in zip(d['predictions'],old['predictions'],strict=True):
        for field in ('case_id','features','mst_prediction','excluded_keys','status'):assert p[field]==q[field]
        fit=bykey[p['subject_id']] if p['cohort']=='development' else d['full']
        assert p['parameters']==(PortableTree(fit['model']['tree']).predict_one(p['features']) if p['features'] is not None else None);counts['predictions']+=1
    result=dict(passed=True,checks=counts,new_fits=0,model_sha256=sha(OUT/'models_PRIVATE.json'),verifier_sha256=sha(Path(__file__)),holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
