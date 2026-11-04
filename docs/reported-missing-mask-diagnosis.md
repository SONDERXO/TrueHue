# Missing-mask report: 31367

29 October 2026. User identifies 31367 as the source described as "Very bad.
No face mask detected." Reproduced detection on the exact saved square256
reference with unchanged YuNet weights and confidence 0.85: **zero detected
faces**. The original failure occurs at face detection; skin-mask computation
is never reached. Do not describe this as a successful empty mask or fix it by
altering skin-color thresholds.

The inspected source is a tightly cropped, occluded side-profile scene with
multiple visible facial regions. This visual observation is not a claim that
the detector found multiple faces: its actual count is zero. Keep the source
excluded under the single-face requirement and preserve both earlier human
rejections. No forced rectangle, selected person, lower confidence threshold,
replacement source or stale ITA was introduced. A diagnostic page now explains
the face-detection failure directly instead of displaying an empty overlay as
if mask generation succeeded. Original historical review pages remain intact.

The active IDE file `focused_mask_review24_v1/review.html` is the original
baseline review. Later candidate pages are separate experiments, and none has
replaced the active calibrated mask. Failure explanations should therefore
identify both the source and stage rather than imply a mask candidate was
deployed.

## Color-rule diagnostic on the same training references

Separately compared the detailed proposal's YCrCb-only rule against the current
HSV AND YCrCb rule, using exactly the existing Cr/Cb thresholds, morphology,
saved facial geometry, component ordering and exclusions. No new landmarks,
threshold tuning, parser model, MST calls or correction fitting.

Both methods have 16 technical-support cases, 6 unavailable-geometry cases and
2 insufficient-color cases. Neither previously insufficient case is rescued:
55166 remains empty and monochrome-rejected, and 14385 remains empty. The six
unavailable cases are 43909, 34898, 13718, 30236, 31367 and 20653. Some other
masks change, which is not evidence of improved coverage or purity. This result
does not justify activating YCrCb-only or transferring old MST thresholds.

All saved AND-arm masks were reconstructed exactly and anatomical containment
checked. The full suite passed **742 tests in 15.54 seconds**; the revised
brightness/chroma and invalid-input unit checks separately passed 3 tests in
0.45 seconds. The reserved training check, development-validation and final test
remain closed; no additional photo review is requested in this stage.

For model progress, this source should remain a documented input rejection.
Do not repeatedly tune the correction model or masking policy to make an
unsuitable detector-failed training reference pass. A reliable pipeline must
explain such failures and avoid producing unsupported ITA/MST/correction values.

- [31367 diagnostic page](../outputs/reported_missing_mask_31367_v1/review.html)
- [Exact detector result](../outputs/reported_missing_mask_31367_v1/diagnosis.json)
- [Color-rule comparison summary](../outputs/focused_ycrcb_diagnostic_v1/summary.json)
- [Saved color-rule comparisons](../outputs/focused_ycrcb_diagnostic_v1/review.html)
