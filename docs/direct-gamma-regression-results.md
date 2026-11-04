# Matched correction-tree improvement experiment

30 October 2026. Trained and tested a new decision-tree candidate using the
paper's direct-gamma target convention. This is an actual matched learning
comparison, not just another mask screen or a converted saved prediction.
The working desktop demo and all active models remain unchanged.

## Exactly one training change

Retain the historically approved 15-source/30-pair clipped-development cohort,
same 15 source/duplicate-group folds, five input Lab/ITA/experimental-MST
features, depth3/seed42/minleaf1 and unweighted fitting. Each held source is
absent from its fitting fold. Fit the original reciprocal-gamma target tree
and a direct-gamma target tree on identical rows. The latter reciprocates
the gamma target; red/blue targets remain unchanged.

Converting a saved prediction preserves its curve exactly. Refitting on
reciprocal targets instead changes the numeric regression loss, potentially
changing partitions and leaf averages. Outputs use the declared matching
operator. No newer unreviewed or rejected mask cohort was admitted, no recipe
regenerated, and no hyperparameter/feature/threshold search occurred.

## Matched held-source results

Lower CIEDE2000 is better; these measure photographic reconstruction against
the same original reference support, not calibrated complexion truth.

| Method | All30pairs | Unchanged15 | Distorted15 | Changed unchanged photos |
| --- | ---: | ---: | ---: | ---: |
| No correction | 10.076 | 0.000 | 20.153 | 0 |
| Original target convention | 8.534 | 5.470 | 11.598 | 6/15 |
| Direct-gamma target convention | 7.628 | 3.464 | 11.791 | 5/15 |

Overall error falls **10.6% relative to the matched original tree**. The gain
comes from less harm on unchanged controls. Distorted-image error becomes
approximately1.7%worse than the original tree, though still below no correction.
Do not report the overall gain as uniform improvement on distorted photos.

Both methods still fail the unchanged-image safety gate. The new candidate
alters five held clean controls and therefore is not eligible to replace the
demo preset. No gate was relaxed or special-case source skip introduced.
Parameter MAEs are reported separately in direct-gamma coordinates in the
summary; numeric gamma errors from different conventions must not be compared
without conversion.

## Verification and scope

Saved30regressors,90held predictions (including no correction) and their images.
Independent refitting reproduces all30trees; the15original-convention trees
also match the historical baseline tree nodes exactly. Reconstruct all90outputs
and metrics and verify source/group separation, explicit gamma conversion,
fixed scoring masks and unchanged outside-support pixels. Checks pass.

This is repeatedly exposed historical development evidence with existing
accepted contamination concerns, weak experimental MST calibration, approximate
targets, clipping and no dark-severity coverage. It is not an independent final
test, the full new three-variant design or proof of intrinsic skin-color
recovery. The old augmentation recipe is retained explicitly so this comparison
isolates learning targets; it is not silently relabeled as the new direct-gamma
augmentation implementation.

No full-data deployment model is claimed from these held-source folds. Saved
direct-gamma trees must be applied using direct-power gamma; feeding those raw
outputs into the legacy reciprocal operator is incorrect. No application loader
or desktop preset was changed to do so. Existing GUI/core modules are unchanged;
the last full suite remains773passing tests. This experiment uses the independent
30-fit/90-output verification as its specific check.

Next development should address clean-versus-distorted decision errors while
retaining this matched baseline and the unchanged clean-harm gate. Do not swap
the working demo simply for a better pooled average or fit on rejected masks.
No additional manual photo review is requested for this comparison.

- [Same-source before/after gallery](../outputs/direct_gamma_regression_comparison_v1/review.html)
- [All predictions and direct-coordinate targets](../outputs/direct_gamma_regression_comparison_v1/predictions.json)
- [Summary and quality gates](../outputs/direct_gamma_regression_comparison_v1/summary.json)
- [Independent verification](../outputs/direct_gamma_regression_comparison_v1/verification.json)
- [Frozen training protocol](direct-gamma-tree-comparison-protocol.md)
