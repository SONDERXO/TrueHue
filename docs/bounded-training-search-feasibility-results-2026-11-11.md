# Bounded non-greedy tree search: generated verification and fitting feasibility

11 November2026. The user authorised implementing/verifying the search and then
one training-only feasibility run. Both steps are complete. The new trainer finds
a substantially lower raw-control fitting loss at the same depth and inputs.
**This is not yet evidence of better correction on a new photo.**

## Generated verification

Added an isolated trainer, `src/model_training/bounded_regression_search.py`.
It searches descendant partitions rather than requiring an immediate improvement,
using exact Fraction leaf costs and ordinary raw-control leaf means. Inference
remains the existing PortableTree; the runtime and demo are unchanged.

Twelve focused tests pass in0.18s. They cover independent exhaustive tiny-data
comparisons at depths0?3 and24additional deterministic randomized cases; a
zero-immediate-gain interaction; all3target outputs; pure/constant and float32-
duplicate cases; exact ties/incumbent preservation; invalid inputs; state/time
exhaustion; and the distinction between a certified best-found objective and a
selected incumbent retained under numerical tolerance. Interrupted subproblems
are not cached as exact. Fixtures are generated numeric arrays, not real images,
labels or annotations; they remain outside scientific data.

## One real-data search, with no held-case inputs

Used exactly40fitting rows from the saved first FFHQ fold, whose held group is
ffhq_source_16061:10identity/10under/10over/10cool. Loaded only their per-case
record JSON files and the first saved incumbent model. Frozen metadata containers
were hashed for integrity; values from other folds were not used for optimization.
No16061case record or image was loaded, and no held prediction was produced.

Kept16input features, raw3-output SSE, depth-at-most4, nominal targets and uniform
row weighting. The saved greedy tree was the incumbent, not refitted. One search
expanded5,000nonterminal subset/depth states and stopped at that fixed cap after
19.82seconds, below the60second limit. It also cached107,732completed subproblems,
including terminal/pure subproblems that require no expansion. The expansion cap
is not a cap on those closed base cases. Four interrupted states were not cached.
No restart, increased limit, extra seed, new feature, loss change or target fit.

| Fitting diagnostic | Saved greedy tree | Better-found tree |
| --- | ---: | ---: |
| Total raw parameter SSE |0.0840447433|0.0059895678|
| Gamma-axis SSE |0.0771428571|0|
| Red-axis SSE |0.0069018861|0.0059895678|
| Blue-axis SSE |0|0|
| Fitting originals with nonidentity controls |7/10|10/10|
| Fitting originals with gamma different from1 |3/10|0/10|
| Largest identity red-gain drift |0.02915452|0.02040816|

The total parameter-loss reduction is about92.9%, NOT92.9%image improvement or
accuracy. Fitting identity-control SSE decreases0.00896115?0.00229968 even though
the number of nonidentity fitting controls increases: more cases have a smaller
red change, and gamma errors disappear. This tradeoff must remain visible.
There are no pixel renders/DeltaE measurements in this fitting-only stage.

The search supports the narrow hypothesis that the saved greedy tree leaves
avoidable fitting error in the same declared model class. It does not show that
greedy fitting is the sole cause of failure. Colour/identity target mixing
remains; blue targets are still constant; unseen-photo performance is unknown.

## Verification and certificate scope

The first run is budget-limited, not globally optimal. Best-found SSE0.00598957
has a conservative lower bound0; no claim is made that the remaining gap can be
closed. Independent verification replays80fitting routes (40per model), graph/
depth constraints, raw leaf means, exact rational SSE, serialized-float SSE and
role accounting. PASS;0verification refits. The candidate's exported-float SSE
matches the recorded objective to the stated tolerance. Existing input/contract/
incumbent hashes remain unchanged.

## Next specified step

The feasibility result justifies preparing the frozen11-photo-fold correction
comparison. Reuse this exact first-fold candidate; perform at most10remaining
searches at the SAME60second/5,000expanded-state cap each. Do not refit this fold
or the saved baseline. Predict/render all44held cases only at the comparison
stage, preserving48attempts and excluded29863. No held error may change the
search limits, split ordering, objective, features or output policy.

Keep all prospective checks from the training contract: coverage/protection,
per-recipe RGB/DeltaE improvement over input and nonworsening versus saved
baseline, and11held identity outputs unchanged. Report all individual harms,
parameter losses and incomplete/budget-limited searches. A training gain does
not waive any held-photo check or complete the paper's broader coverage.

The full comparison is prepared, not executed here. No annotation or adviser
input is needed for it. No all-data tree, ensemble, calibration refit, image-
model call, source-photo/locked reads, acquisition, contact/upload/commit/push,
Android or runtime change. All prior artifacts and completed reviews preserved;
final24/older locks remain byte-unread. The correction model remains unfinished.
