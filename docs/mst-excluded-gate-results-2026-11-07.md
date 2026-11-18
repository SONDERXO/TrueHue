# Gate-only MST exclusion: results and decision

7 November 2026. User approved **Run this fixed comparison**. Completed the
[fixed protocol](mst-excluded-gate-protocol-2026-11-07.md):11gate fits with the
estimated-MST coefficient constrained to exactly zero. ITA/MST remain in the
correction predictors. **The candidate fails clean preservation and is not
adopted.** No Android or desktop runtime changes.

## What changed

One extra coefficient bound, `gate_coefficient[input_mst_score]=0`, is added to
the clean-constrained signed-benefit objective. All12input fields, training
means/scales/weights, alpha1, benefit labels, original fitting/exclusion sets,
clean score<=-1e-6constraints, SLSQP settings and strict score>0decision stay fixed.
Correction predictors, MST estimator, masks, targets and controls are unchanged.
Exactly10nested held-group gates and1full397row gate were fitted. No retries,
MST/control/target fits, image-model inference, new photos or annotations.

All11MST coefficients are exactly zero. All290repeated fitting-clean constraints
pass; these repeat the same29originals across configurations, not290independent
photos or people.1281saved-feature perturbation checks confirm that changing
MST from1to10cannot change this gate's score/action. It can still affect the
unchanged correction predictors, as intended.

## Held-group working256 comparison

RGB MAE is in0–255codes on the original saved measurement region. Lower is better.
These are development-exposed groups, not independent final validation.

| Outcome | Retained gate | Signed, no clean constraints | Prior clean-constrained | MST-excluded clean-constrained |
| --- | ---: | ---: | ---: | ---: |
| Clean RGB MAE |0.05580|1.29554|0.89681|0.88109|
| Core RGB MAE |13.51194|9.62971|11.25878|11.25692|
| Stress RGB MAE |23.75824|23.04107|23.17349|23.66015|
| Changed clean photos |3/29|27/29|7/29|5/29|

Core harms versus unchanged input:9/232retained,15/232prior constrained,
13/232MST-excluded. Stress harms:1/145retained,2/145prior constrained,
2/145MST-excluded. The new candidate blocks3previous constrained clean failures,
retains4and introduces1new clean failure. The most severe clean darkening remains
RGB MAE23.23997with unchanged gamma1.42861and gains1.01866/0.99637.

Availability remains29/30clean,232/240core and145/150stress reference-scored;
397feature predictions,9undefined-ITA unchanged fallbacks and14original-failure
attempts. No fabricated numeric errors are assigned to missing references.

## Later fallback-native224 comparison

| Outcome | Retained gate | Signed, no clean constraints | Prior clean-constrained | MST-excluded clean-constrained |
| --- | ---: | ---: | ---: | ---: |
| Clean RGB MAE |0.02774|3.23507|0.72605|0.10157|
| Core RGB MAE |17.42631|11.64646|14.06100|13.99617|
| Stress RGB MAE |36.22723|36.68627|36.10039|36.72705|
| Changed clean photos |1/23|23/23|3/23|4/23|

The severe orange-face clean correction is blocked; its former15.38955RGB MAE
becomes0. The other2prior constrained clean failures remain, and2new clean
failures appear. This reduces average clean error but increases the count of
unwanted clean edits from3to4. No numerical/perceptual tolerance was substituted
for the zero-change requirement.

Core harms:2/184retained,5/184prior constrained,6/184MST-excluded. Stress harms
remain0/115for these three gates, but the new gate misses more useful correction
in some stress cases: mean stress error worsens. Lower mean core error does not
override clean failures or hide the added individual harms.

## Keep mask-support conditions separate

Each row gives retained / prior clean-constrained / MST-excluded RGB MAE.

| Native224 condition | Clean | Core | Stress |
| --- | ---: | ---: | ---: |
| Borrowed original masks |0.02774 /0.72605 /0.10157|15.42751 /11.04477 /10.97967|24.11074 /24.12117 /24.80358|
| Actual-input masks |0.02774 /0.72605 /0.10157|17.74503 /14.37973 /14.31490|37.71315 /37.58630 /37.86641|
| Detector-fallback masks |0.02774 /0.72605 /0.10157|17.42631 /14.06100 /13.99617|36.22723 /36.10039 /36.72705|

These23clean outputs are identical across all three support conditions, not69
independent clean observations. Native reference availability remains23/24clean,
184/192core and115/120stress. Feature availability remains318/275/291across the
three support conditions. Their errors are not pooled with working256 results.

The previously recovered mild-warm focal case still receives the harmful fixed
controls under detector fallback. Predicted benefit remains+7.53768; full-scene
error increases2.01958→2.05803. Its original facial reference mask is unavailable,
so it remains outside facial-reference averages. Blocking the orange clean case
does not mean the earlier recovered failure is fixed.

## Predeclared screen and interpretation

- Zero changed held-group clean photos: **fail**,5/29changed.
- Zero changed later clean photos: **fail**,4/23changed.
- Lower core error than the retained gate on working256: **pass**.
- Lower core error than the retained gate on fallback224: **pass**.

The overall necessary development screen fails. The fixed feature exclusion has
different effects across cases; it is not a general clean-preservation repair.
No next coefficient, threshold, margin, loss, weight or capacity setting is
selected automatically from these exposed results. This does not prove the task
impossible or that another dataset is necessarily required.

The persistent severe brightness correction remains a concrete unresolved
mechanism. Any further fitting needs a separately justified bounded intervention;
this comparison is closed with the retained research baseline unchanged.

## Verification, bookkeeping and visual review

The fitting runner saved all11models but then exited with a post-save checksum
helper error (`str` passed to a Path-only helper). The completed models and
original runner were preserved. Direct checks of all saved models/source hashes
and the independent full verifier passed **without rerunning any fit**. The
completion record is `postfit_completion_PRIVATE.json` in the model directory.
Do not treat the runner's exit as evidence of missing models or silently refit.

Independent checks:11KKTsystems on free coordinates,11zero coefficients,
290fitting constraints,3573nested gain labels,12852inner fitting-key exclusions,
1281unchanged control/action checks and2828render/metric/RGB replays. CIEDE2000
values are inherited only from byte-identical previously checked outputs.
1281additional gate-only MST-invariance checks pass. Source hashes match.

Focused suite: **30tests passed in6.21seconds**, including3new generated-data
tests for exact MST independence, fitting-clean decisions, unchanged frozen
inputs, restricted objective bounds and invalid schema/constraints. Generated
test fits are separate from the11photographic gate fits; no other real-data fits.

Viewed all61fixed comparison boards via16contact sheets, plus4explicitly
outcome-selected extra-error boards. Dark forehead patches, fragmented supports,
hard boundaries, residual casts and unchanged severe stress inputs remain.
An extra-error selection can be an equal-error case; it is not automatically
additional harm. This was not blind professional appraisal or new skin truth.

Private outputs: `mst_excluded_clean_gate_models_v1`,
`mst_excluded_clean_gate_comparison_v1`, `mst_excluded_clean_gate_assessment_v1`,
`mst_excluded_clean_gate_review_v1`. Scripts544–548; isolated module
`mst_excluded_clean_gate.py`.1428records reuse54originals; conditions/folds are
not independent people. All admissions/adoption remain false. No runtime
integration, contact, external sharing, publication, commit or push.
