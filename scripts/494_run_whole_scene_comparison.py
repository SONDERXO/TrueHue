"""Whole-scene photometric distortion with a matched facial/scene feature comparison."""
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
from src.model_training.whole_scene_features import scene_features,SCENE_FEATURES
PARENT=ROOT/'outputs/stellenbosch_new_subjects_v1'
OUT=ROOT/'outputs/whole_scene_correction_v1'
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
    for rel in ['scripts/494_run_whole_scene_comparison.py','docs/whole-scene-correction-protocol-2026-11-06.md',
        'src/ita_estimation/contextual_mst_experiment.py','src/correction/continuous_mst_candidate.py',
        'src/model_training/target_scaled_tree.py','src/model_training/portable_tree.py',
        'src/model_training/photographic_target_diagnostic.py','src/model_training/blended_recovery_targets.py',
        'src/model_training/whole_scene_features.py','src/distortion_generation/core_colour_recipe.py','src/distortion_generation/development_roles.py',
        'src/distortion_generation/directional_exposure_recipe.py','src/ita_estimation/compute_ita.py']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    originals=read(PARENT/'results_PRIVATE.json')['records'];cases=case_matrix()
    upstream=ROOT/'outputs/nested_correction_diagnostic_v1/results_PRIVATE.json'
    bound[str(upstream)]=sha(upstream)
    bound.update({r['source_path']:r['source_sha256'] for r in originals})
    assert all(sha(Path(p))==h for p,h in bound.items())
    OUT.mkdir(parents=True)
    contract=hashlib.sha256(json.dumps(dict(version='whole224scene_synthesis_frozen_crop_measurement_v1',parent_contract=sha(PARENT/'contract_PRIVATE.json'),
        borrowed_source_mask=True,measurement='originalRGBonborrowedmask',application='hard_saved_measurement_mask',features=list(CONTINUOUS_FEATURES+SCENE_FEATURES)),sort_keys=True).encode()).hexdigest()
    write(OUT/'plan_PRIVATE.json',dict(input_sha256=bound,contract_sha256=contract,source_cases=[r['case_id'] for r in originals],
        distortion_cases=cases,attempts=420,calibration_admitted=False,training_admitted=False,scope='conditional_fixed_measured_region_NOTwholeface_or_inputderivedmask'))
    rows=[];clean=[];target_fits=0;neutral=0
    for original in originals:
        sid=original['case_id'];folder=OUT/sid;folder.mkdir()
        fullreference=cv2.cvtColor(cv2.imread(original['source_path']),cv2.COLOR_BGR2RGB)
        save_rgb(folder/'scene_reference.png',fullreference)
        x0,y0,x1,y1=original['input_bridge']['native_bounds']
        if original['status']!='success':
            for case in cases:
                target=folder/case['id'];target.mkdir()
                scene,recipe,role=distort(fullreference,np.ones(fullreference.shape[:2],float),case)
                save_rgb(target/'scene_input.png',scene)
                rows.append(dict(case_id=sid+'__'+case['id'],source_case=sid,subject_id=original['subject_key'],condition=original['condition'],case=case,status='unavailable_original',reason=original['reason'],features=None,target=None,scene_features=scene_features(scene),recipe=recipe))
            print(sid+' retained original failure',flush=True);continue
        reference=cv2.cvtColor(cv2.imread(str(PARENT/sid/'input.png')),cv2.COLOR_BGR2RGB)
        assert np.array_equal(reference,cv2.resize(fullreference[y0:y1,x0:x1],(256,256),interpolation=cv2.INTER_LINEAR))
        mask=cv2.imread(str(PARENT/sid/'measurement_mask.png'),0);alpha=(mask>0).astype(float);scoring=alpha>0
        save_rgb(folder/'reference.png',reference);cv2.imwrite(str(folder/'mask.png'),mask)
        _,f=statistics(reference,mask)
        assert f is not None
        assert all(f[k]==original['measurement_report']['features'][k] for k in FEATURES)
        clean.append(dict(case_id=sid,subject_id=original['subject_key'],source_mst_exact_decimal=original['source_mst_exact_decimal'],features=f))
        for case in cases:
            target=folder/case['id'];target.mkdir()
            scene,recipe,role=distort(fullreference,np.ones(fullreference.shape[:2],float),case);save_rgb(target/'scene_input.png',scene)
            image=cv2.resize(scene[y0:y1,x0:x1],(256,256),interpolation=cv2.INTER_LINEAR);save_rgb(target/'input.png',image)
            stats,features=statistics(image,mask)
            fitted=fit_target(image,reference,alpha,scoring)
            if case['id']=='clean':neutral+=1
            else:target_fits+=1
            parameters=fitted.get('parameters');oracle=render_rgb8(image,alpha,parameters) if parameters is not None else image.copy()
            save_rgb(target/'oracle.png',oracle)
            assert np.array_equal(oracle[~scoring],image[~scoring])
            rows.append(dict(case_id=sid+'__'+case['id'],source_case=sid,subject_id=original['subject_key'],condition=original['condition'],
                case=case,status='available' if features is not None else 'unavailable_features',reason=None if features is not None else stats['reason'],
                features=features,scene_features=scene_features(scene),statistics=stats,recipe=recipe,role=role,target=parameters,target_report=fitted,
                input_metrics=metrics(image,reference,scoring),oracle_metrics=metrics(oracle,reference,scoring)))
        print(sid+' targets prepared',flush=True)
    write(OUT/'prepared_rows_PRIVATE.json',rows)
    models=read(upstream)['mapping_models'];folds=[];predictions=[]
    for held in sorted({r['subject_id'] for r in rows}):
        outer_id=held;outer=models[outer_id]
        assert held not in outer['training_keys']
        train=[];vectors=[];targets=[];trace=[]
        for r in rows:
            if r['subject_id']==held or r['features'] is None or r['target'] is None:continue
            mid='|'.join(sorted({held,r['subject_id']}));m=models[mid]
            assert not {held,r['subject_id']}&set(m['training_keys'])
            mst=predict(m['model'],r['features']);features=dict(r['features'],input_mst_score=mst['score'])
            vector=[features[k] for k in CONTINUOUS_FEATURES];vectors.append(vector);targets.append(r['target']);train.append(r['case_id'])
            trace.append(dict(case_id=r['case_id'],mapping_id=mid,features=vector,mst_prediction=mst))
        paired={}
        for method in ['face_only','face_plus_scene']:
            names=CONTINUOUS_FEATURES if method=='face_only' else CONTINUOUS_FEATURES+SCENE_FEATURES
            x=[vector+([rows_by_id['scene_features'][k] for k in SCENE_FEATURES] if method=='face_plus_scene' else [])
                for vector,rows_by_id in zip(vectors,[next(r for r in rows if r['case_id']==key) for key in train])]
            payload,model,meta=fit_target_scaled_tree(x,targets,names,dict(held_key=held,method=method,whole_scene_synthesis=True))
            tree=PortableTree(payload)
            np.testing.assert_allclose(tree.predict(x),model.predict(x)*meta['applied_scale']+meta['fitting_target_mean'],atol=1e-12,rtol=0)
            paired[method]=dict(tree=payload,normalization=meta)
        folds.append(dict(held_key=held,training_cases=train,training_feature_trace=trace,models=paired,
            held_cases=[r['case_id'] for r in rows if r['subject_id']==held]))
        for r in rows:
            if r['subject_id']!=held:continue
            if r['status']=='unavailable_original':
                predictions.append(dict(case_id=r['case_id'],source_case=r['source_case'],subject_id=held,layer=r['case']['layer'],status=r['status'],methods=None));continue
            folder=OUT/r['source_case'];pair=folder/r['case']['id'];image=cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
            mst=predict(outer['model'],r['features']) if r['features'] is not None else None
            vector=[dict(r['features'],input_mst_score=mst['score'])[k] for k in CONTINUOUS_FEATURES] if mst else None
            record=dict(case_id=r['case_id'],source_case=r['source_case'],subject_id=held,layer=r['case']['layer'],status=r['status'],mst_prediction=mst,
                input_metrics=r['input_metrics'],oracle_metrics=r['oracle_metrics'],methods={})
            for method,art in paired.items():
                fullvector=vector+([r['scene_features'][k] for k in SCENE_FEATURES] if method=='face_plus_scene' else []) if vector is not None else None
                parameters=PortableTree(art['tree']).predict_one(fullvector) if fullvector is not None else None
                output=render_rgb8(image,mask.astype(float),parameters) if parameters is not None else image.copy()
                assert np.array_equal(output[~mask],image[~mask]);save_rgb(pair/(method+'.png'),output)
                record['methods'][method]=dict(features=fullvector,parameters=parameters,metrics=metrics(output,reference,mask),changed_channels=int(np.count_nonzero(output!=image)))
            predictions.append(record)
        print('paired held fold '+held+' complete',flush=True)
    summary={}
    for layer in ['clean','core','composite_stress_design']:
        attempted=[r for r in predictions if r['layer']==layer];scored=[r for r in attempted if r['methods'] is not None]
        result=dict(attempts=len(attempted),scored=len(scored),available_features=sum(r.get('mst_prediction') is not None for r in scored))
        for method in ['face_only','face_plus_scene']:
            m=dict(harm_vs_input=sum(r['methods'][method]['metrics']['rgb8_mae_codes']>r['input_metrics']['rgb8_mae_codes'] for r in scored),
                clean_changed=sum(r['methods'][method]['changed_channels']>0 for r in scored) if layer=='clean' else None)
            for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
                m[metric]=float(np.mean([r['methods'][method]['metrics'][metric] for r in scored]))
                m['equal_key_'+metric]=float(np.mean([np.mean([r['methods'][method]['metrics'][metric] for r in scored if r['subject_id']==key]) for key in {r['subject_id'] for r in scored}]))
            result[method]=m
        result['input_mae']=float(np.mean([r['input_metrics']['rgb8_mae_codes'] for r in scored]))
        result['target_fit_or_fallback_mae']=float(np.mean([r['oracle_metrics']['rgb8_mae_codes'] for r in scored]))
        summary[layer]=result
    result=dict(summary=summary,folds=folds,records=predictions,new_correction_tree_fits=20,new_mst_fits=0,
        nonclean_target_fit_calls=target_fits,neutral_shortcuts=neutral,admissions=0,production_adopted=False)
    write(OUT/'results_PRIVATE.json',result)
    assert all(sha(Path(p))==h for p,h in bound.items())
    write(OUT/'sha256.json',{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':main()
