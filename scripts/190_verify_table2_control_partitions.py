"""Independent classification-leaf membership, target arithmetic and RGB replay."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.data_preparation.controlled_training_table import TARGETS
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/table2_control_partition_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'plan.json');data=read(out/'summary.json');rows={r['pair_id']:r for r in plan['rows']};columns=plan['features']
    assert len(rows)==20 and len(plan['folds'])==10 and len(columns)==9
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    assert not {p.split('__')[0] for p in rows}&{'51739','40048','42532','63870','713'} and len(plan['retained_holds'])==21
    for fold in plan['folds']:
        folder=out/f"fold_{fold['fold_id']}";classifier=joblib.load(folder/'partition_classifier.joblib')
        payload=read(folder/'decision_tree.json');tree=PortableTree(payload)
        assert classifier.criterion=='gini' and classifier.max_depth==3 and classifier.random_state==42 and classifier.min_samples_leaf==1
        fitting=[rows[p] for p in fold['train_pair_ids']];assert len(fitting)==18
        leaves=classifier.apply([[r[k] for k in columns] for r in fitting])
        for index,node in enumerate(payload['nodes']):
            if node['kind']=='split':
                assert node['threshold']==float(classifier.tree_.threshold[index]) and node['feature']==int(classifier.tree_.feature[index])
                assert node['left']==int(classifier.tree_.children_left[index]) and node['right']==int(classifier.tree_.children_right[index]);continue
            members=[r for r,l in zip(fitting,leaves) if l==index];controls=[r for r in members if r['variant']=='identity']
            expected=[1.,1.,1.] if controls else [sum(r[k] for r in members)/len(members) for k in TARGETS]
            np.testing.assert_allclose(node['values'],expected,rtol=0,atol=1e-12)
        for record in [r for r in data['records'] if r['fold_id']==fold['fold_id']]:
            row=rows[record['pair_id']];assert row['pair_id'] in fold['inner_validation_pair_ids']
            assert all(r['source_image_id']!=row['source_image_id'] and r['duplicate_group_id']!=row['duplicate_group_id'] for r in fitting)
            x=[row[k] for k in columns];assert int(classifier.apply([x])[0])==record['leaf']==tree.leaf_id(x)
            assert tree.predict_one(x)==record['parameters']
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path'])
            mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            g,r,b=record['parameters'];raw=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
            expected=image.copy();expected[mask]=raw[mask]
            output=out/(row['pair_id']+'_corrected.png');assert digest(output)==record['output_sha256'];np.testing.assert_array_equal(rgb(output),expected)
            assert image_errors(reference,expected,scoring)==record['candidate']
    for scope,subset in [('all',data['records']),('identity',[r for r in data['records'] if r['variant']=='identity']),('distorted',[r for r in data['records'] if r['variant']!='identity'])]:
        for method,value in data['aggregate'][scope].items():assert value==float(np.mean([r[method]['ciede2000_source_mask'] for r in subset]))
    harms=[r['pair_id'] for r in data['records'] if r['variant']=='identity' and r['candidate']['ciede2000_source_mask']>0]
    assert harms==data['gate']['harmed_identity_ids']
    assert data['gate']['identity_pass']==(not harms)
    assert data['gate']['overall_improves']==(data['aggregate']['all']['candidate']<data['aggregate']['all']['no_correction'])
    assert data['gate']['passed']==(data['gate']['overall_improves'] and data['gate']['identity_pass'])
    sections=[]
    for name in sorted({p.split('__')[0] for p in rows}):
        strips=[]
        for row in sorted([r for r in rows.values() if r['pair_id'].startswith(name+'__')],key=lambda r:r['variant']):
            panels=[]
            for p,label in [(ROOT/row['reference_path'],'Reference'),(ROOT/row['input_path'],row['variant']),
                (ROOT/'outputs/table2_clean_leaf_policy_v1'/(row['pair_id']+'_corrected.png'),'Previous clean-leaf'),
                (out/(row['pair_id']+'_corrected.png'),'Control-aware partition')]:
                im=cv2.imread(str(p));im=cv2.copyMakeBorder(im,24,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(im,label,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.33,(255,255,255),1);panels.append(im)
            strips.append(np.hstack(panels))
        path=out/(name+'_comparison.png');assert cv2.imwrite(str(path),np.vstack(strips));sections.append(f'<h2>{name}</h2><img src="{path.name}">')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Control partition experiment</title><style>body{font:17px system-ui;margin:25px}img{max-width:100%}</style><h1>Fixed control-aware partition experiment</h1><p>Same held-source inputs and nine features; experimental split objective, not adopted. Both quality gates fail.</p>'+''.join(sections),encoding='utf-8')
    target.write_text(json.dumps(dict(status='pass',verified_models=10,verified_predictions=20,independent_leaf_targets_and_pixels=True,
        source_duplicate_separation=True,original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')),indent=2),encoding='utf-8')
    print('PASS:10models/20predictions,independent fitting-leaf targets,pixels,metrics,gates and hashes')


if __name__=='__main__':main()
