# Proposed fixed colour-only nonharm comparison

9 November 2026. Agree this specific comparison before fitting. One objective intervention, not a loss-weight or capacity sweep.

Reuse the exact reserved-group fitting matrices for the existing ten old-group-held folds plus full configuration. Fit exactly 11 depth-four action trees, preserving all features, action libraries, float64 saved costs, frozen MST calibrations, source exclusions, greedy split/tie rules and row weights.

Retain the existing clean feasibility rule. Additionally forbid an action at a node if any colour-only fitting row at that node has saved RGB cost strictly greater than its identity cost. Colour-only recipes are exactly `colour_cool`, `colour_warm`, `stress_color_none`. Equality is permitted. Identity remains feasible. No tolerance, margin or changed weighting. Recipe names are fitting-only metadata, never inference inputs.

Retain the same 227 excluded reserved conditions/eight development groups and the same 20 reserved usable clean references. Recompute their clean leaf veto on each newly fitted tree, exactly as before. Apply the existing frozen four-feature facial exception with identical pooled clean bounds and rule only to explicitly vetoed leaves. Preserve both pre-veto and final artifacts, documenting that this postprocessing can change feasibility outcomes and checking them explicitly.

Verify all fitting colour-only and clean rows after final postprocessing, as well as source exclusions, matrix/cost/calibration parity and exact clean-reference routing. Failure of those checks invalidates the candidate; do not repair it with an extra unplanned rule.

Evaluate the same 756 attempts and unchanged native alpha/scoring regions. Compare with the current facial-exception candidate for attribution and the original aligned model for acceptance. Joint acceptance remains zero usable clean edits, no increase in core/stress mean RGB/CIEDE2000 or harm counts, and no loss of beneficial outcomes, separately per cohort, plus exact rendering/protection parity. Report failures and harms without successful-only filtering.

The final eight-group, 24-photo holdout stays byte-unread. On any failed requirement, preserve and stop—no alternate recipe subsets, margins, weights, depths, guard search or relaxed criteria. No DINO inference, mask change, dataset/annotation expansion or runtime integration. A passing development result alone is not final validation.
