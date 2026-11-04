"""Independent fitting-class weights, weighted target means and pixel replay."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.portable_tree import PortableTree
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/table2_severity_weighting_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'plan.json');data=read(out/'summary.json');rows={r['pair_id']:r for r in plan['rows']};names=plan['features']
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    assert len(rows)==30 and len(plan['folds'])==15
    for fold in plan['folds']:
        fid=fold['fold_id'];folder=out/f'fold_{fid}';training=[rows[p] for p in fold['train_pair_ids']]
        groups={r['variant'] for r in training if r['variant']!='identity'};n_identity=sum(r['variant']=='identity' for r in training)
        w=np.array([.5/n_identity if r['variant']=='identity' else .5/len(groups)/sum(s['variant']==r['variant'] for s in training) for r in training])
        metadata=read(folder/'weight_statistics.json');assert metadata['fitting_pair_ids']==[r['pair_id'] for r in training]
        np.testing.assert_allclose(w,metadata['weights'],rtol=0,atol=1e-15)
        assert abs(w.sum()-1)<1e-12 and abs(sum(v for r,v in zip(training,w) if r['variant']=='identity')-.5)<1e-12
        model=joblib.load(folder/'weighted_model.joblib');raw=read(folder/'raw_units_tree.json');clean=read(folder/'clean_leaf_tree.json')
        assert model.max_depth==3 and model.random_state==42 and model.min_samples_leaf==1
        leaves=model.apply([[r[k] for k in names] for r in training]);y=np.array([[r[k] for k in TARGETS] for r in training])
        for i,(before,after) in enumerate(zip(raw['nodes'],clean['nodes'])):
            if before['kind']=='split':
                assert before==after and before['threshold']==float(model.tree_.threshold[i]) and before['feature']==int(model.tree_.feature[i]);continue
            subset=leaves==i;expected=(y[subset]*w[subset,None]).sum(axis=0)/w[subset].sum()
            np.testing.assert_allclose(before['values'],expected,rtol=0,atol=1e-12)
            controls=[r for r,l in zip(training,leaves) if l==i and r['variant']=='identity']
            assert after['values']==([1.,1.,1.] if controls else before['values'])
        for record in [r for r in data['records'] if r['fold_id']==fid]:
            row=rows[record['pair_id']];assert row['pair_id'] in fold['inner_validation_pair_ids']
            assert all(r['source_image_id']!=row['source_image_id'] and r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path']);mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            for method,filename in [('severity_weighted','raw_units_tree.json'),('weighted_clean_leaf','clean_leaf_tree.json')]:
                prediction=record['methods'][method];tree=PortableTree(read(folder/filename));query=[row[k] for k in names]
                assert tree.predict_one(query)==prediction['parameters']
                if method=='severity_weighted':np.testing.assert_allclose(model.predict([query])[0],prediction['parameters'],rtol=0,atol=1e-12)
                g,r,b=prediction['parameters'];rawpixels=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
                expected=image.copy();expected[mask]=rawpixels[mask];path=out/(row['pair_id']+'_'+method+'.png')
                assert digest(path)==prediction['output_sha256'];np.testing.assert_array_equal(rgb(path),expected)
                assert image_errors(reference,expected,score)==prediction['metrics']
    for method,aggregates in data['aggregate'].items():
        for scope,subset in [('all',data['records']),('identity',[r for r in data['records'] if r['variant']=='identity']),('distorted',[r for r in data['records'] if r['variant']!='identity'])]:
            assert aggregates[scope]['corrected']==float(np.mean([r['methods'][method]['metrics']['ciede2000_source_mask'] for r in subset]))
        harms=[r['pair_id'] for r in data['records'] if r['variant']=='identity' and r['methods'][method]['metrics']['ciede2000_source_mask']>0]
        gate=data['gates'][method];assert gate['harmed_identity_ids']==harms and gate['identity_pass']==(not harms)
        assert gate['overall_improves']==(aggregates['all']['corrected']<aggregates['all']['no_correction'])
        assert gate['passed']==(gate['overall_improves'] and gate['identity_pass'])
    target.write_text(json.dumps(dict(status='pass',verified_weight_sets=15,verified_weighted_models=15,verified_policy_exports=30,verified_outputs=60,
        independent_weighted_leaf_arithmetic_and_rgb_pixels=True,no_outer_data_in_weights=True,original_hashes_unchanged=True,
        summary_sha256=digest(out/'summary.json')),indent=2),encoding='utf-8')
    print('PASS:15fitting-only weight sets/models,30exports,60predictions,weighted leaf means/pixels/gates')


if __name__=='__main__':main()
