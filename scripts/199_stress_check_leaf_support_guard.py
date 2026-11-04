"""Apply frozen leaf-range guard to all24existing counterfactual probes; no tuning."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import joblib
import numpy as np
from src.model_training.portable_tree import PortableTree,float32
from src.evaluation.correction_prototype import apply_correction,image_errors


def main():
    out=ROOT/'outputs/table2_leaf_support_stress_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    guard=ROOT/'outputs/table2_leaf_support_guard_v1';plan=read(guard/'plan.json')
    assert digest(guard/'summary.json')==read(guard/'verification.json')['summary_sha256']
    stress=ROOT/'outputs/table2_counterfactual_coverage_v1';probes=read(stress/'summary.json')
    assert digest(stress/'summary.json')==read(stress/'verification.json')['summary_sha256']
    folds={p.split('__')[0]:f['fold_id'] for f in plan['folds'] for p in f['inner_validation_pair_ids']}
    paths=[Path(__file__),guard/'plan.json',guard/'summary.json',guard/'verification.json',stress/'summary.json',stress/'verification.json']
    paths+=list(guard.glob('fold_*/*'))
    for r in probes['records']:
        paths.extend([stress/'images'/(r['pair_id']+'_input.png'),ROOT/r['reference_path'],ROOT/r['reference_mask_path']])
        if r['status']=='success':paths.append(stress/'images'/(r['pair_id']+'_mask.png'))
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    out.mkdir();write(out/'plan.json',dict(status='frozen_before_stress_scores',probes=24,source_fold_map=folds,input_sha256=hashes,no_fits_or_rule_changes=True))
    records=[]
    for row in probes['records']:
        pair=row['pair_id'];record=dict(pair_id=pair,severity=row['severity_probe'],status=row['status']);records.append(record)
        if row['status']!='success':record['reason']=row['measurement'].get('reason');continue
        fid=folds[row['source_id']];tree=PortableTree(read(ROOT/f'outputs/table2_five_feature_clean_leaf_v1/fold_{fid}/decision_tree.json'))
        features=row['features'];x=[features[k] for k in plan['features']];leaf=tree.leaf_id(x);ranges=read(guard/f'fold_{fid}/leaf_ranges.json')[str(leaf)]
        outside=[k for i,k in enumerate(plan['features']) if not ranges['minimum'][i]<=float32(x[i])<=ranges['maximum'][i]]
        parameters=[1.,1.,1.] if outside else tree.predict_one(x)
        # Independent original sklearn routing and fitting-array min/max check.
        model=joblib.load(ROOT/f'outputs/table2_reviewed_fifteen_source_evaluation_v1/fold_{fid}/baseline5.joblib')
        fold=next(f for f in plan['folds'] if f['fold_id']==fid);fitting=[r for r in plan['rows'] if r['pair_id'] in fold['train_pair_ids']]
        assert all(r['source_image_id']!=f'fairface__train/{row["source_id"]}.jpg' for r in fitting)
        xf=np.array([[r[k] for k in plan['features']] for r in fitting],np.float32);leaves=model.apply(xf);q=np.array(x,np.float32)
        assert int(model.apply([q])[0])==leaf
        inside=bool(np.all((q>=xf[leaves==leaf].min(axis=0))&(q<=xf[leaves==leaf].max(axis=0))))
        assert inside==(not outside)
        image=rgb(stress/'images'/(pair+'_input.png'));reference=rgb(ROOT/row['reference_path']);mask=cv2.imread(str(stress/'images'/(pair+'_mask.png')),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        corrected=apply_correction(image,mask,parameters);g,r,b=parameters
        raw=np.rint(np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)*255).astype(np.uint8);expected=image.copy();expected[mask]=raw[mask]
        np.testing.assert_array_equal(corrected,expected)
        path=out/(pair+'_corrected.png');assert cv2.imwrite(str(path),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR));np.testing.assert_array_equal(rgb(path),expected)
        record.update(fold_id=fid,leaf=leaf,outside_axes=outside,parameters=parameters,abstained=bool(outside),
            corrected_pixels=int(np.any(corrected!=image,axis=2).sum()),no_correction=image_errors(reference,image,score),guarded=image_errors(reference,corrected,score))
    aggregate={g:dict(attempted=sum(r['severity']==g for r in records),successful=len(subset),
        changed_inputs=sum(r['corrected_pixels']>0 for r in subset),no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in subset])),
        guarded=float(np.mean([r['guarded']['ciede2000_source_mask'] for r in subset])))
        for g in ['light','medium','dark'] if (subset:=[r for r in records if r['severity']==g and r['status']=='success'])}
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(out/'summary.json',dict(status='complete_frozen_guard_stress',records=records,aggregate=aggregate,input_sha256=hashes,runtime_replaced=False,final_validated=False))
    write(out/'verification.json',dict(status='pass',verified_predictions=23,preserved_failures=1,independent_sklearn_ranges_and_rgb_pixels=True,
        original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')))
    print(json.dumps(aggregate,indent=2))


if __name__=='__main__':main()
