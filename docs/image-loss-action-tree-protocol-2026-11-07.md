# One image-loss action-tree redesign

7 November 2026. User explicitly approves implementing the proposed redesign,
constructed-example checks, and one fixed existing-data comparison. This is not
a feature, threshold, weight, capacity or action-library sweep.

## Frozen learning design

Learn a single depth-three tree with all original 12 input features, including
ITA and MST, using the ten original fitting folds and one full fitting cohort.
Use the exact saved nested fitting feature arrays, rows and publisher exclusions.
No additional MST, target, mask or detector fitting/inference.

The action library for EACH fit is exact identity [1,1,1], then the arithmetic
mean saved three-control target for each non-clean recipe represented in that
fit, in sorted recipe-name order (13 recipes in the current complete cohort).
This bounds training cost and keeps the library reproducible. Recipe labels and
reference images are supervision only; runtime receives only the 12 features.
Controls are quantized to this library, not optimized continuously or averaged
inside leaves. This approximation must be reported as a limitation.

For every fitting row/action, compute exact RGB8 reconstruction MAE over its
existing binary correction/reference mask, using the saved image/reference and
the same direct-gamma, gains, clipping and rounding. Use ALL selected pixels;
no pixel sampling or reference-derived runtime feature. Clean pairs must be
identical and identity action cost exactly zero. A leaf action is feasible only
if it changes zero measured pixels in EVERY clean fitting row reaching it.
Since correction and scoring masks coincide for these fitting rows and pixels
outside correction stay fixed, this preserves each fitting clean image exactly.

At a node, select the feasible action minimizing the unweighted sum of per-row
RGB MAE; identity is the first action and wins exact ties. Search all midpoint
thresholds between adjacent distinct FLOAT32 fitting values on all 12 axes.
Min leaf rows remains one. For each split, choose optimal feasible child actions
and minimize their combined cost. Greedily recurse to max_depth3 only when the
cost improves by more than 1e-12 * max(1, abs(parent_cost)), a fixed roundoff
guard. Stable ascending feature/threshold order resolves ties. No lookahead,
randomness, pruning search or balancing parameter. Re-export positive controls
to the existing portable-tree float32/float64 contract; retain training traces.

This JOINT policy replaces separate gamma/gain trees, separate gate, clean-leaf
overrides and leaf-range guard FOR THIS CANDIDATE ONLY. Clean feasibility is
part of split/action optimization, rather than neutralizing already-trained
leaves. Unseen clean preservation is still an empirical requirement, not a
guarantee supplied by fitting constraints. Identical feature vectors with
conflicting desired actions may remain indistinguishable.

## Checks before research fits

Generated examples must show: a mixed root initially forced to identity can
split to protect clean input and correct a distortion; conflicting identical
features stay neutral; an action harming a clean fitting example is infeasible
even when it improves total unprotected error; identity tie-breaking; and exact
RGB8 cost agreement with the full-image renderer. Invalid inputs fail before fit.
Only generated fixtures are used for these checks. Then fit exactly 11 trees.

## One fixed evaluation

Use all 1,428 saved attempts in working256 folds plus borrowed, actual-input and
fallback native224 contexts. Use unchanged features, references, masks, recipes
and missing-feature no-op handling. Main candidate is the joint tree alone:
do NOT add the old gate or range guard back based on outcomes. Compare no
correction, original retained model with gate, and previous original-feature
joint-neutral/support policy with gate. Latest failed feature restriction remains
preserved, not the parent design. No new fitting labels use held evaluation.

Report clean/core/stress separately: changed/harmed counts, RGB MAE/relative
CIEDE2000 photo and equal-key means, available/scored/attempted denominators,
and action coverage. Zero changed scored clean photos remains required, alongside
useful core recovery and explicit stress regression reporting. Never count 1,428
conditions as independent photos: there are 54 originals and exposed groups.

Independently replay fitting action costs/constraints, action-library derivation,
best feasible leaf actions, split decisions and fitting group exclusions. Verify
all predictions, PNG outputs/metrics, source hashes and outside-mask protection.
View 63 fixed boards using the previous policy board selection, plus at most
the worst clean error and worst core regression per nonduplicate main context
as explicitly outcome-selected diagnostics if there are failures.

Stop after this comparison. No automatic next fit/sweep, app integration,
admission, annotation, dataset search, contact, sharing, commit or publication.
