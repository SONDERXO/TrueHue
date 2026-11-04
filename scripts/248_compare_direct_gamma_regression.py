"""Matched15-source training comparison; retain masks, features and all holds."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.ita_estimation.square_measurement import contract
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import PortableTree,export_tree
from src.distortion_generation.paper_gamma import transform_rgb,legacy_to_paper_parameters
from src.evaluation.correction_prototype import apply_correction,image_errors


def main():
    out=ROOT/'outputs/direct_gamma_regression_comparison_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    old=ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1'
    original=read(old/'fit_plan.json');verify=read(old/'verification.json')
    assert digest(old/'fit_plan.json')==verify['fit_plan_sha256']
    assert digest(old/'summary.json')==verify['summary_sha256']
    rows=original['rows'];folds=original['folds'];_,identity=contract(ROOT)
    assert len(rows)==30 and len(folds)==15
    for row in rows:
        assert row['measurement_contract_sha256']==identity
        for key,sha in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256'),('reference_mask_path','reference_mask_sha256')]:
            assert digest(ROOT/row[key])==row[sha]
    targets={r['pair_id']:[1/float(r[TARGETS[0]]),float(r[TARGETS[1]]),float(r[TARGETS[2]])] for r in rows}
    paths=[Path(__file__),ROOT/'docs/direct-gamma-tree-comparison-protocol.md',old/'fit_plan.json',old/'verification.json',
        ROOT/'src/model_training/portable_tree.py',ROOT/'src/model_training/development_build.py',
        ROOT/'src/distortion_generation/paper_gamma.py',ROOT/'src/evaluation/correction_prototype.py']
    for row in rows:
        paths.extend(ROOT/row[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_training',rows=rows,folds=folds,converted_targets=targets,
        features=list(MST_FEATURES),target_names=list(TARGETS),settings=SETTINGS,input_sha256=hashes,
        sample_weight=None,methods=['legacy_refit','paper_gamma_refit'],models_planned=30,
        evidence_role='historically approved, repeatedly exposed development stress cohort; not final test',
        newer_unreviewed_mask_pairs_admitted=False,active_assets_changed=False))
    records=[]
    for fold in folds:
        train=[r for r in rows if r['pair_id'] in fold['train_pair_ids']]
        held=[r for r in rows if r['pair_id'] in fold['inner_validation_pair_ids']]
        assert not {r['source_image_id'] for r in train}&{r['source_image_id'] for r in held}
        assert not {r['duplicate_group_id'] for r in train}&{r['duplicate_group_id'] for r in held}
        folder=out/f'fold_{fold["fold_id"]}';folder.mkdir()
        models={}
        x=np.array([[r[k] for k in MST_FEATURES] for r in train],float)
        for method in ['legacy_refit','paper_gamma_refit']:
            y=np.array([[r[k] for k in TARGETS] if method=='legacy_refit' else targets[r['pair_id']] for r in train],float)
            model=DecisionTreeRegressor(**SETTINGS).fit(x,y)
            payload=export_tree(model,list(MST_FEATURES),list(TARGETS),dict(method=method,held_source_ids=fold['inner_validation_source_ids'],
                gamma_convention='reciprocal_exponent' if method=='legacy_refit' else 'direct_exponent',measurement_contract_sha256=identity))
            (folder/f'{method}.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
            models[method]=PortableTree(payload)
        for row in held:
            image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
            mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
            scoring=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
            features=[row[k] for k in MST_FEATURES]
            for method in ['no_correction','legacy_refit','paper_gamma_refit']:
                if method=='no_correction':output=image.copy();paper_params=[1.,1.,1.];raw_params=None
                else:
                    raw_params=models[method].predict_one(features)
                    if method=='legacy_refit':
                        output=apply_correction(image,mask,raw_params)
                        converted=legacy_to_paper_parameters(*raw_params);paper_params=list(converted.values())
                        alternative=image.copy();alternative[mask]=np.rint(transform_rgb(image.astype(float)/255,**converted)[mask]*255).astype(np.uint8)
                        np.testing.assert_array_equal(output,alternative)
                    else:
                        paper_params=raw_params
                        output=image.copy();output[mask]=np.rint(transform_rgb(image.astype(float)/255,*paper_params)[mask]*255).astype(np.uint8)
                assert np.array_equal(output[~mask],image[~mask])
                path=folder/(row['pair_id']+'_'+method+'.png')
                assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                error=image_errors(reference,output,scoring)
                records.append(dict(pair_id=row['pair_id'],source_image_id=row['source_image_id'],variant=row['variant'],fold_id=fold['fold_id'],
                    method=method,raw_parameters=raw_params,paper_parameters=paper_params,target_paper_parameters=targets[row['pair_id']],
                    changed_input_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),output_sha256=digest(path),**error))
        print('Fold',fold['fold_id'],'complete',flush=True)
    aggregates=[]
    for method in ['no_correction','legacy_refit','paper_gamma_refit']:
        for scope in ['all','identity','distorted']:
            values=[r for r in records if r['method']==method and (scope=='all' or (r['variant']=='identity')==(scope=='identity'))]
            aggregates.append(dict(method=method,scope=scope,pairs=len(values),
                mean_ciede2000=float(np.mean([r['ciede2000_source_mask'] for r in values])),
                mean_rgb_mae=float(np.mean([r['rgb_mae_source_mask'] for r in values])),
                changed_pairs=sum(r['changed_input_pixels']>0 for r in values),
                parameter_mae_direct_coordinates=np.abs(np.array([r['paper_parameters'] for r in values])-np.array([r['target_paper_parameters'] for r in values])).mean(axis=0).tolist()))
    def metric(method,scope):return next(r for r in aggregates if r['method']==method and r['scope']==scope)
    gates={m:dict(overall_improves=metric(m,'all')['mean_ciede2000']<metric('no_correction','all')['mean_ciede2000'],
        clean_unchanged=metric(m,'identity')['changed_pairs']==0) for m in ['legacy_refit','paper_gamma_refit']}
    for gate in gates.values():gate['passed']=gate['overall_improves'] and gate['clean_unchanged']
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items()) and contract(ROOT)[1]==identity
    write('predictions.json',records);write('summary.json',dict(status='complete_no_automatic_promotion',sources=15,pairs=30,
        regression_fits=30,held_predictions=len(records),aggregates=aggregates,gates=gates,active_demo_changed=False,
        final_validation_test_access=False,newer_mask_candidates_admitted=False))
    print(json.dumps(dict(aggregates=aggregates,gates=gates),indent=2))


if __name__=='__main__':main()
