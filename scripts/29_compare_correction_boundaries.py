"""Fixed-model boundary experiment; development diagnostics, no tuning/refit."""
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.model_training.train_model import load_model
from src.data_preparation.controlled_training_table import FEATURE_KEYS
from src.evaluation.correction_prototype import model_arrays, apply_correction, image_errors
from src.evaluation.correction_boundary import feather_correction, correction_edge_jump


def read(path):
    with path.open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = get_config()
    output = ROOT/config.OUTPUTS_ROOT/'correction_boundary_v1'
    if output.exists():
        raise FileExistsError('Boundary experiment exists; refusing overwrite')
    table = ROOT/'data/manifests/controlled_training_v1'
    previous = ROOT/config.OUTPUTS_ROOT/'correction_prototype_v1'
    model_path = ROOT/config.MODELS_ROOT/'correction_prototype_v1/decision_tree.joblib'
    prior_summary = json.loads((previous/'summary.json').read_text())
    assert digest(model_path) == prior_summary['model_sha256']
    model = load_model(str(model_path))
    prepare = importlib.import_module('11_prepare_training_manifests')
    rows = read(table/'development_validation.csv') + read(table/'clipped_stress.csv')
    prior_predictions = {(r['pair_id'],r['method']):r for r in read(previous/'parameter_predictions.csv')}
    prior_metrics = {(r['pair_id'],r['method']):r for r in read(previous/'image_metrics.csv')}
    paths = [model_path, previous/'parameter_predictions.csv', previous/'image_metrics.csv',
             table/'development_validation.csv', table/'clipped_stress.csv', Path(__file__),
             ROOT/'src/evaluation/correction_boundary.py', ROOT/config.FACE_MODEL_PATH,
             ROOT/config.FACE_LANDMARKER_MODEL_PATH]
    for row in rows:
        paths += [ROOT/row['input_path'], Path(row['source_path']), ROOT/row['generation_mask_path']]
    hashes = {str(p):digest(p) for p in paths}
    output.mkdir()
    metrics = []; failures = []
    for row in rows:
        try:
            pair = row['pair_id']
            bgr = cv2.imread(str(ROOT/row['input_path']))
            ref = cv2.cvtColor(cv2.imread(row['source_path']),cv2.COLOR_BGR2RGB)
            rgb = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            source = cv2.imread(str(ROOT/row['generation_mask_path']),0) > 0
            boxes = prepare._detect_face_boxes(bgr,ROOT/config.FACE_MODEL_PATH,.85)
            if len(boxes) != 1: raise ValueError('Expected one face')
            x,y,w,h = boxes[0]; crop = bgr[y:y+h,x:x+w].copy()
            result = prepare.compute_versioned_skin_mask(crop,bgr,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,row['mask_version'])
            stats = prepare.compute_masked_lab_statistics(crop,result.mask,1000)
            if not result.landmarks_available or not stats['valid']: raise ValueError('Invalid mask/features')
            features,_ = model_arrays([row])
            np.testing.assert_allclose([stats[k] for k in FEATURE_KEYS],features[0],atol=.00005,rtol=0)
            params = model.predict(features)[0]
            saved = prior_predictions[(pair,'decision_tree')]
            np.testing.assert_allclose(params,[float(saved[k]) for k in ('gamma','red_gain','blue_gain')],atol=1e-12,rtol=0)
            mask = np.zeros(source.shape,bool); mask[y:y+h,x:x+w] = result.mask > 0
            width = max(2., .03*min(w,h))  # One fixed geometric rule, not an error-selected sweep.
            hard = apply_correction(rgb,mask,params)
            old = cv2.cvtColor(cv2.imread(str(previous/(pair+'__decision_tree.png'))),cv2.COLOR_BGR2RGB)
            np.testing.assert_array_equal(hard,old)
            soft,alpha = feather_correction(rgb,mask,params,width)
            np.testing.assert_array_equal(soft[~mask],rgb[~mask])
            missed = source & ~mask; extra = mask & ~source
            overlay = rgb.copy(); overlay[source&mask] = [0,190,0]
            overlay[missed] = [255,0,0]; overlay[extra] = [0,90,255]
            missing_crop = missed[y:y+h,x:x+w]
            excluded = result.exclusion_mask > 0
            coverage = dict(source_pixels=int(source.sum()),input_pixels=int(mask.sum()),
                missed_source_pixels=int(missed.sum()),extra_input_pixels=int(extra.sum()),
                source_coverage=float((source&mask).sum()/source.sum()),
                missed_inside_feature_exclusion=int((missing_crop&excluded).sum()),
                missed_inside_crop_outside_exclusion=int((missing_crop&~excluded).sum()),
                missed_outside_face_crop=int(missed.sum()-missing_crop.sum()))
            for method,corrected in [('no_correction',rgb),('hard',hard),('inward_feather',soft)]:
                scores = image_errors(ref,corrected,source)
                metrics.append(dict(pair_id=pair,split=row['table_use'],method=method,**scores,**coverage,
                    correction_edge_jump=correction_edge_jump(rgb,corrected,mask),width_pixels=width))
                if method == 'hard':
                    assert abs(scores['ciede2000_source_mask']-float(prior_metrics[(pair,'decision_tree')]['ciede2000_source_mask'])) < 1e-10
                cv2.imwrite(str(output/(pair+'__'+method+'.png')),cv2.cvtColor(corrected,cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(output/(pair+'__input_mask.png')),mask.astype(np.uint8)*255)
            cv2.imwrite(str(output/(pair+'__alpha.png')),np.rint(alpha*255).astype(np.uint8))
            panels = []
            for title,image in [('Reference',ref),('Input',rgb),('Coverage: green/shared red/missed blue/extra',overlay),
                                ('Hard correction',hard),('Inward feather',soft),('Feather alpha',np.repeat(np.rint(alpha[...,None]*255).astype(np.uint8),3,axis=2))]:
                panel = cv2.resize(image,(320,320)); panel = cv2.copyMakeBorder(panel,30,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(panel,title,(4,19),cv2.FONT_HERSHEY_SIMPLEX,.36,(255,255,0),1)
                panels.append(panel)
            sheet = np.vstack([np.hstack(panels[:3]),np.hstack(panels[3:])])
            if not cv2.imwrite(str(output/(pair+'__comparison.png')),cv2.cvtColor(sheet,cv2.COLOR_RGB2BGR)):
                raise OSError('Failed comparison write')
        except Exception as error:
            failures.append(dict(pair_id=row['pair_id'],error=str(error)))
    for filename, records, fields in [('metrics.csv',metrics,list(metrics[0]) if metrics else ['pair_id']),
                                      ('failures.csv',failures,['pair_id','error'])]:
        with (output/filename).open('x',newline='',encoding='utf-8') as stream:
            writer = csv.DictWriter(stream,fields); writer.writeheader(); writer.writerows(records)
    assert all(digest(Path(p)) == value for p,value in hashes.items())
    aggregate = []
    for split in sorted({r['split'] for r in metrics}):
        for method in ('no_correction','hard','inward_feather'):
            selected = [r for r in metrics if r['split']==split and r['method']==method]
            aggregate.append(dict(split=split,method=method,pairs=len(selected),
                **{key:float(np.mean([r[key] for r in selected])) for key in
                   ('ciede2000_source_mask','rgb_mae_source_mask','rgb_mae_outside_source_mask','correction_edge_jump','source_coverage')}))
    summary = dict(attempted_pairs=len(rows),failed_pairs=len(failures),results=aggregate,input_sha256=hashes,
        feather_rule='inward smoothstep(distance / max(2 pixels, 0.03 * min(face width,height)))',
        status='Development experiment only; no refit, mask expansion, feature change or production adoption. Source mask used only for diagnostics/scoring.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))
    if failures: raise RuntimeError('See failures.csv; partial run retained')


if __name__ == '__main__':
    main()
