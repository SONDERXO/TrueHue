# Proposed fixed comparison: reserved clean-photo veto

8 November 2026. Planning only; do not start fitting until this specific comparison is agreed.

## Intervention

Reserve eight of the 32 newly added development publisher groups, chosen by the lowest SHA-256 values of `TrueHue-reserved-clean-veto-v1:` plus group key. This selection uses group keys only, not error, features, mask success ranking or tone labels. Keep the exact keys and row lists private in `outputs/reserved_clean_veto_plan_v1/plan_PRIVATE.json` (script 628). These are not the separate eight unopened holdout groups.

Exclude **all conditions** from reserved groups from every correction-tree fit. Use only their existing usable clean measurements for the veto. Preserve measurement failures in the ledger; do not treat them as evidence that the veto works. Do not select replacements for failed clean measurements.

The frozen selection reserves 227 available conditions, including 20 usable clean references. The full fit would retain 890 conditions and 82 clean references. The other four selected originals lack usable clean measurements; they are not veto successes. No images were opened to make this plan.

Fit exactly 11 trees at depth four using the remaining saved fitting rows/costs: the same ten old-group-held folds plus a full fit. Freeze the 56 old MST calibrations, action sets, features, masks, costs, clean constraints and all other settings. Reserved new groups were absent from those MST calibrations already. Existing outer held groups must remain excluded as before.

After each tree is fitted, route the reserved usable clean feature vectors through it with that fit's frozen MST calibration. Replace each reached nonidentity leaf with identity, once, without moving thresholds, finding a margin, refitting or selecting among policies. Preserve original and vetoed trees and the exact reason for each veto. No reserved distorted outcomes may guide the veto or select the model.

## Evaluation and stopping rule

Evaluate all 756 existing attempts with unchanged prepared inputs, masks, scoring supports and failure handling. Report the pre-veto tree as an attribution comparison, the unreserved depth-four candidate as a reference, and the original aligned model as the acceptance comparator. Repeated use of reserved groups across fits is not independent validation.

Keep the existing joint requirements: zero edits to usable clean evaluation photos; no increase in core/stress RGB or CIEDE2000 mean error or harm counts; no decrease in beneficial counts, separately for both cohorts; exact protection and replay verification. Use no evaluation outcome to choose reservation groups or veto rules. A clean-only success does not qualify as a passing model.

The separate eight-group, 24-photo holdout stays byte-unread. If any requirement fails, stop: no alternate reservation seeds, reserve-size sweep, additional depths, threshold search or relaxed criteria. Passing development checks would still require a separate final-validation decision before opening the holdout or integrating a model.

## Risks and checks

Removing fitting groups can reduce recovery. A clean veto can disable corrections for distorted photos sharing the same leaf, and can miss clean photos that enter other leaves. The reservation is development-exposed and participates in model selection, so it is not a new test set. No real-world safety, fairness or naturalness claim follows.

Verify group exclusions for every condition, frozen matrices/calibrations, all 11 pre-veto greedy fits, exact reserved-clean routing and leaf replacements, preserved non-vetoed leaves, all evaluation pixels/metrics/protection, and both comparators. Keep all private artifacts ignored. No Android or desktop integration is part of this experiment.
