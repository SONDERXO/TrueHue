# Refined MST subject-held assessment — 10 November 2026

The authorized fixed assessment is complete. With the user-refined masks, the
ITA-only monotone mapping achieved held-subject **mean absolute error1.6119**
on the publisher's decimal MST-score scale, compared with **2.9900** for the
fitting-subject median baseline. Allten subjects have lower average error than
the baseline, but individual cases and cool-light performance remain weak.
This is developmental mapping evidence, not validated production calibration or
proof of corrected-image quality.

## Fixed execution

Scripts731–732 use the previously prepared30rows and tenfold allocations without
changing data, masks, formulas, roles or mapping direction. Each fold fits the
other nine subjects'27observations with total weight1 per subject and evaluates
allthree observations of the held subject. Exactly ten nonincreasing isotonic
candidate mappings were fitted. Piecewise-linear interpolation and endpoint
clipping follow the frozen design. The comparator uses the median of the nine
fitting subjects, each counted once. No evaluation score enters that fold's fit.

All30 cases receive exactly one held-subject prediction. No all-data calibration,
integer-category thresholds, old calibration reuse, hyperparameter search,
condition-specific model, correction-tree fit or runtime artifact was produced.
The references remain exact publisher decimal scores, not manufactured category
labels. These are historically exposed development subjects, not a blind final
test; the tenfold results do not create ten independent research datasets.

## Results

| Condition | Cases | Mapping MAE | Median-baseline MAE | Better / worse cases |
| --- | ---: | ---: | ---: | ---: |
| F_cool_600 | 10 | 2.5669 | 2.9900 | 5 /5 |
| H_warm_600 | 10 | 1.1595 | 2.9900 | 9 /1 |
| L_warm_600 | 10 | 1.1092 | 2.9900 | 9 /1 |
| All | 30 | 1.6119 | 2.9900 | 23 /7 |

Image-average and equal-subject MAE agree because all subjects have three
observations. Two held inputs lie outside their fitting ITA support and use
explicit endpoint clipping: case22/cool and case29/H_warm. Maximum single-case
absolute error is4.9667. Within-subject predicted-score ranges run from0 to4.9556,
although the reference score is fixed for each subject across conditions.

Cool-condition predictions occupy only4.2333–4.8875 while reference scores span
2.4–9.2. The constrained mapping therefore compresses strongly differing subjects
under that condition. Better aggregate error than a median comparator does not
establish robust skin-tone discrimination across lighting. No condition or
unfavorable case was dropped, and no formula/sign/feature repair is selected.

## Verification

Five generated-data tests pass in14.01s, including the important leakage check:
changing a held subject's reference score leaves that fold's fitted mapping and
median comparator unchanged. Invalid allocation, weighting, mixed-method and
duplicate-case designs are rejected before fitting. These tests use generated
records and are separate from the ten real-data candidate fits.

The independent stdlib verifier reconstructs allten weighted nonincreasing
least-squares solutions using a separate pooled-adjacent-violators algorithm.
It checks fitted values and interpolation, all30 predictions/errors, allfold
allocations/weights, baselines, support/clipping flags, overall/condition/subject
metrics and within-subject ranges. All pass at1e-11 numerical tolerance.
These are deterministic verification replays, not additional candidate searches.

Private plan/results/verification:
`outputs/refined_mst_assessment_v1`. Output creation refuses existing versioned
directories; previous records, audits, design artifacts and all37annotations are
preserved. Code and protocol/input hashes are bound in the execution plan.

## Decision and next boundary

The refined measurements support a better-than-baseline developmental mapping
signal. Cool-light discrimination and individual error still limit its use.
No numerical production acceptance gate was specified for this developmental
assessment; no passing production status is invented after seeing the results.
Calibration/training admission and runtime-adoption flags remain false.

This closes the specific authorized mapping assessment. Do not automatically
change mapping direction, ITA, features, conditions or fit another candidate.
The next substantive readiness review concerns compatible correction references,
feature/support contracts and grouped validation under the chosen manual-assisted
workflow. These MST reference scores do not provide brightness/gamma/gain targets.
Any later correction-tree comparison still needs its own fixed contract and the
unchanged usefulness/clean-preservation requirements. The final predictor must
remain a decision tree with ITA and compatible mapped MST; no family switch or
MST removal is inferred from the limitation.

The too-bright desktop result is unchanged. Its older controls were not replaced
with any fitted mapping here. No source photographs, annotation images/masks,
final24photos or older locked allocation images were opened during this
metadata-only mapping assessment. No image-model calls, acquisition, external
contact, uploads, commit, push, Android or active-runtime changes occurred.
