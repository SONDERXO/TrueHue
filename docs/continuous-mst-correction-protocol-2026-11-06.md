# Continuous MST correction candidate protocol — 6 November 2026

The user explicitly authorizes testing the continuous MST estimate directly in
the correction model. This supersedes the integer-adapter requirement only for
this isolated experimental branch. It does not adopt a production method or
authorize real photographic fitting. The old integer lookup and correction
interfaces remain the historical comparator, with no fabricated matching fit.

The candidate replaces `input_mst_index` (0–9 category) with `input_mst_score`
(continuous 1–10 contextual estimate). All four actual-input Lab/ITA features
and three gamma/red/blue outputs remain. It uses the contextual estimator's
explicitly clipped score; retain its raw prediction separately for diagnostics.
No integer rounding, minus-one conversion, source-label feature or missing-score
fallback is allowed. Scores above/below range are clipped explicitly, not binned.

The join helper requires matching measurement-contract SHA declarations, exact
input-only features, finite plausible Lab/ITA ranges and consistent raw/clipped
prediction. This checks representation, not prediction provenance, data
eligibility or accuracy. A caller must bind each prediction to the exact input,
eligible estimator artifact and group-isolated fitting history. Contracts alone
cannot prove these conditions.

Before fitting real correction data, obtain justified skin/reference eligibility
and person grouping and fit the contextual estimator under nested subject-held
separation: inner held predictions for correction training, outer training-only
estimator for outer evaluation. Retain technical failures. No source-label MST
may replace predicted MST. Continuous prediction is a feature derived from
the same ITA/Lab inputs, not new independent information; incremental predictive
benefit must be evaluated, not presumed. An eventual no-MST ablation would need
an explicit experiment protocol; it is not the default method here.

Script471 first exercises 12 fictional arithmetic inputs with a declared,
unfitted linear contextual fixture. Include fractional and out-of-range raw
predictions. Fit one existing fixed target-standardized tree on the first eight
arithmetic rows; replay all12 through JSON and portable controls. The other four
rows are arithmetic holdouts, not people or independent photographic evidence.
No estimator is fitted, photographs opened, pixel renderer tested or correction
accuracy claimed. Refuse overwrite, bind sources, preserve old lookup/calibrator
bytes and run focused interface/contextual/tree tests. Stop after this check;
no automatic real fit, new review, source batch, model sweep or app change.
