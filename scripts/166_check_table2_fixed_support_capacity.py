"""Reference-informed capacity on fixed support, including detection failure.

Not an inference fallback, training target admission or global optimality claim.
"""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.recovery_targets import fit_recovery_target
from src.evaluation.correction_prototype import apply_correction,image_errors


def main():
    out=ROOT/'outputs/table2_fixed_support_capacity_v2'
    if out.exists():raise FileExistsError(out)
    parent=ROOT/'outputs/table2_counterfactual_coverage_v1'
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    data=read(parent/'summary.json')
    assert digest(parent/'summary.json')==read(parent/'verification.json')['summary_sha256']
    paths=[Path(__file__),parent/'summary.json',parent/'verification.json',ROOT/'src/model_training/recovery_targets.py']
    paths+=list((parent/'images').glob('*_input.png'))
    paths+=[ROOT/r[k] for r in data['records'] for k in ['reference_path','reference_mask_path']]
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    out.mkdir()
    write(out/'plan.json',dict(probes=24,input_sha256=hashes,
        fit='Same bounded RGB least squares/identity start; fit AND apply on fixed reference support',
        purpose='Separate lost application support from approximate three-parameter recovery capacity; includes failed detection as oracle-only case',
        caveat='Reference-informed diagnostic, never inference fallback; local RGB optimum is not global CIEDE2000 optimum or a mathematical lower bound'))
    records=[]
    for row in data['records']:
        pair=row['pair_id'];image=rgb(parent/'images'/(pair+'_input.png'))
        reference=rgb(ROOT/row['reference_path']);support=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        fit=fit_recovery_target(image,reference,support,support)
        record=dict(pair_id=pair,severity=row['severity_probe'],measurement_status=row['status'],fit=fit,
            no_correction=image_errors(reference,image,support))
        if fit['parameters'] is not None:
            parameters=fit['parameters'];g,r,b=parameters
            raw=np.clip((image.astype(float)/255)**(1/g)*[r,1,b],0,1)
            residual=float(np.sqrt(np.mean((raw[support]-reference[support].astype(float)/255)**2)))
            assert abs(residual-fit['float_rgb_rmse'])<1e-12
            result=apply_correction(image,support,parameters)
            expected=image.copy();expected[support]=np.rint(raw[support]*255).astype(np.uint8)
            np.testing.assert_array_equal(result,expected)
            assert np.array_equal(result[~support],image[~support])
            path=out/(pair+'_oracle.png');assert cv2.imwrite(str(path),cv2.cvtColor(result,cv2.COLOR_RGB2BGR))
            np.testing.assert_array_equal(rgb(path),expected)
            record['fixed_support_oracle']=image_errors(reference,result,support)
            record['independent_residual']=residual
            # Where inference succeeded, reuse its exact parameters over the reference support
            # only as a second reference-informed application diagnostic.
            if 'parameters' in row:
                record['frozen_parameters_reference_support']=image_errors(reference,apply_correction(image,support,row['parameters']),support)
                record['original_input_support_oracle']=row['oracle']
        records.append(record)
    aggregate={}
    for severity in ['light','medium','dark']:
        all_rows=[r for r in records if r['severity']==severity and 'fixed_support_oracle' in r]
        paired=[r for r in all_rows if 'original_input_support_oracle' in r]
        aggregate[severity]=dict(all_count=len(all_rows),paired_count=len(paired),
            all_fixed_support_oracle=float(np.mean([r['fixed_support_oracle']['ciede2000_source_mask'] for r in all_rows])),
            paired_fixed_support_oracle=float(np.mean([r['fixed_support_oracle']['ciede2000_source_mask'] for r in paired])),
            paired_original_support_oracle=float(np.mean([r['original_input_support_oracle']['ciede2000_source_mask'] for r in paired])),
            paired_frozen_parameters_reference_support=float(np.mean([r['frozen_parameters_reference_support']['ciede2000_source_mask'] for r in paired])))
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(out/'summary.json',dict(status='complete_capacity_diagnostic',records=records,aggregate=aggregate,input_sha256=hashes,
        models_fitted=0,training_admitted=0,runtime_replaced=False))
    write(out/'verification.json',dict(status='pass',independent_rgb_residuals_and_pngs_checked=24,
        summary_sha256=digest(out/'summary.json'),original_hashes_unchanged=True,
        evidence_sha256={p.name:digest(p) for p in out.glob('*.png')}))
    print(json.dumps(aggregate,indent=2))


if __name__=='__main__':main()
