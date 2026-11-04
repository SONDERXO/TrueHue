"""Saved ten-fold replay, independent RGB reconstruction and review accounting."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.portable_tree import PortableTree
from src.evaluation.correction_prototype import image_errors


def main():
    out=ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'fit_plan.json');summary=read(out/'summary.json');review=read(out/'user_review.json')
    rows={r['pair_id']:r for r in plan['rows']};folds={f['fold_id']:f for f in plan['folds']}
    assert len(rows)==20 and len(folds)==10 and len(summary['records'])==20
    rejected={'51739','40048','42532','63870','713'}
    assert not {p.split('__')[0] for p in rows}&rejected
    assert {r['pair_id'].split('__')[0] for r in plan['excluded']}==rejected
    assert len(plan['retained_holds'])==21
    assert review['decisions']['713']==dict(decision='reject',reason='captures hair in mask')
    for p,h in plan['input_sha256'].items():assert digest(ROOT/p)==h
    for r in rows.values():
        if r['pair_id'].startswith('51803__'):assert r['review_concern']=='a minor hole in the mask'
        for path,key in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256'),('reference_mask_path','reference_mask_sha256')]:assert digest(ROOT/r[path])==r[key]
    for record in summary['records']:
        row=rows[record['pair_id']];fold=folds[record['fold_id']]
        assert row['pair_id'] in fold['inner_validation_pair_ids']
        training=[rows[p] for p in fold['train_pair_ids']]
        assert len(training)==18
        assert all(r['source_image_id']!=row['source_image_id'] and r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
        model=joblib.load(out/f"fold_{fold['fold_id']}/decision_tree.joblib")
        portable=PortableTree(read(out/f"fold_{fold['fold_id']}/decision_tree.json"))
        x=[row[k] for k in MST_FEATURES]
        np.testing.assert_allclose(model.predict([x])[0],record['parameters'],rtol=0,atol=1e-12)
        np.testing.assert_allclose(portable.predict_one(x),record['parameters'],rtol=0,atol=1e-12)
        leaves=model.apply([[r[k] for k in MST_FEATURES] for r in training])
        for leaf in set(leaves):
            mean=np.mean([[r[k] for k in TARGETS] for r,l in zip(training,leaves) if l==leaf],axis=0)
            np.testing.assert_allclose(mean,model.tree_.value[leaf].ravel(),rtol=0,atol=1e-12)
        image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path'])
        mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        def independent(parameters):
            g,r,b=parameters;transformed=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
            result=image.copy();result[mask]=transformed[mask];return result
        output=out/(row['pair_id']+'_corrected.png');assert digest(output)==record['output_sha256']
        corrected=rgb(output);np.testing.assert_array_equal(corrected,independent(record['parameters']))
        np.testing.assert_array_equal(corrected[~mask],image[~mask])
        for method,result in [('no_correction',image),('learned',corrected),('oracle',independent([row[k] for k in TARGETS]))]:
            assert image_errors(reference,result,scoring)==record[method]
    identities=[r for r in summary['records'] if r['variant']=='identity']
    harmed=[r['pair_id'] for r in identities if r['learned']['ciede2000_source_mask']>0]
    assert harmed==summary['gate']['harmed_identity_ids']
    for group,subset in [('all',summary['records']),('identity',identities),('distorted',[r for r in summary['records'] if r['variant']!='identity'])]:
        for method in ['no_correction','learned','oracle']:
            assert float(np.mean([r[method]['ciede2000_source_mask'] for r in subset]))==summary['aggregate'][group][method+'_ciede2000']
    assert summary['gate']['overall_improves']==(summary['aggregate']['all']['learned_ciede2000']<summary['aggregate']['all']['no_correction_ciede2000'])
    assert summary['gate']['identity_pass']==(not harmed)
    assert summary['gate']['passed']==(summary['gate']['identity_pass'] and summary['gate']['overall_improves'])
    links=[];board_hashes={}
    for name in sorted({p.split('__')[0] for p in rows}):
        strips=[]
        for row in sorted([r for r in rows.values() if r['pair_id'].startswith(name+'__')],key=lambda r:r['variant']):
            panels=[]
            for p,label in [(ROOT/row['reference_path'],'Photographic reference'),(ROOT/row['input_path'],row['variant']),(out/(row['pair_id']+'_corrected.png'),'Held-source prediction')]:
                image=cv2.imread(str(p));panel=cv2.copyMakeBorder(image,25,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(panel,label,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.36,(255,255,255),1);panels.append(panel)
            strips.append(np.hstack(panels))
        path=out/(name+'_comparison.png');assert cv2.imwrite(str(path),np.vstack(strips));board_hashes[path.name]=digest(path)
        links.append(f'<h2>{name}</h2><img src="{path.name}">')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Ten-source held evaluation</title><style>body{font:17px system-ui;margin:25px}img{max-width:100%}</style><h1>Ten-source held evaluation</h1><p>Frozen settings, experimental MST, ordinary photo references. Identity gate fails; no model adoption.</p>'+''.join(links),encoding='utf-8')
    target.write_text(json.dumps(dict(status='pass',verified_predictions=20,verified_folds=10,
        independent_rgb_replay=True,leaf_means_and_metrics_recomputed=True,all_five_rejected_sources_excluded=True,
        retained_holds=21,review_concern_preserved=True,summary_sha256=digest(out/'summary.json'),
        fit_plan_sha256=digest(out/'fit_plan.json'),comparison_sha256=board_hashes),indent=2),encoding='utf-8')
    print('PASS:20 predictions,10 saved folds,independent pixels/metrics/leaf means/review/exclusions')


if __name__=='__main__':main()
