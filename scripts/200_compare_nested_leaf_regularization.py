"""Fixed nested1/2/4minimum-leaf selection using fitting-only quality gates."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.data_preparation.source_group_folds import source_group_folds
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.portable_tree import PortableTree,export_tree
from src.evaluation.correction_prototype import apply_correction,image_errors

OUT=ROOT/'outputs/table2_nested_leaf_regularization_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    parent=ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1';plan=read(parent/'fit_plan.json')
    assert digest(parent/'fit_plan.json')==read(parent/'verification.json')['fit_plan_sha256']
    rows={r['pair_id']:r for r in plan['rows']};names=plan['baseline_features'];sizes=[1,2,4]
    paths=[Path(__file__),ROOT/'docs/table2-nested-regularization-protocol.md',parent/'fit_plan.json',parent/'verification.json']
    for r in rows.values():paths.extend(ROOT/r[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    OUT.mkdir();write(OUT/'plan.json',dict(status='frozen_before_inner_fits',rows=plan['rows'],outer_folds=plan['folds'],features=names,
        min_leaf_sizes=sizes,max_depth=3,seed=42,selection='Inner strict improvement AND zero clean harm;lowest eligible error,tie larger leaf;else identity',
        excluded=plan['excluded'],retained_holds=plan['retained_holds'],input_sha256=hashes,planned_inner_fits=630))
    images={p:rgb(ROOT/r['input_path']) for p,r in rows.items()};refs={p:rgb(ROOT/r['reference_path']) for p,r in rows.items()}
    masks={p:cv2.imread(str(ROOT/r['input_mask_path']),0)>0 for p,r in rows.items()};scores={p:cv2.imread(str(ROOT/r['reference_mask_path']),0)>0 for p,r in rows.items()}
    metric_cache={}
    def error(pair,parameters):
        key=(pair,tuple(parameters))
        if key not in metric_cache:metric_cache[key]=image_errors(refs[pair],apply_correction(images[pair],masks[pair],parameters),scores[pair])['ciede2000_source_mask']
        return metric_cache[key]
    def fit(training,size,folder,provenance):
        model=DecisionTreeRegressor(max_depth=3,random_state=42,min_samples_leaf=size).fit([[r[k] for k in names] for r in training],[[r[k] for k in TARGETS] for r in training])
        raw=export_tree(model,names,TARGETS,provenance);modified=deepcopy(raw);tree=PortableTree(raw)
        for r in training:
            if r['variant']=='identity':modified['nodes'][tree.leaf_id([r[k] for k in names])]['values']=[1.,1.,1.]
        modified['provenance']['leaf_policy']='identity_if_any_fitting_control'
        folder.mkdir();write(folder/'raw_tree.json',raw);write(folder/'policy_tree.json',modified)
        return PortableTree(modified)
    inner_records=[];outer_records=[];decisions=[];inner_fits=0;outer_fits=0
    for outer in plan['folds']:
        fid=outer['fold_id'];folder=OUT/f'outer_{fid}';folder.mkdir();pool=[rows[p] for p in outer['train_pair_ids']]
        inner_folds=source_group_folds(pool);assert len(pool)==28 and len(inner_folds)==14
        write(folder/'inner_plan.json',inner_folds);candidate_scores=[]
        outer_groups={rows[p]['duplicate_group_id'] for p in outer['inner_validation_pair_ids']}
        for size in sizes:
            records=[]
            for inner in inner_folds:
                training=[rows[p] for p in inner['train_pair_ids']];validation=[rows[p] for p in inner['inner_validation_pair_ids']]
                assert len(training)==26
                assert not ({r['duplicate_group_id'] for r in training}|{r['duplicate_group_id'] for r in validation})&outer_groups
                tree=fit(training,size,folder/f"size_{size}_inner_{inner['fold_id']}",dict(outer_fold_id=fid,inner_fold_id=inner['fold_id'],min_samples_leaf=size))
                inner_fits+=1
                for row in validation:
                    parameters=tree.predict_one([row[k] for k in names]);record=dict(outer_fold_id=fid,inner_fold_id=inner['fold_id'],min_leaf=size,
                        pair_id=row['pair_id'],identity=row['variant']=='identity',parameters=parameters,error=error(row['pair_id'],parameters),no_correction=error(row['pair_id'],[1.,1.,1.]))
                    records.append(record);inner_records.append(record)
            harms=[r['pair_id'] for r in records if r['identity'] and r['error']>0];mean=float(np.mean([r['error'] for r in records]));base=float(np.mean([r['no_correction'] for r in records]))
            candidate_scores.append(dict(min_leaf=size,mean_error=mean,no_correction_mean=base,clean_harms=harms,eligible=not harms and mean<base))
        eligible=sorted([r for r in candidate_scores if r['eligible']],key=lambda r:(r['mean_error'],-r['min_leaf']))
        selected=eligible[0]['min_leaf'] if eligible else None
        decision=dict(outer_fold_id=fid,candidates=candidate_scores,selected_min_leaf=selected,selected='tree' if selected else 'identity')
        write(folder/'selection.json',decision);decisions.append(decision)
        tree=fit(pool,selected,folder/'selected_tree',dict(outer_fold_id=fid,min_samples_leaf=selected)) if selected else None
        outer_fits+=tree is not None
        for pair in outer['inner_validation_pair_ids']:
            row=rows[pair];parameters=tree.predict_one([row[k] for k in names]) if tree else [1.,1.,1.]
            corrected=apply_correction(images[pair],masks[pair],parameters);path=OUT/(pair+'_corrected.png');assert cv2.imwrite(str(path),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
            outer_records.append(dict(pair_id=pair,identity=row['variant']=='identity',outer_fold_id=fid,selected_min_leaf=selected,parameters=parameters,
                error=error(pair,parameters),no_correction=error(pair,[1.,1.,1.]),changed_pixels=int(np.any(corrected!=images[pair],axis=2).sum()),output_sha256=digest(path)))
        print('outer',fid,'selected',selected,'inner harm counts',[len(r['clean_harms']) for r in candidate_scores],flush=True)
    aggregate={scope:dict(pairs=len(subset),no_correction=float(np.mean([r['no_correction'] for r in subset])),corrected=float(np.mean([r['error'] for r in subset])),changed_inputs=sum(r['changed_pixels']>0 for r in subset))
        for scope,subset in [('all',outer_records),('identity',[r for r in outer_records if r['identity']]),('distorted',[r for r in outer_records if not r['identity']])]}
    harms=[r['pair_id'] for r in outer_records if r['identity'] and r['error']>0]
    gate=dict(overall_improves=aggregate['all']['corrected']<aggregate['all']['no_correction'],identity_pass=not harms,harmed_identity_ids=harms)
    gate['passed']=gate['overall_improves'] and gate['identity_pass']
    assert inner_fits==630 and len(inner_records)==1260 and len(outer_records)==30
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',dict(status='complete_exposed_nested_development',inner_records=inner_records,outer_records=outer_records,decisions=decisions,aggregate=aggregate,gate=gate,
        inner_fits=inner_fits,outer_refits=outer_fits,input_sha256=hashes,runtime_replaced=False,final_validated=False))
    print(json.dumps(dict(aggregate=aggregate,gate=gate,outer_refits=outer_fits),indent=2))


if __name__=='__main__':main()
