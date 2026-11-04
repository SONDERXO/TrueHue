# Input brightness-feature audit

24 October 2026. All31 existing development inputs support the fixed proposed feature set. No model was fitted and the runtime model is unchanged.

Retain the original four inputs (mean Lab and ITA) and add six measurements from the same distorted-input estimation mask: shadow brightness (10th percentile), median brightness, highlight brightness (90th percentile), brightness spread (75th minus25th percentile), left-minus-right mean brightness and top-minus-bottom mean brightness. This freezes ten inputs for the next controlled comparison; none were selected using correction outcomes.

Brightness uses the existing OpenCV-to-L* conversion (0 to100), linear percentiles and halves of the occupied mask bounding box. Halves are relative to the image, not anatomical cheek regions or normalized for pose. Minimum counts were set before extraction:1000 total mask pixels and100 per half. No unavailable value is imputed and no reference value is substituted.

## Availability and sensitivity

All31 inputs and all31 eroded-mask probes were available; the smallest original half contained13,563 pixels. Eroding the mask by one pixel retained91.8% to96.1% of its pixels. Original half boundaries were held fixed for the sensitivity comparison; recomputed-boundary results were also saved.

| Added measurement | Median absolute change | Largest absolute change |
|---|---:|---:|
| input_l_p10 | 0.784 | 1.961 |
| input_l_median | 0.392 | 0.392 |
| input_l_p90 | 0.000 | 0.392 |
| input_l_iqr | 0.392 | 0.784 |
| input_l_left_minus_right | 0.131 | 0.455 |
| input_l_top_minus_bottom | 0.286 | 0.802 |

Changes are in L* units. There is no validated stability cutoff: this is a local mask-boundary sensitivity probe, not proof of robustness to lighting, compression, pose or segmentation failure. It also does not establish any predictive benefit. Existing masks can have biased coverage; extra features cannot be assumed to fix that.

## Verification and next step

All four existing feature values reproduced the frozen table exactly. Independent quantile and half-region mean calculations verified all31 new feature rows. Repeated extraction was identical and original model/input/table hashes remained unchanged. Existing suite: **464 passed**.

The next experiment is fixed before fitting: compare baseline4 versus proposed10 inputs with depth3, seed42 and leaf minimum1 on the same eight source-group folds, same31 probes, targets and correction/scoring masks. Include no correction, unchanged/mild controls, every distortion, shared22/new9 and source-balanced summaries. Avoid feature selection or depth tuning on those results. Retain failures and keep the runtime model unchanged unless stronger evidence supports adoption.

The extractor accepts only the distorted input and estimation mask. References, inverse targets, distortion labels and source IDs are excluded from its computation. IDs are retained solely to join audit rows. This remains a development diagnostic; continuous ITA without operational MST, final dataset eligibility, calibrated-color evaluation and visible-neck support remain unresolved. The feature extension is recorded for later thesis-method edits and does not amend the proposal.

[Frozen feature schema](../outputs/brightness_feature_audit_v1/feature_schema.json) ? [Input feature table](../outputs/brightness_feature_audit_v1/input_features.csv) ? [Full sensitivity audit](../outputs/brightness_feature_audit_v1/summary.json) ? [Independent verification](../outputs/brightness_feature_audit_v1/verification.json)

Follow-up: [completed fixed feature comparison](brightness-feature-comparison.md). Candidate improves over baseline but is not ready for runtime adoption.
