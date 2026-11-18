"""Bind one artificial conditional-reference prior design. No prior fitting."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if sys.argv[1:]!=['--specify-only']:raise SystemExit('Explicit specification flag required')
    out=ROOT/'outputs/conditional_prior_generated_design_v1'
    if out.exists():raise FileExistsError('Preserve design')
    files=['docs/conditional-reference-prior-generated-protocol-2026-11-13.md','docs/conditional-reference-colour-prior-review-2026-11-13.md','scripts/specify_conditional_prior_generated.py']
    plan=dict(status='SPECIFIED_GENERATED_ONLY_NOT_EXECUTED',schema='truehue_green_conditional_reference_prior_v1',green_bins=8,bin_rule='min(7,floor(8*G))',input_units='normalized_encoded_RGB_0_to_1',log_definition=['log(R/G)','log(B/G)'],positive_RGB_only=True,
      source_weighting='equal_contributing_source_bin_means',smoothing=False,interpolation=False,pseudocount=False,missing_bin='null_unavailable_no_imputation',
      descriptor_fields=['available','positive_fraction','supported_fraction','mean_red_residual','mean_blue_residual'],missing_residual=None,fraction_denominator='all_input_pixels',
      generated_fitting_sources=['A','B','C'],generated_excluded_sources=['H'],select_fitting_ID_before_pixel_access=True,reference_records_per_source=1,
      trend=dict(green='(k+0.5)/8',red_log_ratio='0.12+0.08*G',blue_log_ratio='-0.15+0.04*G',used_k=list(range(6)),unpopulated_bins=[6,7]),
      reference_counts=dict(A=[1]*6,B=[1,2,3,4,5,6],C=[6,5,4,3,2,1],H=[2,1,4,1,3,5]),
      roles=dict(identity=[1.,1.],red_decrease=[245/255,1.],blue_decrease=[1.,245/255],blue_increase=[1.,255/245]),
      probes=dict(ideal=16,source_offsets=36,source_offset_axis=[-.1,0.,.1],weighting_source_pixels=[1,100],stress_continuous_quantized=14,clipping_pixel=[.99,.6875,.98],leakage_traps=True,missing_zero=True),
      canonical_reduction='source_ID_sorted_scalar_math_fsum',independent_reconstruction='numpy_counts_bin_source_means_residuals',numeric_tolerance=dict(abs_tol=1e-12,rel_tol=1e-12),
      real_roster_selected=False,real_prior_fit_allowed=False,tree_fit_allowed=False,tree_family_selected=False,new_review_task=False,solver_executed=False,real_arrays=0,model_adopted=False,input_sha256={n:sha(ROOT/n) for n in files})
    assert len(plan['generated_fitting_sources'])==len(set(plan['generated_fitting_sources']))==3 and not set(plan['generated_fitting_sources'])&set(plan['generated_excluded_sources'])
    assert plan['probes']['ideal']==4*4 and plan['probes']['source_offsets']==9*4 and plan['probes']['stress_continuous_quantized']==7*2
    assert all(len(v)==6 for v in plan['reference_counts'].values())
    out.mkdir();(out/'plan_PRIVATE.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/n)==h for n,h in plan['input_sha256'].items())
    (out/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,metadata_only=True,plan_sha256=sha(out/'plan_PRIVATE.json'),prior_fitted=False,tree_fitted=False,arrays_decoded=0),indent=2)+'\n',encoding='utf-8')
    print('Generated conditional-prior specification PASS; no table/tree fit or array reads')
if __name__=='__main__':main()
