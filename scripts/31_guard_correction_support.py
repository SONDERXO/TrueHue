"""Interior-only fill: fixed-model pair comparison and broader mask diagnostics."""
import csv
import importlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.model_training.train_model import load_model
from src.evaluation.correction_prototype import model_arrays,apply_correction,image_errors
from src.data_preparation.controlled_training_table import FEATURE_KEYS
from src.distortion_generation.generate_distortions import transform_rgb
from src.skin_masking.correction_support_experiment import complete_correction_support
from src.skin_masking.guarded_correction_support import guarded_correction_support


def sheet(path,images,titles,columns=3):
    panels = []
    for image,title in zip(images,titles):
        panel = cv2.copyMakeBorder(cv2.resize(image,(256,256)),32,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(panel,title,(3,19),cv2.FONT_HERSHEY_SIMPLEX,.36,(255,255,0),1)
        panels.append(panel)
    combined = np.vstack([np.hstack(panels[i:i+columns]) for i in range(0,len(panels),columns)])
    if not cv2.imwrite(str(path),cv2.cvtColor(combined,cv2.COLOR_RGB2BGR)): raise OSError('Sheet write failed')


def main():
    helper = importlib.import_module('29_compare_correction_boundaries')
    prepare = importlib.import_module('11_prepare_training_manifests')
    config = get_config(); output = ROOT/config.OUTPUTS_ROOT/'guarded_correction_support_v1'
    if output.exists(): raise FileExistsError('Existing run; refusing overwrite')
    table = ROOT/'data/manifests/controlled_training_v1'
    review_path = ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    sources = [r for r in helper.read(review_path) if r['original_visual_decision']=='accept' or r['image_id']=='fairface__train/29962.jpg']
    if len(sources)!=46 or any(r['partition']=='reserved_test' for r in sources): raise ValueError('Unexpected development cohort')
    pairs = helper.read(table/'development_validation.csv')+helper.read(table/'clipped_stress.csv')
    model_path = ROOT/config.MODELS_ROOT/'correction_prototype_v1/decision_tree.joblib'
    metadata_path = model_path.parent/'metadata.json'
    model = load_model(str(model_path))
    assert helper.digest(model_path)==json.loads(metadata_path.read_text())['model_sha256']
    paths = [Path(__file__),ROOT/'src/skin_masking/guarded_correction_support.py',
             ROOT/'src/skin_masking/correction_support_experiment.py',ROOT/'scripts/11_prepare_training_manifests.py',
             ROOT/'src/evaluation/correction_prototype.py',ROOT/'src/distortion_generation/generate_distortions.py',
             ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,model_path,metadata_path,
             review_path,table/'development_validation.csv',table/'clipped_stress.csv']
    for r in sources: paths.append(Path(r['image_path']))
    for r in pairs: paths += [ROOT/r['input_path'],Path(r['source_path']),ROOT/r['generation_mask_path'],ROOT/config.OUTPUTS_ROOT/'correction_support_v1'/(r['pair_id']+'__original.png')]
    hashes = {str(p):helper.digest(p) for p in paths}
    output.mkdir(); (output/'pairs').mkdir(); (output/'broader').mkdir()
    metrics = []; broad = []; failures = []

    def masks(bgr):
        boxes = prepare._detect_face_boxes(bgr,ROOT/config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1: raise ValueError('Expected one face; found '+str(len(boxes)))
        x,y,w,h = boxes[0]; crop = bgr[y:y+h,x:x+w].copy()
        result = prepare.compute_versioned_skin_mask(crop,bgr,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
        if not result.landmarks_available: raise ValueError('Landmarks unavailable')
        original = result.mask>0; excluded = result.exclusion_mask>0
        hull = complete_correction_support(original,excluded)
        guard = guarded_correction_support(original,excluded)
        assert np.all(guard[original]) and not guard[~hull].any() and not guard[excluded].any()
        full = []
        for mask in (original,hull,guard):
            frame = np.zeros(bgr.shape[:2],bool); frame[y:y+h,x:x+w] = mask; full.append(frame)
        return full,crop,result

    for row in pairs:
        try:
            pair = row['pair_id']; bgr = cv2.imread(str(ROOT/row['input_path']))
            rgb = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            reference = cv2.cvtColor(cv2.imread(row['source_path']),cv2.COLOR_BGR2RGB)
            source = cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
            supports,crop,result = masks(bgr)
            stats = prepare.compute_masked_lab_statistics(crop,result.mask,1000)
            if not stats['valid']: raise ValueError('Invalid inference features')
            features,_ = model_arrays([row])
            np.testing.assert_allclose([stats[k] for k in FEATURE_KEYS],features[0],atol=.00005,rtol=0)
            params = model.predict(features)[0]; corrected_images = []
            for method,mask in zip(('original','hull','guarded'),supports):
                corrected = apply_correction(rgb,mask,params); corrected_images.append(corrected)
                np.testing.assert_array_equal(corrected[~mask],rgb[~mask])
                if method=='original': np.testing.assert_array_equal(corrected,cv2.cvtColor(cv2.imread(str(ROOT/config.OUTPUTS_ROOT/'correction_support_v1'/(pair+'__original.png'))),cv2.COLOR_BGR2RGB))
                metrics.append(dict(pair_id=pair,split=row['table_use'],method=method,**image_errors(reference,corrected,source),
                    coverage=float((mask&source).sum()/source.sum()),extra_pixels=int((mask&~source).sum()),
                    added_pixels=int((mask&~supports[0]).sum())))
                cv2.imwrite(str(output/'pairs'/(pair+'__'+method+'.png')),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
                cv2.imwrite(str(output/'pairs'/(pair+'__'+method+'_mask.png')),mask.astype(np.uint8)*255)
            additions = rgb.copy(); additions[supports[1]&~supports[0]] = [255,70,0]; additions[supports[2]&~supports[0]] = [0,220,220]
            sheet(output/'pairs'/(pair+'__comparison.png'),[reference,rgb,additions]+corrected_images,
                  ['Reference','Input','Orange: removed / cyan: retained additions','Original correction','Unrestricted fill','Guarded fill'])
        except Exception as error: failures.append(dict(stage='pairs',image_id=row['pair_id'],error=str(error)))

    for row in sources:
        source_id = row['image_id']; safe = source_id.replace('/','_')
        try:
            clean_bgr = cv2.imread(row['image_path']); clean_rgb = cv2.cvtColor(clean_bgr,cv2.COLOR_BGR2RGB)
            clean_masks,_,_ = masks(clean_bgr)
            source = clean_masks[0]  # Used to generate distortion and for diagnostics only.
            shifted = clean_rgb.copy()
            transformed = transform_rgb(clean_rgb.astype(float)/255,1.,.85,1.15)
            shifted[source] = np.rint(transformed[source]*255).astype(np.uint8)
        except Exception as error:
            for variant in ('clean','color_shift'): failures.append(dict(stage='broader_'+variant,image_id=source_id,error='Source preparation: '+str(error)))
            continue
        for variant,rgb in [('clean',clean_rgb),('color_shift',shifted)]:
            try:
                # The generated-input mask is inferred independently; clean geometry never guides it.
                supports,_,_ = masks(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)) if variant!='clean' else (clean_masks,None,None)
                record = dict(image_id=source_id,variant=variant,original_review=row['original_visual_decision'],
                    sentinel=source_id in ('fairface__train/29962.jpg','fairface__train/83184.jpg'),
                    known_geometry_case=source_id=='fairface__train/83184.jpg',partition=row['partition'],
                    source_pixels=int(source.sum()),baseline_pixels=int(supports[0].sum()))
                overlays = [rgb]
                for method,mask in zip(('original','hull','guarded'),supports):
                    record[method+'_coverage'] = float((mask&source).sum()/source.sum())
                    record[method+'_extra_pixels'] = int((mask&~source).sum())
                    record[method+'_added_pixels'] = int((mask&~supports[0]).sum())
                    overlay = rgb.copy(); overlay[mask] = np.rint(.5*rgb[mask]+.5*np.array([0,200,0])).astype(np.uint8)
                    overlay[mask&~supports[0]] = [0,220,220]; overlays.append(overlay)
                broad.append(record)
                sheet(output/'broader'/(safe+'__'+variant+'.png'),overlays,
                      [safe+' '+variant,'Original support','Hull additions: cyan','Guarded additions: cyan'],columns=2)
            except Exception as error: failures.append(dict(stage='broader_'+variant,image_id=source_id,error=str(error)))
        if len(broad)%20==0: print('Broader diagnostic rows completed:',len(broad),flush=True)

    for filename,records,fields in [('pair_metrics.csv',metrics,list(metrics[0]) if metrics else ['pair_id']),('broader_mask_diagnostics.csv',broad,list(broad[0]) if broad else ['image_id']),('failures.csv',failures,['stage','image_id','error'])]:
        with (output/filename).open('x',newline='',encoding='utf-8') as stream:
            writer = csv.DictWriter(stream,fields); writer.writeheader(); writer.writerows(records)
    assert all(helper.digest(Path(p))==value for p,value in hashes.items())
    aggregate = []
    for split in sorted({r['split'] for r in metrics}):
        for method in ('original','hull','guarded'):
            subset = [r for r in metrics if r['split']==split and r['method']==method]
            aggregate.append(dict(split=split,method=method,pairs=len(subset),**{k:float(np.mean([r[k] for r in subset])) for k in ('ciede2000_source_mask','rgb_mae_outside_source_mask','coverage','extra_pixels')}))
    summary = dict(pair_attempts=len(pairs),broader_sources=len(sources),broader_attempts=2*len(sources),broader_successes=len(broad),
        failures=failures,pair_results=aggregate,input_sha256=hashes,
        rules='New pixels only: hull outer distance > max(2px,3% crop min dimension); feature distance > max(2px,2% crop min dimension). No model or estimation changes.',
        warning='Exploratory development diagnostics. Broader generation masks are not human segmentation truth. Rejected sources remain rejected; broader mask-only checks are not model performance.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__': main()
