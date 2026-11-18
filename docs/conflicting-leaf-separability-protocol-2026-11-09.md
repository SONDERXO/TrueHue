# Saved conflicting-leaf separability audit

The user approved the next proposed step on 9 November: audit saved fitting
features and costs before considering local constrained partition refinement.
No new fit, split/threshold search, model alteration, evaluation prediction,
render, image read or final-holdout access is included.

Select every pre-veto leaf whose action differs between the previous facial
exception and completed fixed-structure nonharm models. This selection uses
fitting artifacts, not evaluation outcomes. Preserve all original artifacts.

Within each leaf, define colour blockers as colour-only fitting rows for which
the old leaf action costs more than identity. Define exposure beneficiaries as
fitting recipes ending in under/over (exposure-only and combined, including
stress) for which the old action costs less than identity. Report any fitting
clean blockers separately. Keep the old action and all saved costs fixed.

Round existing input features to the portable tree's float32 contract. For each
of the 12 features, record each set's min/max and strict interval disjointness.
Report blockers outside the exposure set's axis-aligned bounding box and exact
12-feature vector collisions between the two sets. Verify saved leaf members
using the existing tree routing. Record all changed leaves, not selected axes.

Do not enumerate thresholds, choose a best feature, estimate child action costs,
fit new nodes, or use evaluation vectors/metrics to choose a split. Disjoint
ranges show a possible fitting-data separator for these two sets, not general
separability of every row, feasibility after veto/exception, or unseen safety.
Overlapping marginal ranges do not prove multivariate inseparability. No exact
collision does not establish a useful generalising classifier. Repeated fold
rows are not independent samples.

Independently verify row definitions, float32 extrema, interval relations,
collisions, route membership and source hashes. Save a private receipt and a
public summary without private row vectors. A specific approved protocol would
still be needed before any local refinement experiment.
