"""Verify cached fitting parity and independently enumerate greedy split costs."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/colour_nonharm_models_v1'
def main():
    read=lambda p:json.loads(Path(p).read_text())
    d=read(OUT/'models_PRIVATE.json');old=read(ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json')
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    assert read(ROOT/'outputs/facial_veto_exception_models_v1/verification_PRIVATE.json')['passed']
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    for field in ('calibrations','new_fitting_cases','new_publisher_groups','feature_names','measurement_contract_sha256'):assert d[field]==old[field]
    assert d['facial_exception_policy']==old['facial_exception_policy']
    def decide(f,x):
        t=PortableTree(f['model']['tree']);leaf=t.leaf_id(x);bounds=d['facial_exception_policy']['fits'][f['held_key']]['clean_bounds']
        from src.model_training.portable_tree import float32
        outside=any(float32(x[d['feature_names'].index(k)])<v[0] or float32(x[d['feature_names'].index(k)])>v[1] for k,v in bounds.items())
        return PortableTree(f['pre_veto_model']['tree']).predict_one(x) if str(leaf) in f['vetoed_leaves'] and outside else t.predict_one(x)
    counts=dict(fits=0,nodes=0,split_options=0,clean_constraints=0,predictions=0)
    for f,p in zip(d['folds']+[d['full']],old['folds']+[old['full']],strict=True):
        for field in ('held_key','training_cases','training_features','training_trace','parent_rows','new_rows'):assert f[field]==p[field]
        m=f['pre_veto_model'];pm=p['model']
        for field in ('costs','clean','actions'):assert m[field]==pm[field]
        x=np.asarray(f['training_features'],np.float32);loss=np.asarray(m['costs']);flags=np.asarray(m['clean']);tree=m['tree'];safe=np.asarray(m['nonharm']);assert safe.tolist()==[c.split('__',1)[1] in ('colour_cool','colour_warm','stress_color_none') for c in f['training_cases']]
        def best(ix):
            sums=loss[ix].sum(axis=0);sums[np.any(((loss[ix]>0)&flags[ix,None])|((loss[ix]>loss[ix,0,None])&safe[ix,None]),axis=0)]=np.inf
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
        import copy
        expected=copy.deepcopy(m);portable=PortableTree(m['tree']);hits={}
        for r in f['reserved_clean_vectors']:
            leaf=portable.leaf_id(r['features'])
            if portable.predict_one(r['features'])!=[1.,1.,1.]:hits.setdefault(str(leaf),[]).append(r['case_id'])
        assert hits==f['vetoed_leaves'] and f['reserved_clean_vectors']==p['reserved_clean_vectors']
        for leaf in hits:expected['tree']['nodes'][int(leaf)]['values']=[1.,1.,1.]
        assert expected==f['model']
        for j,row in enumerate(f['training_features']):
            a=m['actions'].index(decide(f,row));v=loss[j,a]
            if flags[j]:assert v==0
            if safe[j]:assert v<=loss[j,0]
        for r in f['reserved_clean_vectors']:assert decide(f,r['features'])==[1.,1.,1.]
        counts['fits']+=1;print('Verified',f['held_key'],flush=True)
    fits={f['held_key']:f for f in d['folds']}
    for q,p in zip(d['predictions'],old['predictions'],strict=True):
        for k in q:
            if k!='parameters':assert q[k]==p[k]
        f=fits[q['subject_id']] if q['cohort']=='development' else d['full']
        assert q['parameters']==(decide(f,q['features']) if q['features'] is not None else None)
        counts['predictions']+=1
    result=dict(passed=True,checks=counts,model_sha256=sha(OUT/'models_PRIVATE.json'),new_fits=0,holdout_image_reads=0,verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
