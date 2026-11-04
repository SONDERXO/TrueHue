# Fixed chroma-distribution feature comparison

28 October 2026. Executed the [predeclared hypothesis](table2-chroma-distribution-protocol.md)
on the same reviewed ten-source/20pair cohort. Added four actual-input facial
statistics to the required five Lab/ITA/MST features: a* IQR, b* IQR, covariance
of L* with a*, and covariance of L* with b*. This tests color distribution rather
than repeating the earlier lightness-percentile/regional feature experiment.

All 20 inputs supply candidate features from their unchanged measurement masks.
ITA means, the square256 measurement contract and experimental MST lookup remain
unchanged. No reference statistics enter features. The correction-model schema
is a separately labeled nine-feature development experiment, not an adopted
method amendment or new MST calibration.

Reused the verified five-feature baseline and fitted exactly ten candidate
trees with the same source/known-duplicate folds, depth3/seed42/minimumleaf1,
unweighted targets, application masks and fixed reference scoring support.
Each fold trains on18pairs and predicts two from the held source group.
No source, feature subset, hyperparameter, threshold or gate was selected after
seeing outcomes. All five rejected source IDs and21held sources remain out;
51803's accepted minor-hole concern remains in the inherited plan.

| Mean CIEDE2000 | No correction | Baseline five features | Candidate nine features | Fitted oracle |
| --- | ---: | ---: | ---: | ---: |
| All20 | 10.577 | 9.643 | 8.898 | 4.775 |
| Ten unchanged | 0.000 | 5.489 | 3.488 | 0.000 |
| Ten distorted | 21.154 | 13.797 | 14.309 | 9.550 |

Overall mean improves, and unchanged-image mean decreases, but distorted-image
mean worsens. Six clean controls remain harmed:22211,62331,84364,75027,51803,
83205. The candidate passes the overall gate and fails the zero-identity-harm
gate. It is not eligible for adoption. A better average than the baseline does
not establish reliable correction or final thesis validity.

An important trade-off is53109: clean error drops1.686to0, but its distorted
error rises7.187to25.487. On62331clean, error decreases13.434to1.487, while
75027clean remains27.672. Bothlightdistortions remain unchanged. These failures
must accompany any reported mean improvement. Oracle values are reference-informed
capacity, never learned performance or globally optimal perceptual lower bounds.

Codex inspected all ten comparison boards.53109's distorted candidate remains
visibly dark while the baseline brightens it;67583's distortion improves
visually relative to its uncorrected baseline, with visible seams retained.
Clean62331is much less lightened;75027still shows severe over-lightening.
Patch boundaries persist on several medium inputs. This is qualitative
inspection, not photographer MOS or new human acceptance.

## Validation and disposition

`src/model_training/chroma_distribution.py` is isolated from default inference.
Three new tests check analytic two-color distribution/covariance, invariance to
unselected pixels, constant-channel behavior, minimum support and mask dtype.
The initial analytic fixture used double-precision conventional Lab and differed
from the pipeline's documented float32 conversion; corrected the fixture's
conversion, without changing the feature definition or fitting recipe.

The complete suite passes **695 tests in12.48seconds**, using a fresh workspace
pytest temporary directory and cache disabled. Script174 independently recomputes
20feature vectors with separate sorted-quantile and covariance arithmetic,
reloads20predictions/10models and portable exports, checks fitting-leaf means,
reconstructs corrected pixels, recomputes metrics/gates and checks unchanged
baseline evidence/source-group separation/original hashes. All checks pass.

No active Python model, Android asset, mask, source admission or lookup changed.
The experiment shows a trade-off and does not establish that color distribution
solves clean/distorted ambiguity. Preserve the candidate as a failed-gate
development comparison. Do not stack further unplanned features, blend methods
on these outcomes or choose a skip threshold from these exposed cases. A future
training design must address clean preservation explicitly with a predeclared
comparison and fitting-only decisions, while retaining MST and all negative
results. Current data/reference/MST coverage and recovery-capacity limitations
remain; Android is paused and CPM deferred.

- [Frozen comparison plan](../outputs/table2_chroma_distribution_comparison_v1/plan.json)
- [Features](../outputs/table2_chroma_distribution_comparison_v1/features.json)
- [Metrics and gate](../outputs/table2_chroma_distribution_comparison_v1/summary.json)
- [Independent verification](../outputs/table2_chroma_distribution_comparison_v1/verification.json)
- [All comparison images](../outputs/table2_chroma_distribution_comparison_v1/review.html)
