"""Frozen factorial diagnostics: predicted/known parameters x current/source masks."""
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
from src.correction.correct_image import MATERIAL_HAIR_POLICY
from src.distortion_generation.generate_distortions import inverse_parameters,transform_rgb
from src.evaluation.correction_prototype import apply_correction,image_errors
from src.evaluation.correction_error_diagnosis import region_errors,factorial_gaps

METHODS=('no_correction','tree_current_mask','known_current_mask','tree_source_mask_oracle','known_source_mask_oracle')


def main():
    helper=importlib.import_module('29_compare_correction_boundaries')
    draw=importlib.import_module('31_guard_correction_support').sheet
    config=get_config();base=ROOT/config.OUTPUTS_ROOT;integrated=base/'integrated_correction_v1';out=base/'mask_parameter_diagnosis_v1'
    if out.exists():raise FileExistsError('Diagnostic exists; refusing overwrite')
    integrated_summary=json.loads((integrated/'summary.json').read_text())
    # Use the frozen outputs, not a new estimator/model run.
    if not all(helper.digest(Path(p))==value for p,value in integrated_summary['input_sha256'].items()):raise ValueError('Integrated run inputs changed')
    if json.loads((integrated/'run_status.json').read_text())['status']!='complete':raise ValueError('Integrated run incomplete')
    table=ROOT/'data/manifests/controlled_training_v1';rows=[]
    files=('train.csv','development_validation.csv','clipped_stress.csv','excluded_pairs.csv')
    for filename in files:rows+=helper.read(table/filename)
    if len(rows)!=24 or len({r['pair_id'] for r in rows})!=24:raise ValueError('Expected 24 unique attempts')
    paths=[Path(__file__),ROOT/'src/evaluation/correction_error_diagnosis.py',ROOT/'src/evaluation/correction_prototype.py',
        ROOT/'src/distortion_generation/generate_distortions.py',integrated/'summary.json',integrated/'run_status.json']+[table/name for name in files]
    for row in rows:
        paths += [ROOT/row['input_path'],Path(row['source_path']),ROOT/row['generation_mask_path']]
        if row['table_use']!='excluded':
            paths += [integrated/'pairs'/row['pair_id']/MATERIAL_HAIR_POLICY/name for name in ('metadata.json','corrected.png','correction_mask.png')]
    hashes={str(p):helper.digest(p) for p in paths}
    out.mkdir();(out/'pairs').mkdir()
    status_path=out/'run_status.json'
    def status(value,**kw):status_path.write_text(json.dumps(dict(status=value,**kw),indent=2),encoding='utf-8')
    status('running',attempted_pairs=24)
    metric_rows=[];region_rows=[];gap_rows=[];attempts=[];parameter_rows=[]
    for row in rows:
        pair=row['pair_id'];split=row['table_use']
        if split=='excluded':
            attempts.append(dict(pair_id=pair,table_use=split,status='preserved_prior_exclusion',reason=row['input_exclusion_reason']))
            continue
        directory=integrated/'pairs'/pair/MATERIAL_HAIR_POLICY
        metadata=json.loads((directory/'metadata.json').read_text())
        if metadata['mask_policy']!=MATERIAL_HAIR_POLICY or metadata['transform_version']!=row['transform_version']:raise ValueError('Version mismatch')
        input_rgb=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(row['source_path']),cv2.COLOR_BGR2RGB)
        current=cv2.imread(str(directory/'correction_mask.png'),0)>0
        source=cv2.imread(str(ROOT/row['generation_mask_path']),0)>0
        if source.shape!=input_rgb.shape[:2] or current.shape!=source.shape or not source.any():raise ValueError('Invalid scoring support')
        distortion=[float(row[k]) for k in ('distortion_gamma','distortion_red_gain','distortion_blue_gain')]
        known_dict=inverse_parameters(*distortion);known=np.asarray(list(known_dict.values()),float)
        np.testing.assert_allclose(known,[float(row[k]) for k in ('target_gamma','target_red_gain','target_blue_gain')],atol=1e-12,rtol=0)
        # Check that these exact known targets really describe the saved input.
        np.testing.assert_array_equal(apply_correction(reference,source,distortion),input_rgb)
        unbounded=transform_rgb(reference.astype(float)/255,*distortion,clip=False)
        clipped=int((source&((unbounded<0)|(unbounded>1)).any(axis=2)).sum())
        if clipped!=int(row['clipped_pixel_count']):raise ValueError('Clipping provenance differs')
        predicted=np.asarray([metadata['parameters'][k] for k in ('gamma','red_gain','blue_gain')],float)
        for origin,values in [('frozen_tree_prediction',predicted),('known_synthetic_inverse',known)]:
            parameter_rows.append(dict(pair_id=pair,table_use=split,origin=origin,**dict(zip(('gamma','red_gain','blue_gain'),map(float,values)))))
        outputs=dict(no_correction=input_rgb.copy(),tree_current_mask=apply_correction(input_rgb,current,predicted),
            known_current_mask=apply_correction(input_rgb,current,known),tree_source_mask_oracle=apply_correction(input_rgb,source,predicted),
            known_source_mask_oracle=apply_correction(input_rgb,source,known))
        saved=cv2.cvtColor(cv2.imread(str(directory/'corrected.png')),cv2.COLOR_BGR2RGB)
        np.testing.assert_array_equal(outputs['tree_current_mask'],saved)
        shared=source&current
        np.testing.assert_array_equal(outputs['known_current_mask'][shared],outputs['known_source_mask_oracle'][shared])
        np.testing.assert_array_equal(outputs['tree_current_mask'][shared],outputs['tree_source_mask_oracle'][shared])
        for method in ('tree_current_mask','known_current_mask'):
            np.testing.assert_array_equal(outputs[method][~current],input_rgb[~current])
        errors={}
        for method,image in outputs.items():
            measured=image_errors(reference,image,source);regions=region_errors(reference,image,source,current)
            n_shared=regions['shared_source_and_current']['pixels'];n_missed=regions['source_missed_by_current']['pixels']
            weighted=sum(regions[name]['pixels']*(regions[name]['ciede2000'] or 0.) for name in ('shared_source_and_current','source_missed_by_current'))/(n_shared+n_missed)
            np.testing.assert_allclose(weighted,measured['ciede2000_source_mask'],atol=1e-10,rtol=0)
            errors[method]=measured['ciede2000_source_mask']
            metric_rows.append(dict(pair_id=pair,table_use=split,method=method,diagnostic_only=method not in ('no_correction','tree_current_mask'),
                **measured,source_pixels=int(source.sum()),current_pixels=int(current.sum()),shared_pixels=int(shared.sum()),
                missed_source_pixels=int((source&~current).sum()),extra_current_pixels=int((current&~source).sum()),clipped_pixel_count=clipped))
            for region,values in regions.items():region_rows.append(dict(pair_id=pair,table_use=split,method=method,region=region,**values))
            if not cv2.imwrite(str(out/'pairs'/(pair+'__'+method+'.png')),cv2.cvtColor(image,cv2.COLOR_RGB2BGR)):raise OSError('Diagnostic image write failed')
        gaps=factorial_gaps(errors)
        gap_rows.append(dict(pair_id=pair,table_use=split,**gaps))
        attempts.append(dict(pair_id=pair,table_use=split,status='diagnosed',reason=''))
        region_map=input_rgb.copy();region_map[shared]=[0,190,0];region_map[source&~current]=[255,0,0];region_map[current&~source]=[0,90,255]
        mask_rgb=lambda mask:np.repeat((mask.astype(np.uint8)*255)[...,None],3,axis=2)
        draw(out/'pairs'/(pair+'__comparison.png'),
            [reference,input_rgb,region_map,outputs['tree_current_mask'],outputs['known_current_mask'],mask_rgb(current),
             outputs['tree_source_mask_oracle'],outputs['known_source_mask_oracle'],mask_rgb(source)],
            ['Reference','Input','Green shared / red missed / blue extra','Tree + current mask','Known + current mask (diagnostic)','Current correction mask',
             'Tree + source mask (oracle)','Known + source mask (oracle)','Source generation mask'],columns=3)
        status('running',diagnosed_pairs=len(gap_rows))
    for name,records in [('image_metrics.csv',metric_rows),('region_metrics.csv',region_rows),('factorial_gaps.csv',gap_rows),('attempts.csv',attempts),('parameters.csv',parameter_rows)]:
        with (out/name).open('x',newline='',encoding='utf-8') as stream:
            writer=csv.DictWriter(stream,list(records[0]));writer.writeheader();writer.writerows(records)
    assert len(metric_rows)==115 and len(gap_rows)==23 and len(attempts)==24
    aggregate=[];gap_aggregate=[]
    for split in ('train','development_validation','stress_only'):
        for method in METHODS:
            selected=[r for r in metric_rows if r['table_use']==split and r['method']==method]
            aggregate.append(dict(table_use=split,method=method,pairs=len(selected),
                mean_ciede2000=float(np.mean([r['ciede2000_source_mask'] for r in selected])),
                mean_rgb_mae=float(np.mean([r['rgb_mae_source_mask'] for r in selected])),
                mean_outside_source_rgb_mae=float(np.mean([r['rgb_mae_outside_source_mask'] for r in selected]))))
        selected=[r for r in gap_rows if r['table_use']==split]
        gap_aggregate.append(dict(table_use=split,pairs=len(selected),**{key:float(np.mean([r[key] for r in selected])) for key in factorial_gaps({method:0. for method in METHODS if method!='no_correction'})}))
    assert all(helper.digest(Path(p))==value for p,value in hashes.items())
    summary=dict(attempted_pairs=24,diagnosed_pairs=23,preserved_excluded_pairs=1,input_sha256=hashes,
        image_results=aggregate,signed_factorial_gaps=gap_aggregate,
        current_mask_policy=MATERIAL_HAIR_POLICY,parameter_source='Recorded frozen tree output or verified inverse of known synthetic distortion',
        warning='Source masks and known parameters are unavailable oracle diagnostics, not learned performance or inference changes. Signed differences interact and are not independent error percentages. Generation support is not human skin truth; clipping and uint8 rounding remain in the oracle floor.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');status('complete',diagnosed_pairs=23,preserved_excluded_pairs=1)
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':main()
