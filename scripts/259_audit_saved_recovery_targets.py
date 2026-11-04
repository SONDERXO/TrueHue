"""Separate saved-target, fixed-support and learned errors on approved pairs."""
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.evaluation.correction_prototype import image_errors
h=importlib.import_module('256_compare_clean_control_tree_depth')


def main():
    out=ROOT/'outputs/saved_recovery_target_audit_v1'
    if out.exists():raise FileExistsError(out)
    parent=ROOT/'outputs/accepted_clean_control_comparison_v1'
    plan=h.read(parent/'plan.json')
    assert h.read(parent/'verification.json')['status']=='pass'
    for path,sha in plan['input_sha256'].items():assert h.digest(ROOT/path)==sha
    rows=[r for r in plan['rows'] if r['variant']!='identity']
    assert len(rows)==15
    records=[]
    for row in rows:
        fit=row['target_fit'];report=ROOT/row['target_fit_report_path']
        assert h.digest(report)==row['target_fit_report_sha256']
        assert fit['status']=='available_approximate_target'
        params=row['paper_target']
        np.testing.assert_allclose(params,[1/fit['parameters'][0],*fit['parameters'][1:]],rtol=0,atol=0)
        image,reference,mask,score,output=h.render(row,params)
        selected=mask&score
        assert int(selected.sum())==fit['selected_pixels']
        # Independent legacy-coordinate reconstruction verifies curve and residual.
        legacy=fit['parameters']
        floating=np.clip(np.power(image[selected].astype(float)/255,1/legacy[0])*[legacy[1],1,legacy[2]],0,1)
        residual=float(np.sqrt(np.mean((floating-reference[selected].astype(float)/255)**2)))
        assert abs(residual-fit['float_rgb_rmse'])<1e-12
        quantized=float(np.mean(np.abs(np.rint(floating*255)-reference[selected].astype(float)))/255)
        assert abs(quantized-fit['quantized_rgb_mae'])<1e-12
        np.testing.assert_array_equal(output[selected],np.rint(floating*255).astype(np.uint8))
        # Reference-copy on application support is diagnostic only. Unreachable
        # scoring pixels remain input pixels; their error is a support floor.
        ideal=image.copy();ideal[mask]=reference[mask]
        floor=image_errors(reference,ideal,score)['ciede2000_source_mask']
        baseline=image_errors(reference,image,score)['ciede2000_source_mask']
        target=image_errors(reference,output,score)['ciede2000_source_mask']
        assert target+1e-12>=floor
        records.append(dict(pair_id=row['pair_id'],saved_direct_parameters=params,
            input_error=baseline,saved_target_error=target,support_only_lower_bound=floor,
            scoring_pixels=int(score.sum()),reachable_scoring_pixels=int(selected.sum()),
            unreachable_scoring_pixels=int((score&~mask).sum()),
            saved_target_improves=target<baseline,clipped_pixel_fraction=row['clipped_pixel_fraction'],
            verified_float_rgb_rmse=residual))
    out.mkdir()
    h.write(out/'summary.json',dict(status='reference_informed_diagnostic_only',pairs=15,
        mean_input_error=float(np.mean([r['input_error'] for r in records])),
        mean_saved_target_error=float(np.mean([r['saved_target_error'] for r in records])),
        mean_support_only_lower_bound=float(np.mean([r['support_only_lower_bound'] for r in records])),
        saved_target_improves_pairs=sum(r['saved_target_improves'] for r in records),records=records,
        caveat='Saved target is bounded local RGB fit, not globally optimal CIEDE2000; support floor permits arbitrary reference-informed per-pixel correction, unavailable at inference.',
        training_target_changes=0,active_demo_changed=False))
    h.write(out/'verification.json',dict(status='pass',independent_curve_residual_and_quantization_checks=15,
        source_hashes_verified=True,original_target_report_hashes_verified=15,
        summary_sha256=h.digest(out/'summary.json'),producer_sha256=h.digest(Path(__file__))))
    print(json.dumps({k:v for k,v in h.read(out/'summary.json').items() if k not in ('records','caveat')}))


if __name__=='__main__':main()
