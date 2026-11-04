"""Independent saved inner-tree replay and training-only selection verification."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/table2_nested_safety_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'plan.json');data=read(out/'summary.json');rows={r['pair_id']:r for r in plan['rows']};columns=plan['features']
    assert len(data['inner_records'])==180 and len(data['outer_records'])==20
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    images={p:rgb(ROOT/r['input_path']) for p,r in rows.items()};refs={p:rgb(ROOT/r['reference_path']) for p,r in rows.items()}
    masks={p:cv2.imread(str(ROOT/r['input_mask_path']),0)>0 for p,r in rows.items()};scoring={p:cv2.imread(str(ROOT/r['reference_mask_path']),0)>0 for p,r in rows.items()}
    def independent(pair,parameters):
        g,r,b=parameters;image=images[pair];transformed=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
        result=image.copy();result[masks[pair]]=transformed[masks[pair]]
        return image_errors(refs[pair],result,scoring[pair]),result
    fits=0
    for outer in plan['outer_folds']:
        fid=outer['fold_id'];folder=out/f'outer_{fid}';inner_plan=read(folder/'inner_plan.json')
        outer_groups={rows[p]['duplicate_group_id'] for p in outer['inner_validation_pair_ids']}
        for inner in inner_plan['folds']:
            prefix=folder/f"inner_{inner['fold_id']}";model=joblib.load(prefix.with_suffix('.joblib'));payload=read(prefix.with_suffix('.json'));portable=PortableTree(payload)
            training=[rows[p] for p in inner['train_pair_ids']];validation=[rows[p] for p in inner['inner_validation_pair_ids']]
            assert len(training)==16 and len(validation)==2
            tg={r['duplicate_group_id'] for r in training};vg={r['duplicate_group_id'] for r in validation}
            assert not tg&vg and not (tg|vg)&outer_groups
            assert set(inner['train_pair_ids'])|set(inner['inner_validation_pair_ids'])==set(outer['train_pair_ids'])
            leaves=model.apply([[r[k] for k in columns] for r in training])
            for index,node in enumerate(payload['nodes']):
                if node['kind']=='split':
                    assert node['feature']==int(model.tree_.feature[index]) and node['threshold']==float(model.tree_.threshold[index])
                    assert node['left']==int(model.tree_.children_left[index]) and node['right']==int(model.tree_.children_right[index]);continue
                members=[r for r,l in zip(training,leaves) if l==index]
                controls=[r for r in members if r['variant']=='identity']
                expected=[1.,1.,1.] if controls else model.tree_.value[index].ravel().tolist()
                np.testing.assert_allclose(node['values'],expected,atol=1e-12,rtol=0)
            for row in validation:
                record=next(r for r in data['inner_records'] if r['outer_fold_id']==fid and r['inner_fold_id']==inner['fold_id'] and r['pair_id']==row['pair_id'])
                x=[row[k] for k in columns];leaf=int(model.apply([x])[0])
                controls=[r for r,l in zip(training,leaves) if l==leaf and r['variant']=='identity']
                expected=[1.,1.,1.] if controls else model.predict([x])[0].tolist()
                assert record['parameters']==expected==portable.predict_one(x)
                assert independent(row['pair_id'],expected)[0]==record['policy']
                assert independent(row['pair_id'],[1.,1.,1.])[0]==record['no_correction']
            fits+=1
        records=[r for r in data['inner_records'] if r['outer_fold_id']==fid]
        harms=[r['pair_id'] for r in records if r['variant']=='identity' and r['policy']['ciede2000_source_mask']>0]
        policy_mean=float(np.mean([r['policy']['ciede2000_source_mask'] for r in records]));base_mean=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in records]))
        selected='conservative_tree' if not harms and policy_mean<base_mean else 'identity'
        decision=read(folder/'selection.json')
        assert decision['selected']==selected and decision['inner_harmed_identity_ids']==harms
        assert decision['inner_policy_mean']==policy_mean and decision['inner_no_correction_mean']==base_mean
        outertree=PortableTree(read(ROOT/f'outputs/table2_clean_leaf_policy_v1/fold_{fid}/decision_tree.json'))
        for record in [r for r in data['outer_records'] if r['outer_fold_id']==fid]:
            row=rows[record['pair_id']];expected=outertree.predict_one([row[k] for k in columns]) if selected=='conservative_tree' else [1.,1.,1.]
            assert record['parameters']==expected and record['selected']==selected
            metrics,pixels=independent(row['pair_id'],expected);assert metrics==record['nested']
            path=out/(row['pair_id']+'_corrected.png');assert digest(path)==record['output_sha256'];np.testing.assert_array_equal(rgb(path),pixels)
    assert fits==90
    for group,subset in [('all',data['outer_records']),('identity',[r for r in data['outer_records'] if r['variant']=='identity']),('distorted',[r for r in data['outer_records'] if r['variant']!='identity'])]:
        for method,value in data['aggregate'][group].items():assert value==float(np.mean([r[method]['ciede2000_source_mask'] for r in subset]))
    harmed=[r['pair_id'] for r in data['outer_records'] if r['variant']=='identity' and r['nested']['ciede2000_source_mask']>0]
    assert harmed==data['gate']['harmed_identity_ids']
    assert data['gate']['identity_pass']==(not harmed)
    assert data['gate']['overall_improves']==(data['aggregate']['all']['nested']<data['aggregate']['all']['no_correction'])
    assert data['gate']['passed']==(data['gate']['identity_pass'] and data['gate']['overall_improves'])
    target.write_text(json.dumps(dict(status='pass',verified_inner_models=90,verified_inner_predictions=180,verified_outer_predictions=20,
        training_only_decisions=10,source_duplicate_separation=True,independent_pixels_metrics_policy_and_gates=True,
        original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')),indent=2),encoding='utf-8')
    print('PASS:90 inner models,180 inner predictions,10 training-only decisions,20 outer predictions')


if __name__=='__main__':main()
