"""Recompute saved predictions, metrics, leaf targets and evidence hashes."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.evaluation.correction_prototype import apply_correction,image_errors
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.portable_tree import PortableTree


def main():
    out=ROOT/'outputs/table2_stress_evaluation_v2';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=json.loads((out/'fit_plan.json').read_text());summary=json.loads((out/'summary.json').read_text())
    rows={r['pair_id']:r for r in plan['rows']};folds={r['fold_id']:r for r in plan['folds']}
    assert len(rows)==len(summary['records'])==10
    for p,h in plan['input_sha256'].items():assert digest(ROOT/p)==h
    for record in summary['records']:
        row=rows[record['pair_id']];fold=folds[record['fold_id']]
        assert record['pair_id'] in fold['inner_validation_pair_ids']
        assert set(fold['train_source_ids']).isdisjoint(fold['inner_validation_source_ids'])
        model=joblib.load(out/f"fold_{fold['fold_id']}/decision_tree.joblib")
        portable=PortableTree(json.loads((out/f"fold_{fold['fold_id']}/decision_tree.json").read_text()))
        x=[row[k] for k in MST_FEATURES]
        assert np.allclose(model.predict([x])[0],record['parameters'],atol=1e-12,rtol=0)
        assert np.allclose(portable.predict_one(x),record['parameters'],atol=1e-12,rtol=0)
        training=[rows[p] for p in fold['train_pair_ids']]
        train_x=np.asarray([[r[k] for k in MST_FEATURES] for r in training])
        leaves=model.apply(train_x)
        for leaf in set(leaves):
            expected=np.mean([[r[k] for k in TARGETS] for r,l in zip(training,leaves) if l==leaf],axis=0)
            assert np.allclose(model.tree_.value[leaf].ravel(),expected,atol=1e-12,rtol=0)
        def rgb(path):return cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB)
        image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path'])
        mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        output=out/(row['pair_id']+'_corrected.png');assert digest(output)==record['output_sha256']
        corrected=rgb(output);assert np.array_equal(corrected,apply_correction(image,mask,record['parameters']))
        assert np.array_equal(corrected[~mask],image[~mask])
        for method,content in [('no_correction',image),('learned',corrected),('oracle',apply_correction(image,mask,[row[k] for k in TARGETS]))]:
            actual=image_errors(reference,content,scoring)
            for k,v in actual.items():assert v==record[method][k]
    for name in sorted({p.split('__')[0] for p in rows}):
        tiles=[]
        for variant in ['identity',next(rows[p]['variant'] for p in rows if p.startswith(name+'__') and rows[p]['variant']!='identity')]:
            p=name+'__'+variant;row=rows[p];record=next(r for r in summary['records'] if r['pair_id']==p)
            def tile(path,label):
                frame=cv2.imread(str(path));frame=cv2.copyMakeBorder(frame,25,0,0,0,cv2.BORDER_CONSTANT,value=(255,255,255))
                cv2.putText(frame,label,(5,17),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1);return frame
            tiles.append(np.hstack([tile(ROOT/row['reference_path'],'reference'),tile(ROOT/row['input_path'],variant),
                tile(out/(p+'_corrected.png'),f"held-source tree DE {record['learned']['ciede2000_source_mask']:.2f}")]))
        assert cv2.imwrite(str(out/f'{name}_comparison.png'),np.vstack(tiles))
    identity=[r for r in summary['records'] if r['variant']=='identity']
    harmed=[r['pair_id'] for r in identity if r['learned']['ciede2000_source_mask']>0]
    assert harmed==summary['gate']['harmed_identity_ids']
    for key,subset in [('all',summary['records']),('identity',identity),('distorted',[r for r in summary['records'] if r['variant']!='identity'])]:
        for method in ['no_correction','learned','oracle']:
            assert float(np.mean([r[method]['ciede2000_source_mask'] for r in subset]))==summary['aggregate'][key][method+'_ciede2000']
    target.write_text(json.dumps(dict(status='pass',summary_sha256=digest(out/'summary.json'),
        fit_plan_sha256=digest(out/'fit_plan.json'),verified_predictions=10,verified_folds=5,
        leaf_means_checked=True,source_exclusion_checked=True,all_pixel_metrics_recomputed=True),indent=2))
    print('PASS: 10 saved predictions, 5 folds, leaf targets, pixels, metrics and gate')


if __name__=='__main__':main()
