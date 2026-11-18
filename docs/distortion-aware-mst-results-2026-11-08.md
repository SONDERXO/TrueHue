# Distortion-aware MST input comparison — 8 November 2026

The estimator became more stable under the synthetic distortions but less
accurate on clean photos. Correction still changes four clean photos and does
not improve consistently. **The candidate is not adopted. The correction model
is not finished.**

## Fixed intervention

The thesis uses estimated skin tone as a correction input. The saved aligned
pipeline fits its contextual MST calibration on22clean development photos, then
applies it to distorted measurements. A saved-prediction check showed a sizeable
appearance shift: core-distortion score MAE1.95development/2.06later versus
0.65/0.75on clean inputs. This motivates one supervision comparison, not a claim
that MST drift caused the correction errors.

Under the user's standing development instruction, fitted exactly56matching
ITA+Lab ridge1 calibrations on the227available conditions from those same22clean-
reference sources. Each source retains its existing continuous publisher score
across its synthetic variants. Every publisher group receives total fitting
weight1. Full/single/pair exclusions are retained; no later labels enter fitting.

Only the MST feature changes in the aligned parent's12inputs. Same native masks,
alpha, fitting rows, action libraries, pixel costs, depth3/minleaf1/greedy settings
and clean constraints. Exactly11joint action trees were fitted. The rejected
face-local context is not used. No new masks, sources, labels, targets, gate,
image-model forwards, dependency installation or scientific admission.

## Skin-tone estimate results

All values are continuous source-score units, not integer-category accuracy.

| Cohort/input | Parent score MAE | Candidate score MAE | Predictions |
| --- | ---: | ---: | ---: |
| Development clean | 0.650 | 1.419 | 22 |
| Later clean | 0.751 | 1.643 | 18 |
| Development core | 1.948 | 1.582 | 161 |
| Later core | 2.063 | 1.812 | 132 |
| Development stress | 3.104 | 1.965 | 63 |
| Later stress | 3.198 | 2.356 | 55 |

Mean absolute estimate drift from each paired clean prediction falls1.717→0.651
in development core147pairs and1.797→0.657later128pairs. Stress drift falls
3.267→1.499development58pairs and3.274→1.700later52pairs. Remaining available
distortions lack a usable clean measurement and are not silently assigned one.
The parent clips12/8core predictions and20/29stress predictions at1or10; the
candidate clips none. Clean errors worsen under both image and equal-key means.

Lower drift and less clipping therefore do not establish better tone estimation.
The model can trade away clean tone discrimination for distortion stability.
This experiment does not establish a validated, lighting-invariant MST feature.

## Same-support correction results

| Measure | Aligned parent | Candidate |
| --- | ---: | ---: |
| Changed clean photos,development | 2/22usable | 2/22usable |
| Changed clean photos,later | 2/18usable | 2/18usable |
| Development core RGB MAE | 8.02869 | 8.02686 |
| Later core RGB MAE | 9.75667 | 9.79218 |
| Development core harms | 1/176scored | 2/176scored |
| Later core harms | 5/144scored | 5/144scored |
| Development stress RGB MAE | 39.22194 | 39.10416 |
| Later stress RGB MAE | 43.94616 | 44.08910 |

Development core CIEDE2000 worsens3.44055→3.45177 despite its tiny RGB improvement;
later core worsens4.18859→4.23253. Development stress CIEDE improves15.25632→15.16204,
later stress worsens16.68433→16.80807. These are relative photographic differences
on unchanged reference regions, not calibrated physical skin colour.

The candidate's clean errors are case_20(4.31RGB MAE),case_28(24.19),eval_07(7.13)
and eval_16(9.89). The former case_02/eval_13/eval_15clean errors disappear, but
three different clean errors arise and the forehead darkening persists. Counts
alone do not establish preservation of the same photos.

Across all11trees, MST is now selected10times, but sceneLmedian still appears43
times. Actual feature use does not establish useful skin-tone conditioning or
fairness. The zero-clean requirement fails in both cohorts; development core
harm count and later core/stress error requirements also fail.

All756attempts remain,451measurements are available and560conditions have scoring
regions.14clean measurement failures are not counted as learned clean safety.
Folds/conditions/pixels are not independent people; publisher identifiers are
not verified cross-dataset identity. All groups have been exposed during
development. No independent final evaluation is claimed.

## Verification and review

Scripts593–596 implement this single cycle. The evaluator/verifier reuse frozen
589/591/592implementations with explicit model/output redirection. The inherited
filename `face_local.png` is only an implementation filename; this model uses
whole-scene context with changed MST supervision. Gallery titles identify paired-MST.

Independent training verification checked all56normal equations,2270nested
feature rows,220repeated fitting-clean constraints,165nodes,53764candidate split
options and756predictions. Reused fitting memberships,costs,actions and all11
non-MST input entries match the parent. Verification performs no refits.

Independent output verification reproduced756RGB8outputs,560regional and756scene
metric records, checked protection/outside-support equality and summary counts.
Viewed59fixed boards in15contact sheets and4explicitly outcome-selected worst
clean/core boards. Fragmented edges, residual forehead darkening and a severely
brightened distorted face remain visible. The focused estimator/tree/blending
suite passed30tests in2.92seconds using generated software fixtures, not extra
research-data fits or scientific validation.

Private artifacts: `outputs/distortion_aware_mst_action_models_v1` and
`outputs/distortion_aware_mst_action_comparison_v1`. Previous artifacts and app
assets remain unchanged. No sharing, contact, publication, commit or push.

## Next development boundary

Close this fixed comparison without a ridge-weight, feature or severity sweep.
The thesis's skin-tone input must retain useful tone information as well as
stability; replacing it with a more invariant but less accurate estimate does
not finish the correction model. The unresolved work remains clean-photo action
selection, usable skin support and defensible skin-tone evaluation. The result
does not prove impossibility or make a new dataset/annotation round mandatory.
