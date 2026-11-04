"""Two fixed semantic correction-mask candidates; no tuning or tree refit."""
import argparse
import csv
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
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter,face_skin_support,hair_veto_support,LABELS
from src.skin_masking.material_checked_support import material_checked_support
from src.evaluation.correction_prototype import apply_correction,image_errors,model_arrays
from src.evaluation.material_point_review import validate_labels,score_points
from src.data_preparation.controlled_training_table import FEATURE_KEYS
from src.distortion_generation.generate_distortions import transform_rgb
from src.model_training.train_model import load_model

METHODS=('original','material_checked','semantic_face_skin','semantic_hair_veto')
NEW_METHODS=METHODS[2:]
PALETTE=np.array([[0,0,0],[115,55,10],[255,190,130],[0,190,0],[20,90,220],[220,50,180]],np.uint8)


def main():
    helper=importlib.import_module('29_compare_correction_boundaries')
    prepare=importlib.import_module('11_prepare_training_manifests')
    draw=importlib.import_module('31_guard_correction_support').sheet
    parser=argparse.ArgumentParser();parser.add_argument('--output-name',default='semantic_support_v1');args=parser.parse_args()
    if not args.output_name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in args.output_name): raise ValueError('Invalid output name')
    config=get_config();base=ROOT/config.OUTPUTS_ROOT;out=base/args.output_name
    if out.exists(): raise FileExistsError('Output exists; refusing overwrite')
    table=ROOT/'data/manifests/controlled_training_v1';review=ROOT/'data/manifests/material_review_v1'
    manifest_path=review/'review_manifest.json';labels_path=review/'material_review_labels.json'
    manifest=json.loads(manifest_path.read_text());manifest_sha=helper.digest(manifest_path)
    labels=validate_labels(manifest,json.loads(labels_path.read_text()),manifest_sha)
    old_predictions=json.loads((review/'prediction_observations.json').read_text())
    if old_predictions['manifest_sha256']!=manifest_sha: raise ValueError('Previous observations mismatch')
    points_by_source={r['image_id']:[p for p in manifest['points'] if p['image_id']==r['image_id']] for r in manifest['sources']}
    sources_path=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    sources=[r for r in helper.read(sources_path) if r['original_visual_decision']=='accept' or r['image_id']=='fairface__train/29962.jpg']
    if len(sources)!=46 or any(r['partition']=='reserved_test' for r in sources): raise ValueError('Unexpected development cohort')
    pairs=helper.read(table/'development_validation.csv')+helper.read(table/'clipped_stress.csv')
    model_path=ROOT/config.MODELS_ROOT/'correction_prototype_v1/decision_tree.joblib'
    segment_path=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    if helper.digest(model_path)!=json.loads((model_path.parent/'metadata.json').read_text())['model_sha256']: raise ValueError('Correction model changed')
    provenance=json.loads(segment_path.with_suffix('.provenance.json').read_text())
    if helper.digest(segment_path)!=provenance['sha256']: raise ValueError('Segmentation model changed')
    model=load_model(str(model_path));segmenter=SelfieMaterialSegmenter(segment_path)
    paths=[Path(__file__),ROOT/'src/skin_masking/selfie_material_segmenter.py',ROOT/'src/skin_masking/material_checked_support.py',
        ROOT/'src/skin_masking/guarded_correction_support.py',ROOT/'src/skin_masking/correction_support_experiment.py',
        ROOT/'src/evaluation/correction_prototype.py',ROOT/'src/evaluation/material_point_review.py',ROOT/'src/utilities/config.py',
        ROOT/'src/distortion_generation/generate_distortions.py',ROOT/'scripts/11_prepare_training_manifests.py',
        ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,model_path,segment_path,
        segment_path.with_suffix('.provenance.json'),manifest_path,labels_path,review/'prediction_observations.json',sources_path,
        table/'development_validation.csv',table/'clipped_stress.csv']
    paths += [Path(r['image_path']) for r in sources]
    for r in pairs: paths += [ROOT/r['input_path'],Path(r['source_path']),ROOT/r['generation_mask_path'],base/'material_checked_support_v1/pairs'/(r['pair_id']+'__material_checked.png')]
    hashes={str(p):helper.digest(p) for p in paths}
    out.mkdir();(out/'pairs').mkdir();(out/'broader').mkdir()
    status_path=out/'run_status.json'
    def status(state,**kw): status_path.write_text(json.dumps(dict(state=state,**kw),indent=2),encoding='utf-8')
    status('running',expected_pair_inputs=len(pairs),expected_broader_inputs=92)
    metrics=[];broad=[];failures=[];observations=[];timings=[]

    def baseline(bgr):
        if bgr is None: raise ValueError('Missing input')
        boxes=prepare._detect_face_boxes(bgr,ROOT/config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1: raise ValueError('Expected one face')
        x,y,w,h=boxes[0];crop=bgr[y:y+h,x:x+w].copy()
        result=prepare.compute_versioned_skin_mask(crop,bgr,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
        if not result.landmarks_available: raise ValueError('Landmarks unavailable')
        return boxes[0],crop,result

    def infer(bgr,key,folder):
        masks={m:None for m in METHODS};errors={};category=None;crop=result=box=None
        try:
            box,crop,result=baseline(bgr);x,y,w,h=box
            original=np.zeros(bgr.shape[:2],bool);original[y:y+h,x:x+w]=result.mask>0;masks['original']=original
        except Exception as error:
            errors={m:str(error) for m in METHODS}
        if not errors:
            try:
                material=material_checked_support(crop,result.mask>0,result.exclusion_mask>0)
                full=np.zeros_like(original);full[y:y+h,x:x+w]=material;masks['material_checked']=full
            except Exception as error: errors['material_checked']=str(error);errors['semantic_hair_veto']='Material support unavailable: '+str(error)
            try:
                start=time.perf_counter();category=segmenter.categories_bgr(bgr);ms=(time.perf_counter()-start)*1000
                timings.append(dict(input_id=key,segment_ms=ms))
                masks['semantic_face_skin']=face_skin_support(category,box,result.exclusion_mask>0)
                if masks['material_checked'] is not None: masks['semantic_hair_veto']=hair_veto_support(category,masks['material_checked'])
            except Exception as error:
                for method in NEW_METHODS: masks[method]=None;errors[method]=str(error)
        for method,mask in masks.items():
            if mask is not None:
                if mask.shape!=bgr.shape[:2]: raise ValueError('Mask dimensions changed')
                if not cv2.imwrite(str(folder/(key+'__'+method+'_mask.png')),mask.astype(np.uint8)*255): raise OSError('Mask write failed')
            else: failures.append(dict(input_id=key,method=method,error=errors.get(method,'Unavailable')))
        if category is not None: cv2.imwrite(str(folder/(key+'__categories.png')),category)
        record=dict(input_id=key,available={m:mask is not None for m,mask in masks.items()},errors=errors)
        with (out/'inference_records.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
        return masks,crop,result,category

    try:
        for row in pairs:
            pair=row['pair_id'];bgr=cv2.imread(str(ROOT/row['input_path']));rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(row['source_path']),cv2.COLOR_BGR2RGB);source=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
            masks,crop,result,category=infer(bgr,pair,out/'pairs')
            if result is None:continue
            stats=prepare.compute_masked_lab_statistics(crop,result.mask,1000)
            if not stats['valid']:raise ValueError('Original pair features invalid')
            features,_=model_arrays([row]);np.testing.assert_allclose([stats[k] for k in FEATURE_KEYS],features[0],atol=.00005,rtol=0)
            params=model.predict(features)[0];corrected={}
            for method,mask in masks.items():
                if mask is None:continue
                image=apply_correction(rgb,mask,params);np.testing.assert_array_equal(image[~mask],rgb[~mask]);corrected[method]=image
                if method=='material_checked':np.testing.assert_array_equal(image,cv2.cvtColor(cv2.imread(str(base/'material_checked_support_v1/pairs'/(pair+'__material_checked.png'))),cv2.COLOR_BGR2RGB))
                metrics.append(dict(pair_id=pair,split=row['table_use'],method=method,**image_errors(reference,image,source),coverage=float((mask&source).sum()/source.sum()),extra_pixels=int((mask&~source).sum())))
                cv2.imwrite(str(out/'pairs'/(pair+'__'+method+'.png')),cv2.cvtColor(image,cv2.COLOR_RGB2BGR))
            if all(m in corrected for m in METHODS) and category is not None:
                draw(out/'pairs'/(pair+'__comparison.png'),[reference,rgb,PALETTE[category],corrected['material_checked'],corrected['semantic_face_skin'],corrected['semantic_hair_veto']],
                     ['Reference','Input','Categories: green face / brown hair','Previous color check','Semantic face skin','Previous + semantic hair veto'])

        for row in sources:
            image_id=row['image_id'];safe=image_id.replace('/','_');clean=cv2.imread(row['image_path'])
            try:
                box,_,result=baseline(clean);x,y,w,h=box
                source=np.zeros(clean.shape[:2],bool);source[y:y+h,x:x+w]=result.mask>0
                rgb=cv2.cvtColor(clean,cv2.COLOR_BGR2RGB);shift=rgb.copy();shift[source]=np.rint(transform_rgb(rgb.astype(float)/255,1.,.85,1.15)[source]*255).astype(np.uint8)
                variants={'clean':rgb,'color_shift':shift}
            except Exception as error:
                for variant in ('clean','color_shift'):
                    for method in METHODS:failures.append(dict(input_id=safe+'__'+variant,method=method,error='Source preparation: '+str(error)))
                    for point in points_by_source.get(image_id,[]):
                        for method in NEW_METHODS:observations.append(dict(point_id=point['point_id'],variant=variant,method=method,selected=None,error=str(error)))
                continue
            for variant,input_rgb in variants.items():
                key=safe+'__'+variant;masks,_,_,category=infer(cv2.cvtColor(input_rgb,cv2.COLOR_RGB2BGR),key,out/'broader')
                record=dict(image_id=image_id,variant=variant);panels=[input_rgb];titles=[key]
                for method,mask in masks.items():
                    record[method+'_available']=mask is not None
                    record[method+'_coverage']=float((mask&source).sum()/source.sum()) if mask is not None else None
                    record[method+'_extra_pixels']=int((mask&~source).sum()) if mask is not None else None
                    overlay=input_rgb.copy()
                    if mask is not None:overlay[mask]=np.rint(.5*input_rgb[mask]+.5*np.array([0,200,0])).astype(np.uint8)
                    panels.append(overlay);titles.append(method if mask is not None else method+' UNAVAILABLE')
                panels.append(PALETTE[category] if category is not None else np.zeros_like(input_rgb));titles.append('Category map' if category is not None else 'Categories unavailable')
                draw(out/'broader'/(key+'.png'),panels,titles,columns=3);broad.append(record)
                for point in points_by_source.get(image_id,[]):
                    for method in ('original','material_checked'):
                        if masks[method] is not None:
                            prior=next(r for r in old_predictions['observations'] if r['point_id']==point['point_id'] and r['variant']==variant and r['method']==method)
                            assert prior['selected']==bool(masks[method][point['y'],point['x']])
                    for method in NEW_METHODS:
                        mask=masks[method];observations.append(dict(point_id=point['point_id'],variant=variant,method=method,selected=bool(mask[point['y'],point['x']]) if mask is not None else None,error=None if mask is not None else 'See inference ledger'))
                if len(broad)%20==0:status('running',broader_inputs_completed=len(broad));print('Broader inputs:',len(broad),flush=True)
    finally:segmenter.close()
    assert len(observations)==96 and len({(r['point_id'],r['variant'],r['method']) for r in observations})==96
    for filename,records,fields in [('pair_metrics.csv',metrics,list(metrics[0]) if metrics else ['pair_id']),('broader_mask_diagnostics.csv',broad,list(broad[0]) if broad else ['image_id']),('failures.csv',failures,['input_id','method','error']),('segmentation_timing.csv',timings,['input_id','segment_ms'])]:
        with (out/filename).open('x',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(records)
    point_result=dict(manifest_sha256=manifest_sha,labels_sha256=helper.digest(labels_path),new_observations=observations,
        results=score_points(old_predictions['observations']+observations,labels),warning='Known development regression points; not pixel-area accuracy or independent validation.')
    (out/'point_results.json').write_text(json.dumps(point_result,indent=2),encoding='utf-8')
    aggregate=[]
    for split in sorted({r['split'] for r in metrics}):
        for method in METHODS:
            selected=[r for r in metrics if r['split']==split and r['method']==method]
            if selected:aggregate.append(dict(split=split,method=method,pairs=len(selected),**{k:float(np.mean([r[k] for r in selected])) for k in ('ciede2000_source_mask','coverage','extra_pixels','rgb_mae_outside_source_mask')}))
    assert all(helper.digest(Path(p))==value for p,value in hashes.items())
    summary=dict(pair_attempts=len(pairs),broader_attempts=92,broader_inputs_recorded=len(broad),
        broader_available_by_method={m:sum(r[m+'_available'] for r in broad) for m in METHODS},failures=failures,pair_results=aggregate,
        segmenter_labels=list(LABELS),model_provenance=provenance,input_sha256=hashes,
        warmed_segment_median_ms=float(np.median([r['segment_ms'] for r in timings[1:]])) if len(timings)>1 else None,
        rules='Full-input multiclass argmax, no confidence tuning. face-skin class3 inside face box minus exclusions; hair veto removes class1 only from prior color-checked support.',
        warning='Correction-mask development trial only; estimation masks and tree fixed. No default adoption, final thesis score, paint class or Android timing claim.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');status('complete',broader_inputs_completed=len(broad),pair_metric_rows=len(metrics))
    print(json.dumps({k:v for k,v in summary.items() if k not in ('input_sha256','failures','model_provenance')},indent=2))


if __name__=='__main__':main()
