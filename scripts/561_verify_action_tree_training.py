"""Recompute supervision costs and enumerate split/leaf checks without fitting."""
from pathlib import Path
import hashlib,json,sys,math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/image_loss_action_tree_models_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    models=read(OUT/'models_PRIVATE.json');assert models['new_action_tree_fits']==11
    assert all(sha(p)==h for p,h in models['input_sha256'].items())
    table={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')}
    context={r['case_id']:r for r in read(ROOT/'outputs/gamma_scene_chroma_comparison_v3/results_PRIVATE.json')['records'] if r['suite']=='fold_working256'}
    baseline={f['held_key']:f for f in read(ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json')['folds']}
    full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json');pixels={}
    for cid in models['full_training_cases']:
        r=context[cid];mask=cv2.imread(r['mask_path'],0)>0
        assert r['mask_path']==r['reference_mask_path']
        pixels[cid]=(rgb(r['image_path'])[mask][:,None,:],rgb(r['reference_path'])[mask][:,None,:])
    counts=dict(cost_replays=0,nodes=0,split_options=0,clean_occurrences=0,training_routes=0)
    items=[(f['held_key'],f['model'],f['training_cases'],f['training_features']) for f in models['folds']]+[('full',models['full_model'],models['full_training_cases'],models['full_training_features'])]
    for key,model,cases,features in items:
        prior=full if key=='full' else baseline[key]
        assert cases==prior['training_cases'] and features==prior['training_features']
        if key!='full':assert all(table[c]['subject_id']!=key for c in cases)
        recipes=['identity']+sorted({table[c]['case']['id'] for c in cases if table[c]['case']['id']!='clean'})
        actions=[[1.,1.,1.]]+[np.mean([table[c]['target'] for c in cases if table[c]['case']['id']==r],axis=0).tolist() for r in recipes[1:]]
        assert actions==model['actions'] and recipes==model['action_recipes']
        clean=np.array([table[c]['case']['id']=='clean' for c in cases]);assert clean.tolist()==model['clean']
        costs=np.array(model['costs']);x=np.asarray(features,np.float32);tree=model['tree'];portable=PortableTree(tree)
        for i,cid in enumerate(cases):
            im,ref=pixels[cid];mask=np.ones(im.shape[:2],float)
            for j,a in enumerate(actions):
                output=render_rgb8(im,mask,a)
                cost=float(np.abs(output.astype(float)-ref.astype(float)).mean())
                assert cost==costs[i,j];counts['cost_replays']+=1
        def best(ids):
            summed=costs[ids].sum(axis=0)
            for a in range(len(actions)):
                if np.any(costs[ids[clean[ids]],a]>0):summed[a]=np.inf
            return int(np.argmin(summed)),float(np.min(summed))
        def walk(node,ids,depth):
            trace=model['trace'][node];n=tree['nodes'][node]
            assert trace['node']==node and trace['depth']==depth and set(trace['rows'])==set(ids.tolist())
            action,cost=best(ids)
            assert trace['action']==action and abs(cost-trace['cost'])<1e-9
            counts['nodes']+=1
            minimum=cost;chosen_cost=None
            if depth<3 and len(ids)>1:
                for f in range(x.shape[1]):
                    values=np.unique(x[ids,f])
                    for a,b in zip(values[:-1],values[1:]):
                        t=(float(a)+float(b))/2.;left=ids[x[ids,f]<=t];right=ids[x[ids,f]>t]
                        value=best(left)[1]+best(right)[1];minimum=min(minimum,value);counts['split_options']+=1
                        if n['kind']=='split' and n['feature']==f and n['threshold']==t:chosen_cost=value
            tolerance=1e-12*max(1.,abs(cost))
            if n['kind']=='leaf':
                assert n['values']==actions[action]
                assert minimum>=cost-2*tolerance or depth==3
                return
            assert depth<3 and chosen_cost is not None
            assert abs(chosen_cost-trace['immediate_child_cost'])<1e-8
            assert chosen_cost<cost-tolerance and chosen_cost<=minimum+2*tolerance
            f=n['feature'];left=ids[x[ids,f]<=n['threshold']];right=ids[x[ids,f]>n['threshold']]
            walk(n['left'],left,depth+1);walk(n['right'],right,depth+1)
        walk(0,np.arange(len(cases)),0)
        for i,row in enumerate(features):
            node=portable.leaf_id(row);action=model['trace'][node]['action']
            assert portable.predict_one(row)==actions[action];counts['training_routes']+=1
            if clean[i]:assert costs[i,action]==0;counts['clean_occurrences']+=1
        print('Verified fitting costs, clean feasibility and greedy split choices:',key,flush=True)
    assert counts['training_routes']==3570 and counts['clean_occurrences']==290
    assert all(sha(p)==h for p,h in models['input_sha256'].items())
    result=dict(passed=True,**counts,source_hashes=len(models['input_sha256']),verifier_sha256=sha(Path(__file__)),new_fits=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
