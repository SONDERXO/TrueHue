# Remaining ten-feature overcorrections

24 October 2026. The extra brightness measurements helped some cases, but the largest persistent errors still reach the same wrong-distortion training examples. No retraining, threshold tuning or runtime changes were made in this audit.

## What the traces show

- Twelve unchanged/mild probes remain worse than leaving the input alone; three remain better and one earlier failure (22454 mild) is now better. No previously better mild probe became a new failure.
- Four of sixteen controls have higher error than baseline4, including one mild probe that still beats no correction. Higher error than the earlier model and failure relative to no correction are different comparisons.
- All eight unchanged probes still receive unwanted changes. Four mild probes remain harmful.
- Twelve of sixteen ten-feature control predictions come from leaves mixing multiple correction targets; four come from wrong-distortion-only leaves.

| Source/control | Baseline4 error | Brightness10 error | Actual ten-feature leaf |
|---|---:|---:|---|
| 51739 identity_control | 12.89 | 12.89 | dark:2 |
| 51739 mild_bright_exposure | 15.19 | 15.19 | dark:2 |
| 62331 identity_control | 6.35 | 6.35 | color_shift:3 |
| 62331 mild_bright_exposure | 8.18 | 8.18 | color_shift:3 |
| 75027 identity_control | 13.31 | 4.42 | color_shift:2, identity_control:2, dark:1 |
| 6236 identity_control | 1.16 | 2.81 | bright_warm:4, mild_bright_exposure:6, identity_control:4 |

For51739, the final branch uses median brightness and sends both controls to the darkened6236/84897 examples. For62331, the final two decisions use mean b* and send both controls to color-shifted14272/75027/84897. These are the same leaf-member sets as baseline4, despite changed upstream splits. Adding brightness inputs did not change the resulting correction for these four probes.

Only5/16 ten-feature controls fall inside every individual fitting-feature range, versus14/16 with four features. Adding dimensions makes that criterion harder to satisfy; it is not a confidence score, proof of poor joint coverage, or a valid correction-skip rule. Nearest-example distances are exploratory training-fold standardized distances, not validated similarity measurements.

## Mask inspection

Codex inspected all16 input/mask overlays. Each mask has pixels in all four occupied-box quadrants; the smallest quadrant fraction is15.9%. These masks are not tiny or reduced to one visible corner.51739 and62331 retain broad forehead/cheek/jaw coverage. This makes grossly missing support an inadequate explanation for their persistent errors, but does not prove segmentation accuracy or rule out feature bias.

Mask boundaries remain box-influenced, with hairline, eye-edge, facial-hair and lower-jaw uncertainties. Regional halves are image-relative and vary with pose. Green overlays mean selected pixels, not verified skin. No pixels were newly annotated. Actual neck skin is not automatically an error; collar/clothing must be distinguished from the separately requested visible-neck correction scope.

## Recommended next work

Stop adding depth or measurements on these same eight sources for now. Prepare one bounded additional training-source screening batch with a predeclared selection rule, emphasizing a spread of recorded brightness and color and keeping unchanged/mild controls for every eligible source. Use only the remaining training allocation and the append-only exposure ledger; preserve rejected/stress cases and group all variants by source. Do not select or reject sources solely because they make these known failures pass. The aim is broader independent source coverage around the branch confusions; new source screening must precede any fitting.

This is a recommended development step, not evidence that more data will solve the problem. Keep the ten-feature schema frozen while collecting the next evidence and keep final reserved data untouched. Runtime model, human decisions and final cohort eligibility remain unchanged. The extra features/continuous ITA remain recorded proposal-method distinctions; operational MST and face-and-neck support are still pending.

## Verification and evidence

Replayed32 control predictions across16 saved models with their actual4/10-column schemas. Checked fitting/evaluation pair, source and duplicate-group separation, model hashes, exact saved predictions and leaf-target means. Input mask coverage and prior boundary-sensitivity values were retained per case; original artifacts stayed unchanged. **464 tests passed**.

[Full split paths, leaf members, nearest examples and mask measurements](../outputs/brightness_control_diagnosis_v1/summary.json) ? [Masks1](../outputs/brightness_control_diagnosis_v1/masks_contact1.png) ? [Masks2](../outputs/brightness_control_diagnosis_v1/masks_contact2.png) ? [Correction comparisons](../outputs/brightness_features_sourcecv_v1/review-index.md)

Follow-up: [completed bounded training-source screen](brightness-color-source-screen.md).
