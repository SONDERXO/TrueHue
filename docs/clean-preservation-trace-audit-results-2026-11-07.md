# Why the latest gate still changes clean photos

7 November 2026. Completed a [saved-trace audit](clean-preservation-trace-audit-protocol-2026-11-07.md)
after the user resumed correction development. No model was fitted, no image
model was run, and no mask, control, annotation or runtime was changed.

## Main findings

The fitting clean constraints pass, and saved gate actions reproduce correctly.
The remaining clean edits are genuine generalization errors, not a detected
export, score-sign or optimizer-roundoff mismatch.

Two severe cases dominate the clean error: unnecessary darkening of a forehead
region in the development comparison, and a large red/blue colour change in
the later comparison. The gate permits these already-saved harmful controls.

| Saved comparison | Available clean photos / attempts | Constrained clean edits | Retained edits | Largest clean RGB MAE | Share of summed per-photo clean errors from that one case |
| --- | ---: | ---: | ---: | ---: | ---: |
| Held-group working256 |29/30|7|3|23.23997|89.36%|
| Later fallback-native224 |23/24|3|1|15.38955|92.16%|

The percentages use sums of individual photo MAEs within each comparison, not
pooled pixels, independent population observations or failure probabilities.
The photos/renderer conditions are not pooled. Each unavailable original remains
an unavailable attempt, not a successful no-op measurement.

The development constrained gate keeps2of3retained-gate clean failures, suppresses
the third, and introduces5new clean failures. In the later comparison it
suppresses the retained gate's1clean failure but introduces3different ones.
Thus protecting a particular earlier failure does not establish a safer gate.

## What changes the gate's score

For each of52available clean queries, we selected the nearest fitting-clean
feature vector in that gate's frozen standardized12-feature coordinates.
The query score is exactly the reference score plus12weighted feature changes.
This is descriptive arithmetic, not a new nearest-neighbour classifier or a
recommended inference rule. Nearest references never use held-group labels.

- The estimated-MST term is the largest positive change in4of7development clean
  failures and all3later clean failures. Other development failures are led by
  red/green facial colour or facial lightness.
- All3later mistaken scores are clearly positive:4.37185–6.95594 predicted RGB
  benefit. These are not roundoff crossings around zero or the1e-6fitting margin.
- Their MST term changes the score by approximately+4.95,+9.31and+24.88 relative
  to the corresponding nearest protected clean vectors, partly cancelled by
  other terms. This does not mean these are actual correction benefits.
- The later failed clean vector nearest to fitting clean support has standardized
  distance0.35061and a final positive score4.64817. That distance is not a
  probability, validated neighbourhood radius or evidence of photo equivalence.
-2of7development failures and1of3later failures lie inside every individual
  fitting-clean feature range. Per-feature range membership therefore does not
  imply that the combination is protected by the affine clean constraints.

The constrained model is guaranteed to protect the fitting clean vectors and
their convex combinations, not arbitrary unseen vectors. Large MST contributions
motivate a specific gate restriction, but do not prove that the estimator is
wrong, that the other inputs cannot reconstruct similar information, or that
excluding MST will repair the refitted gate.

## The severe controls are different

- Development worst case: gamma1.42861with gains1.01866/0.99637. With the direct
  exponent renderer, this darkens the already clean selected region. The saved
  board shows a distinct forehead patch; the retained gate leaves it unchanged.
- Later worst case: gamma0.99893with gains1.21383/0.64796. The large blue
  attenuation/red boost produces an orange facial change. The retained gate
  leaves this case unchanged.

The same one-gamma correction repair would not address both mechanisms.
Mask fragmentation and restricted application remain visible; this audit does
not isolate mask causality or supply actual-skin ground truth.

## Proposed next comparison, not run

Test one added constraint: **the gate's estimated-MST coefficient must be zero**.
ITA, estimated MST and Lab remain in the correction predictors. All other gate
settings, saved controls, splits, masks and data stay fixed. This tests whether
the extra apply/no-apply decision benefits from avoiding that dependence.

The [proposed protocol](mst-excluded-gate-proposed-protocol-2026-11-07.md) specifies
11gate fits and the unchanged necessary clean-preservation/core-improvement
screen. It remains pending user agreement. No threshold/feature sweep or new
fit is activated by the audit. Passing a development screen would still not
authorize deployment or establish independent validation.

## Verification and visual selection

Script542replays688available saved gate scores/actions across the two selected
suites, checks290repeated fitting-clean constraint occurrences, held-group
exclusions and52nearest-reference score decompositions. These counts do not
represent additional independent people or fitting runs.

Script543independently uses raw affine slopes/intercepts and explicitly
recomputes52saved clean RGB errors/change counts from original output PNGs.
It verifies nearest references, comparison means and error shares, and source
hashes. All checks pass. No pytest run was needed for this read-only audit;
the prior24demo-integration tests and38gate-focused tests are historical results,
not new scientific evidence.

Viewed3existing comparison boards: the worst clean RGB error in each suite and
the later failed clean closest to fitting-clean support. This is explicitly
outcome-selected diagnosis, not blind aesthetic review. No additional user
annotations or review rounds were requested.

Private outputs: `outputs/clean_preservation_trace_audit_v1/` with case-level
decompositions, nearest references, source hashes and independent verification.
The later groups are development-exposed and identities across sources are not
verified. The model remains unfinished and the constrained gate remains unadopted.
