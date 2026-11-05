# Actual distorted-input masks: recovery remains useful, object protection drifts

5November2026. The authorised check is complete on all168 fixed cases from the
same12 FFHQ sources. The pipeline now measured/masked the actual distorted
images instead of borrowing original masks. **Core recovery remains close to
the reference, but masking changes increase error and can reintroduce objects.**

[Open the comparison gallery](../outputs/ffhq_distorted_input_support_v1/review.html).
Panels: reference; distorted input; new correction green/lost source support
pink; previous fixed-alpha fitted recovery; new input-alpha fitted recovery.
Both recovery columns are target-aware oracle fits, not trained predictions.

## What was executed

The [protocol](distorted-input-support-protocol-2026-11-05.md) was recorded before
inference. All168 existing RGB8 cases, including12clean controls, were retained.
There were no new photographs, variants, severity groups or replacements.
The common engineering severity preset remains unrelated to skin/MST labels.

The existing single-face detector, ordered landmark helper, semantic parser and
nostril exclusions ran on actual input pixels.167parent attempts succeeded.
48879/stress_exposure_over failed at the nostril-measurement stage with
`Nasal-base geometry unavailable`. It remains a failed case, not a replacement.
The other167 aligned inputs received one fixed CPU FaceOcc pass each, all
technically successful. Their preferred-service measurements/statistics/features
were saved, with skin validity unverified, no calibration/training admission
and MST unavailable. Existing beard/hair/lighting limitations remain.

Correction masks/neck association, object veto, clear-lens approximation and
inward alpha were rebuilt from each distorted input. Prior explicit clear-lens
choices for16061/59807 and opaque sunglasses29617 were retained; other cases
used uncertain handling. This is not automatic glasses classification. No source
mask or original protection was used to repair/clamp the new masks.

There were155new nonclean local target fits and12clean neutral shortcuts.
Recovery fits used actual input alpha and the intersection with original scoring
support, as required by the unchanged solver. **Final scores use the entire
original scoring region, including pixels the new mask misses.** The failed
case's operational output is explicitly unchanged input, included in all-case
averages; it has no fitted target or successful-recovery claim.

## Recovery on original, fixed scoring regions

RGB MAE is mean channel error on the0–255 scale. The original fixed-alpha oracle
is the frozen422 result. Every layer's current mean includes all its attempts,
including the stress failure, rather than a successful-only denominator.

| Layer | Recovery available/attempted | Input RGB MAE | Fixed-alpha oracle MAE | Actual-input-alpha oracle MAE |
|---|---:|---:|---:|---:|
| Clean | 12/12 | 0 | 0 | 0 |
| Core | 96/96 | 18.665 | 0.135 | 0.591 |
| Composite stress design | 59/60 | 53.593 | 11.034 | 13.526 |

All12 clean masks reproduce the saved source correction AND measurement masks;
outputs remain exactly identical. Mean current relative CIEDE2000 is0.312 for
core and8.886 for all60stress attempts. Core has no regression against input
under either metric; worst core case MAE is1.665codes on48879/combined_cool_under.
These results do not establish automatic correction or independent generalisation.

Four current stress recoveries worsen in CIEDE2000 versus input:
32685/stress_exposure_over(16.466→18.582),
32685/stress_combined_over(16.902→19.127),
53146/stress_exposure_over(20.136→20.381), and
48879/stress_combined_over(16.329→24.186). The earlier fixed-alpha regressions
are preserved separately; the failed48879/stress_exposure_over is not counted
as a successful recovery or silently erased.

## Mask/measurement consistency, not segmentation accuracy

| Layer | Correction mean IoU with saved source | Measurement mean IoU | Comparison denominator |
|---|---:|---:|---:|
| Clean | 1.0000 | 1.0000 | 12/12 |
| Core | 0.9744 | 0.9719 | 96/96 |
| Stress | 0.9444 | 0.9299 | 59/60 |

Both sides of these comparisons are predictions, not ground truth. High average
IoU does not certify actual skin or complete object protection. All96 core
masks lose some original correction pixels (12–863per case). All59 available
stress masks lose some (28–2079). These regions stay in the recovery score.

Every core recovery changes at least one previously protected pixel (median96.5,
maximum1714);58of60stress attempts also do so. Mean RGB change outside original
support is0.048codes for core and0.439 for all stress attempts. Some disagreement
can be a harmless boundary shift or originally mistaken protection; these counts
are **not certified numbers of corrected object pixels**. New-veto pixels are
unchanged exactly, but the new veto can miss an object that the old one detected.

## Visual findings and decision

The assistant inspected the24predeclared boards: combined_cool_under and
stress_combined_under on all12 sources at256px. Core recoveries are generally
close, but hairline/jaw/neck transitions move.32685's core support extends onto
the right collar area;49131 shows a jaw/neck transition. In29863's stress-under
case, the mask clearly re-admits the white head covering and recovery visibly
changes its colour.16061's stress forehead support leaves a dark untreated edge.
Severe stress face posterisation and eye/mouth artifacts remain. Other glasses,
microphone/hand and hair boundaries remain uncertain; no complete-protection claim.

The [assessment](../outputs/ffhq_distorted_input_support_assessment_v1/assessment.json)
contains all12 assistant notes, aggregate denominators and the retained failure;
the [168-row CSV](../outputs/ffhq_distorted_input_support_assessment_v1/cases.csv)
includes measured input ITA where technically available, with MST empty and
training admission false. This is not human/expert review of all168outputs or
annotation truth. Photo attribution remains linked in the gallery.

This answers the next model-development question: source masks cannot simply
stand in for input-derived masks. The recovery operator is still effective on
the fixed core recipes, but boundary/object instability is now a demonstrated
limitation, particularly under severe distortion. Do not silently intersect
with the source mask in the application, filter to easy cases or claim this is
fixed by a good mean score. No new repair/threshold/model search was performed.

Before training admission, resolve the observed object/neck/measurement eligibility
issues under a justified scope. The core target evidence can be retained as
conditional capacity, while stress cases remain failure diagnostics. Reliable
compatible MST, person grouping, source/reference quality and final features/
evaluation are still needed for the retained full tree. No fake label or MST
omission was introduced; ITA-to-MST remains deferred.

## Verification

Scripts424–426 save stage attempts, inputs/categories/landmarks, aligned inputs,
logits, measurement reports/features/masks, actual correction/neck/veto/alpha,
fits, operational outputs and the full gallery in new packages. Old artifacts
and raw photos are unchanged.167saved service/correction replays,168all-attempt
metric checks,12clean mask parities, renderer parity and protected/outside-new-
support invariance passed. Verification used no new model forwards or refits.
168CSV/JSON rows match; input and artifact manifests were verified unchanged.
26focused tests passed in5.07seconds, including lost-region scoring, spill
accounting and empty/invalid support; not a full-suite run or scientific validation.

Verification record:
`outputs/ffhq_distorted_input_support_verification_v1/verification.json`.
No tree/MST training, admissions, new variants, publication, contacts, runtime
switch or submitted/working thesis edits. The panel register records the actual-
input experiment and limitations without claiming panel approval.
