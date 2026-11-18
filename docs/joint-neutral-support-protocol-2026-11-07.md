# Joint neutral-control and fitting-support check

7 November 2026. The user approved proceeding after the saved-tree diagnosis
recommended addressing exposure and neutral colour controls together. This is
one fixed, zero-fit research comparison, not permission for a sweep or adoption.

## Reason for this check

The severe clean darkening routes to an exposure leaf with no clean members;
the query lies outside that leaf's observed input ranges. Colour leaves also
average clean and distorted targets, producing non-neutral gains. Exact neutral
controls must address all three outputs. The older five-feature clean-leaf/range
policy already reduced coverage substantially (28 October). This check explicitly
reuses that conservative idea on the current two-head model; it is not a new
algorithm or independent validation. It tests whether the diagnosed failure can
be blocked and quantifies the accompanying loss of correction.

## Frozen policy

- Reuse the ten saved split-control folds and the saved full model. No fitting.
- For each head, route only its original fitting rows through the unchanged tree.
  Record float32 minima/maxima on **all 12 input axes** separately in each leaf.
- If a leaf contains any fitting row whose existing recipe is clean, substitute
  exact neutral output: gamma 1 or gains [1, 1]. Clean targets must already be
  [1, 1, 1]; do not infer cleanliness from held-out data.
- At prediction, if either head's query is outside any of its reached leaf's
  inclusive fitting ranges, return the full identity [1, 1, 1]. No range margin,
  tolerance, nearest-neighbour adjustment, or head-specific partial correction.
- Otherwise concatenate the two clean-anchored outputs. Retain the original
  frozen binary gate and its decisions. Report the policy without that gate too,
  as a diagnostic, not a second candidate to select.
- Preserve ITA, MST, all other inputs, masks, controls outside this policy,
  renderer, splits, recipes and unavailable-input no-op handling. Held publisher
  keys must be excluded from all fold metadata; later keys must be disjoint from
  the full fitting keys.

## Evaluation and disposition

Use all 1,428 saved condition records: working-resolution folds and native borrowed,
actual-input, and fallback-mask contexts. Report clean/core/stress separately,
both RGB MAE and relative CIEDE2000, photo- and equal-key means, changed counts,
harm counts, missing features and support abstentions. Compare no correction and
the retained split model with its original gate; include ungated diagnostics.
These are repeated conditions from 54 original photos, not 1,428 people or
independent photos. Later photos are already exposed development evidence.

The clean screen remains zero altered clean photos. A clean-screen pass alone
does not establish adequate distortion recovery. Explicitly count previously
beneficial actions that are lost. No automatic threshold/range/feature adjustment,
additional fit or app integration follows any outcome.

Verify metadata independently by manually traversing original trees, check every
fitting clean prediction, independently reconstruct saved RGB outputs, metrics,
mask protection and source hashes. Review all available clean boards in the two
nonduplicate suites, the first available core/stress row per suite, and the known
recovered warm case. Additional outcome-selected views must be labelled.
