# Fixed chroma-distribution comparison

28 October 2026. Hypothesis frozen before computing candidate features or
fitting: pooled Lab means/ITA/MST omit within-support color dispersion and
lightness/chroma dependence that could help distinguish source appearance from
synthetic distortions. This is unproven; earlier lightness-percentile/regional
features failed clean controls on a different development cohort.

Retain the existing five input features and add exactly four statistics: linear
a* IQR, linear b* IQR, population covariance(L*,a*) and population covariance(L*,b*).
Use the existing uint8 OpenCV Lab conversion and conventional Lab units on the
same actual input measurement mask. Minimum1000selected pixels; invalid inputs
are unavailable, never imputed. Constant channels naturally give zero covariance.
No reference, source identifier, severity, target, correction mask or approval
label enters feature computation. Estimation masks, mean Lab/ITA and the frozen
experimental MST lookup are unchanged; this is an additive correction-model
schema experiment, not a newly calibrated MST measurement contract.

Compare only the fixed reviewed ten-source/20pair cohort and its exact ten
held-source/known-duplicate-group folds. Reuse the verified saved five-feature
baseline; fit exactly one nine-feature candidate per fold using identical
depth3/seed42/minimumleaf1/unweighted settings and targets. No feature/depth search,
skip rule, arbitrary cutoff, additional source selection or counterfactual probes.
If any candidate feature is unavailable, preserve the failure and do not silently
reduce the cohort. No outcome-based feature substitution or rerun selection.

Evaluate identical application and reference-scoring masks. Report no correction,
saved baseline, candidate and reference-informed oracle separately for all pairs,
clean controls and distortions, plus per-input changes. Original gates remain:
overall error strictly improves against no correction AND zero unchanged-control
harm. Improvement against baseline alone is insufficient. No runtime promotion
from this exposed-development comparison, even if the numerical gate passes.
Retain all five rejected source IDs,21held sources and51803minor-hole concern.
MST remains experimental, lack ofMST10/dark-group coverage remains; photographic
references are not calibrated skin truth. Source grouping is not proven person
separation. Covariances can be sensitive to illumination/support contamination;
they are not automatically causal distortion indicators or validated confidence.
