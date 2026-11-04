"""Independent sklearn fitting ranges, float32 query tests and RGB reconstruction."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.evaluation.correction_prototype import image_errors


def main():
    parent=ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1';previous=ROOT/'outputs/table2_five_feature_clean_leaf_v1';out=ROOT/'outputs/table2_leaf_support_guard_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'plan.json');data=read(out/'summary.json');rows={r['pair_id']:r for r in plan['rows']};names=plan['features']
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    assert len(rows)==30 and len(plan['folds'])==15 and len(plan['retained_holds'])==74
    for fold in plan['folds']:
        fid=fold['fold_id'];model=joblib.load(parent/f'fold_{fid}/baseline5.joblib')
        training=[rows[p] for p in fold['train_pair_ids']];xfit=np.asarray([[r[k] for k in names] for r in training],np.float32)
        leaves=model.apply(xfit);ranges=read(out/f'fold_{fid}/leaf_ranges.json')
        conservative=read(previous/f'fold_{fid}/decision_tree.json')
        for leaf in set(leaves):
            expected=ranges[str(int(leaf))];subset=xfit[leaves==leaf]
            assert expected['minimum']==subset.min(axis=0).astype(float).tolist()
            assert expected['maximum']==subset.max(axis=0).astype(float).tolist()
            assert set(expected['fitting_pair_ids'])=={r['pair_id'] for r,l in zip(training,leaves) if l==leaf}
        for record in [r for r in data['records'] if r['fold_id']==fid]:
            row=rows[record['pair_id']];assert row['pair_id'] in fold['inner_validation_pair_ids']
            assert all(r['source_image_id']!=row['source_image_id'] and r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
            query=np.asarray([row[k] for k in names],np.float32);leaf=int(model.apply([query])[0]);support=xfit[leaves==leaf]
            inside=np.all((query>=support.min(axis=0))&(query<=support.max(axis=0)))
            expected=conservative['nodes'][leaf]['values'] if inside else [1.,1.,1.]
            assert record['parameters']==expected and record['leaf']==leaf and record['abstained']==(not bool(inside))
            assert record['outside_axes']==[names[i] for i in range(len(names)) if not support[:,i].min()<=query[i]<=support[:,i].max()]
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path']);mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            g,r,b=expected;raw=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
            corrected=image.copy();corrected[mask]=raw[mask];path=out/(row['pair_id']+'_corrected.png')
            assert digest(path)==record['output_sha256'];np.testing.assert_array_equal(rgb(path),corrected)
            assert image_errors(reference,corrected,score)==record['guarded']
    for scope,subset in [('all',data['records']),('identity',[r for r in data['records'] if r['variant']=='identity']),('distorted',[r for r in data['records'] if r['variant']!='identity'])]:
        for method,value in data['aggregate'][scope].items():assert value==float(np.mean([r[method]['ciede2000_source_mask'] for r in subset]))
    harms=[r['pair_id'] for r in data['records'] if r['variant']=='identity' and r['guarded']['ciede2000_source_mask']>0]
    assert data['gate']['harmed_identity_ids']==harms and data['gate']['identity_pass']==(not harms)
    assert data['gate']['overall_improves']==(data['aggregate']['all']['guarded']<data['aggregate']['all']['no_correction'])
    assert data['gate']['passed']==(data['gate']['overall_improves'] and data['gate']['identity_pass'])
    assert data['abstentions']==sum(r['abstained'] for r in data['records'])
    target.write_text(json.dumps(dict(status='pass',verified_fitting_range_sets=15,verified_outputs=30,independent_sklearn_float32_decisions=True,
        independent_pixels_and_metrics=True,original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')),indent=2),encoding='utf-8')
    print('PASS:15fitting-range sets,30held decisions and RGB outputs,metrics/gates/hashes')


if __name__=='__main__':main()
