"""Verify reserved fitting exclusions, greedy fits and exact clean-only vetoes."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/reserved_clean_veto_models_v1'
def main():
    read=lambda p:json.loads(Path(p).read_text())
    d=read(OUT/'pre_veto_models_PRIVATE.json');final=read(OUT/'models_PRIVATE.json');old=read(ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json')
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    assert read(ROOT/'outputs/expanded_correction_models_v1/verification_PRIVATE.json')['passed']
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    for field in ('calibrations','new_fitting_cases','new_publisher_groups','feature_names','measurement_contract_sha256'):assert d[field]==old[field]
    import copy
    original=copy.deepcopy(old)
    reserved=set(d['reserved_all_conditions'])
    plan=read(ROOT/'outputs/reserved_clean_veto_plan_v1/plan_PRIVATE.json')
    assert reserved==set(plan['reserved_all_available_conditions']) and d['reserved_usable_clean']==plan['reserved_usable_clean']
    for f in old['folds']+[old['full']]:
        keep=[i for i,c in enumerate(f['training_cases']) if c not in reserved]
        for field in ('training_cases','training_features','training_trace'):f[field]=[f[field][i] for i in keep]
        for field in ('costs','clean'):f['model'][field]=[f['model'][field][i] for i in keep]
        f['new_rows']-=len(reserved)
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
    veto_count=0
    for f,pre,source in zip(final['folds']+[final['full']],d['folds']+[d['full']],original['folds']+[original['full']],strict=True):
        assert not set(f['training_cases'])&reserved
        assert f['pre_veto_model']==pre['model']
        expected=copy.deepcopy(pre['model']);portable=PortableTree(expected['tree']);hits={}
        assert [r['case_id'] for r in f['reserved_clean_vectors']]==plan['reserved_usable_clean']
        for r in f['reserved_clean_vectors']:
            j=source['training_cases'].index(r['case_id'])
            assert r['features']==source['training_features'][j] and source['model']['clean'][j]
            leaf=portable.leaf_id(r['features'])
            if portable.predict_one(r['features'])!=[1.,1.,1.]:hits.setdefault(str(leaf),[]).append(r['case_id'])
        assert hits==f['vetoed_leaves']
        for leaf in hits:expected['tree']['nodes'][int(leaf)]['values']=[1.,1.,1.]
        assert expected==f['model'];veto_count+=len(hits)
        for r in f['reserved_clean_vectors']:assert PortableTree(f['model']['tree']).predict_one(r['features'])==[1.,1.,1.]
    ff={f['held_key']:f for f in final['folds']}
    for q in final['predictions']:
        f=ff[q['subject_id']] if q['cohort']=='development' else final['full']
        assert q['parameters']==(PortableTree(f['model']['tree']).predict_one(q['features']) if q['features'] is not None else None)
    counts['vetoed_leaf_occurrences']=veto_count
    counts['reserved_clean_checks']=len(plan['reserved_usable_clean'])*11
    result=dict(passed=True,checks=counts,model_sha256=sha(OUT/'models_PRIVATE.json'),new_fits=0,holdout_image_reads=0,verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
