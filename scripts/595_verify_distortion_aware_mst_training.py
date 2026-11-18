"""Check ridge normal equations, nested exclusions, frozen costs and tree behavior."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/distortion_aware_mst_action_models_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'models_PRIVATE.json');old=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    rows={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    assert d['calibration_cohort']==old['full']['training_cases'];cohort=d['calibration_cohort'];calibs=0;features=0;constraints=0;nodes=0;options=0
    for mapping in d['calibrations'].values():
        ids=[cid for cid in cohort if rows[cid]['subject_id'] not in mapping['excluded_keys']]
        assert ids==mapping['training_cases'] and all(rows[cid]['cohort']=='development' for cid in ids)
        m=mapping['model'];x=np.array([[rows[cid]['raw_features'][n] for n in m['features']] for cid in ids]);y=np.array([float(rows[cid]['source_mst_exact_decimal']) for cid in ids])
        keys=[rows[cid]['subject_id'] for cid in ids];w=np.array([1/keys.count(k) for k in keys]);mean=np.average(x,axis=0,weights=w);mean=np.where(np.ptp(x,axis=0)==0,x[0],mean)
        scale=np.sqrt(np.average((x-mean)**2,axis=0,weights=w));scale=np.where(scale==0,1.,scale)
        np.testing.assert_allclose(mean,m['mean'],atol=1e-12,rtol=0);np.testing.assert_allclose(scale,m['scale'],atol=1e-12,rtol=0)
        intercept=float(np.average(y,weights=w));assert intercept==m['intercept'];z=(x-mean)/scale
        residual=(z.T@(w[:,None]*z)+np.eye(4))@m['coefficient']-z.T@(w*(y-intercept));assert np.max(np.abs(residual))<1e-9;calibs+=1
    def mst(cid,excluded):
        m=d['calibrations']['|'.join(sorted(excluded))]['model'];x=np.array([rows[cid]['raw_features'][n] for n in m['features']]);raw=float(((x-m['mean'])/m['scale'])@m['coefficient']+m['intercept']);return raw,float(np.clip(raw,1,10))
    for fit,parent in zip(d['folds']+[d['full']],old['folds']+[old['full']],strict=True):
        assert fit['training_cases']==parent['training_cases'];m=fit['model'];pm=parent['model']
        assert m['actions']==pm['actions'] and m['costs']==pm['costs'] and m['clean']==pm['clean']
        for cid,x,px,t in zip(fit['training_cases'],fit['training_features'],parent['training_features'],fit['training_trace'],strict=True):
            excluded={rows[cid]['subject_id']} if fit['held_key']=='full' else {fit['held_key'],rows[cid]['subject_id']}
            assert t['excluded_keys']==sorted(excluded);raw,score=mst(cid,excluded);assert abs(raw-t['mst_prediction']['raw'])<1e-12 and abs(score-x[4])<1e-12
            assert x[:4]==px[:4] and x[5:]==px[5:];features+=1
        x=np.asarray(fit['training_features'],np.float32);cost=np.asarray(m['costs']);flags=np.asarray(m['clean']);tree=m['tree'];portable=PortableTree(tree)
        def best(ids):
            sums=cost[ids].sum(axis=0);sums[np.any((cost[ids]>0)&flags[ids,None],axis=0)]=np.inf;return int(np.argmin(sums)),float(np.min(sums))
        def walk(node,ids,depth):
            nonlocal nodes,options
            t=m['trace'][node];n=tree['nodes'][node];action,value=best(ids);assert set(t['rows'])==set(ids.tolist()) and t['action']==action and abs(t['cost']-value)<1e-8;nodes+=1
            minimum=value;chosen=None
            if depth<3:
                for f in range(x.shape[1]):
                    vals=np.unique(x[ids,f])
                    for lo,hi in zip(vals[:-1],vals[1:]):
                        threshold=(float(lo)+float(hi))/2.;left=ids[x[ids,f]<=threshold];right=ids[x[ids,f]>threshold];v=best(left)[1]+best(right)[1];minimum=min(minimum,v);options+=1
                        if n['kind']=='split' and n['feature']==f and n['threshold']==threshold:chosen=v
            tol=1e-12*max(1.,abs(value))
            if n['kind']=='leaf':assert n['values']==m['actions'][action] and minimum>=value-2*tol;return
            assert chosen is not None and chosen<value-tol and chosen<=minimum+2*tol
            f=n['feature'];walk(n['left'],ids[x[ids,f]<=n['threshold']],depth+1);walk(n['right'],ids[x[ids,f]>n['threshold']],depth+1)
        walk(0,np.arange(len(x)),0)
        for i in np.flatnonzero(flags):assert cost[i,m['trace'][portable.leaf_id(x[i])]['action']]==0;constraints+=1
        print('Verified',fit['held_key'],flush=True)
    bykey={f['held_key']:f for f in d['folds']}
    for p,q in zip(d['predictions'],old['predictions'],strict=True):
        assert p['excluded_keys']==q['excluded_keys']
        if p['features'] is None:assert q['features'] is None and p['parameters'] is None;continue
        raw,score=mst(p['case_id'],p['excluded_keys']);assert abs(score-p['features'][4])<1e-12
        assert p['features'][:4]==q['features'][:4] and p['features'][5:]==q['features'][5:]
        fit=bykey[p['subject_id']] if p['cohort']=='development' else d['full'];assert PortableTree(fit['model']['tree']).predict_one(p['features'])==p['parameters']
    result=dict(passed=True,calibration_equations=calibs,features=features,clean_constraints=constraints,nodes=nodes,split_options=options,predictions=756,new_fits=0,
        model_sha256=sha(OUT/'models_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(result)

if __name__=='__main__':main()
