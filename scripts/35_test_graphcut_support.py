"""Test fixed GrabCut initialization against frozen labels and prior mask runs."""
import csv
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.evaluation.correction_prototype import apply_correction,image_errors,model_arrays
from src.evaluation.material_point_review import validate_labels,score_points
from src.data_preparation.controlled_training_table import FEATURE_KEYS
from src.model_training.train_model import load_model
from src.distortion_generation.generate_distortions import transform_rgb
from src.skin_masking.material_checked_support import material_checked_support
from src.skin_masking.graphcut_correction_support import graphcut_correction_support


def main():
    helper=importlib.import_module('29_compare_correction_boundaries')
    prepare=importlib.import_module('11_prepare_training_manifests')
    draw=importlib.import_module('31_guard_correction_support').sheet
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-name',default='graphcut_support_v1')
    args=parser.parse_args()
    if not args.output_name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.output_name):
        raise ValueError('Output name must be a simple directory name')
    config=get_config();base=ROOT/config.OUTPUTS_ROOT;out=base/args.output_name
    if out.exists(): raise FileExistsError('Existing graph-cut run; refusing overwrite')
    table=ROOT/'data/manifests/controlled_training_v1'
    review=ROOT/'data/manifests/material_review_v1'
    manifest_path=review/'review_manifest.json';labels_path=review/'material_review_labels.json'
    manifest=json.loads(manifest_path.read_text());payload=json.loads(labels_path.read_text())
    manifest_sha=helper.digest(manifest_path);labels=validate_labels(manifest,payload,manifest_sha)
    previous_predictions=json.loads((review/'prediction_observations.json').read_text())
    assert previous_predictions['manifest_sha256']==manifest_sha
    points_by_source={r['image_id']:[p for p in manifest['points'] if p['image_id']==r['image_id']] for r in manifest['sources']}
    sources_path=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    sources=[r for r in helper.read(sources_path) if r['original_visual_decision']=='accept' or r['image_id']=='fairface__train/29962.jpg']
    assert len(sources)==46 and not any(r['partition']=='reserved_test' for r in sources)
    pairs=helper.read(table/'development_validation.csv')+helper.read(table/'clipped_stress.csv')
    model_path=ROOT/config.MODELS_ROOT/'correction_prototype_v1/decision_tree.joblib'
    assert helper.digest(model_path)==json.loads((model_path.parent/'metadata.json').read_text())['model_sha256']
    model=load_model(str(model_path))
    paths=[Path(__file__),ROOT/'src/skin_masking/graphcut_correction_support.py',
        ROOT/'src/skin_masking/material_checked_support.py',ROOT/'src/skin_masking/guarded_correction_support.py',
        ROOT/'src/skin_masking/correction_support_experiment.py',ROOT/'src/evaluation/material_point_review.py',
        ROOT/'scripts/11_prepare_training_manifests.py',ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,
        model_path,manifest_path,labels_path,review/'prediction_observations.json',sources_path,
        table/'development_validation.csv',table/'clipped_stress.csv',
        base/'material_checked_support_v1/broader_mask_diagnostics.csv']
    for r in sources: paths.append(Path(r['image_path']))
    for r in pairs: paths += [ROOT/r['input_path'],Path(r['source_path']),ROOT/r['generation_mask_path'],
                              base/'material_checked_support_v1/pairs'/(r['pair_id']+'__material_checked.png')]
    hashes={str(p):helper.digest(p) for p in paths}
    out.mkdir();(out/'pairs').mkdir();(out/'broader').mkdir()
    pair_metrics=[];broader=[];failures=[];new_observations=[]

    def infer(bgr):
        boxes=prepare._detect_face_boxes(bgr,ROOT/config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1: raise ValueError('Expected one face')
        x,y,w,h=boxes[0];crop=bgr[y:y+h,x:x+w].copy()
        result=prepare.compute_versioned_skin_mask(crop,bgr,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
        if not result.landmarks_available: raise ValueError('Landmarks unavailable')
        original=result.mask>0;excluded=result.exclusion_mask>0
        material=material_checked_support(crop,original,excluded)
        started=time.perf_counter();graph=graphcut_correction_support(crop,original,excluded)
        graph_ms=(time.perf_counter()-started)*1000
        assert not graph[~material].any() and not graph[excluded].any()
        full=[]
        for local in (original,material,graph):
            frame=np.zeros(bgr.shape[:2],bool);frame[y:y+h,x:x+w]=local;full.append(frame)
        return full,crop,result,graph_ms

    for row in pairs:
        try:
            pair=row['pair_id'];bgr=cv2.imread(str(ROOT/row['input_path']));rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(row['source_path']),cv2.COLOR_BGR2RGB)
            source=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
            masks,crop,result,ms=infer(bgr)
            stats=prepare.compute_masked_lab_statistics(crop,result.mask,1000)
            if not stats['valid']: raise ValueError('Invalid original features')
            features,_=model_arrays([row]);np.testing.assert_allclose([stats[k] for k in FEATURE_KEYS],features[0],atol=.00005,rtol=0)
            parameters=model.predict(features)[0];corrected=[]
            for method,mask in zip(('original','material_checked','graphcut'),masks):
                image=apply_correction(rgb,mask,parameters);corrected.append(image)
                np.testing.assert_array_equal(image[~mask],rgb[~mask])
                if method=='material_checked': np.testing.assert_array_equal(image,cv2.cvtColor(cv2.imread(str(base/'material_checked_support_v1/pairs'/(pair+'__material_checked.png'))),cv2.COLOR_BGR2RGB))
                pair_metrics.append(dict(pair_id=pair,split=row['table_use'],method=method,**image_errors(reference,image,source),
                    coverage=float((mask&source).sum()/source.sum()),extra_pixels=int((mask&~source).sum()),graphcut_step_ms=ms))
                cv2.imwrite(str(out/'pairs'/(pair+'__'+method+'.png')),cv2.cvtColor(image,cv2.COLOR_RGB2BGR))
                cv2.imwrite(str(out/'pairs'/(pair+'__'+method+'_mask.png')),mask.astype(np.uint8)*255)
            removed=rgb.copy();removed[masks[1]&~masks[2]]=[255,70,0]
            draw(out/'pairs'/(pair+'__comparison.png'),[reference,rgb,removed]+corrected,
                 ['Reference','Input','Orange: graph-cut removals','Original','Color-checked fill','Graph-cut refinement'])
        except Exception as error: failures.append(dict(stage='pairs',image_id=row['pair_id'],error=str(error)))

    def record_unavailable(image_id,variant,error):
        failures.append(dict(stage='broader_'+variant,image_id=image_id,error=error))
        for point in points_by_source.get(image_id,[]):
            new_observations.append(dict(point_id=point['point_id'],variant=variant,method='graphcut',selected=None,error=error))

    for row in sources:
        image_id=row['image_id'];clean_bgr=cv2.imread(row['image_path'])
        try:
            # This generation support never enters shifted-input inference.
            boxes=prepare._detect_face_boxes(clean_bgr,ROOT/config.FACE_MODEL_PATH,.85)
            if len(boxes)!=1: raise ValueError('Expected one clean source face')
            x,y,w,h=boxes[0];clean_crop=clean_bgr[y:y+h,x:x+w].copy()
            result=prepare.compute_versioned_skin_mask(clean_crop,clean_bgr,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
            if not result.landmarks_available: raise ValueError('Clean source landmarks unavailable')
            source=np.zeros(clean_bgr.shape[:2],bool);source[y:y+h,x:x+w]=result.mask>0
            rgb=cv2.cvtColor(clean_bgr,cv2.COLOR_BGR2RGB);shift=rgb.copy()
            shift[source]=np.rint(transform_rgb(rgb.astype(float)/255,1.,.85,1.15)[source]*255).astype(np.uint8)
        except Exception as error:
            for variant in ('clean','color_shift'): record_unavailable(image_id,variant,'Source preparation: '+str(error))
            continue
        for variant,input_rgb in [('clean',rgb),('color_shift',shift)]:
            try:
                masks,_,_,ms=infer(cv2.cvtColor(input_rgb,cv2.COLOR_RGB2BGR))
                record=dict(image_id=image_id,variant=variant,graphcut_step_ms=ms)
                panels=[input_rgb]
                for method,mask in zip(('original','material_checked','graphcut'),masks):
                    record[method+'_coverage']=float((mask&source).sum()/source.sum())
                    record[method+'_extra_pixels']=int((mask&~source).sum())
                    overlay=input_rgb.copy();overlay[mask]=np.rint(.5*input_rgb[mask]+.5*np.array([0,200,0])).astype(np.uint8);panels.append(overlay)
                broader.append(record)
                draw(out/'broader'/(image_id.replace('/','_')+'__'+variant+'.png'),panels,
                     [image_id+' '+variant,'Original support','Color-checked support','Graph-cut support'],columns=2)
                for point in points_by_source.get(image_id,[]):
                    for old_method,mask in zip(('original','material_checked'),masks[:2]):
                        old=next(r for r in previous_predictions['observations'] if r['point_id']==point['point_id'] and r['variant']==variant and r['method']==old_method)
                        assert old['selected']==bool(mask[point['y'],point['x']])
                    new_observations.append(dict(point_id=point['point_id'],variant=variant,method='graphcut',selected=bool(masks[2][point['y'],point['x']]),error=None))
            except Exception as error: record_unavailable(image_id,variant,str(error))
        if len(broader)%20==0: print('Broader inputs completed:',len(broader),flush=True)
    assert len(new_observations)==48 and len({(r['point_id'],r['variant']) for r in new_observations})==48
    for filename,records,fields in [('pair_metrics.csv',pair_metrics,list(pair_metrics[0]) if pair_metrics else ['pair_id']),
                                   ('broader_mask_diagnostics.csv',broader,list(broader[0]) if broader else ['image_id']),
                                   ('failures.csv',failures,['stage','image_id','error'])]:
        with (out/filename).open('x',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(records)
    point_result=dict(manifest_sha256=manifest_sha,labels_sha256=helper.digest(labels_path),
        results=score_points(previous_predictions['observations']+new_observations,labels),new_observations=new_observations,
        warning='Frozen known development labels used for regression, not independent validation or image-area accuracy.')
    (out/'point_results.json').write_text(json.dumps(point_result,indent=2),encoding='utf-8')
    aggregate=[]
    for split in sorted({r['split'] for r in pair_metrics}):
        for method in ('original','material_checked','graphcut'):
            selected=[r for r in pair_metrics if r['split']==split and r['method']==method]
            aggregate.append(dict(split=split,method=method,pairs=len(selected),**{k:float(np.mean([r[k] for r in selected])) for k in ('ciede2000_source_mask','coverage','extra_pixels','rgb_mae_outside_source_mask')}))
    assert all(helper.digest(Path(p))==value for p,value in hashes.items())
    summary=dict(pair_attempts=len(pairs),broader_attempts=92,broader_successes=len(broader),failures=failures,
        pair_results=aggregate,input_sha256=hashes,
        rule='Five GrabCut iterations; fixed central ellipse foreground, excluded features and one-pixel border background. Output subset of material-checked support. RNG42 serial.',
        warning='Correction-mask experiment only. No estimation/model changes or default adoption. Foreground/background seeds may be wrong; no semantic skin classifier or final thesis result.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__': main()
