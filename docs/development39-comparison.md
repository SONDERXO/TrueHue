# Fixed31-versus39 training comparison

24 October 2026. Adding the eight proposed pairs worsened the fixed ten-feature tree overall. Keep this expansion experimental; do not replace the runtime model.

Both methods evaluated the same39 probes in ten source/known-duplicate-group folds. Original31 used only remaining original31 rows; expanded39 used remaining39. Both used frozen ten inputs, depth3, seed42, leaf minimum1, identical three targets and correction/scoring masks. No feature, depth or correction-threshold search.

| Held-source group | No correction | Original31 | Expanded39 |
|---|---:|---:|---:|
| All39 | 5.38 | 6.25 | 7.59 |
| Shared31 | 5.46 | 6.15 | 7.17 |
| New8 | 5.09 | 6.65 | 9.23 |
| bright_warm | 8.19 | 8.03 | 8.83 |
| color_shift | 7.30 | 8.23 | 8.90 |
| dark | 12.69 | 5.34 | 11.22 |
| identity_control | 0.00 | 5.49 | 5.91 |
| mild_bright_exposure | 2.82 | 5.40 | 5.21 |

Lower error is better. Equal-source averages worsened6.35 to7.48; no correction scored5.05. Both the shared31 and new8 groups worsened. Original31 reproduces the prior ten-feature result6.1499 on shared31; its all39 mean6.2531 is different because the probe set now includes eight new cases. Do not compare differing probe universes as if they were the same test.

All10 unchanged probes received unwanted changes under both methods. Five of ten mild probes were worse than no correction under both, although the mild average improved slightly5.40 to5.21. Darkened-image error worsened5.34 to11.22. The expansion is not uniformly worse on every case but does not support adoption.

Codex inspected all39 comparison boards. Major dark-recovery regressions are visible on62331,75027 and62676; unnecessary control brightening and hard mask seams remain. These qualitative observations are not expert MOS. Passing a mask-retention screen establishes neither correct reference skin color nor improved learning.

## Verification

Saved20 fold models and117 held-source records. Original31 parameters/image metrics reproduce the prior run exactly on all31 shared probes. Independent replay checked training and held-source predictions using actual ten-feature columns, recomputed training parameter MAE, original31-only fitting, and source/duplicate separation. Original hashes and outside-support pixels are unchanged. **464 tests passed**. No final all-source model was fitted or promoted.

## Recommended next step

Pause incremental pair additions and consolidate a training-design checkpoint before another fitting experiment. Review the small number of independent sources, per-source variant imbalance caused by mask failures, original-photo reference limitations, and the difficulty of distinguishing complexion from illumination using current input measurements. Define a larger source-review protocol and a fixed comparison plan before further collection; keep the current failures as regression examples without choosing sources for whether they fix them. Do not remove these eight proposals solely because they worsened this model, or claim that another larger cohort is guaranteed to succeed.

Keep runtime behavior unchanged and preserve both31/39 artifacts. All source review statuses remain pending for final eligibility; prior held and clipped cases stay excluded. This remains repeated development analysis, not independent final evaluation. Operational MST, face-and-neck support and final thesis evaluation remain pending. Feature/data/reference distinctions are recorded for future thesis edits, not silently applied to the proposal.

[Full metrics and folds](../outputs/development39_sourcecv_v1/summary.json) | [All39 image comparisons](../outputs/development39_sourcecv_v1/review-index.md) | [Independent replay checks](../outputs/development39_sourcecv_v1/independent_verification.json)

Follow-up: [completed training-design review and next protocol](training-design-checkpoint.md).
