"""Independent feature/model/pixel replay, retained reviews and matched-old-cohort scores."""
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
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'fit_plan.json');data=read(out/'summary.json');review=read(out/'user_review.json')
    rows={r['pair_id']:dict(r) for r in plan['rows']};columns=plan['features']
    assert len(rows)==30 and len(plan['folds'])==15 and len(plan['retained_holds'])==74
    rejected={'51739','40048','42532','63870','713','12222','60381'}
    assert not {p.split('__')[0] for p in rows}&rejected
    assert {r['pair_id'].split('__')[0] for r in plan['excluded']}==rejected
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    for r in rows.values():
        name=r['pair_id'].split('__')[0]
        if name in review['decisions']:
            assert review['decisions'][name]['decision']=='accept'
            assert r['review_concern']==review['decisions'][name]['concern']
            assert r['mask_review_report_sha256']==digest(out/'user_review.json')
        for path,key in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256'),('reference_mask_path','reference_mask_sha256')]:assert digest(ROOT/r[path])==r[key]
    assert all(r['review_concern']=='some hair is captured in face mask' for p,r in rows.items() if p.startswith('59944__'))
    features=read(out/'features.json')
    for f in features:
        row=rows[f['pair_id']];image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        stats=compute_masked_lab_statistics(image,mask.astype(np.uint8)*255,1000)
        for key,feature in [('mean_l_star','input_mean_l_star'),('mean_a_star','input_mean_a_star'),('mean_b_star','input_mean_b_star'),('ita_degrees','input_ita_degrees')]:assert stats[key]==row[feature]
        encoded=cv2.cvtColor(image,cv2.COLOR_BGR2LAB)[mask]
        L=(encoded[:,0].astype(np.float32)*np.float32(100/255)).astype(float);a=encoded[:,1].astype(float)-128;b=encoded[:,2].astype(float)-128
        values=[float(np.quantile(a,.75)-np.quantile(a,.25)),float(np.quantile(b,.75)-np.quantile(b,.25)),
            float(np.dot(L-L.mean(),a-a.mean())/len(L)),float(np.dot(L-L.mean(),b-b.mean())/len(L))]
        np.testing.assert_allclose(values,list(f['features'].values()),rtol=0,atol=1e-9);row.update(f['features'])
    for fold in plan['folds']:
        folder=out/f"fold_{fold['fold_id']}";training=[rows[p] for p in fold['train_pair_ids']]
        assert len(training)==28
        for method in ['baseline5','chroma9']:
            model=joblib.load(folder/(method+'.joblib'));payload=read(folder/(method+'.json'));tree=PortableTree(payload);names=tree.feature_names
            assert model.max_depth==3 and model.random_state==42 and model.min_samples_leaf==1
            leaves=model.apply([[r[k] for k in names] for r in training])
            for leaf in set(leaves):
                expected=np.mean([[r[k] for k in TARGETS] for r,l in zip(training,leaves) if l==leaf],axis=0)
                np.testing.assert_allclose(expected,model.tree_.value[leaf].ravel(),rtol=0,atol=1e-12)
                np.testing.assert_allclose(expected,payload['nodes'][int(leaf)]['values'],rtol=0,atol=1e-12)
            if method=='chroma9':
                clean=read(folder/'clean_leaf.json')
                for i,(original,changed) in enumerate(zip(payload['nodes'],clean['nodes'])):
                    if original['kind']=='split':assert original==changed;continue
                    controls=[r for r,l in zip(training,leaves) if l==i and r['variant']=='identity']
                    assert changed['values']==([1.,1.,1.] if controls else original['values'])
        for record in [r for r in data['records'] if r['fold_id']==fold['fold_id']]:
            row=rows[record['pair_id']];assert row['pair_id'] in fold['inner_validation_pair_ids']
            assert all(r['source_image_id']!=row['source_image_id'] and r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path']);mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            assert image_errors(reference,image,scoring)==record['no_correction']
            for method,prediction in record['methods'].items():
                tree=PortableTree(read(folder/(method+'.json')));x=[row[k] for k in tree.feature_names]
                assert tree.predict_one(x)==prediction['parameters']
                if method!='clean_leaf':np.testing.assert_allclose(joblib.load(folder/(method+'.joblib')).predict([x])[0],prediction['parameters'],rtol=0,atol=1e-12)
                g,r,b=prediction['parameters'];transformed=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
                expected=image.copy();expected[mask]=transformed[mask]
                path=out/(row['pair_id']+'_'+method+'.png');assert digest(path)==prediction['output_sha256'];np.testing.assert_array_equal(rgb(path),expected)
                assert image_errors(reference,expected,scoring)==prediction['metrics']
    for method,groups in data['aggregate'].items():
        for scope,subset in [('all',data['records']),('identity',[r for r in data['records'] if r['variant']=='identity']),('distorted',[r for r in data['records'] if r['variant']!='identity'])]:
            assert groups[scope]['corrected']==float(np.mean([r['methods'][method]['metrics']['ciede2000_source_mask'] for r in subset]))
            assert groups[scope]['no_correction']==float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in subset]))
        harms=[r['pair_id'] for r in data['records'] if r['variant']=='identity' and r['methods'][method]['metrics']['ciede2000_source_mask']>0]
        gate=data['gates'][method];assert gate['harmed_identity_ids']==harms
        assert gate['identity_pass']==(not harms) and gate['overall_improves']==(groups['all']['corrected']<groups['all']['no_correction'])
        assert gate['passed']==(gate['identity_pass'] and gate['overall_improves'])
    # Avoid claiming model improvement solely from a different cohort average.
    oldfolder=ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1';oldplan=read(oldfolder/'fit_plan.json')
    oldrows={r['pair_id']:r for r in oldplan['rows']};old5={r['pair_id']:r['learned']['ciede2000_source_mask'] for r in read(oldfolder/'summary.json')['records']}
    oldpolicy=read(ROOT/'outputs/table2_clean_leaf_policy_v1/summary.json')
    previous={'baseline5':old5,'chroma9':{r['pair_id']:r['original']['ciede2000_source_mask'] for r in oldpolicy['records']},
        'clean_leaf':{r['pair_id']:r['policy']['ciede2000_source_mask'] for r in oldpolicy['records']}}
    matched={}
    for method in previous:
        selected=[r for r in data['records'] if r['pair_id'] in oldrows]
        for r in selected:
            for k in ['input_sha256','input_mask_sha256','reference_mask_sha256',*plan['baseline_features'],*TARGETS]:assert rows[r['pair_id']][k]==oldrows[r['pair_id']][k]
        matched[method]={scope:dict(pairs=len(subset),old=float(np.mean([previous[method][r['pair_id']] for r in subset])),
            expanded=float(np.mean([r['methods'][method]['metrics']['ciede2000_source_mask'] for r in subset])))
            for scope,subset in [('all',selected),('identity',[r for r in selected if r['variant']=='identity']),('distorted',[r for r in selected if r['variant']!='identity'])]}
    (out/'matched_old_cohort.json').write_text(json.dumps(matched,indent=2),encoding='utf-8')
    sections=[]
    for name in sorted({p.split('__')[0] for p in rows}):
        strips=[]
        for row in sorted([r for r in rows.values() if r['pair_id'].startswith(name+'__')],key=lambda r:r['variant']):
            panels=[]
            for p,label in [(ROOT/row['reference_path'],'Reference'),(ROOT/row['input_path'],row['variant'])]+[(out/(row['pair_id']+'_'+m+'.png'),m) for m in ['baseline5','chroma9','clean_leaf']]:
                im=cv2.imread(str(p));im=cv2.copyMakeBorder(im,24,0,0,0,cv2.BORDER_CONSTANT);cv2.putText(im,label,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1);panels.append(im)
            strips.append(np.hstack(panels))
        path=out/(name+'_comparison.png');assert cv2.imwrite(str(path),np.vstack(strips));sections.append(f'<h2>{name}</h2><img src="{path.name}">')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Reviewed fifteen-source comparison</title><style>body{font:17px system-ui;margin:25px}img{max-width:100%}</style><h1>Fixed fifteen-source comparison</h1><p>Explicit accepted mask concerns retained. Exposed development,not final validation or automatic adoption.</p>'+''.join(sections),encoding='utf-8')
    target.write_text(json.dumps(dict(status='pass',verified_features=30,verified_regression_fits=30,verified_method_predictions=90,
        verified_clean_leaf_exports=15,source_duplicate_separation=True,all_seven_rejected_sources_excluded=True,
        retained_holds=74,accepted_concerns_preserved=True,independent_features_leaf_targets_pixels_metrics=True,
        matched_old_pairs=20,summary_sha256=digest(out/'summary.json'),fit_plan_sha256=digest(out/'fit_plan.json')),
        indent=2),encoding='utf-8')
    print('PASS:30features,30fits,90predictions,15clean-leaf exports,concerns/exclusions and20matched old pairs')
    print(json.dumps(matched,indent=2))


if __name__=='__main__':main()
