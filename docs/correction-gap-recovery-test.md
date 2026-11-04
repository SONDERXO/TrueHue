# Correction-only enclosed-gap recovery test

25 October 2026. Tested one fixed candidate across32 regenerated masks and the earlier clean/global-shift labeled-point probes. It adds19 pixels in two masks and is not adopted. This limited result does not resolve the user's broader coverage concern.

The rule was saved before running: fill an entire connected gap only when enclosed away from the image boundary, at most64 pixels, no overlap with intentional eye/brow/complete-mouth exclusions, all pixels more than2 pixels away from exclusions, all classified as face/body skin, and all consistent with the existing robust Lab material test (distance at most3, scale floors12/6/6). No threshold search, face-box expansion or landmark-failure fallback. Existing correction pixels are preserved; measurement, generation, feature values and input images are unchanged.

## Result

- 40048 unchanged:17 pixels added at the cheek-side hole, bounds `[200,122,204,128)`.
- 60162 color shift:2 pixels added near the face/background edge, bounds `[221,129,222,131)`.
- Other30 masks are unchanged. Most remaining enclosed components fail feature-proximity, material or semantic checks. Large/outer-background components remain excluded.

Codex inspected both changed source boards and pixel-enlarged crops. The17-pixel addition looks like plausible cheek skin. The2-pixel edge change is visually ambiguous at this source resolution; passing the heuristic is not proof that it is skin. Neither has been silently adopted. Preserve this ambiguity instead of accepting every filled pixel as an improvement.

The previous122-pixel gap audit and this19-pixel result are different diagnostic quantities: proximity/material/semantic checks may reject some audit gaps, and feature regions remain protected. Boundary-connected missing skin is deliberately not recovered. No claim of fully covered face, improved corrected-image quality or universal material exclusion follows.

## Earlier hair/paint checks

At the original24 labeled coordinates on clean images and their reused global-shift counterparts (48 observations, not48 independent annotations), correction selection is unchanged. Skin remains12/12 selected in each variant; paint0/3 and other0/5 remain excluded. Clean hair remains1/4 selected, shifted hair0/4. This preserves the sparse regression but does not establish area accuracy or fix existing hair errors. There is no new paint classifier.

## Verification

Six synthetic safety cases checked accepted small skin gaps and rejection of protected features, non-skin categories, oversized gaps, boundary-connected gaps and materially inconsistent colors. All32 saved outputs replay exactly from their stored category/exclusion maps. Original correction support is preserved, additions avoid intentional exclusions, and original input/measurement/generation/model/review/ledger hashes are unchanged. **464 tests passed**. No model fitted, dataset regenerated or runtime behavior changed.

## Next step

Review [the two changed masks and enlarged crops](../outputs/correction_gap_recovery_v1/review.html). Keep the candidate experimental, especially the ambiguous2-pixel edge addition. Do not relax protection rules merely to fill more pixels. The larger user concern requires a separate inspection of boundary-connected facial gaps and exclusion margins; identify actual skin before any contour expansion. Keep the measurement mask distinct from correction support and check hair/paint/clothing/background regression for every future addition rule.

The32-pair cohort remains pending correction-coverage resolution and staging.31154 remains held, the original fourth evaluation fold remains empty, and the proposed nine-source evaluation has not run. Visible-neck support, operational MST and final thesis/reference/data/evaluation requirements remain unfinished. Correction-only additions are a separately recorded experimental method distinction, not a thesis amendment.

[Fixed policy](../outputs/correction_gap_recovery_v1/policy.json) | [Full component and labeled-point results](../outputs/correction_gap_recovery_v1/summary.json) | [Independent safety and replay checks](../outputs/correction_gap_recovery_v1/verification.json) | [Allnine source boards](../outputs/correction_gap_recovery_v1/review-index.md)
