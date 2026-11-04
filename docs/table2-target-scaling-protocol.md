# Fixed fitting-only output-standardization experiment

28 October2026. Hypothesis: unscaled multi-output squared error combines gamma,
red-gain and blue-gain errors in unequal numeric ranges. Test equalized target
scales without adding features or adjusting source outcomes. This does not
assume target scale is the cause of the remaining failures.

For every prescribed15sourcefold, compute mean and population standard deviation
of each of three targets using only28fittingpairs. Standardize those targets,
fit the same5inputfeature/depth3/seed42/minimumleaf1/unweighted decision-tree
regressor and export its learned splits with raw-unit fitting target means in
the leaves. A constant target axis uses scale1and retains its exact constant
prediction. No fitted target normalization is needed at portable inference.

Exactly15newfits. No output weights/margins/depth/feature search, new data,
mask changes, guessed MST or held-label fitting. Compare raw-unit baseline5,
the standardized-target tree and its already defined training-control identity
leaf policy on the same30heldinputs. The latter reuses splits, not a second fit.
Keep separate gamma/red/blue target errors and reconstruction quality; do not
claim normalized training MSE equals perceptual quality. All accepted concerns,
7rejectedsourceIDs,74holds and existing gates remain. No adoption based on this
exposed development result; no additional scales after seeing outcomes.
