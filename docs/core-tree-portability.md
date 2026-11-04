# Core decision-tree portability check

27 October 2026. User direction: set CPM aside, retain paint/makeup protection
as a limitation, and continue the paper's core method. CPM conversion and
further paint-model work are deferred; previous experiments/artifacts remain
historical evidence. No automatic review reversal or final-data admission.

This bounded implementation advances on-device decision-tree inference without
creating an Android app, retraining, changing masks or inventing an MST lookup.
The existing four-feature depth3prototype remains the frozen source model.
It is a development model, not a final validated thesis model. Its weak quality
and absent operational MST remain explicit limitations.

Before execution, define these checks:

- Export feature/target order, complete split thresholds/children and leaf
  vectors to versioned JSON, retaining source model/hash/version metadata.
- A separate standard-library evaluator validates the tree, quantizes inputs
  to float32 before comparing with float64 thresholds (the installed sklearn
  contract), and returns gamma/red/blue in their exact saved order. Reject
  malformed graphs, schema mismatches and nonfinite/overflowing inputs.
- Compare predictions/leaves on all23 original available feature rows
  (16training,3development,4clipped stress). The original failed row remains
  excluded, with no feature substitution. No rows enter a new fit.
- Independently exercise both sides and neighboring float32 values of every
  reachable split. Preserve node/leaf coverage and exact discrepancies.
- Compare correction outputs on a deterministic synthetic RGB grid using the
  same fixed mask; no new source image, source exposure or mask is needed.
- Record hashes and file size, verify previous model/review/ledger artifacts
  unchanged, and run meaningful schema/routing tests plus the Python suite.

Success is prediction/software parity only. It does not establish corrected
image quality, generalization, Android end-to-end timing, MST classification or
the feasibility of every other pipeline model on-device. No automatic runtime
replacement follows. The face/visible-neck request remains recorded separately;
this component does not implement neck localization.
