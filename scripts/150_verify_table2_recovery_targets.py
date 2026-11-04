"""Synthetic-only Table2 capacity check; no study images or tree fitting."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.distortion_generation.table2_composite import composite_rgb
from src.model_training.recovery_targets import fit_recovery_target


def main():
    out=ROOT/'outputs/table2_target_verification_v1'
    if out.exists():raise FileExistsError(out)
    reference=np.random.default_rng(42).integers(40,210,(32,32,3),dtype=np.uint8)
    selected=np.ones(reference.shape[:2],bool);records=[]
    for group in ['light','medium','dark']:
        distorted,transform=composite_rgb(reference,group)
        report=fit_recovery_target(distorted,reference,selected,selected)
        assert report['status']=='available_approximate_target'
        p=report['parameters'];corrected=np.clip(np.power(distorted.astype(float)/255,1/p[0])*[p[1],1,p[2]],0,1)
        residual=float(np.sqrt(np.mean((corrected-reference.astype(float)/255)**2)))
        assert abs(residual-report['float_rgb_rmse'])<1e-12
        assert 0<residual<report['identity_float_rgb_rmse']
        records.append(dict(group=group,transform=transform,target_fit=report))
    files=[Path(__file__),ROOT/'src/distortion_generation/table2_composite.py',ROOT/'src/model_training/recovery_targets.py',ROOT/'docs/table2-target-fit-protocol.md']
    summary=dict(status='synthetic_only_capacity_checks_pass',records=records,study_images_opened=0,
        correction_tree_fits=0,new_training_admissions=0,production_runtime_changed=False,
        input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        limitation='Reference-informed bounded local optimization; not exact inversion, learned performance or final dataset admission.')
    out.mkdir();(out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(records,indent=2))


if __name__=='__main__':main()
