"""Diagnose color gates and test input-only correction support, without refit."""
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
from src.skin_masking.correction_support_experiment import complete_correction_support
from src.skin_masking.skin_mask import keep_largest_connected_component
from src.data_preparation.controlled_training_table import FEATURE_KEYS


def main():
    helper = importlib.import_module('29_compare_correction_boundaries')
    prepare = importlib.import_module('11_prepare_training_manifests')
    config = get_config(); output = ROOT/config.OUTPUTS_ROOT/'correction_support_v1'
    if output.exists(): raise FileExistsError('Experiment exists; refusing overwrite')
    previous = ROOT/config.OUTPUTS_ROOT/'correction_boundary_v1'
    table = ROOT/'data/manifests/controlled_training_v1'
    rows = helper.read(table/'development_validation.csv')+helper.read(table/'clipped_stress.csv')
    model_path = ROOT/config.MODELS_ROOT/'correction_prototype_v1/decision_tree.joblib'
    model = load_model(str(model_path))
    assert helper.digest(model_path) == json.loads((ROOT/config.MODELS_ROOT/'correction_prototype_v1/metadata.json').read_text())['model_sha256']
    paths = [model_path,Path(__file__),ROOT/'src/skin_masking/correction_support_experiment.py',
             ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,
             table/'development_validation.csv',table/'clipped_stress.csv']
    for row in rows: paths += [ROOT/row['input_path'],Path(row['source_path']),ROOT/row['generation_mask_path'],previous/(row['pair_id']+'__input_mask.png')]
    hashes = {str(p):helper.digest(p) for p in paths}
    output.mkdir(); metrics = []; diagnostics = []; failures = []
    for row in rows:
        try:
            pair = row['pair_id']; bgr = cv2.imread(str(ROOT/row['input_path']))
            rgb = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            reference = cv2.cvtColor(cv2.imread(row['source_path']),cv2.COLOR_BGR2RGB)
            source = cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
            boxes = prepare._detect_face_boxes(bgr,ROOT/config.FACE_MODEL_PATH,.85)
            if len(boxes)!=1: raise ValueError('Expected one face')
            x,y,w,h = boxes[0]; crop = bgr[y:y+h,x:x+w].copy()
            result = prepare.compute_versioned_skin_mask(crop,bgr,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,row['mask_version'])
            stats = prepare.compute_masked_lab_statistics(crop,result.mask,1000)
            if not result.landmarks_available or not stats['valid']: raise ValueError('Invalid estimation mask')
            features,_ = model_arrays([row])
            np.testing.assert_allclose([stats[k] for k in FEATURE_KEYS],features[0],atol=.00005,rtol=0)
            original = np.zeros(source.shape,bool); original[y:y+h,x:x+w] = result.mask>0
            np.testing.assert_array_equal(original,cv2.imread(str(previous/(pair+'__input_mask.png')),0)>0)
            # Only this call chooses new support: input mask and input anatomical exclusions.
            completed_crop = complete_correction_support(result.mask>0,result.exclusion_mask>0)
            completed = np.zeros_like(original); completed[y:y+h,x:x+w] = completed_crop
            assert not (completed_crop & (result.exclusion_mask>0)).any()
            assert np.all(completed[original])
            parameters = model.predict(features)[0]
            hsv = cv2.cvtColor(crop,cv2.COLOR_BGR2HSV); ycc = cv2.cvtColor(crop,cv2.COLOR_BGR2YCrCb)
            hgate = cv2.inRange(hsv,np.array([0,48,0],np.uint8),np.array([20,255,255],np.uint8))>0
            cgate = cv2.inRange(ycc,np.array([0,133,77],np.uint8),np.array([255,173,127],np.uint8))>0
            region = source[y:y+h,x:x+w]  # Diagnostics only, after support chosen.
            candidate = result.candidate_mask>0
            largest = keep_largest_connected_component(result.candidate_mask)>0
            diagnostics.append(dict(pair_id=pair,source_pixels=int(source.sum()),source_pixels_in_crop=int(region.sum()),
                hsv_rejected_in_source_crop=int((region&~hgate).sum()),ycrcb_rejected_in_source_crop=int((region&~cgate).sum()),
                either_gate_rejected_in_source_crop=int((region&~(hgate&cgate)).sum()),
                cleaned_candidate_rejected=int((region&~candidate).sum()),
                largest_component_rejected=int((region&candidate&~largest).sum()),
                anatomical_excluded_after_largest=int((region&largest&(result.exclusion_mask>0)).sum())))
            images = [reference,rgb]; titles = ['Reference','Input']
            for method,mask in [('original',original),('input_hull',completed)]:
                corrected = apply_correction(rgb,mask,parameters)
                if method=='original': np.testing.assert_array_equal(corrected,cv2.cvtColor(cv2.imread(str(previous/(pair+'__hard.png'))),cv2.COLOR_BGR2RGB))
                np.testing.assert_array_equal(corrected[~mask],rgb[~mask])
                metrics.append(dict(pair_id=pair,split=row['table_use'],method=method,**image_errors(reference,corrected,source),
                    coverage=float((mask&source).sum()/source.sum()),extra_pixels=int((mask&~source).sum()),
                    added_pixels=int((mask&~original).sum())))
                cv2.imwrite(str(output/(pair+'__'+method+'.png')),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
                cv2.imwrite(str(output/(pair+'__'+method+'_mask.png')),mask.astype(np.uint8)*255)
                images.append(corrected); titles.append(method+' correction')
            for title,mask in [('Original support',original),('Hull support',completed)]:
                overlay = rgb.copy(); overlay[mask&source] = [0,190,0]; overlay[source&~mask] = [255,0,0]; overlay[mask&~source] = [0,90,255]
                images.append(overlay); titles.append(title+' (red/missed blue/extra)')
            panels = []
            for title,image in zip(titles,images):
                panel = cv2.copyMakeBorder(cv2.resize(image,(320,320)),30,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(panel,title,(3,19),cv2.FONT_HERSHEY_SIMPLEX,.4,(255,255,0),1); panels.append(panel)
            if not cv2.imwrite(str(output/(pair+'__comparison.png')),cv2.cvtColor(np.vstack([np.hstack(panels[:3]),np.hstack(panels[3:])]),cv2.COLOR_RGB2BGR)): raise OSError('Comparison write failed')
        except Exception as error: failures.append(dict(pair_id=row['pair_id'],error=str(error)))
    for filename,records,fields in [('metrics.csv',metrics,list(metrics[0]) if metrics else ['pair_id']),('gate_diagnostics.csv',diagnostics,list(diagnostics[0]) if diagnostics else ['pair_id']),('failures.csv',failures,['pair_id','error'])]:
        with (output/filename).open('x',newline='',encoding='utf-8') as stream:
            writer = csv.DictWriter(stream,fields); writer.writeheader(); writer.writerows(records)
    assert all(helper.digest(Path(p))==value for p,value in hashes.items())
    aggregate = []
    for split in sorted({r['split'] for r in metrics}):
        for method in ('original','input_hull'):
            subset = [r for r in metrics if r['split']==split and r['method']==method]
            aggregate.append(dict(split=split,method=method,pairs=len(subset),**{key:float(np.mean([r[key] for r in subset])) for key in ('ciede2000_source_mask','rgb_mae_source_mask','rgb_mae_outside_source_mask','coverage','extra_pixels')}))
    summary = dict(attempted_pairs=len(rows),failures=failures,results=aggregate,input_sha256=hashes,
        warning='Post-validation development experiment. Correction support only; estimation mask/model fixed. Hull may include non-skin; not adopted. Source masks diagnostic only.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))
    if failures: raise RuntimeError('Partial experiment retained; see failures.csv')


if __name__=='__main__': main()
