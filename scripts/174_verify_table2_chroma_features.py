"""Independent feature arithmetic and saved nine-feature fold replay."""
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
    out=ROOT/'outputs/table2_chroma_distribution_comparison_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'plan.json');data=read(out/'summary.json');features=read(out/'features.json')
    rows={r['pair_id']:dict(r) for r in plan['rows']};columns=plan['features']
    assert len(rows)==20 and len(columns)==9 and len(plan['folds'])==10
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    assert not {p.split('__')[0] for p in rows}&{'51739','40048','42532','63870','713'}
    assert len(plan['retained_holds'])==21
    for record in features:
        row=rows[record['pair_id']];image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        encoded=cv2.cvtColor(image,cv2.COLOR_BGR2LAB)[mask]
        # Reproduce documented float32 Lab conversion, then use separate sums/quantile formula.
        L=(encoded[:,0].astype(np.float32)*np.float32(100/255)).astype(float)
        a=encoded[:,1].astype(float)-128;b=encoded[:,2].astype(float)-128;n=len(L)
        def percentile(v,q):
            ordered=sorted(map(float,v));index=(n-1)*q;lo=int(index);hi=min(lo+1,n-1)
            return ordered[lo]+(ordered[hi]-ordered[lo])*(index-lo)
        expected=[percentile(a,.75)-percentile(a,.25),percentile(b,.75)-percentile(b,.25),
            sum((float(x)-float(np.mean(L)))*(float(y)-float(np.mean(a))) for x,y in zip(L,a))/n,
            sum((float(x)-float(np.mean(L)))*(float(y)-float(np.mean(b))) for x,y in zip(L,b))/n]
        np.testing.assert_allclose(list(record['features'].values()),expected,rtol=0,atol=1e-9)
        row.update(record['features'])
    parent=ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1'
    base={r['pair_id']:r for r in read(parent/'summary.json')['records']}
    for record in data['records']:
        row=rows[record['pair_id']];fold=next(f for f in plan['folds'] if f['fold_id']==record['fold_id'])
        assert row['pair_id'] in fold['inner_validation_pair_ids']
        training=[rows[p] for p in fold['train_pair_ids']]
        assert len(training)==18 and all(r['source_image_id']!=row['source_image_id'] and r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
        model=joblib.load(out/f"fold_{fold['fold_id']}/decision_tree.joblib")
        portable=PortableTree(read(out/f"fold_{fold['fold_id']}/decision_tree.json"))
        x=[row[k] for k in columns]
        np.testing.assert_allclose(model.predict([x])[0],record['parameters'],rtol=0,atol=1e-12)
        np.testing.assert_allclose(portable.predict_one(x),record['parameters'],rtol=0,atol=1e-12)
        leaves=model.apply([[r[k] for k in columns] for r in training])
        for leaf in set(leaves):
            mean=np.mean([[r[k] for k in TARGETS] for r,l in zip(training,leaves) if l==leaf],axis=0)
            np.testing.assert_allclose(mean,model.tree_.value[leaf].ravel(),rtol=0,atol=1e-12)
        image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path'])
        mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        g,r,b=record['parameters'];transformed=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
        expected=image.copy();expected[mask]=transformed[mask]
        output=out/(row['pair_id']+'_corrected.png');assert digest(output)==record['output_sha256']
        np.testing.assert_array_equal(rgb(output),expected)
        assert image_errors(reference,expected,scoring)==record['candidate']
        for method,key in [('baseline','learned'),('no_correction','no_correction'),('oracle','oracle')]:assert record[method]==base[row['pair_id']][key]
    for group,subset in [('all',data['records']),('identity',[r for r in data['records'] if r['variant']=='identity']),('distorted',[r for r in data['records'] if r['variant']!='identity'])]:
        for method,value in data['aggregate'][group].items():assert value==float(np.mean([r[method]['ciede2000_source_mask'] for r in subset]))
    harmed=[r['pair_id'] for r in data['records'] if r['variant']=='identity' and r['candidate']['ciede2000_source_mask']>0]
    assert harmed==data['gate']['harmed_identity_ids']
    assert data['gate']['identity_pass']==(not harmed)
    assert data['gate']['overall_improves']==(data['aggregate']['all']['candidate']<data['aggregate']['all']['no_correction'])
    assert data['gate']['passed']==(data['gate']['identity_pass'] and data['gate']['overall_improves'])
    links=[]
    for name in sorted({p.split('__')[0] for p in rows}):
        strips=[]
        for row in sorted([r for r in rows.values() if r['pair_id'].startswith(name+'__')],key=lambda r:r['variant']):
            panels=[]
            for path,label in [(ROOT/row['reference_path'],'Reference'),(ROOT/row['input_path'],row['variant']),
                (parent/(row['pair_id']+'_corrected.png'),'Baseline 5'),(out/(row['pair_id']+'_corrected.png'),'Chroma 9')]:
                im=cv2.imread(str(path));im=cv2.copyMakeBorder(im,24,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(im,label,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.38,(255,255,255),1);panels.append(im)
            strips.append(np.hstack(panels))
        path=out/(name+'_comparison.png');assert cv2.imwrite(str(path),np.vstack(strips));links.append(f'<h2>{name}</h2><img src="{path.name}">')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Chroma distribution comparison</title><style>body{font:17px system-ui;margin:25px}img{max-width:100%}</style><h1>Five versus nine features</h1><p>Identical held-source folds, targets, masks and tree settings. Exposed development only; clean gate fails. No runtime replacement.</p>'+''.join(links),encoding='utf-8')
    target.write_text(json.dumps(dict(status='pass',independent_features=20,verified_predictions=20,verified_folds=10,
        independent_pixels_metrics_and_leaf_means=True,baseline_unchanged=True,source_group_separation=True,
        summary_sha256=digest(out/'summary.json'),features_sha256=digest(out/'features.json')),indent=2),encoding='utf-8')
    print('PASS:20 input-feature calculations,20 saved predictions,10 folds,pixels,metrics and leaf means')


if __name__=='__main__':main()
