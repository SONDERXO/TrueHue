# Training-only safety selection and same-cohort thesis metrics

28 October2026. Completed the predeclared
[nested safety procedure](table2-nested-safety-protocol.md), followed by a
same-cohort report of all four development methods. This is a continuation of
the exposed-data implementation, not a new independent final evaluation.

Within each of ten outer held-source groups, the remaining nine groups provide
nine inner held-group folds. Each inner tree fits16pairs/eightgroups using the
same9features, fixed tree settings and training-identity leaf output rule. The
outer held source and known duplicate group are absent from all those inner
fitting and validation partitions. Ninety inner trees produce180inner held
predictions. No feature, parameter, policy or gate search occurs.

Each outer decision uses only its18inner predictions: permit the existing outer
conservative tree only when overall error improves against no correction AND
all inner held clean controls remain unchanged. Otherwise select identity.
Decisions are saved before either outer held score is calculated. References
are used only for inner selection/scoring, never prediction features. This is
training-procedure selection, not a per-image classifier or online source lookup.

## Result

**All ten inner assessments fail the clean gate**, with one to three harmed
controls in each. All ten outer decisions therefore select identity. Every
outer output equals its input: zero clean harm and zero correction benefit.

| Mean CIEDE2000 | No correction | Nested selection |
| --- | ---: | ---: |
| All20pairs | 10.577 | 10.577 |
| Ten unchanged | 0.000 | 0.000 |
| Ten distorted | 21.154 | 21.154 |

The unchanged-image gate passes; the strict overall-improvement gate fails.
This is safe abstention on this cohort, not a successful correction model.
No method is promoted, no75027special case is introduced and no acceptance
threshold is relaxed. Passing an in-training clean-preservation property did
not establish a policy reliable enough for inner held-source selection.

The representation/hypotheses were developed through repeated exposure to these
same sources. Nested partitions prevent the specified per-fold selection leakage
but do not erase that wider development exposure. Do not present the results
as unbiased final performance or evidence of all-MST-category robustness.

## Same-cohort comparison for thesis reporting

All rows below use exactly the same20pairs and ten source groups, eliminating
the cohort-composition issue found in the earlier eight-to-ten-source audit.

| Method | Overall CIEDE2000 | Clean CIEDE2000 | Distorted CIEDE2000 | Harmed clean controls |
| --- | ---: | ---: | ---: | ---: |
| Five-feature tree | 9.643 | 5.489 | 13.797 | 7/10 |
| Nine-feature chroma tree | 8.898 | 3.488 | 14.309 | 6/10 |
| Training-control leaf policy | 8.538 | 2.767 | 14.309 | 1/10 |
| Training-only nested selection | 10.577 | 0.000 | 21.154 | 0/10 |

No row passes both quality gates. Record the accuracy/safety trade-off, rather
than selecting a method from its best average alone. The modified leaf policy
is a separate experimental method, not an unreported ordinary-tree result.

Script179also supplies separate mean absolute errors for gamma, red gain and
blue gain by method and unchanged/distorted/all scope. They compare predictions
with the saved reference-informed approximate recovery targets; identity targets
are exact. These are parameter-target errors, not skin-tone label MAE, calibrated
skin-color accuracy or expert quality. Do not pool the three output MAEs into
one number because their scales differ. Photographic-reference CIEDE2000 and
MST evaluation must remain separately labeled.

## Verification and next design constraint

Script178independently reloads all90inner sklearn models and portable exports,
reconstructs fitting membership/identity leaf outputs, replays180inner and20outer
predictions with a separate RGB formula, verifies10training-only selections,
all group exclusions, corrected PNGs, metrics/gates and original hashes. All
checks pass. Script179checks80same-cohort per-pair records and12aggregate rows,
CSV roundtrips and source evidence hashes. No shared algorithm module changed;
latest full suite remains695passed from the chroma-feature stage, not a new run.

The next learning design requires reliable evidence for correction need on
previously unseen sources. More post-hoc adjustments to these ten sources cannot
establish it. Preserve this fixed safety-selection result before pursuing another
reference/data design or independently reviewed training study. Synthetic clean
controls do not establish that a source photograph has neutral exposure/color.
Retain Table2's approximate-recovery/clipping limitations, weak experimental MST,
absent dark-group coverage and unverified person separation. Final data/reference
evaluation, expert MOS and Android correction integration remain unfinished.
Android stays paused and CPM deferred. No active model or Android asset changed.

- [Nested plans and frozen settings](../outputs/table2_nested_safety_v1/plan.json)
- [All inner/outer predictions and decisions](../outputs/table2_nested_safety_v1/summary.json)
- [Independent nested verification](../outputs/table2_nested_safety_v1/verification.json)
- [Same-cohort metrics, including parameter MAE](../outputs/table2_same_cohort_report_v1/aggregate_metrics.csv)
- [All80per-input method records](../outputs/table2_same_cohort_report_v1/pair_metrics.csv)
- [Report verification](../outputs/table2_same_cohort_report_v1/verification.json)
