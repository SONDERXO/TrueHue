"""Independent fitting statistics, normalized-leaf arithmetic and raw-pixel replay."""
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
    out=ROOT/'outputs/table2_target_scaling_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'plan.json');data=read(out/'summary.json');rows={r['pair_id']:r for r in plan['rows']};names=plan['features']
    assert len(rows)==30 and len(plan['folds'])==15 and len(names)==5
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    assert len(plan['retained_holds'])==74 and not {p.split('__')[0] for p in rows}&{'51739','40048','42532','63870','713','12222','60381'}
    for fold in plan['folds']:
        fid=fold['fold_id'];folder=out/f'fold_{fid}';model=joblib.load(folder/'standardized_target_model.joblib');stats=read(folder/'target_statistics.json')
        training=[rows[p] for p in fold['train_pair_ids']];x=[[r[k] for k in names] for r in training];y=np.array([[r[k] for k in TARGETS] for r in training])
        mean=np.mean(y,axis=0);std=np.sqrt(np.mean((y-mean)**2,axis=0));scale=np.where(std==0,1.,std)
        np.testing.assert_allclose(stats['fitting_target_mean'],mean,rtol=0,atol=1e-12);np.testing.assert_allclose(stats['fitting_population_std'],std,rtol=0,atol=1e-12)
        np.testing.assert_allclose(stats['applied_scale'],scale,rtol=0,atol=1e-12)
        assert stats['fitting_rows']==28 and model.max_depth==3 and model.min_samples_leaf==1 and model.random_state==42
        raw=read(folder/'raw_units_tree.json');clean=read(folder/'clean_leaf_tree.json');leaves=model.apply(x)
        for i,(node,conservative) in enumerate(zip(raw['nodes'],clean['nodes'])):
            if node['kind']=='split':
                assert node==conservative and node['threshold']==float(model.tree_.threshold[i]) and node['feature']==int(model.tree_.feature[i]);continue
            selected=y[leaves==i];expected=selected.mean(axis=0)
            np.testing.assert_allclose(node['values'],expected,rtol=0,atol=1e-12)
            np.testing.assert_allclose(model.tree_.value[i].ravel(),((selected-mean)/scale).mean(axis=0),rtol=0,atol=1e-12)
            controls=[r for r,l in zip(training,leaves) if l==i and r['variant']=='identity']
            assert conservative['values']==([1.,1.,1.] if controls else node['values'])
        for record in [r for r in data['records'] if r['fold_id']==fid]:
            row=rows[record['pair_id']];assert row['pair_id'] in fold['inner_validation_pair_ids']
            assert all(r['source_image_id']!=row['source_image_id'] and r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path']);mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            for method,filename in [('scaled_targets','raw_units_tree.json'),('scaled_clean_leaf','clean_leaf_tree.json')]:
                prediction=record['methods'][method];tree=PortableTree(read(folder/filename));query=[row[k] for k in names]
                assert tree.predict_one(query)==prediction['parameters']
                if method=='scaled_targets':np.testing.assert_allclose(model.predict([query])[0]*scale+mean,prediction['parameters'],rtol=0,atol=1e-12)
                g,r,b=prediction['parameters'];transformed=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
                expected=image.copy();expected[mask]=transformed[mask];path=out/(row['pair_id']+'_'+method+'.png')
                assert digest(path)==prediction['output_sha256'];np.testing.assert_array_equal(rgb(path),expected)
                assert image_errors(reference,expected,score)==prediction['metrics']
    for method,aggregates in data['aggregate'].items():
        for scope,subset in [('all',data['records']),('identity',[r for r in data['records'] if r['variant']=='identity']),('distorted',[r for r in data['records'] if r['variant']!='identity'])]:
            a=aggregates[scope];assert a['corrected']==float(np.mean([r['methods'][method]['metrics']['ciede2000_source_mask'] for r in subset]))
            for i,k in enumerate(TARGETS):assert a['target_mae'][k]==float(np.mean([abs(r['methods'][method]['parameters'][i]-rows[r['pair_id']][k]) for r in subset]))
        harms=[r['pair_id'] for r in data['records'] if r['variant']=='identity' and r['methods'][method]['metrics']['ciede2000_source_mask']>0]
        gate=data['gates'][method];assert gate['harmed_identity_ids']==harms and gate['identity_pass']==(not harms)
        assert gate['overall_improves']==(aggregates['all']['corrected']<aggregates['all']['no_correction'])
        assert gate['passed']==(gate['overall_improves'] and gate['identity_pass'])
    target.write_text(json.dumps(dict(status='pass',verified_fitting_statistics=15,verified_normalized_models=15,verified_portable_exports=30,
        verified_new_predictions_and_pngs=60,independent_normalized_leaf_means_raw_targets_pixels_metrics=True,
        no_held_data_in_statistics=True,original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')),indent=2),encoding='utf-8')
    print('PASS:15fitting-only normalizations/models,30exports,60predictions/pixels,leaf means/metrics/gates')


if __name__=='__main__':main()
