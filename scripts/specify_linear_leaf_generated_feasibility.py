"""Bind generated-only method design metadata. Never import a trainer or arrays."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if sys.argv[1:]!=['--specify-only']:raise SystemExit('Explicit specification flag required')
    out=ROOT/'outputs/linear_leaf_generated_design_v1'
    if out.exists():raise FileExistsError('Preserve design')
    names=['generated_feature_'+str(i) for i in range(281)]
    names[5]='scene_log_r_over_g';names[6]='scene_log_b_over_g';names[13]='input_green_p50_codes'
    paths=['docs/linear-leaf-generated-feasibility-protocol-2026-11-13.md','docs/linear-leaf-model-tree-candidate-review-2026-11-13.md','scripts/specify_linear_leaf_generated_feasibility.py','src/model_training/whole_scene_features.py','src/model_training/portable_tree.py']
    plan=dict(status='SPECIFIED_GENERATED_ONLY_NOT_EXECUTED',schema='truehue_linear_leaf_tree_v1',single_hard_tree=True,max_depth=4,max_nodes=31,
      generated_interface_names=names,actual_frozen281_interface_extracted=False,leaf_coordinates=[dict(index=5,name=names[5]),dict(index=6,name=names[6])],
      leaf_coefficients=9,max_leaf_coefficients=144,max_axis_branch_scalars=45,target_names=['gamma','red_gain','blue_gain'],target_normalization=False,
      objective='mean_squared_vector_residual_plus_lambda_slope_Frobenius_squared',lambda_fixed=.01,intercept_penalized=False,
      input_scaling='fitting_leaf_mean_population_std_exact_zero_scale_1_fold_to_raw',solver='single_2x2_centered_ridge_direct_solve',independent_solver='scalar_2x2_inverse',
      canonical_inference='float32_inputs_float64_coefficients_math_fsum_intercept_then_two_products',prediction_tolerance=dict(abs_tol=1e-12,rel_tol=1e-12),
      generated_branch=dict(feature_index=13,under_value=64,colour_value=128,over_value=224,under_threshold=80,colour_threshold=180),
      invalid_controls='explicit_rejection_nonfinite_or_nonpositive_no_render_no_identity_fallback',positive_extrapolation='report_not_claim_safe',
      probes=dict(separable_fit=9,separable_interpolation=4,neutral_fit=9,three_leaf_records=13,nuisance_total=36,nuisance_fit=4,nuisance_held=32,extrapolation=[[-10,0],[10,0]],
        degenerate=['single_row','identical_conflicting','zero_variance','correlated','empty_leaf']),
      recipe_grid=False,feature_grid=False,penalty_grid=False,real_roster_selected=False,real_fit_allowed=False,new_review_task=False,
      generated_solver_executed=False,arrays_decoded=0,fits=0,predictions=0,runtime_changes=False,model_adopted=False,input_sha256={p:sha(ROOT/p) for p in paths})
    assert plan['leaf_coefficients']==3*(2+1) and plan['max_leaf_coefficients']==16*plan['leaf_coefficients']
    assert plan['probes']['nuisance_fit']+plan['probes']['nuisance_held']==plan['probes']['nuisance_total']
    assert len(names)==len(set(names))==281 and plan['lambda_fixed']>0
    out.mkdir();(out/'plan_PRIVATE.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/p)==h for p,h in plan['input_sha256'].items())
    (out/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,metadata_only=True,plan_sha256=sha(out/'plan_PRIVATE.json'),real_fit_allowed=False,solver_executed=False),indent=2)+'\n',encoding='utf-8')
    print('Generated-only design specified:2leaf coordinates/9coefficients/lambda0.01; no execution')
if __name__=='__main__':main()
