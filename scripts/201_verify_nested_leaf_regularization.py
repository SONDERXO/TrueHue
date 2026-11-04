"""Independent saved-tree leaf arithmetic, inner selection and pixel replay."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.data_preparation.controlled_training_table import TARGETS
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/table2_nested_leaf_regularization_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'plan.json');data=read(out/'summary.json');rows={r['pair_id']:r for r in plan['rows']};names=plan['features']
    assert len(data['inner_records'])==1260 and len(data['outer_records'])==30
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    images={p:rgb(ROOT/r['input_path']) for p,r in rows.items()};refs={p:rgb(ROOT/r['reference_path']) for p,r in rows.items()}
    masks={p:cv2.imread(str(ROOT/r['input_mask_path']),0)>0 for p,r in rows.items()};scores={p:cv2.imread(str(ROOT/r['reference_mask_path']),0)>0 for p,r in rows.items()}
    cache={}
    def evaluate(pair,parameters):
        key=(pair,tuple(parameters))
        if key not in cache:
            image=images[pair];g,r,b=parameters;raw=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
            pixels=image.copy();pixels[masks[pair]]=raw[masks[pair]]
            cache[key]=(image_errors(refs[pair],pixels,scores[pair])['ciede2000_source_mask'],pixels)
        return cache[key]
    def verify_tree(folder,training,size):
        raw=read(folder/'raw_tree.json');policy=read(folder/'policy_tree.json');tree=PortableTree(raw);candidate=PortableTree(policy)
        leaves={}
        for r in training:leaves.setdefault(tree.leaf_id([r[k] for k in names]),[]).append(r)
        for i,(before,after) in enumerate(zip(raw['nodes'],policy['nodes'])):
            if before['kind']=='split':assert before==after;continue
            members=leaves[i];assert len(members)>=size
            mean=[sum(r[k] for r in members)/len(members) for k in TARGETS]
            np.testing.assert_allclose(before['values'],mean,atol=1e-12,rtol=0)
            controls=[r for r in members if r['variant']=='identity']
            assert after['values']==([1.,1.,1.] if controls else before['values'])
        return candidate
    inner_count=0;refits=0
    for outer in plan['outer_folds']:
        fid=outer['fold_id'];folder=out/f'outer_{fid}';inner_folds=read(folder/'inner_plan.json');outer_groups={rows[p]['duplicate_group_id'] for p in outer['inner_validation_pair_ids']}
        all_candidate=[]
        for size in plan['min_leaf_sizes']:
            selected_records=[]
            for inner in inner_folds:
                fitting=[rows[p] for p in inner['train_pair_ids']];validation=[rows[p] for p in inner['inner_validation_pair_ids']]
                assert len(fitting)==26 and len(validation)==2
                tg={r['duplicate_group_id'] for r in fitting};vg={r['duplicate_group_id'] for r in validation}
                assert not tg&vg and not (tg|vg)&outer_groups
                assert set(inner['train_pair_ids'])|set(inner['inner_validation_pair_ids'])==set(outer['train_pair_ids'])
                tree=verify_tree(folder/f"size_{size}_inner_{inner['fold_id']}",fitting,size);inner_count+=1
                records=[r for r in data['inner_records'] if r['outer_fold_id']==fid and r['inner_fold_id']==inner['fold_id'] and r['min_leaf']==size]
                assert {r['pair_id'] for r in records}==set(inner['inner_validation_pair_ids'])
                for record in records:
                    row=rows[record['pair_id']];parameters=tree.predict_one([row[k] for k in names])
                    assert record['parameters']==parameters
                    assert evaluate(row['pair_id'],parameters)[0]==record['error']
                    assert evaluate(row['pair_id'],[1.,1.,1.])[0]==record['no_correction']
                selected_records+=records
            mean=float(np.mean([r['error'] for r in selected_records]));base=float(np.mean([r['no_correction'] for r in selected_records]))
            harms=[r['pair_id'] for r in selected_records if r['identity'] and r['error']>0]
            all_candidate.append(dict(min_leaf=size,mean_error=mean,no_correction_mean=base,clean_harms=harms,eligible=not harms and mean<base))
        decision=read(folder/'selection.json');assert decision['candidates']==all_candidate
        eligible=sorted([r for r in all_candidate if r['eligible']],key=lambda r:(r['mean_error'],-r['min_leaf']))
        selected=eligible[0]['min_leaf'] if eligible else None
        assert decision['selected_min_leaf']==selected
        tree=verify_tree(folder/'selected_tree',[rows[p] for p in outer['train_pair_ids']],selected) if selected else None
        refits+=tree is not None
        for record in [r for r in data['outer_records'] if r['outer_fold_id']==fid]:
            row=rows[record['pair_id']];assert row['pair_id'] in outer['inner_validation_pair_ids']
            parameters=tree.predict_one([row[k] for k in names]) if tree else [1.,1.,1.]
            assert parameters==record['parameters'] and record['selected_min_leaf']==selected
            error,pixels=evaluate(row['pair_id'],parameters);assert record['error']==error
            path=out/(row['pair_id']+'_corrected.png');assert digest(path)==record['output_sha256'];np.testing.assert_array_equal(rgb(path),pixels)
            assert record['changed_pixels']==int(np.any(pixels!=images[row['pair_id']],axis=2).sum())
    assert inner_count==630 and refits==data['outer_refits']
    for scope,subset in [('all',data['outer_records']),('identity',[r for r in data['outer_records'] if r['identity']]),('distorted',[r for r in data['outer_records'] if not r['identity']])]:
        expected=dict(pairs=len(subset),no_correction=float(np.mean([r['no_correction'] for r in subset])),corrected=float(np.mean([r['error'] for r in subset])),changed_inputs=sum(r['changed_pixels']>0 for r in subset))
        assert data['aggregate'][scope]==expected
    harms=[r['pair_id'] for r in data['outer_records'] if r['identity'] and r['error']>0]
    assert data['gate']['harmed_identity_ids']==harms and data['gate']['identity_pass']==(not harms)
    assert data['gate']['overall_improves']==(data['aggregate']['all']['corrected']<data['aggregate']['all']['no_correction'])
    assert data['gate']['passed']==(data['gate']['overall_improves'] and data['gate']['identity_pass'])
    target.write_text(json.dumps(dict(status='pass',verified_inner_models=630,verified_inner_predictions=1260,verified_outer_predictions=30,
        verified_training_only_selections=15,verified_outer_refits=refits,independent_leaf_arithmetic_and_rgb_metrics=True,
        source_duplicate_separation=True,original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')),indent=2),encoding='utf-8')
    print('PASS:630inner trees,1260inner predictions,15training-only selections,30outer outputs')


if __name__=='__main__':main()
