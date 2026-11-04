"""Independent saved-fold replay and comparison boards; no fitting."""
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
from src.evaluation.correction_prototype import apply_correction,image_errors


def main():
    out=ROOT/'outputs/table2_reviewed_expansion_evaluation_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=json.loads((out/'fit_plan.json').read_text());summary=json.loads((out/'summary.json').read_text())
    rows={r['pair_id']:r for r in plan['rows']};folds={f['fold_id']:f for f in plan['folds']}
    assert len(rows)==16 and len(folds)==8 and len(summary['records'])==16
    assert not {p.split('__')[0] for p in rows}&{'51739','40048','42532','63870'}
    assert {p['pair_id'].split('__')[0] for p in plan['excluded']}=={'51739','40048','42532','63870'}
    for p,h in plan['input_sha256'].items():assert digest(ROOT/p)==h
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    for record in summary['records']:
        row=rows[record['pair_id']];fold=folds[record['fold_id']]
        assert row['pair_id'] in fold['inner_validation_pair_ids']
        assert not set(fold['train_source_ids'])&set(fold['inner_validation_source_ids'])
        training=[rows[p] for p in fold['train_pair_ids']]
        assert len(training)==14 and all(r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
        model=joblib.load(out/f"fold_{fold['fold_id']}/decision_tree.joblib")
        portable=PortableTree(json.loads((out/f"fold_{fold['fold_id']}/decision_tree.json").read_text()))
        x=[row[k] for k in MST_FEATURES]
        assert np.allclose(model.predict([x])[0],record['parameters'],rtol=0,atol=1e-12)
        assert np.allclose(portable.predict_one(x),record['parameters'],rtol=0,atol=1e-12)
        leaves=model.apply([[r[k] for k in MST_FEATURES] for r in training])
        for leaf in set(leaves):
            targets=np.mean([[r[k] for k in TARGETS] for r,l in zip(training,leaves) if l==leaf],axis=0)
            assert np.allclose(model.tree_.value[leaf].ravel(),targets,rtol=0,atol=1e-12)
        for path,key in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256'),('reference_mask_path','reference_mask_sha256')]:assert digest(ROOT/row[path])==row[key]
        image=rgb(ROOT/row['input_path']);reference=rgb(ROOT/row['reference_path'])
        mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        output=out/(row['pair_id']+'_corrected.png');assert digest(output)==record['output_sha256'];corrected=rgb(output)
        assert np.array_equal(corrected,apply_correction(image,mask,record['parameters']))
        assert np.array_equal(corrected[~mask],image[~mask])
        for method,result in [('no_correction',image),('learned',corrected),('oracle',apply_correction(image,mask,[row[k] for k in TARGETS]))]:
            assert image_errors(reference,result,scoring)==record[method]
    identities=[r for r in summary['records'] if r['variant']=='identity']
    harmed=[r['pair_id'] for r in identities if r['learned']['ciede2000_source_mask']>0]
    assert harmed==summary['gate']['harmed_identity_ids']
    for key,subset in [('all',summary['records']),('identity',identities),('distorted',[r for r in summary['records'] if r['variant']!='identity'])]:
        for method in ['no_correction','learned','oracle']:
            assert float(np.mean([r[method]['ciede2000_source_mask'] for r in subset]))==summary['aggregate'][key][method+'_ciede2000']
    board_hashes={}
    for name in sorted({p.split('__')[0] for p in rows}):
        panels=[]
        for variant in ['identity',next(r['variant'] for p,r in rows.items() if p.startswith(name+'__') and r['variant']!='identity')]:
            pair=name+'__'+variant;row=rows[pair]
            def tile(path,label):
                image=cv2.imread(str(path));image=cv2.copyMakeBorder(image,24,0,0,0,cv2.BORDER_CONSTANT,value=(255,255,255))
                cv2.putText(image,label,(4,17),cv2.FONT_HERSHEY_SIMPLEX,.44,(0,0,0),1);return image
            panels.append(np.hstack([tile(ROOT/row['reference_path'],'reference'),tile(ROOT/row['input_path'],variant),tile(out/(pair+'_corrected.png'),'held-source prediction')]))
        path=out/f'{name}_comparison.png';assert cv2.imwrite(str(path),np.vstack(panels));board_hashes[path.name]=digest(path)
    target.write_text(json.dumps(dict(status='pass',summary_sha256=digest(out/'summary.json'),fit_plan_sha256=digest(out/'fit_plan.json'),
        verified_predictions=16,verified_folds=8,leaf_means_and_pixels_and_metrics_recomputed=True,
        all_four_rejected_sources_excluded=True,comparison_sha256=board_hashes),indent=2))
    print('PASS: 16 predictions, 8 source/group folds, pixels, metrics, leaf targets and rejected-source exclusions')


if __name__=='__main__':main()
