"""Exercise the same single-image runtime on all controlled attempts and labels."""
import csv
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.correction.correct_image import LEGACY_POLICY,MATERIAL_HAIR_POLICY
from src.data_preparation.controlled_training_table import FEATURES
from src.evaluation.correction_prototype import image_errors
from src.evaluation.material_point_review import validate_labels,score_points
from src.distortion_generation.generate_distortions import transform_rgb


def main():
    api=importlib.import_module('39_correct_image');helper=importlib.import_module('29_compare_correction_boundaries')
    draw=importlib.import_module('31_guard_correction_support').sheet
    config=get_config();base=ROOT/config.OUTPUTS_ROOT;out=base/'integrated_correction_v1'
    if out.exists():raise FileExistsError('Integrated validation exists; refusing overwrite')
    tables=ROOT/'data/manifests/controlled_training_v1';review=ROOT/'data/manifests/material_review_v1'
    rows=[]
    for name in ('train.csv','development_validation.csv','clipped_stress.csv','excluded_pairs.csv'):rows+=helper.read(tables/name)
    if len(rows)!=24 or len({r['pair_id'] for r in rows})!=24:raise ValueError('Expected 24 unique attempts')
    manifest_path=review/'review_manifest.json';labels_path=review/'material_review_labels.json'
    manifest=json.loads(manifest_path.read_text());manifest_sha=api.digest(manifest_path)
    labels=validate_labels(manifest,json.loads(labels_path.read_text()),manifest_sha)
    prior=json.loads((base/'semantic_support_channels_v1/point_results.json').read_text())
    original_predictions=json.loads((review/'prediction_observations.json').read_text())
    if prior['manifest_sha256']!=manifest_sha or prior['labels_sha256']!=api.digest(labels_path):raise ValueError('Frozen review changed')
    expected_points={(r['point_id'],r['variant']):r for r in prior['new_observations'] if r['method']=='semantic_hair_veto'}
    paths=[Path(__file__),ROOT/'scripts/39_correct_image.py',ROOT/'src/correction/correct_image.py',ROOT/'src/utilities/config.py',
        ROOT/'src/skin_masking/material_checked_support.py',ROOT/'src/skin_masking/selfie_material_segmenter.py',
        ROOT/'src/skin_masking/guarded_correction_support.py',ROOT/'src/skin_masking/correction_support_experiment.py',
        ROOT/'scripts/11_prepare_training_manifests.py',ROOT/'src/evaluation/correction_prototype.py',
        ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,ROOT/config.SELFIE_SEGMENTER_MODEL_PATH,
        ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,manifest_path,labels_path,
        review/'prediction_observations.json',base/'semantic_support_channels_v1/point_results.json']
    paths += [tables/name for name in ('train.csv','development_validation.csv','clipped_stress.csv','excluded_pairs.csv')]
    for row in rows:paths += [ROOT/row['input_path'],Path(row['source_path']),ROOT/row['generation_mask_path']]
    for source in manifest['sources']:paths.append(Path(source['image_path']))
    hashes={str(p):api.digest(p) for p in paths}
    out.mkdir();(out/'pairs').mkdir();(out/'points').mkdir()
    status_path=out/'run_status.json'
    def status(value,**kw):status_path.write_text(json.dumps(dict(status=value,**kw),indent=2),encoding='utf-8')
    status('running',expected_pairs=24,expected_point_inputs=12)
    runtime=api.CorrectionRuntime();metrics=[];failures=[];attempts=[];observations=[]
    try:
        for row in rows:
            pair=row['pair_id'];image=cv2.imread(str(ROOT/row['input_path']))
            results={};expected_exclusion=row['table_use']=='excluded'
            for policy in (LEGACY_POLICY,MATERIAL_HAIR_POLICY):
                try:
                    result=runtime.correct(image,policy)
                    if expected_exclusion:raise RuntimeError('Previously excluded input unexpectedly accepted')
                    np.testing.assert_allclose([result.features[k] for k in FEATURES],[float(row[k]) for k in FEATURES],atol=.00005,rtol=0)
                    results[policy]=result
                    api.save_result(out/'pairs'/pair/policy,image,result,dict(input_path=row['input_path'],input_sha256=api.digest(ROOT/row['input_path']),pair_id=pair))
                except Exception as error:
                    failures.append(dict(pair_id=pair,policy=policy,expected_exclusion=expected_exclusion,error=str(error)))
            attempts.append(dict(pair_id=pair,table_use=row['table_use'],expected_exclusion=expected_exclusion,
                legacy_success=LEGACY_POLICY in results,material_hair_success=MATERIAL_HAIR_POLICY in results))
            if len(results)!=2:continue
            legacy=results[LEGACY_POLICY];new=results[MATERIAL_HAIR_POLICY]
            assert legacy.features==new.features and legacy.parameters==new.parameters
            np.testing.assert_array_equal(legacy.estimation_mask,new.estimation_mask)
            reference=cv2.imread(row['source_path']);scoring=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
            for policy,result in results.items():
                np.testing.assert_array_equal(result.corrected_bgr[~result.correction_mask],image[~result.correction_mask])
                metrics.append(dict(pair_id=pair,table_use=row['table_use'],policy=policy,
                    **image_errors(cv2.cvtColor(reference,cv2.COLOR_BGR2RGB),cv2.cvtColor(result.corrected_bgr,cv2.COLOR_BGR2RGB),scoring),
                    correction_pixels=int(result.correction_mask.sum()),semantic_hair_pixels_removed=result.metadata['semantic_hair_pixels_removed']))
            if row['table_use']!='train':
                old_legacy=cv2.imread(str(base/'correction_prototype_v1'/(pair+'__decision_tree.png')))
                old_new=cv2.imread(str(base/'semantic_support_channels_v1/pairs'/(pair+'__semantic_hair_veto.png')))
                old_mask=cv2.imread(str(base/'semantic_support_channels_v1/pairs'/(pair+'__semantic_hair_veto_mask.png')),0)>0
                np.testing.assert_array_equal(legacy.corrected_bgr,old_legacy)
                np.testing.assert_array_equal(new.corrected_bgr,old_new);np.testing.assert_array_equal(new.correction_mask,old_mask)
            overlay=image.copy();overlay[new.correction_mask]=np.rint(.5*image[new.correction_mask]+.5*np.array([0,200,0])).astype(np.uint8)
            draw(out/'pairs'/(pair+'__comparison.png'),[cv2.cvtColor(im,cv2.COLOR_BGR2RGB) for im in
                (reference,image,legacy.corrected_bgr,new.corrected_bgr,overlay,cv2.cvtColor(new.correction_mask.astype(np.uint8)*255,cv2.COLOR_GRAY2BGR))],
                ['Reference','Input','Legacy correction','Material + hair veto','New correction support','New binary mask'])
            status('running',pair_attempts_completed=len(attempts))

        for source in manifest['sources']:
            clean=cv2.imread(source['image_path']);clean_result=runtime.correct(clean,MATERIAL_HAIR_POLICY)
            rgb=cv2.cvtColor(clean,cv2.COLOR_BGR2RGB);shift=rgb.copy();generation=clean_result.estimation_mask
            shift[generation]=np.rint(transform_rgb(rgb.astype(float)/255,1.,.85,1.15)[generation]*255).astype(np.uint8)
            for variant,image in [('clean',clean),('color_shift',cv2.cvtColor(shift,cv2.COLOR_RGB2BGR))]:
                result=clean_result if variant=='clean' else runtime.correct(image,MATERIAL_HAIR_POLICY)
                key=source['image_id'].replace('/','_')+'__'+variant
                api.save_result(out/'points'/key,image,result,dict(image_id=source['image_id'],variant=variant))
                for point in [p for p in manifest['points'] if p['image_id']==source['image_id']]:
                    selected=bool(result.correction_mask[point['y'],point['x']])
                    assert selected==expected_points[(point['point_id'],variant)]['selected']
                    original=next(r for r in original_predictions['observations'] if r['point_id']==point['point_id'] and r['variant']==variant and r['method']=='original')
                    assert bool(result.estimation_mask[point['y'],point['x']])==original['selected']
                    if labels[point['point_id']]=='paint':
                        assert not selected
                        np.testing.assert_array_equal(result.corrected_bgr[point['y'],point['x']],image[point['y'],point['x']])
                    observations.append(dict(point_id=point['point_id'],variant=variant,method=MATERIAL_HAIR_POLICY,selected=selected))
    finally:runtime.close()
    for name,records,fields in [('image_metrics.csv',metrics,list(metrics[0])),('attempts.csv',attempts,list(attempts[0])),('failures.csv',failures,['pair_id','policy','expected_exclusion','error'])]:
        with (out/name).open('x',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(records)
    assert len(attempts)==24 and len(metrics)==46 and len(observations)==48
    assert len(failures)==2 and all(r['expected_exclusion'] for r in failures)
    assert all(api.digest(Path(p))==value for p,value in hashes.items())
    aggregate=[]
    for split in ('train','development_validation','stress_only'):
        for policy in (LEGACY_POLICY,MATERIAL_HAIR_POLICY):
            selected=[r for r in metrics if r['table_use']==split and r['policy']==policy]
            aggregate.append(dict(table_use=split,policy=policy,pairs=len(selected),
                mean_ciede2000=float(np.mean([r['ciede2000_source_mask'] for r in selected])),
                mean_rgb_mae=float(np.mean([r['rgb_mae_source_mask'] for r in selected]))))
    points=dict(manifest_sha256=manifest_sha,labels_sha256=api.digest(labels_path),observations=observations,results=score_points(observations,labels))
    (out/'point_regression.json').write_text(json.dumps(points,indent=2),encoding='utf-8')
    summary=dict(attempted_pairs=24,successful_pairs=23,expected_excluded_pairs=1,unexpected_failures=0,
        compared_policy_outputs=46,point_inputs=12,point_observations=48,results=aggregate,input_sha256=hashes,
        verification='Seven held-out/stress image outputs and masks reproduce previous experiments exactly; features/parameters unchanged across both policies; all frozen points match. Reviewed paint points untouched.',
        warning='Integration verification, not new held-out evidence. Train reconstruction and nonindependent stress diagnostics are separate; no refitting, source expansion or final thesis score.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');status('complete',successful_pairs=23,expected_excluded_pairs=1,point_inputs=12)
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':main()
