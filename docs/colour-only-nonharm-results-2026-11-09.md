# Colour-only nonharm constraint: results

9 November 2026. **The candidate removes the observed stress harm and preserves clean photos, but loses useful exposure corrections.** It fails the unchanged joint acceptance requirements and is not adopted.

## Implemented change

Completed exactly 11 depth-four correction-tree fits under the [fixed protocol](colour-only-nonharm-protocol-2026-11-09.md). An action is infeasible when it makes any colour-only fitting row worse than identity under saved RGB cost. Clean fitting constraints remain exact; colour equality is allowed. The three recipe labels identify fitting constraints only and are never inference inputs.

Kept the reserved-group fitting matrices, features, costs, actions, frozen MST calibrations and source exclusions unchanged. Reapplied the reserved-clean veto and existing frozen facial exception to each new tree. All fitting clean/colour constraints and reserved clean references also pass after final postprocessing. No masks, DINO models or runtime settings changed.

## Fixed evaluation results

| Check | Original aligned comparator | Previous facial-exception candidate | Colour-nonharm candidate |
| --- | ---: | ---: | ---: |
| Unwanted clean edits, development | 2 / 22 | 0 / 22 | **0 / 22** |
| Unwanted clean edits, later | 2 / 18 | 0 / 18 | **0 / 18** |
| Core RGB error, development | 8.03 | 9.73 | 10.13 |
| Core RGB error, later | 9.76 | 10.36 | 10.98 |
| Core beneficial conditions, development | 106 / 176 | 91 / 176 | 88 / 176 |
| Core beneficial conditions, later | 84 / 144 | 78 / 144 | 75 / 144 |
| Core harms, development / later | 1 / 5 | 0 / 0 | **0 / 0** |
| Stress harms, development / later | 0 / 1 | 0 / 1 | **0 / 0** |

Lower error is better. Benefits/harms compare reconstruction with the distorted input within the same reference scoring region; they do not establish naturalness or true skin colour. The 14 clean measurement failures remain separate unchanged no-ops, not learned safety successes.

Core CIEDE2000 errors worsen from 3.97 to 4.10 in development and 4.29 to 4.48 later; aligned values are 3.44 and 4.19. The core harm/benefit counts agree under both metrics.

Development stress is unchanged: RGB 38.79, CIEDE2000 15.16, 40 / 110 beneficial outcomes. Later stress improves from RGB 43.86 to 43.59 and CIEDE2000 16.84 to 16.77; beneficial count remains 35 / 90. Later stress colour error still exceeds the aligned comparator's 16.68, and stress benefit counts remain below its 45 / 110 and 43 / 90.

There are zero regional RGB or CIEDE2000 harms across the scored clean/core/stress conditions in this reused development evaluation. This is a useful milestone on exposed data, **not** proof of zero real-world harms or acceptable image quality.

## What changed in individual outputs

Thirteen control decisions changed across six originals; 743 other outputs and candidate metric records match the previous candidate exactly. Eleven changed conditions have reference regions; two do not and are not scored as successes.

The known harmful case `eval_02__stress_color_none` now receives identity. Its RGB error falls from 31.53 to the input's 6.67: this avoids damage rather than correcting the colour distortion.

Three useful underexposure conditions from `case_01` and three from `eval_16` now receive identity, losing six core benefits. Some other controls change without losing benefit. The new constraint prevents the model from trading away the fitting colour example, but it changes branch decisions that previously helped underexposed evaluation inputs.

Viewed every one of the 13 changed-decision boards on four contact sheets, rather than choosing only improvements. Existing partial masks and visible facial/neck boundaries remain; no new mask-quality claim follows. No fresh review of all unchanged boards is claimed.

## Verification

- Ten focused tests passed in 9.39 seconds, including the new aggregate-gain/colour-harm conflict and permitted equal-cost action cases.
- Independent greedy replay verified 11 fits, 307 nodes, 272,921 split options, 880 repeated fitting clean constraints and 756 predictions, exact fitting matrix/cost/action/calibration parity, clean veto replacements and frozen exception routing.
- The fitting code and verifier checked 2,383 repeated colour constraints and 220 reserved-clean occurrences after postprocessing. These reuse fitting references across configurations, not independent photos.
- Independent native output replay passed for 756 outputs, 560 regional records, 756 scene records, protection, 20,144 source hashes, colour summaries and transitions. Whole-scene RGB harm counts are also zero across all six cohort/layer combinations. No pixel support or scoring region was changed.

Private artifacts: `outputs/colour_nonharm_models_v1`, `outputs/colour_nonharm_comparison_v1`. Experimental implementation is isolated in `src/model_training/colour_nonharm_action_tree.py`; the original fitter and app are untouched. Scripts 658–662 preserve previous artifacts. Model traces/costs describe pre-veto fitting; final predictions include the explicitly recorded postprocessing.

## Decision

Keep this candidate frozen as evidence that the fitting nonharm intervention transfers to the observed stress failure. It still fails the original comparator's core-error and benefit-count requirements, so it does not qualify for adoption or final-holdout access. Do not weaken constraints, change recipe subsets, tune weights/depth or launch a follow-up sweep automatically.

Next, a saved-tree comparison can identify whether the six lost underexposure benefits arise from a blocked mixed leaf or a changed upstream partition. That diagnosis requires no new fit. It should precede another model intervention.

The final eight-group, 24-photo holdout remains byte-unread. No DINO inference, app integration, external sharing, dataset/annotation expansion or scientific admission occurred.
