"""Independent sklearn leaf membership and RGB replay for conservative policy."""
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
    out=ROOT/'outputs/table2_clean_leaf_policy_v1';parent=ROOT/'outputs/table2_chroma_distribution_comparison_v1'
    target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(out/'plan.json');data=read(out/'summary.json');rows={r['pair_id']:r for r in plan['rows']};columns=plan['features']
    assert len(rows)==20 and len(plan['folds'])==10
    for p,h in data['input_sha256'].items():assert digest(ROOT/p)==h
    assert not {p.split('__')[0] for p in rows}&{'51739','40048','42532','63870','713'}
    assert len(plan['retained_holds'])==21
    training_controls_checked=0
    for fold in plan['folds']:
        fid=fold['fold_id'];model=joblib.load(parent/f'fold_{fid}/decision_tree.joblib')
        original=read(parent/f'fold_{fid}/decision_tree.json');modified=read(out/f'fold_{fid}/decision_tree.json');portable=PortableTree(modified)
        training=[rows[p] for p in fold['train_pair_ids']]
        leaves=model.apply([[r[k] for k in columns] for r in training])
        for index,(before,after) in enumerate(zip(original['nodes'],modified['nodes'])):
            if before['kind']=='split':assert before==after;continue
            controls=[r for r,l in zip(training,leaves) if l==index and r['variant']=='identity']
            assert after['values']==([1.,1.,1.] if controls else before['values'])
        for r in training:
            if r['variant']=='identity':
                assert portable.predict_one([r[k] for k in columns])==[1.,1.,1.];training_controls_checked+=1
        for record in [r for r in data['records'] if r['fold_id']==fid]:
            row=rows[record['pair_id']];x=[row[k] for k in columns];leaf=int(model.apply([x])[0])
            assert leaf==record['leaf'] and record['pair_id'] in fold['inner_validation_pair_ids']
            assert all(r['source_image_id']!=row['source_image_id'] and r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
            controls=[r for r,l in zip(training,leaves) if l==leaf and r['variant']=='identity']
            expected_parameters=[1.,1.,1.] if controls else model.predict([x])[0].tolist()
            assert record['parameters']==expected_parameters
            assert portable.predict_one(x)==record['parameters']
            image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path'])
            mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            g,r,b=expected_parameters;raw=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8)
            expected=image.copy();expected[mask]=raw[mask]
            path=out/(row['pair_id']+'_corrected.png');assert digest(path)==record['output_sha256']
            np.testing.assert_array_equal(rgb(path),expected)
            assert image_errors(reference,expected,scoring)==record['policy']
    assert training_controls_checked==90
    for group,subset in [('all',data['records']),('identity',[r for r in data['records'] if r['variant']=='identity']),('distorted',[r for r in data['records'] if r['variant']!='identity'])]:
        for method,value in data['aggregate'][group].items():assert value==float(np.mean([r[method]['ciede2000_source_mask'] for r in subset]))
    harmed=[r['pair_id'] for r in data['records'] if r['variant']=='identity' and r['policy']['ciede2000_source_mask']>0]
    assert harmed==data['gate']['harmed_identity_ids']
    assert data['gate']['identity_pass']==(not harmed)
    assert data['gate']['overall_improves']==(data['aggregate']['all']['policy']<data['aggregate']['all']['no_correction'])
    assert data['gate']['passed']==(data['gate']['overall_improves'] and data['gate']['identity_pass'])
    sections=[];board_hashes={}
    for name in sorted({p.split('__')[0] for p in rows}):
        strips=[]
        for row in sorted([r for r in rows.values() if r['pair_id'].startswith(name+'__')],key=lambda r:r['variant']):
            panels=[]
            for p,label in [(ROOT/row['reference_path'],'Reference'),(ROOT/row['input_path'],row['variant']),
                (parent/(row['pair_id']+'_corrected.png'),'Original chroma9'),(out/(row['pair_id']+'_corrected.png'),'Training-control leaf policy')]:
                im=cv2.imread(str(p));im=cv2.copyMakeBorder(im,24,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(im,label,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1);panels.append(im)
            strips.append(np.hstack(panels))
        p=out/(name+'_comparison.png');assert cv2.imwrite(str(p),np.vstack(strips));board_hashes[p.name]=digest(p)
        sections.append(f'<h2>{name}</h2><img src="{p.name}">')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Training-control leaf policy</title><style>body{font:17px system-ui;margin:25px}img{max-width:100%}</style><h1>Separate conservative leaf-policy experiment</h1><p>Same splits, inputs, features and masks. Identity leaf outputs use fitting controls only. Held clean gate fails; no runtime adoption.</p>'+''.join(sections),encoding='utf-8')
    target.write_text(json.dumps(dict(status='pass',verified_held_predictions=20,verified_fold_exports=10,verified_fitting_controls=90,
        split_nodes_unchanged=True,training_only_policy=True,independent_pixels_metrics_and_gates=True,
        excluded_sources_and_holds_preserved=True,original_hashes_unchanged=True,
        summary_sha256=digest(out/'summary.json'),comparison_sha256=board_hashes),indent=2),encoding='utf-8')
    print('PASS:20 held predictions,10 exports,90 fitting controls,unchanged splits,independent pixels/metrics')


if __name__=='__main__':main()
