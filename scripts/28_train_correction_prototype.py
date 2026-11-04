"""Fit one fixed small tree and evaluate three development-validation pairs.

Not final thesis training/evaluation. No hyperparameter search or validation
fitting. Stress cases and prior failed attempts remain separately accounted.
"""
import importlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from sklearn.tree import export_text
from src.utilities.config import get_config
from src.model_training.train_model import train,save_model,load_model
from src.evaluation.evaluate_model import compute_mae,measure_inference_time
from src.evaluation.correction_prototype import model_arrays,apply_correction,image_errors
from src.data_preparation.controlled_training_table import FEATURES,TARGETS,FEATURE_KEYS


def main():
    common=importlib.import_module('16_compare_face_outline')
    prepare=importlib.import_module('11_prepare_training_manifests')
    csv_helper=importlib.import_module('21_synthetic_pair_pilot')
    checks=importlib.import_module('15_prepare_fairface_mask_review')
    config=get_config()
    tables=ROOT/'data/manifests/controlled_training_v1'
    train_path=tables/'train.csv';val_path=tables/'development_validation.csv';stress_path=tables/'clipped_stress.csv'
    training=common.read(train_path);validation=common.read(val_path);stress=common.read(stress_path)
    failures=common.read(tables/'excluded_pairs.csv')
    if len(training)!=16 or len(validation)!=3:
        raise ValueError('Expected the recorded 16/3 controlled table')
    if any(r['table_use']!='train' or int(r['clipped_pixel_count']) for r in training):
        raise ValueError('Training contains held-out or clipped data')
    if any(r['table_use']!='development_validation' or int(r['clipped_pixel_count']) for r in validation):
        raise ValueError('Validation table has invalid routing')
    for key in ('mask_version','transform_version','policy_version'):
        if len({r[key] for r in training+validation+stress})!=1:
            raise ValueError('Mixed pipeline versions: '+key)
    for key in ('source_image_id','duplicate_group_id'):
        if {r[key] for r in training}&{r[key] for r in validation}:
            raise ValueError('Train/validation source or duplicate-group overlap')
    output=ROOT/config.OUTPUTS_ROOT/'correction_prototype_v1'
    models=ROOT/config.MODELS_ROOT/'correction_prototype_v1'
    if output.exists() or models.exists():
        raise FileExistsError('Prototype exists; refusing overwrite')
    yunet,landmarker=ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH
    paths=[train_path,val_path,stress_path,tables/'excluded_pairs.csv',tables/'schema_and_summary.json',
        yunet,landmarker,Path(__file__),ROOT/'src/model_training/train_model.py',
        ROOT/'src/evaluation/correction_prototype.py',ROOT/'src/distortion_generation/generate_distortions.py',
        ROOT/'scripts/11_prepare_training_manifests.py']
    for r in training+validation+stress:
        paths.extend([ROOT/r['input_path'],Path(r['source_path']),ROOT/r['generation_mask_path']])
    fingerprints={str(p):checks.digest(p) for p in paths}
    x_train,y_train=model_arrays(training)
    # Fixed before inspecting validation errors; no tuning on the one held-out source.
    model,training_metrics=train(x_train,y_train,max_depth=3)
    mean_parameters=y_train.mean(axis=0)
    output.mkdir();models.mkdir()
    model_path=models/'decision_tree.joblib'
    save_model(model,str(model_path))
    restored=load_model(str(model_path))
    np.testing.assert_allclose(restored.predict(x_train),model.predict(x_train),rtol=0,atol=0)
    (output/'tree_rules.txt').write_text(export_text(model,feature_names=list(FEATURES)),encoding='utf-8')
    prediction_rows=[];metric_rows=[];rerun_failures=[];primary_x,_=model_arrays(validation)
    prediction_ms=measure_inference_time(model.predict,primary_x[:1],n_runs=100)
    for row in validation+stress:
        split='development_validation' if row['table_use']=='development_validation' else 'clipped_stress_not_independent'
        x,y=model_arrays([row]);predicted=model.predict(x)[0]
        params={'no_correction':np.ones(3),'training_mean_parameters':mean_parameters,'decision_tree':predicted,
                'known_parameters_input_mask':y[0],'known_parameters_source_mask_oracle':y[0]}
        for method,p in params.items():
            prediction_rows.append(dict(pair_id=row['pair_id'],source_image_id=row['source_image_id'],
                evaluation_split=split,method=method,is_oracle=method.startswith('known_parameters'),
                **{k:float(v) for k,v in zip(('gamma','red_gain','blue_gain'),p)},
                **{k:float(v) for k,v in zip(('mae_gamma','mae_red_gain','mae_blue_gain'),np.abs(p-y[0]))}))
        try:
            input_bgr=cv2.imread(str(ROOT/row['input_path']))
            reference_bgr=cv2.imread(row['source_path'])
            source_mask=cv2.imread(str(ROOT/row['generation_mask_path']),cv2.IMREAD_GRAYSCALE)
            if input_bgr is None or reference_bgr is None or source_mask is None:
                raise ValueError('Missing evaluation image/mask')
            reference_rgb=cv2.cvtColor(reference_bgr,cv2.COLOR_BGR2RGB)
            input_rgb=cv2.cvtColor(input_bgr,cv2.COLOR_BGR2RGB)
            scoring_mask=source_mask>0
            started=time.perf_counter()
            boxes=prepare._detect_face_boxes(input_bgr,yunet,.85)
            if len(boxes)!=1:
                raise ValueError('Evaluation input not single-face')
            bx,by,bw,bh=boxes[0];crop=input_bgr[by:by+bh,bx:bx+bw].copy()
            masked=prepare.compute_versioned_skin_mask(crop,input_bgr,boxes[0],landmarker,row['mask_version'])
            stats=prepare.compute_masked_lab_statistics(crop,masked.mask,1000)
            if not masked.landmarks_available or not stats['valid']:
                raise ValueError('Evaluation input no longer has valid versioned features')
            actual=np.asarray([stats[k] for k in FEATURE_KEYS])
            if not np.allclose(actual,x[0],atol=.00005,rtol=0):
                raise ValueError('Recomputed input feature vector differs from table')
            # Prediction is repeated on the recomputed inference features, not reference values.
            params['decision_tree']=model.predict(actual[None,:])[0]
            input_mask=np.zeros(input_bgr.shape[:2],bool);input_mask[by:by+bh,bx:bx+bw]=masked.mask>0
            feature_ms=(time.perf_counter()-started)*1000
            common_pixels=int((scoring_mask&input_mask).sum());source_pixels=int(scoring_mask.sum())
            grid_images=[reference_bgr,input_bgr]
            labels=['Reference','No correction']
            for method,p in params.items():
                started=time.perf_counter()
                if method=='no_correction':
                    corrected=input_rgb.copy();application='none'
                else:
                    application='source_mask_oracle' if method=='known_parameters_source_mask_oracle' else 'distorted_input_mask'
                    corrected=apply_correction(input_rgb,scoring_mask if application=='source_mask_oracle' else input_mask,p)
                transform_ms=(time.perf_counter()-started)*1000
                destination=output/(row['pair_id']+'__'+method+'.png')
                csv_helper.write_rgb(destination,corrected)
                scores=image_errors(reference_rgb,corrected,scoring_mask)
                metric_rows.append(dict(pair_id=row['pair_id'],source_image_id=row['source_image_id'],
                    evaluation_split=split,method=method,is_oracle=method.startswith('known_parameters'),
                    correction_mask=application,scoring_region='fixed_source_generation_mask',
                    **scores,input_mask_source_region_coverage=common_pixels/source_pixels,
                    input_feature_and_prediction_ms=feature_ms,correction_transform_ms=transform_ms,
                    corrected_path=destination.relative_to(ROOT).as_posix()))
                if method!='no_correction':
                    grid_images.append(cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR));labels.append(method)
            panels=[]
            for im,label in zip(grid_images,labels):
                im=cv2.resize(im,(224,224));cv2.rectangle(im,(0,0),(224,25),(0,0,0),-1)
                cv2.putText(im,label,(3,16),cv2.FONT_HERSHEY_SIMPLEX,.33,(0,255,255),1);panels.append(im)
            # Two rows: reference/input/constant, tree/known-input-mask/known-source-mask.
            if not cv2.imwrite(str(output/(row['pair_id']+'__comparison.png')),
                               np.vstack([np.hstack(panels[:3]),np.hstack(panels[3:])])):
                raise OSError('Comparison write failed')
        except Exception as error:
            rerun_failures.append(dict(pair_id=row['pair_id'],evaluation_split=split,error=str(error)))
    csv_helper.write_csv(output/'parameter_predictions.csv',prediction_rows)
    if metric_rows:csv_helper.write_csv(output/'image_metrics.csv',metric_rows)
    with (output/'evaluation_failures.csv').open('x',encoding='utf-8',newline='') as stream:
        import csv
        writer=csv.DictWriter(stream,['pair_id','evaluation_split','error']);writer.writeheader();writer.writerows(rerun_failures)
    aggregate=[]
    for split in sorted({r['evaluation_split'] for r in metric_rows}):
        for method in params:
            subset=[r for r in metric_rows if r['evaluation_split']==split and r['method']==method]
            if subset:
                aggregate.append(dict(evaluation_split=split,method=method,pairs=len(subset),
                    source_count=len({r['source_image_id'] for r in subset}),
                    mean_rgb_mae=float(np.mean([r['rgb_mae_source_mask'] for r in subset])),
                    mean_ciede2000=float(np.mean([r['ciede2000_source_mask'] for r in subset]))))
    parameter_aggregate=[]
    for method,predictor in [('no_correction',lambda x:np.ones((len(x),3))),
                              ('training_mean_parameters',lambda x:np.tile(mean_parameters,(len(x),1))),
                              ('decision_tree',model.predict)]:
        _,val_targets=model_arrays(validation)
        error=compute_mae(val_targets,predictor(primary_x))
        parameter_aggregate.append(dict(method=method,**dict(zip(('gamma_mae','red_gain_mae','blue_gain_mae'),map(float,error)))))
    if any(checks.digest(Path(p))!=v for p,v in fingerprints.items()):
        raise RuntimeError('Build inputs/code changed during training/evaluation')
    summary=dict(training_pairs=len(training),training_sources=len({r['source_image_id'] for r in training}),
        development_validation_pairs=len(validation),development_validation_sources=len({r['source_image_id'] for r in validation}),
        preexisting_failed_pairs=len(failures),clipped_stress_pairs=len(stress),rerun_failures=len(rerun_failures),
        tree=dict(max_depth=3,random_state=42,fitted_depth=int(model.get_depth()),leaves=int(model.get_n_leaves()),tuned_on_validation=False),
        feature_columns=list(FEATURES),target_columns=list(TARGETS),training_mae={k:float(v) for k,v in training_metrics.items()},
        validation_parameter_mae=parameter_aggregate,image_results=aggregate,
        tree_prediction_only_ms=prediction_ms,training_mean_parameters=mean_parameters.tolist(),
        model_path=model_path.relative_to(ROOT).as_posix(),model_sha256=checks.digest(model_path),input_sha256=fingerprints,
        mask_version=training[0]['mask_version'],transform_version=training[0]['transform_version'],policy_version=training[0]['policy_version'],
        warning='Implementation check on one validation source and three fixed variant settings, not final thesis evaluation. Oracles use known targets and are not learned performance.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (models/'metadata.json').write_text(json.dumps({k:summary[k] for k in ('feature_columns','target_columns','tree','model_sha256','mask_version','transform_version','policy_version','warning')},indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':
    main()
