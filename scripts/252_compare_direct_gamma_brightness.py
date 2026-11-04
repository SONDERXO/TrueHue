"""One fixed11feature comparison on the same source-held direct-gamma cohort."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.facial_brightness_features import facial_brightness_features,ADDITIONS
from src.model_training.portable_tree import PortableTree,export_tree
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors


def main():
    parent=ROOT/'outputs/direct_gamma_regression_comparison_v1';baseline=ROOT/'outputs/direct_gamma_clean_leaf_v1'
    out=ROOT/'outputs/direct_gamma_brightness_comparison_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    for name,sha in read(baseline/'verification.json')['evidence_sha256'].items():assert digest(baseline/name)==sha
    plan=read(parent/'plan.json');prior={r['pair_id']:r for r in read(baseline/'predictions.json')}
    for p,sha in plan['input_sha256'].items():assert digest(ROOT/p)==sha
    rows=plan['rows'];columns=tuple(plan['features'])+ADDITIONS
    paths=[Path(__file__),ROOT/'docs/direct-gamma-brightness-protocol.md',ROOT/'src/model_training/facial_brightness_features.py',
        ROOT/'src/model_training/training_identity_leaf_policy.py',ROOT/'scripts/72_audit_brightness_features.py',
        parent/'plan.json',baseline/'verification.json']
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_feature_extraction',features=list(columns),settings=plan['settings'],
        sources=15,pairs=30,folds=plan['folds'],input_sha256=hashes,regression_fits_planned=15,
        raw_and_protected_both_reported=True,active_demo_changed=False))
    old_helper=importlib.import_module('72_audit_brightness_features');features={};feature_reports=[]
    for row in rows:
        image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        result=facial_brightness_features(image,mask)
        assert result==old_helper.brightness_features(image,mask)
        feature_reports.append(dict(pair_id=row['pair_id'],**result))
        if result['valid']:features[row['pair_id']]=[row[k] for k in plan['features']]+[result['features'][k] for k in ADDITIONS]
    write('features.json',feature_reports)
    if len(features)!=30:
        write('summary.json',dict(status='blocked_unavailable_features',available=len(features),attempted=30,regression_fits=0));return
    records=[];controls=0
    for fold in plan['folds']:
        fid=fold['fold_id'];train=[r for r in rows if r['pair_id'] in fold['train_pair_ids']]
        held=[r for r in rows if r['pair_id'] in fold['inner_validation_pair_ids']]
        assert not {r['source_image_id'] for r in train}&{r['source_image_id'] for r in held}
        assert not {r['duplicate_group_id'] for r in train}&{r['duplicate_group_id'] for r in held}
        x=np.array([features[r['pair_id']] for r in train]);y=np.array([plan['converted_targets'][r['pair_id']] for r in train])
        raw=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,y),list(columns),plan['target_names'],
            dict(gamma_convention='direct_exponent',features_version='existing_brightness6_plus_Lab_ITA_MST_v1',held_source_ids=fold['inner_validation_source_ids']))
        protected,membership=protect_identity_leaves(raw,x.tolist(),[r['variant']=='identity' for r in train])
        folder=out/f'fold_{fid}';folder.mkdir()
        for method,payload in [('brightness_raw',raw),('brightness_protected',protected)]:
            (folder/f'{method}.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
        (folder/'membership.json').write_text(json.dumps(membership,indent=2),encoding='utf-8')
        models={m:PortableTree(p) for m,p in [('brightness_raw',raw),('brightness_protected',protected)]}
        for r in train:
            if r['variant']=='identity':assert models['brightness_protected'].predict_one(features[r['pair_id']])==[1.,1.,1.];controls+=1
        for row in held:
            image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
            mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            for method,tree in models.items():
                params=tree.predict_one(features[row['pair_id']]);output=image.copy()
                output[mask]=np.rint(transform_rgb(image.astype(float)/255,*params)[mask]*255).astype(np.uint8)
                assert np.array_equal(output[~mask],image[~mask])
                path=folder/(row['pair_id']+'_'+method+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                records.append(dict(pair_id=row['pair_id'],source_image_id=row['source_image_id'],variant=row['variant'],fold_id=fid,method=method,
                    parameters=params,changed_input_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),
                    no_correction_error=prior[row['pair_id']]['no_correction_error'],baseline5_error=prior[row['pair_id']]['metrics']['ciede2000_source_mask'],
                    metrics=image_errors(reference,output,score),output_sha256=digest(path)))
        print('Fold',fid,'complete',flush=True)
    aggregates=[];gates={}
    for method in ['brightness_raw','brightness_protected']:
        for scope in ['all','identity','distorted']:
            selected=[r for r in records if r['method']==method and (scope=='all' or (r['variant']=='identity')==(scope=='identity'))]
            aggregates.append(dict(method=method,scope=scope,pairs=len(selected),
                no_correction=float(np.mean([r['no_correction_error'] for r in selected])),
                baseline5=float(np.mean([r['baseline5_error'] for r in selected])),
                candidate=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in selected])),
                changed_pairs=sum(r['changed_input_pixels']>0 for r in selected)))
        all_values=next(r for r in aggregates if r['method']==method and r['scope']=='all')
        identity=next(r for r in aggregates if r['method']==method and r['scope']=='identity')
        gate=dict(overall_improves=all_values['candidate']<all_values['no_correction'],clean_unchanged=identity['changed_pairs']==0)
        gate['passed']=gate['overall_improves'] and gate['clean_unchanged'];gates[method]=gate
    assert controls==210 and all(digest(ROOT/p)==sha for p,sha in hashes.items())
    write('predictions.json',records);write('summary.json',dict(status='complete_exposed_development_no_promotion',sources=15,pairs=30,
        regression_fits=15,held_predictions=60,aggregates=aggregates,gates=gates,active_demo_changed=False,
        feature_helper_parity=30,final_validation_test_access=False,newer_mask_rows_admitted=False))
    print(json.dumps(dict(aggregates=aggregates,gates=gates),indent=2))


if __name__=='__main__':main()
