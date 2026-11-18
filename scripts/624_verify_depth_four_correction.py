"""Verify cached fitting parity and independently enumerate greedy split costs."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/depth_four_correction_models_v1'
def main():
    read=lambda p:json.loads(Path(p).read_text())
    d=read(OUT/'models_PRIVATE.json');old=read(ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json')
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    assert read(ROOT/'outputs/expanded_correction_models_v1/verification_PRIVATE.json')['passed']
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    for field in ('calibrations','new_fitting_cases','new_publisher_groups','feature_names','measurement_contract_sha256'):assert d[field]==old[field]
    counts=dict(fits=0,nodes=0,split_options=0,clean_constraints=0,predictions=0)
    for f,p in zip(d['folds']+[d['full']],old['folds']+[old['full']],strict=True):
        for field in ('held_key','training_cases','training_features','training_trace','parent_rows','new_rows'):assert f[field]==p[field]
        m=f['model'];pm=p['model']
        for field in ('costs','clean','actions'):assert m[field]==pm[field]
        x=np.asarray(f['training_features'],np.float32);loss=np.asarray(m['costs']);flags=np.asarray(m['clean']);tree=m['tree']
        def best(ix):
            sums=loss[ix].sum(axis=0);sums[np.any((loss[ix]>0)&flags[ix,None],axis=0)]=np.inf
            return int(np.argmin(sums)),float(np.min(sums))
        def walk(i,ix,depth):
            n=tree['nodes'][i];t=m['trace'][i];a,cost=best(ix)
            assert set(t['rows'])==set(ix.tolist()) and t['depth']==depth and t['action']==a and abs(t['cost']-cost)<1e-8
            counts['nodes']+=1;minimum=cost;chosen=None
            if depth<4:
                for j in range(x.shape[1]):
                    vals=np.unique(x[ix,j])
                    for lo,hi in zip(vals[:-1],vals[1:]):
                        threshold=(float(lo)+float(hi))/2
                        l=ix[x[ix,j]<=threshold];r=ix[x[ix,j]>threshold]
                        total=best(l)[1]+best(r)[1];minimum=min(minimum,total);counts['split_options']+=1
                        if n['kind']=='split' and n['feature']==j and n['threshold']==threshold:chosen=total
            tol=1e-12*max(1.,abs(cost))
            if n['kind']=='leaf':assert n['values']==m['actions'][a] and minimum>=cost-2*tol;return
            assert depth<4 and chosen is not None and chosen<cost-tol and chosen<=minimum+2*tol
            j=n['feature'];walk(n['left'],ix[x[ix,j]<=n['threshold']],depth+1);walk(n['right'],ix[x[ix,j]>n['threshold']],depth+1)
        walk(tree['root'],np.arange(len(x)),0);portable=PortableTree(tree)
        for i in np.flatnonzero(flags):assert loss[i,m['trace'][portable.leaf_id(x[i])]['action']]==0;counts['clean_constraints']+=1
        counts['fits']+=1;print('Verified',f['held_key'],flush=True)
    fits={f['held_key']:f for f in d['folds']}
    for q,p in zip(d['predictions'],old['predictions'],strict=True):
        for k in q:
            if k!='parameters':assert q[k]==p[k]
        f=fits[q['subject_id']] if q['cohort']=='development' else d['full']
        assert q['parameters']==(PortableTree(f['model']['tree']).predict_one(q['features']) if q['features'] is not None else None)
        counts['predictions']+=1
    result=dict(passed=True,checks=counts,model_sha256=sha(OUT/'models_PRIVATE.json'),new_fits=0,holdout_image_reads=0,verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
