"""One authorized real photographic tree diagnostic on fixed borrowed support."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.contextual_mst_experiment import FEATURES,_ridge,predict
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.correction.continuous_mst_candidate import continuous_model_features,CONTINUOUS_FEATURES
from src.model_training.photographic_target_diagnostic import case_matrix,distort,metrics
from src.model_training.blended_recovery_targets import fit_target,render_rgb8
from src.model_training.target_scaled_tree import fit_target_scaled_tree
from src.model_training.portable_tree import PortableTree
PARENT=ROOT/'outputs/stellenbosch_new_subjects_v1'
OUT=ROOT/'outputs/nested_correction_diagnostic_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
write=lambda p,v:p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')


def statistics(image,mask):
    s=compute_masked_lab_statistics(cv2.cvtColor(image,cv2.COLOR_RGB2BGR),mask)
    return s,dict(zip(FEATURES,[s['ita_degrees'],s['mean_l_star'],s['mean_a_star'],s['mean_b_star']])) if s['valid'] else None


def save_rgb(path,rgb):
    assert cv2.imwrite(str(path),cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR))


def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound={str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()}
    for rel in ['scripts/480_run_nested_correction_diagnostic.py','docs/exploratory-correction-tree-protocol-2026-11-06.md',
        'src/ita_estimation/contextual_mst_experiment.py','src/correction/continuous_mst_candidate.py',
        'src/model_training/target_scaled_tree.py','src/model_training/portable_tree.py',
        'src/model_training/photographic_target_diagnostic.py','src/model_training/blended_recovery_targets.py',
        'src/distortion_generation/core_colour_recipe.py','src/distortion_generation/development_roles.py',
        'src/distortion_generation/directional_exposure_recipe.py','src/ita_estimation/compute_ita.py']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(Path(p))==h for p,h in bound.items())
    originals=read(PARENT/'results_PRIVATE.json')['records'];cases=case_matrix()
    OUT.mkdir(parents=True)
    contract=hashlib.sha256(json.dumps(dict(version='conditional_fixed_measurement_region_rgb_v1',parent_contract=sha(PARENT/'contract_PRIVATE.json'),
        borrowed_source_mask=True,measurement='originalRGBonborrowedmask',application='hard_saved_measurement_mask',features=list(CONTINUOUS_FEATURES)),sort_keys=True).encode()).hexdigest()
    write(OUT/'plan_PRIVATE.json',dict(input_sha256=bound,contract_sha256=contract,source_cases=[r['case_id'] for r in originals],
        distortion_cases=cases,attempts=420,calibration_admitted=False,training_admitted=False,scope='conditional_fixed_measured_region_NOTwholeface_or_inputderivedmask'))
    rows=[];clean=[];target_fits=0;neutral=0
    for original in originals:
        sid=original['case_id'];folder=OUT/sid;folder.mkdir()
        if original['status']!='success':
            for case in cases:rows.append(dict(case_id=sid+'__'+case['id'],source_case=sid,subject_id=original['subject_key'],
                condition=original['condition'],case=case,status='unavailable_original',reason=original['reason'],features=None,target=None))
            print(sid+' retained original failure',flush=True);continue
        reference=cv2.cvtColor(cv2.imread(str(PARENT/sid/'input.png')),cv2.COLOR_BGR2RGB)
        mask=cv2.imread(str(PARENT/sid/'measurement_mask.png'),0);alpha=(mask>0).astype(float);scoring=alpha>0
        save_rgb(folder/'reference.png',reference);cv2.imwrite(str(folder/'mask.png'),mask)
        _,f=statistics(reference,mask)
        assert f is not None
        assert all(f[k]==original['measurement_report']['features'][k] for k in FEATURES)
        clean.append(dict(case_id=sid,subject_id=original['subject_key'],source_mst_exact_decimal=original['source_mst_exact_decimal'],features=f))
        for case in cases:
            target=folder/case['id'];target.mkdir()
            image,recipe,role=distort(reference,alpha,case);save_rgb(target/'input.png',image)
            stats,features=statistics(image,mask)
            fitted=fit_target(image,reference,alpha,scoring)
            if case['id']=='clean':neutral+=1
            else:target_fits+=1
            parameters=fitted.get('parameters');oracle=render_rgb8(image,alpha,parameters) if parameters is not None else image.copy()
            save_rgb(target/'oracle.png',oracle)
            assert np.array_equal(image[~scoring],reference[~scoring]) and np.array_equal(oracle[~scoring],image[~scoring])
            rows.append(dict(case_id=sid+'__'+case['id'],source_case=sid,subject_id=original['subject_key'],condition=original['condition'],
                case=case,status='available' if features is not None else 'unavailable_features',reason=None if features is not None else stats['reason'],
                features=features,statistics=stats,recipe=recipe,role=role,target=parameters,target_report=fitted,
                input_metrics=metrics(image,reference,scoring),oracle_metrics=metrics(oracle,reference,scoring)))
        print(sid+' targets prepared',flush=True)
    write(OUT/'prepared_rows_PRIVATE.json',rows)
    models={}
    def mapping(excluded):
        key='|'.join(sorted(excluded))
        if key not in models:
            training=[r for r in clean if r['subject_id'] not in excluded]
            assert len({r['subject_id'] for r in training})>=2
            models[key]=dict(excluded_keys=sorted(excluded),training_cases=[r['case_id'] for r in training],
                training_keys=sorted({r['subject_id'] for r in training}),model=_ridge(training,FEATURES))
        return key,models[key]['model']
    def full_features(row,model):
        p=predict(model,row['features'])
        f=continuous_model_features(row['features'],p,measurement_contract_sha256=contract,estimator_measurement_contract_sha256=contract)
        return [f[k] for k in CONTINUOUS_FEATURES],p
    folds=[];predictions=[];boards=[]
    for held in sorted({r['subject_id'] for r in rows}):
        outer_id,outer=mapping({held});training=[];x=[];y=[];trace=[]
        for r in rows:
            if r['subject_id']==held or r['features'] is None or r['target'] is None:continue
            inner_id,inner=mapping({held,r['subject_id']});vector,p=full_features(r,inner)
            training.append(r['case_id']);x.append(vector);y.append(r['target']);trace.append(dict(case_id=r['case_id'],mapping_id=inner_id,features=vector,mst_prediction=p))
        payload,normalized,meta=fit_target_scaled_tree(x,y,CONTINUOUS_FEATURES,dict(exploratory=True,held_key=held,contract_sha256=contract))
        tree=PortableTree(payload)
        np.testing.assert_allclose(tree.predict(x),normalized.predict(x)*meta['applied_scale']+meta['fitting_target_mean'],atol=1e-12,rtol=0)
        fold=dict(held_key=held,outer_mapping_id=outer_id,training_cases=training,training_feature_trace=trace,tree=payload,normalization=meta,
            held_cases=[r['case_id'] for r in rows if r['subject_id']==held]);folds.append(fold)
        for r in rows:
            if r['subject_id']!=held:continue
            if r['status']=='unavailable_original':
                predictions.append(dict(case_id=r['case_id'],subject_id=held,layer=r['case']['layer'],status='unavailable_original',reason=r['reason']));continue
            folder=OUT/r['source_case'];image=cv2.cvtColor(cv2.imread(str(folder/r['case']['id']/'input.png')),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0;alpha=mask.astype(float)
            parameters=None;vector=None;p=None
            if r['features'] is not None:
                vector,p=full_features(r,outer);parameters=tree.predict_one(vector)
            output=render_rgb8(image,alpha,parameters) if parameters is not None else image.copy()
            assert np.array_equal(output[~mask],image[~mask])
            save_rgb(folder/r['case']['id']/'prediction.png',output)
            pred=dict(case_id=r['case_id'],subject_id=held,layer=r['case']['layer'],status='predicted' if parameters is not None else 'unchanged_feature_failure',
                parameters=parameters,features=vector,mst_prediction=p,input_metrics=r['input_metrics'],oracle_metrics=r['oracle_metrics'],
                predicted_metrics=metrics(output,reference,mask),changed_channel_samples=int(np.count_nonzero(output!=image)))
            predictions.append(pred)
            if r['case']['id'] in ['combined_cool_under','stress_combined_under']:
                oracle=cv2.cvtColor(cv2.imread(str(folder/r['case']['id']/'oracle.png')),cv2.COLOR_BGR2RGB)
                board=np.concatenate([cv2.resize(im,(160,160)) for im in [reference,image,output,oracle]],axis=1)
                label=np.full((28,640,3),255,np.uint8);cv2.putText(label,r['case_id']+' ref/input/tree/oracle',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
                boards.append((r['case_id'],np.concatenate([label,cv2.cvtColor(board,cv2.COLOR_RGB2BGR)])))
        print('held fold '+held+' complete',flush=True)
    summary={}
    for layer in ['clean','core','composite_stress_design']:
        allrows=[r for r in predictions if r['layer']==layer];scored=[r for r in allrows if 'predicted_metrics' in r]
        values=dict(attempts=len(allrows),scored=len(scored),predictions=sum(r['status']=='predicted' for r in allrows),
            unavailable_without_scoring_support=len(allrows)-len(scored),regressed_rgb=sum(r['predicted_metrics']['rgb8_mae_codes']>r['input_metrics']['rgb8_mae_codes'] for r in scored),
            changed_clean_cases=sum(r['changed_channel_samples']>0 for r in scored) if layer=='clean' else None)
        for method in ['input','predicted','oracle']:
            for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
                values[method+'_'+metric]=float(np.mean([r[method+'_metrics'][metric] for r in scored]))
                bykey={key:np.mean([r[method+'_metrics'][metric] for r in scored if r['subject_id']==key]) for key in {r['subject_id'] for r in scored}}
                values['equal_key_'+method+'_'+metric]=float(np.mean(list(bykey.values())))
        summary[layer]=values
    result=dict(scope='conditional_fixed_measured_support',summary=summary,records=predictions,folds=folds,mapping_models=models,
        mapping_ridge_fits=len(models),correction_tree_fits=len(folds),nonclean_target_fit_calls=target_fits,neutral_target_shortcuts=neutral,
        calibration_admitted=False,training_admitted=False,production_adopted=False,scientific_validation=False)
    write(OUT/'results_PRIVATE.json',result)
    for key,board in boards:cv2.imwrite(str(OUT/(key+'_board.png')),board)
    for offset in range(0,len(boards),10):cv2.imwrite(str(OUT/f'contact_{offset//10+1:02d}_PRIVATE.png'),np.concatenate([b for _,b in boards[offset:offset+10]]))
    assert len(rows)==420 and len(predictions)==420 and all(sha(Path(p))==h for p,h in bound.items())
    write(OUT/'sha256.json',{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps(dict(summary=summary,mapping_fits=len(models),tree_fits=len(folds),target_fits=target_fits),indent=2),flush=True)


if __name__=='__main__':main()
