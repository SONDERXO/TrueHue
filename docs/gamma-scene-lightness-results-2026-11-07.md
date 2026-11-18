# Removing scene brightness: clean protection, little core recovery

7 November 2026. Completed the user-authorized fixed
[gamma scene-lightness comparison](gamma-scene-lightness-protocol-2026-11-07.md).
**Not adopted. The correction model remains unfinished.**

## What we changed

Refitted only the brightness predictor without the three whole-scene lightness
percentiles. ITA, MST, facial Lab, scene chroma ratios and clipping measurements
remain. The full 12-input interface is unchanged; excluded gamma fitting columns
are zero and cannot appear in its splits. Exactly 11 gamma fits were completed:
ten existing held-group folds and one full model.

The colour predictor, tree settings, targets, fitting rows, masks, recipes and
old gate stayed fixed. The previous joint policy also stayed fixed: clean fitting
leaves return exact neutral controls, and out-of-range queries receive no
correction. Its range check still uses all 12 original inputs, including the
three excluded gamma predictors. This deliberately avoids combining feature
removal with a range-rule relaxation.

## Results in simple terms

The candidate preserves all 29 development and 23 later scored clean photos,
both with and without the gate. It also removes almost all useful correction
of the standard distortions. With the gate, **no core-distortion photo changes**
in any of the four saved evaluation contexts.

Mean per-photo RGB error in existing reference regions; lower is better:

| Comparison | Retained model + gate | Previous joint policy + gate | Revised joint policy + same gate |
| --- | ---: | ---: | ---: |
| Development clean, 29 scored | 0.06 | 0.00 | 0.00 |
| Development core, 232 scored | **13.51** | 15.05 | 20.73 |
| Development stress, 145 scored | **23.76** | 45.91 | 44.35 |
| Later clean, 23 scored | 0.03 | 0.00 | 0.00 |
| Later core, 184 scored, fallback masks | **17.43** | 19.34 | 21.39 |
| Later stress, 115 scored, fallback masks | **36.23** | 50.66 | 50.29 |

- Core errors equal doing nothing with the gate. All 47 previously beneficial
  joint-policy development core actions and all 18 later core actions are lost.
- Ungated core recovery is also weak: MAE 20.15 development and 21.25 later
  fallback. Only five development core attempts and two later fallback core
  attempts change; one of the latter lacks an original facial reference.
- Stress improves slightly versus the previous conservative policy, but remains
  much worse than the retained research model. Gated stress changes 23 development
  attempts and 17 later fallback attempts, versus 21 and 12 previously.
- The revised policy has zero reference-scored RGB harms versus input in every
  context, with and without the gate. This narrow development result reflects
  limited intervention and does not establish general safety or adequate recovery.
- Relative CIEDE2000 and equal-key means show the same main trade-off. Gated core
  CIEDE2000 worsens from 5.73 to 7.68 development and 7.32 to 8.02 later fallback
  against the previous policy. Gated stress improves slightly, 17.58 to 17.13 and
  19.47 to 19.30. Complete per-context metrics are preserved privately.

## Why the candidate stops correcting core inputs

The revised tree places many clean and distorted fitting rows together. The
unchanged clean-leaf rule then makes those leaves neutral. In the full fit,
three gamma leaves contain all 29 clean fitting originals and many ordinary
exposure-distortion rows. Their raw gamma means are approximately 1.1193,
0.7980 and 1.4529, but the existing protection policy replaces each with exactly
1. The gains policy can likewise neutralize its clean-containing leaves.

The saved action ledger accounts for every reference-scored core condition:

| Why no correction occurs | Development, 232 | Later fallback, 184 |
| --- | ---: | ---: |
| Outside a reached leaf's fitting ranges | 94 | 80 |
| Inside ranges, but full controls exactly neutral | 133 | 97 |
| Non-neutral controls rejected by existing gate | 5 | 1 |
| Missing usable input features | 0 | 6 |

Consequently, changing the gate alone cannot restore most of this candidate's
lost core recovery. Almost all controls have already become neutral before
the gate makes its decision. This is a result for this fixed depth-three model
and protection policy, not evidence that skin correction is impossible.

The previously failing later clean photo now reaches a clean-containing gamma
leaf and also fails one original scene-lightness support range. Its bright patch
is gone. The earlier severe clean darkening case is also unchanged, with a clean
gamma leaf and support abstention. The recovered warm fallback case is blocked
too; its original facial reference remains unavailable. These case fixes do not
outweigh the loss of standard-distortion recovery.

## Verification and scope

Eight focused tests passed in 5.17 seconds. The new tests use one tiny generated
gamma fit to check excluded-feature invariance, raw means and frozen gains; the
research experiment performs only the specified 11 gamma fits. No gain, gate,
MST or target fits, new image-model inference, dataset search or annotations.

Independent verification checks all 11 gamma artifacts, fitting exclusions,
normalization, raw target leaf means, forbidden splits, unchanged gain heads,
saved gates, input/reference/mask identity and previous-policy records. It
reconstructs support metadata, actions, RGB8 outputs, metrics and outside-mask
pixel protection. Exact completion counts are recorded in the private
`verification_PRIVATE.json`; the action ledger, equal-key means, harm counts and
23 duplicated native clean outputs are checked in `assessment_PRIVATE.json`.

All verification checks pass: 88 raw gamma leaf means across 3,570 fitting-row
routes; 176 support-leaf metadata checks; 290 repeated fitting clean occurrences;
1,281 action, raw-gamma invariance and frozen-gate checks; 2,828 RGB8 output
replays; 2,744 reference metric checks; 2,016 scene metric checks; and 6,809 bound
source hashes. Viewed all 63 fixed boards through 16 contact sheets. No extra
outcome-selected image boards were added for this comparison.

Scripts 555–558; policy module
`src/model_training/gamma_scene_lightness_restriction.py`. Private outputs:
`outputs/gamma_scene_lightness_models_v1` and
`outputs/gamma_scene_lightness_comparison_v1`. All 1,428 saved attempts remain,
including measurement/reference failures. They come from 54 original photos;
conditions, native mask alternatives and folds are not independent people.

The gate was not retrained for these controls. Its original fitting exclusions
are verified, but its transferred objective remains a limitation. No claim of a
matched-gate evaluation or independent final holdout is made.

## Decision

Close this fixed feature-removal comparison. Do not adopt it or automatically
remove more inputs, relax support ranges, change leaf protection, increase tree
capacity or retrain gates. A useful next design must preserve clean controls
while retaining a distinction between clean and distorted fitting rows; simply
deleting scene-brightness cues under the existing policy does not achieve that.
No next fit is selected or started by this result.

No desktop/Android update, scientific admission, sharing, contact, publication,
commit or push. Earlier models and outputs remain intact. Small exposed cohorts,
synthetic lighting, partial/uncertain masks, hard boundaries and reconstruction
metrics that do not measure true skin colour or naturalness remain limitations.
