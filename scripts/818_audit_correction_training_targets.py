"""Audit saved recipe coverage and feasible nominal renders; no fitting."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
OUT=ROOT/'outputs/correction_training_target_audit_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')

def main():
    if OUT.exists():raise FileExistsError('Preserve completed or partial audit')
    rows=read(P/'rows_PRIVATE.json');parent=ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1'
    predictions={r['case_id']:r for r in read(parent/'predictions_PRIVATE.json')}
    files=[P/'rows_PRIVATE.json',P/'verification_PRIVATE.json',parent/'summary_PRIVATE.json',parent/'review_PRIVATE.json',parent/'predictions_PRIVATE.json',ROOT/'outputs/proposal_scope_validation_20261103_v1/pages.json',ROOT/'docs/proposal-distortion-recipe-audit-2026-11-03.md',ROOT/'docs/core-colour-recipe-results-2026-11-03.md',ROOT/'docs/training-exposure-colour-audit-2026-11-09.md',ROOT/'src/distortion_generation/paper_gamma.py',ROOT/'src/distortion_generation/development_roles.py',ROOT/'src/distortion_generation/core_colour_recipe.py',ROOT/'src/correction/seamless_blend.py',Path(__file__)]
    bound={str(p):sha(p) for p in files};assert len(rows)==44
    roles=Counter(r['experimental_role'] for r in rows);records=[]
    OUT.mkdir();write(OUT/'execution_plan_PRIVATE.json',dict(rows=44,target_fits=0,tree_fits=0,original_photo_reads=0,holdout_reads=0,input_sha256=bound))
    for r in rows:
        assert sha(r['pixels_file'])==r['pixels_sha256'];bound[r['pixels_file']]=r['pixels_sha256']
        q=r['recipe'];g=q['gamma'];gains=np.array([q['red_gain'],1.,q['blue_gain']]);inverse=[1/g,q['red_gain']**(-1/g),q['blue_gain']**(-1/g)]
        np.testing.assert_array_equal(inverse,r['nominal_controls'])
        with np.load(r['pixels_file'],allow_pickle=False) as z:
            image=z['input_rgb8'];reference=z['reference_rgb8'];a=z['alpha'];mask=z['scoring_mask'];protected=z['protected'];assert np.array_equal(mask,a>0)
            clean=reference/255.;forward=clean**g*gains
            np.testing.assert_array_equal(np.rint(255*np.clip(forward,0,1)).astype(np.uint8),image)
            exact=forward**inverse[0]*[inverse[1],1.,inverse[2]]
            analytic_error=float(np.abs(exact-clean).max());assert analytic_error<1e-12
            u=image/255.;corrected=np.clip(u**inverse[0]*[inverse[1],1.,inverse[2]],0,1)
            unblended=np.rint(255*corrected).astype(np.uint8)
            output=np.rint(255*(u*(1-a[:,:,None])+corrected*a[:,:,None])).astype(np.uint8)
            assert np.array_equal(output[protected],image[protected]) and np.array_equal(output[a==0],image[a==0])
            lo=np.rint(255*u*(1-a[:,:,None]));hi=np.rint(255*(u*(1-a[:,:,None])+a[:,:,None]))
            target=reference.astype(float);floor=np.maximum(np.maximum(lo-target,target-hi),0)
            error=np.abs(output.astype(float)-target);assert np.all(error+1e-12>=floor)
            rgb=float(error[mask].mean());base=float(np.abs(image[mask].astype(float)-target[mask]).mean())
            de=float(deltaE_ciede2000(rgb2lab(output[mask]/255.),rgb2lab(reference[mask]/255.)).mean())
            fractional=(a>0)&(a<1)
            records.append(dict(case_id=r['case_id'],role=r['experimental_role'],nominal_controls=inverse,analytic_float_inverse_max_error=analytic_error,input_RGB=base,unblended_nominal_RGB=float(np.abs(unblended[mask].astype(float)-target[mask]).mean()),blended_nominal_RGB=rgb,blended_nominal_DE=de,interval_relaxation_RGB_lower_bound=float(floor[mask].mean()),unreachable_target_channels=int(np.count_nonzero(floor[mask])),scored_channels=int(mask.sum()*3),fractional_alpha_pixels=int(fractional.sum()),scored_pixels=int(mask.sum()),nominal_corrected_changed_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),saved_tree_RGB=predictions[r['case_id']]['output_RGB'],saved_tree_DE=predictions[r['case_id']]['output_DE'],protected_and_zero_alpha_preserved=True))
    by_role={}
    for role in roles:
        own=[r for r in records if r['role']==role]
        keys=['input_RGB','unblended_nominal_RGB','blended_nominal_RGB','blended_nominal_DE','interval_relaxation_RGB_lower_bound','saved_tree_RGB','saved_tree_DE']
        by_role[role]={k:float(np.mean([r[k] for r in own])) for k in keys}
        by_role[role].update(cases=len(own),nominal_RGB_improves=sum(r['blended_nominal_RGB']<r['input_RGB']-1e-12 for r in own))
    coverage=dict(roles=dict(roles),reference_bases=len({r['publisher_group'] for r in rows}),distinct_gamma_targets=sorted({r['nominal_controls'][0] for r in rows}),distinct_red_targets=sorted({r['nominal_controls'][1] for r in rows}),distinct_blue_targets=sorted({r['nominal_controls'][2] for r in rows}),combined_cases=0,severity_settings=['medium'],provided_MST_labels=0,complete_Table2_implementation=False,historical_broader_recipes_already_tested=True)
    summary=dict(rows=44,coverage=coverage,by_role=by_role,all_nominal_controls_algebraically_correct=True,nominal_render_is_feasible_candidate_not_optimum=True,interval_bound_is_relaxed_lower_bound_not_exact_three_parameter_optimum=True,new_target_fits=0,new_tree_fits=0,new_learned_predictions=0,deterministic_nominal_diagnostic_renders=44,image_model_calls=0,original_photo_reads=0,holdout_reads=0)
    write(OUT/'rows_PRIVATE.json',records);write(OUT/'summary_PRIVATE.json',summary);write(OUT/'input_sha256_PRIVATE.json',bound)
    assert all(sha(p)==h for p,h in bound.items());print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
