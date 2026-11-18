"""Independent features, greedy split checks, constraints and unchanged-data parity."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.whole_scene_features import scene_features
OUT=ROOT/'outputs/face_local_action_models_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'models_PRIVATE.json');old=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    rows={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    assert d['calibrations']==old['calibrations'] and d['new_action_tree_fits']==11 and d['new_matching_MST_fits']==0
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    local={}
    for cid,r in rows.items():
        if r['status']!='available':continue
        image=cv2.cvtColor(cv2.imread(r['scene_path']),cv2.COLOR_BGR2RGB);x0,y0,x1,y1=r['input_bridge']['native_bounds']
        crop=image[y0:y1,x0:x1];local[cid]=list(scene_features(crop).values())
        for value in (32,128,224):
            changed=np.full_like(image,value);changed[y0:y1,x0:x1]=crop
            assert list(scene_features(changed[y0:y1,x0:x1]).values())==local[cid]
    counts=dict(fits=0,features=0,clean_constraints=0,nodes=0,split_options=0,predictions=0)
    for fit,parent in zip(d['folds']+[d['full']],old['folds']+[old['full']],strict=True):
        for field in ('held_key','training_cases','training_trace'):assert fit[field]==parent[field]
        m=fit['model'];pm=parent['model'];assert m['actions']==pm['actions'] and m['costs']==pm['costs'] and m['clean']==pm['clean']
        for cid,x,px in zip(fit['training_cases'],fit['training_features'],parent['training_features'],strict=True):
            assert x==px[:5]+local[cid];counts['features']+=1
        x=np.asarray(fit['training_features'],np.float32);cost=np.asarray(m['costs']);flags=np.asarray(m['clean']);tree=m['tree'];portable=PortableTree(tree)
        def best(ids):
            sums=cost[ids].sum(axis=0);sums[np.any((cost[ids]>0)&flags[ids,None],axis=0)]=np.inf
            return int(np.argmin(sums)),float(np.min(sums))
        def walk(node,ids,depth):
            t=m['trace'][node];n=tree['nodes'][node];a,value=best(ids)
            assert set(t['rows'])==set(ids.tolist()) and t['action']==a and abs(t['cost']-value)<1e-8
            counts['nodes']+=1;minimum=value;chosen=None
            if depth<3:
                for f in range(x.shape[1]):
                    vals=np.unique(x[ids,f])
                    for lo,hi in zip(vals[:-1],vals[1:]):
                        threshold=(float(lo)+float(hi))/2.;left=ids[x[ids,f]<=threshold];right=ids[x[ids,f]>threshold]
                        v=best(left)[1]+best(right)[1];minimum=min(minimum,v);counts['split_options']+=1
                        if n['kind']=='split' and n['feature']==f and n['threshold']==threshold:chosen=v
            tol=1e-12*max(1.,abs(value))
            if n['kind']=='leaf':assert n['values']==m['actions'][a] and minimum>=value-2*tol;return
            assert chosen is not None and chosen<value-tol and chosen<=minimum+2*tol
            f=n['feature'];walk(n['left'],ids[x[ids,f]<=n['threshold']],depth+1);walk(n['right'],ids[x[ids,f]>n['threshold']],depth+1)
        walk(0,np.arange(len(x)),0)
        for i in np.flatnonzero(flags):
            assert cost[i,m['trace'][portable.leaf_id(x[i])]['action']]==0;counts['clean_constraints']+=1
        counts['fits']+=1;print('Verified',fit['held_key'],flush=True)
    bykey={f['held_key']:f for f in d['folds']}
    for q,p in zip(d['predictions'],old['predictions'],strict=True):
        expected=p['features'][:5]+local[p['case_id']] if p['features'] is not None else None
        assert q['features']==expected and q['mst_prediction']==p['mst_prediction'] and q['excluded_keys']==p['excluded_keys']
        fit=bykey[q['subject_id']] if q['cohort']=='development' else d['full']
        assert q['parameters']==(PortableTree(fit['model']['tree']).predict_one(expected) if expected is not None else None)
        counts['predictions']+=1
    result=dict(passed=True,checks=counts,source_hashes=len(d['input_sha256']),new_fits=0,new_image_model_forwards=0,
        model_sha256=sha(OUT/'models_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
