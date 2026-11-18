# One-step local nonharm refinement comparison

User approved the proposed intervention on 9 November 2026 ("okay lets do
that"). This protocol is frozen before fitting or inspecting new evaluation
outcomes. One comparison, eleven existing configurations, no sweep.

Start from the verified fixed-structure nonharm pre-veto trees. Eligible leaves
are exactly the eleven whose actions differ from the preceding facial-exception
pre-veto trees, as recorded in the fitting-only separability audit. Add at most
one binary split at each eligible leaf; do not recursively refine its children.
Keep all original ancestor splits, other leaves, fitting data, calibrated MST,
features, cost matrices and fourteen actions fixed. Zero new MST/target fits.

For each eligible leaf, enumerate all twelve features in schema order and the
midpoints of adjacent distinct sorted float32 fitting feature values in
ascending order. Both children must contain fitting rows; no other minimum
child size is introduced. Route with float32 inputs and <= float64 threshold.
For each child choose the smallest-index feasible action minimising the sum of
saved RGB costs, using math.fsum in ascending global row-index order. Feasibility
requires zero cost for each clean row and cost <= identity for each colour-only
row. All other row costs enter the objective with their existing equal weights.

The baseline is the constrained unsplit leaf cost. Accept a candidate only if
its child-cost sum improves on the current best by more than
1e-12 * max(1, abs(baseline)). Keep the first within this tolerance, hence feature
schema order and ascending midpoint resolve split ties; action ties use smallest
index. If no strict improvement exists, preserve the whole leaf and its trace.
Append two terminal children for an accepted split; existing node indices stay
fixed. The original trace is historical except the refined leaf entry and new
children, which explicitly record this local fitting step.

Recompute the reserved-clean leaf veto on the refined pre-veto model, then apply
the SAME frozen facial exception bounds and routing rule. Child node IDs may
change veto membership, but policy and reserved vectors do not change. Recheck
all fitting clean/colour constraints and reserved-clean identity decisions after
postprocessing. Any failed final constraint stops evaluation; do not repair by
loosening rules or retrying a different configuration.

Before evaluation independently exhaustively verify local candidate choice,
child rows/actions, unchanged nodes/traces/data/roles/calibrations, final policy,
756 predictions and all bound source hashes. Preserve all prior artifacts and
write to new local_nonharm_refinement_models_v1/comparison_v1 output folders.

Evaluate the same 756 prepared attempts. Independently replay pixels, protected
and zero-alpha regions, RGB/DE metrics, summaries and source hashes. Compare the
previous facial exception, global nonharm and fixed-structure candidates for
attribution; the original aligned comparator remains the acceptance comparator.
Review every changed output against the fixed-structure parent, reusing prior
review only for exact pixel-and-metric matches. Check parity with the previous
facial-exception candidate separately to make any review reuse explicit.

Unchanged joint criteria per cohort: zero usable clean edits; core/stress RGB
and CIEDE2000 mean error and harms no greater than aligned; benefit counts no
lower than aligned. All protection and replay checks must pass. Failure stops
adoption and automatic follow-up. Passing exposed development does not authorise
holdout access or automatic runtime adoption. No new data, parser/DINO run,
annotation, integration, external contact/upload, commit or push is included.
The eight-group, 24-photo final holdout remains byte-unread.
