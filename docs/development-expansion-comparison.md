# Development expansion comparison

24 October 2026. The nine additions did not improve the fixed decision-tree comparison. Keep this as a development result; do not replace the runtime model.

Eight source-group folds held every source and all its variants together. Both trees evaluated the same 31 probes. The original tree used the remaining original22 rows; the expanded tree used the remaining31. Fixed depth3, seed42, leaf minimum1, four baseline Lab/ITA features, three inverse-parameter targets, and identical additions-only correction support. Sixteen fold models were saved; no final all-source model was fitted.

Lower color error is better (CIEDE2000, relative to the source photograph):

| Probe group | No correction | Original22 | Expanded31 |
|---|---:|---:|---:|
| All31 | 5.46 | 6.60 | 7.80 |
| Shared22 | 5.16 | 6.92 | 8.16 |
| New9 | 6.20 | 5.83 | 6.92 |

The equal-source average also worsened: original6.61 versus expanded7.77 (no correction5.13). Darkened probes improved from9.17 to7.91, but mildly altered probes worsened from3.89 to7.13. Already unchanged inputs still received unwanted correction: average error5.68 versus6.30. Bright/warm and color-shift averages also worsened.

Codex visually inspected all31 comparisons in four contact sheets. Darkened-face recovery improved in some examples, but unwanted brightening/color changes and sharp mask seams remain. This is a qualitative development inspection, not expert MOS or new human annotations.

Saved-model predictions replayed exactly. Fitting and evaluation pairs, source IDs and duplicate groups were disjoint in every fold; original hashes stayed unchanged, and pixels outside correction support were preserved. Full existing suite: **464 passed**.

Recommended next step: audit the largest control regressions against their actual training-leaf members and compare similar feature vectors with incompatible targets. This can distinguish sparse data/tree splits from inadequate features before collecting another batch or changing the model. Do not infer that these two new sources are bad data solely from this result.

Limitations: eight selected development sources; subject independence unverified; synthetic reconstruction is not calibrated skin-color accuracy. No external development, stress or reserved test images were evaluated. Continuous ITA without operational MST remains a proposal distinction; face-and-neck support is still pending. No formal proposal amendment or final dataset promotion.

[Full metrics and fold provenance](../outputs/development_expansion_sourcecv_v1/summary.json) ? [All image comparisons](../outputs/development_expansion_sourcecv_v1/review-index.md)

Follow-up: [control-error diagnosis](expansion-control-diagnosis.md).
