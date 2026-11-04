"""Exact selected/missed-region error accounting on the fixed30pair cohort."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
from src.data_preparation.controlled_training_table import TARGETS
from src.evaluation.correction_prototype import apply_correction,image_errors


def main():
    out=ROOT/'outputs/table2_recovery_budget_v1';parent=ROOT/'outputs/table2_reviewed_fifteen_source_evaluation_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    plan=read(parent/'fit_plan.json');data=read(parent/'summary.json');verify=read(parent/'verification.json')
    assert digest(parent/'fit_plan.json')==verify['fit_plan_sha256'] and digest(parent/'summary.json')==verify['summary_sha256']
    rows={r['pair_id']:r for r in plan['rows']};paths=[Path(__file__),parent/'fit_plan.json',parent/'summary.json',parent/'verification.json']
    for r in rows.values():paths.extend(ROOT/r[k] for k in ['input_path','input_mask_path','reference_path','reference_mask_path'])
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    out.mkdir();write(out/'plan.json',dict(status='frozen_before_accounting',pairs=30,input_sha256=hashes,
        question='Exact fixed-reference-region contribution from missed application support, versus selected-region reconstruction',
        masks='Unchanged; no segmentation improvement or new quality annotations',
        floor='Nonnegative missed-region CIEDE sum / reference pixel count is a bound for any output preserving pixels outside the current application support',
        oracle='Existing RGB-fitted targets,not globally optimal perceptual recovery; comparison gap may be signed',new_fits=0))
    records=[]
    for previous in data['records']:
        row=rows[previous['pair_id']];reference=rgb(ROOT/row['reference_path']);image=rgb(ROOT/row['input_path'])
        application=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        selected=score&application;missed=score&~application;n=int(score.sum())
        ref_lab=rgb2lab(reference.astype(float)/255)
        input_delta=deltaE_ciede2000(ref_lab,rgb2lab(image.astype(float)/255))
        floor=float(input_delta[missed].sum()/n)
        methods={}
        for method,parameters in [('no_correction',[1.,1.,1.]),('learned5',previous['methods']['baseline5']['parameters']),('fitted_target',[row[k] for k in TARGETS])]:
            corrected=apply_correction(image,application,parameters)
            np.testing.assert_array_equal(corrected[~application],image[~application])
            delta=deltaE_ciede2000(ref_lab,rgb2lab(corrected.astype(float)/255))
            squared=(corrected.astype(float)/255-reference.astype(float)/255)**2
            contributions=dict(selected_ciede2000=float(delta[selected].sum()/n),missed_ciede2000=float(delta[missed].sum()/n),
                selected_rgb_mse=float(squared[selected].sum()/(3*n)),missed_rgb_mse=float(squared[missed].sum()/(3*n)))
            total_delta=float(delta[score].mean());total_mse=float(squared[score].mean())
            assert abs(total_delta-contributions['selected_ciede2000']-contributions['missed_ciede2000'])<1e-10
            assert abs(total_mse-contributions['selected_rgb_mse']-contributions['missed_rgb_mse'])<1e-12
            assert abs(contributions['missed_ciede2000']-floor)<1e-10
            # Existing independent metric API checks the full reference denominator.
            metric=image_errors(reference,corrected,score);assert metric['ciede2000_source_mask']==total_delta
            if method=='learned5':assert metric==previous['methods']['baseline5']['metrics']
            methods[method]=dict(total_ciede2000=total_delta,total_rgb_mse=total_mse,**contributions)
        records.append(dict(pair_id=row['pair_id'],variant=row['variant'],severity=row['severity_probe'],review_concern=row['review_concern'],
            reference_pixels=n,selected_reference_pixels=int(selected.sum()),missed_reference_pixels=int(missed.sum()),
            missed_fraction=float(missed.sum()/n),fixed_support_ciede2000_floor=floor,methods=methods,
            learned_minus_rgb_fitted_ciede2000=methods['learned5']['total_ciede2000']-methods['fitted_target']['total_ciede2000']))
    aggregate={}
    for scope,subset in [('all',records),('identity',[r for r in records if r['variant']=='identity']),('distorted',[r for r in records if r['variant']!='identity']),
        ('light_distorted',[r for r in records if r['variant']=='table2_light']),('medium_distorted',[r for r in records if r['variant']=='table2_medium'])]:
        aggregate[scope]=dict(pairs=len(subset),mean_missed_fraction=float(np.mean([r['missed_fraction'] for r in subset])),
            mean_fixed_support_floor=float(np.mean([r['fixed_support_ciede2000_floor'] for r in subset])),
            methods={m:{k:float(np.mean([r['methods'][m][k] for r in subset])) for k in records[0]['methods'][m]} for m in methods})
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(out/'summary.json',dict(status='complete_exact_error_accounting',records=records,aggregate=aggregate,input_sha256=hashes,
        new_fits=0,masks_changed=False,runtime_replaced=False))
    write(out/'verification.json',dict(status='pass',verified_cases=30,method_outputs_accounted_for=90,
        exact_ciede2000_and_rgb_mse_partition=True,full_reference_metric_recomputed=True,outside_application_pixels_unchanged=True,
        original_hashes_unchanged=True,summary_sha256=digest(out/'summary.json')))
    print(json.dumps({s:dict(pairs=a['pairs'],missed_fraction=a['mean_missed_fraction'],floor=a['mean_fixed_support_floor'],
        scores={m:v['total_ciede2000'] for m,v in a['methods'].items()}) for s,a in aggregate.items()},indent=2))


if __name__=='__main__':main()
