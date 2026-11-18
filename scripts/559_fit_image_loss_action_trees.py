"""Eleven fixed image-loss trees; identity and correction learned jointly."""
from pathlib import Path
from collections import defaultdict
import json,hashlib,sys,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.image_loss_action_tree import action_costs,fit_action_tree
OUT=ROOT/'outputs/image_loss_action_tree_models_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    if OUT.exists():raise FileExistsError('Preserve existing fits; do not automatically refit: '+str(OUT))
    S=ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json'
    F=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json'
    T=ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json'
    C=ROOT/'outputs/gamma_scene_chroma_comparison_v3/results_PRIVATE.json'
    split=read(S);full=read(F);table={r['case_id']:r for r in read(T)}
    context={r['case_id']:r for r in read(C)['records'] if r['suite']=='fold_working256'}
    paths=[S,F,T,C,Path(__file__),ROOT/'src/model_training/image_loss_action_tree.py',ROOT/'src/model_training/portable_tree.py',ROOT/'docs/image-loss-action-tree-protocol-2026-11-07.md']
    bound={str(p):sha(p) for p in paths};pixels={}
    for cid in full['training_cases']:
        c=context[cid];assert c['mask_path']==c['reference_mask_path']
        for p in (c['image_path'],c['reference_path'],c['mask_path']):bound[p]=sha(p)
        mask=cv2.imread(c['mask_path'],0)>0
        pixels[cid]=(rgb(c['image_path'])[mask],rgb(c['reference_path'])[mask])
        if table[cid]['case']['id']=='clean':assert np.array_equal(*pixels[cid])
    OUT.mkdir();folds=[];count=0;start=time.monotonic()
    items=[(f['held_key'],f['training_cases'],f['training_features'],f['held_cases']) for f in split['folds']]+[('full',full['training_cases'],full['training_features'],[])]
    for key,cases,features,held in items:
        assert key=='full' or all(table[c]['subject_id']!=key for c in cases)
        grouped=defaultdict(list)
        for c in cases:
            recipe=table[c]['case']['id']
            if recipe!='clean':grouped[recipe].append(table[c]['target'])
        recipes=['identity']+sorted(grouped)
        actions=[[1.,1.,1.]]+[np.mean(grouped[r],axis=0).tolist() for r in recipes[1:]]
        costs=[action_costs(*pixels[c],actions) for c in cases]
        clean=[table[c]['case']['id']=='clean' for c in cases]
        model=fit_action_tree(features,costs,clean,actions,full['feature_names'],max_depth=3)
        model.update(costs=costs,clean=clean,action_recipes=recipes)
        record=dict(held_key=key,training_cases=cases,training_features=features,held_cases=held,model=model)
        (OUT/(key+'_PRIVATE.json')).write_text(json.dumps(record,indent=2,allow_nan=False),encoding='utf-8')
        if key!='full':folds.append(record)
        else:full_record=record
        count+=1;print('Saved action tree',count,'/11;',len(cases),'rows;',len(actions),'actions;',len(model['tree']['nodes']),'nodes;',round(time.monotonic()-start,1),'seconds',flush=True)
    result=dict(folds=folds,full_model=full_record['model'],full_training_cases=full['training_cases'],full_training_features=full['training_features'],
        input_sha256=bound,new_action_tree_fits=count,new_target_fits=0,other_research_fits=0,production_adopted=False,admissions=0)
    assert count==11
    (OUT/'models_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    print('Completed exactly11 joint action trees; previous models unchanged.',flush=True)

if __name__=='__main__':main()
