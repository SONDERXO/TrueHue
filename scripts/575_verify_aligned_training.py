"""Independent calibration equations, nested exclusions, costs and tree checks."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.portable_tree import PortableTree
P=ROOT/'outputs/aligned_correction_preparation_v1';OUT=ROOT/'outputs/aligned_action_tree_models_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    data=read(OUT/'models_PRIVATE.json');prepared=read(P/'results_PRIVATE.json');rows={r['case_id']:r for r in prepared['records']}
    clean={r['source_case']:r for r in rows.values() if r['cohort']=='development' and r['recipe']=='clean' and r['status']=='available'}
    assert all(sha(p)==h for p,h in data['input_sha256'].items());maps=data['calibrations'];mapping_checks=0
    for item in maps.values():
        expected=[r for r in clean.values() if r['subject_id'] not in item['excluded_keys']]
        assert [r['source_case'] for r in expected]==item['training_cases']
        assert not set(item['training_keys']) & set(item['excluded_keys']) and not item['calibration_admitted']
        model=item['model']
        if model is None:continue
        x=np.array([[r['raw_features'][n] for n in model['features']] for r in expected]);y=np.array([float(r['source_mst_exact_decimal']) for r in expected])
        groups=[r['subject_id'] for r in expected];w=np.array([1/groups.count(g) for g in groups])
        mean=np.average(x,axis=0,weights=w);mean=np.where(np.ptp(x,axis=0)==0,x[0],mean)
        scale=np.sqrt(np.average((x-mean)**2,axis=0,weights=w));scale=np.where(scale==0,1.,scale)
        np.testing.assert_allclose(mean,model['mean'],atol=1e-12,rtol=0);np.testing.assert_allclose(scale,model['scale'],atol=1e-12,rtol=0)
        z=(x-mean)/scale;intercept=float(np.average(y,weights=w));assert intercept==model['intercept'] and model['alpha']==1.
        residual=(z.T@(w[:,None]*z)+np.eye(x.shape[1]))@model['coefficient']-z.T@(w*(y-intercept))
        assert np.max(np.abs(residual))<1e-9;mapping_checks+=1
    def vector(r,excluded):
        item=maps['|'.join(sorted(excluded))];m=item['model']
        if r['status']!='available' or m is None:return None
        raw=float(np.dot((np.array([r['raw_features'][n] for n in m['features']])-m['mean'])/m['scale'],m['coefficient'])+m['intercept'])
        values=dict(r['raw_features'],input_mst_score=float(np.clip(raw,1,10)),**r['scene_features'])
        return [values[n] for n in data['feature_names']]
    parent=read(ROOT/'outputs/image_loss_action_tree_models_v1/models_PRIVATE.json');old={f['held_key']:f['model']['actions'] for f in parent['folds']};old['full']=parent['full_model']['actions']
    cost_checks=0;clean_checks=0;node_checks=0;options=0;training_features=0
    for fit in data['folds']+[data['full']]:
        model=fit['model'];key=fit['held_key']
        if model is None:continue
        assert model['actions']==old[key];cost=np.array(model['costs']);x=np.asarray(fit['training_features'],np.float32);flags=np.array(model['clean']);tree=model['tree'];portable=PortableTree(tree)
        for i,(cid,v,trace) in enumerate(zip(fit['training_cases'],fit['training_features'],fit['training_trace'])):
            r=rows[cid];excluded={r['subject_id']} if key=='full' else {key,r['subject_id']}
            assert r['cohort']=='development' and r['subject_id']!=key and r['reference_support_available'] and r['status']=='available'
            assert trace['excluded_keys']==sorted(excluded) and vector(r,excluded)==v;training_features+=1
            im=rgb(r['scene_path']);ref=rgb(r['reference_path']);scoring=cv2.imread(r['scoring_path'],0)>0;alpha=np.load(r['alpha_path'],allow_pickle=False)
            for a,params in enumerate(model['actions']):
                output=render_rgb8(im[scoring][:,None,:],alpha[scoring][:,None],params)
                expected=float(np.abs(output.astype(float)-ref[scoring][:,None,:].astype(float)).mean())
                assert expected==cost[i,a];cost_checks+=1
            if flags[i]:assert r['recipe']=='clean' and cost[i,model['trace'][portable.leaf_id(v)]['action']]==0;clean_checks+=1
        def best(ids):
            summed=cost[ids].sum(axis=0);summed[np.any((cost[ids]>0)&flags[ids,None],axis=0)]=np.inf
            return int(np.argmin(summed)),float(np.min(summed))
        def walk(node,ids,depth):
            nonlocal node_checks,options
            t=model['trace'][node];n=tree['nodes'][node];a,value=best(ids);assert set(t['rows'])==set(ids.tolist()) and t['action']==a and abs(t['cost']-value)<1e-8;node_checks+=1
            minimum=value;chosen=None
            if depth<3:
                for f in range(x.shape[1]):
                    vals=np.unique(x[ids,f])
                    for lo,hi in zip(vals[:-1],vals[1:]):
                        threshold=(float(lo)+float(hi))/2.;left=ids[x[ids,f]<=threshold];right=ids[x[ids,f]>threshold]
                        v=best(left)[1]+best(right)[1];minimum=min(minimum,v);options+=1
                        if n['kind']=='split' and n['feature']==f and n['threshold']==threshold:chosen=v
            tol=1e-12*max(1.,abs(value))
            if n['kind']=='leaf':assert n['values']==model['actions'][a] and minimum>=value-2*tol;return
            assert depth<3 and chosen is not None and chosen<value-tol and chosen<=minimum+2*tol
            f=n['feature'];walk(n['left'],ids[x[ids,f]<=n['threshold']],depth+1);walk(n['right'],ids[x[ids,f]>n['threshold']],depth+1)
        walk(0,np.arange(len(x)),0);print('Verified aligned fitting configuration:',key,flush=True)
    prediction_checks=0
    fits={f['held_key']:f for f in data['folds']}
    for q in data['predictions']:
        r=rows[q['case_id']];excluded={r['subject_id']} if r['cohort']=='development' else set();v=vector(r,excluded)
        assert q['features']==v and q['excluded_keys']==sorted(excluded)
        fit=fits[r['subject_id']] if r['cohort']=='development' else data['full']
        params=PortableTree(fit['model']['tree']).predict_one(v) if v is not None and fit['model'] is not None else None
        assert params==q['parameters'];prediction_checks+=1
    assert all(sha(p)==h for p,h in data['input_sha256'].items())
    result=dict(passed=True,matching_calibration_equations=mapping_checks,nested_training_features=training_features,action_cost_replays=cost_checks,clean_constraint_occurrences=clean_checks,nodes=node_checks,split_options=options,predictions=prediction_checks,source_hashes=len(data['input_sha256']),new_fits=0,verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
