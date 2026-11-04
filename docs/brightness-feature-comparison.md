# Fixed brightness-feature comparison

24 October 2026. The frozen ten-feature model improved over the four-feature model on this development comparison, but did not beat leaving inputs unchanged overall. Keep it experimental; runtime model unchanged.

Same31 pairs and eight source/known-duplicate-group folds. Both models use depth3, seed42, minimum leaf1, identical targets and correction/scoring masks. Only the input schema changes: baseline mean Lab/ITA versus those four plus six frozen brightness-distribution/regional measurements. No feature selection or depth search was performed after seeing results.

| Held-source probes | No correction | Baseline4 | Brightness10 |
|---|---:|---:|---:|
| All31 | 5.46 | 7.80 | 6.15 |
| Shared22 | 5.16 | 8.16 | 6.61 |
| New9 | 6.20 | 6.92 | 5.01 |
| bright_warm | 8.36 | 9.91 | 7.80 |
| color_shift | 7.43 | 9.49 | 9.17 |
| dark | 12.68 | 7.91 | 6.09 |
| identity_control | 0.00 | 6.30 | 4.83 |
| mild_bright_exposure | 2.83 | 7.13 | 4.80 |

Lower CIEDE2000 is better; this measures reconstruction relative to source photographs, not calibrated skin-color truth. Equal-source averages improved7.77 to5.96, but no correction scored5.13. Four source averages improved, three worsened and one was unchanged versus baseline4. Improvement is not consistent across people.

All8 unchanged inputs still receive unwanted correction. Their average error decreased6.30 to4.83. Mild-input error decreased7.13 to4.80, with4/8 harmed relative to no correction versus5/8 at baseline. Color-shift inputs still score worse than no correction. These weaknesses rule out automatic adoption.

Codex inspected all31 comparison boards. Recovery improved on some darkened inputs and unwanted color shifts reduced in some controls, especially22454, but51739 remains strongly overbrightened. Patch boundaries and excluded-feature contrast remain visible. This is a qualitative development inspection, not expert MOS.

## Verification

Saved16 fold models and93 held-source prediction records. Every baseline4 prediction and image metric exactly reproduces the previous comparison. Independent replay checked saved training and held-source predictions and recomputed training parameter MAE with each model's actual4/10-column schema. Fitting/evaluation pairs, sources and duplicate groups are disjoint; original hashes and outside-support pixels are unchanged. Existing suite: **464 passed**.

## Next recommendation

Keep the ten-feature candidate and freeze this result. Audit the remaining unchanged/mild failures against the ten-feature model's actual leaves and its input-only mask coverage before adding features or tuning. Identify whether errors persist in the same wrong-distortion branches or are newly introduced, and preserve examples where baseline4 was better. That audit should guide the next data or measurement change; do not tune a correction/skip threshold on these31 probes or present repeated development comparisons as independent validation.

No final all-source model, production integration, external/reserved evaluation or human-label promotion occurred. Four-feature runtime unchanged. The ten-feature extension remains a recorded proposal-method distinction; operational MST, face-and-neck correction, final dataset eligibility and final thesis evaluation remain pending.

[Full metrics and provenance](../outputs/brightness_features_sourcecv_v1/summary.json) ? [All31 image comparisons](../outputs/brightness_features_sourcecv_v1/review-index.md) ? [Independent replay](../outputs/brightness_features_sourcecv_v1/independent_verification.json)

Follow-up: [remaining-control and input-mask diagnosis](brightness-control-diagnosis.md).
