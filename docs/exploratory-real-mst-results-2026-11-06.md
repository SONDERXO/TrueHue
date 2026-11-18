# First exploratory real-data contextual MST result — 6 November 2026

The user explicitly selected **Run the exploratory real-data experiment**.
The bounded experiment is complete:20real ridge fits across10publisher-key-held
folds, using all30fixed new-source photos. This is the first real-data fit of
the contextual estimator in this sequence, not another generated-data result.
No photographic correction tree or production estimator was trained/exported.

## Fixed experiment

Use only `stellenbosch_new_subjects_v1`:10publisher subject keys, three fixed
conditions each, one frozen acquisition/measurement contract. Do not pool the
earlier30, use the six hand-marked references as a fitting cohort or select only
the visually plausible cases. All29available measurements enter the appropriate
training folds; the landmark failure remains unavailable. Source decimal scores
are preserved. Known skin omissions, beard/object inclusion and exposure remain.

`src/ita_estimation/exploratory_real_mst.py` is a separate explicitly unadmitted
evaluator. It reuses the fixed weighted ridge arithmetic and prediction/metric
functions without changing the qualified evaluator or declaring admission.
Every original calibration/training admission flag stays false. Explicit
exploratory authorization permits this diagnostic, not scientific eligibility.

Each fold holds every photo of one publisher key out of scaling, fitting and
baseline construction. Each training key has total weight1in scaling and ridge
fitting. Fixed alpha1, intercept, four ITA/Lab features; fixed ITA-only ridge
ablation; median of training-key scores as baseline. No lighting code or source
label enters inference features. No search, new image inference, mask repair,
favorable-subset fit or all-data deployment refit.

## Predictive results against publisher decimal scores

| Method | Predictions / attempts | Image MAE | Equal-key MAE |
| --- | ---: | ---: | ---: |
| ITA + Lab ridge |29/30|0.7314|0.7448|
| ITA-only ridge |29/30|2.3655|2.4126|
| Training-key median |29/30|2.9655|2.9900|

Errors are absolute score differences on the continuous1–10source-score scale,
not percentage accuracy or integer-category error. MAE is calculated on the29
available matched predictions; the failed attempt has no fabricated prediction
or numeric penalty. Attempt/unavailable counts are reported separately. For a
matched comparison the median baseline uses the same availability mask, although
it could mathematically return a value without image measurements.

| Reporting condition | Available / attempted | ITA + Lab MAE | ITA-only MAE | Median MAE |
| --- | ---: | ---: | ---: | ---: |
| F_cool_600 |10/10|0.8004|2.4568|2.9900|
| H_warm_600 |9/10|0.7515|2.2630|2.9111|
| L_warm_600 |10/10|0.6443|2.3665|2.9900|

ITA+Lab raw predictions range1.6742–9.3336; none are clipped. ITA-only raw
predictions range4.8698–6.0810, a narrow range despite smaller within-key
variation. Lower variation alone is therefore not a sufficient estimator
criterion. ITA+Lab within-key ranges span0.1230–1.5127points across the available
photos. These are descriptive development findings, not statistical significance,
causal lighting effects, unseen-cohort accuracy or successful correction.

## Verification

Script479preserved the exact prepared rows and all source/mask/package hashes.
For20saved models, weighted feature means/scales and ridge normal equations were
checked independently. All58held-image linear predictions replay exactly without
refitting. Fold memberships exclude the held publisher key. Saved outputs include
fold coefficients, memberships, prediction ranges, source-score interval and
condition summaries, failure reasons and raw/clipped predictions.

Seven new exploratory-evaluator tests plus15existing contextual tests:
**22passed in0.54seconds**. New tests show that changing held-key labels cannot
change that key's fitted fold, rows remain unchanged, failed outcomes retain
their denominator, and admission/schema/nonfinite/label inconsistencies reject.
These tests perform additional generated fits, not additional real-data fits.
No full-suite, phone test or independent scientific validation is claimed.

Private outputs: `outputs/exploratory_real_mst_results_v1/`, prepared actual
inputs: `outputs/exploratory_real_mst_preparation_v1/`. Script479refuses overwrite.
The user-approved experimental choice supersedes the original protocol's
pending-choice status; its frozen bytes remain unchanged.

## What this changes for correction development

There is now a real predictive result supporting contextual ITA+Lab over the
fixed comparators on this specific development sample. Reliable automatic skin
measurement is still unresolved: the model may exploit recorded colour and
mask artifacts. Small, preselected, development-exposed samples and limited
conditions do not establish calibration adequacy, fairness or generalization.
Publisher keys provide within-release grouping, not cross-source verified
person identities. Source scores are photographic dataset targets, not physical
skin truth. The private data-use conditions remain unchanged.

The next correction-model step is a separately frozen compatible exploratory
correction experiment with nested group-held MST features. Do not transfer this
estimator to FFHQ, a changed mask pipeline or synthetic distortion distributions
without accounting for those changes. No training-label MST substitution or
in-sample MST prediction for held correction subjects. This experiment does not
automatically activate new distortions, correction-tree fits, final-model
admission or an Android update.
