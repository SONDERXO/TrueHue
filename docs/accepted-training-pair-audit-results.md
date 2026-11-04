# Accepted reference and distorted-input audit

Executed follow-up: [fixed input-mask robustness comparison](table2-input-mask-robustness-results.md).
Four rule policies on the same20pairs produced no defensible promotion:
YCrCb-only changes screen passes3→4but increases outside-oval selection;
oval arms pass1each.19clippedinputsremainunchanged. No new model fitted.

29 October 2026. Joined the completed60 original-mask human reviews with exact
saved processing, color-reference, feature, target and input-mask evidence.
All21 human acceptances and39rejections remain unchanged, with exact notes.
No semantic candidate acceptance was substituted for baseline-mask approval.

| Evidence | Sources/pairs |
| --- | ---: |
| Human-accepted references | 21 |
| Accepted reference still technically failed: 43909 | 1 |
| Accepted references with measurable reference/input and available target | 20 |
| Associated distorted inputs containing clipping | 19 |
| Unclipped distorted inputs | 1 |
| Existing exploratory support-loss screen flagged | 17 |
| Identical reference/input masks | 0 |

Only14418 is both unclipped and screen-passing. Its original acceptance includes
insufficient facial coverage, which remains preserved; passing the screen does
not remove that concern. The other screen-passing sources are85815 and56839,
both clipped. Counts overlap and should not be summed as separate exclusions.
The20 technically usable pairs comprise16medium/4light experimental severity
estimates, with no dark group. These are not official FairFace MST labels.

The existing support screen measures whole/quadrant retention against the
synthetic generation region using the previously declared .5 measurement/.8
application fractions and100regionalpixel minimum. It is an exploratory
development warning, not human skin ground truth or a newly validated quality
threshold. All20 input masks differ from their references; the original
reference-only review does not approve those input masks. The accepted16033
hair concern is an explicit follow-up, without rewriting its human decision.

Saved features were recomputed for40reference/input measurements. Each input
uses its own mask and experimental MST mapping; no failed input uses reference
features. All20 Table2 composites and clipping reports were reconstructed
exactly, saved image hashes match original verification, approximate target
parameters are finite and bounded, and the original measurement contract is
unchanged. Exact identity target[1,1,1] remains separate from approximate
distortion-recovery parameters. No optimizer or correction tree was run.

The new machine-readable source/pair disposition file reports barriers
together: human reference rejection, technical failure, unresolved accepted
hair concern, unreviewed distorted mask, clipping outside an unclipped primary
experiment and exploratory support-loss flags. All fitting eligibility remains
false. This is a joined audit for future fitting callers; it does not
retroactively enforce policy on every historical script.

**Do not launch a new primary correction-tree fit on this cohort:** one
unclipped/screen-passing pair cannot establish useful correction generalization.
Clipped stress pairs remain recorded separately and cannot silently replace
an unclipped primary analysis. No no-correction/clean-harm gate was relaxed.
The next development issue is mask robustness and usable evidence under the
paper's exact Table2 transformations, not another depth/feature tweak or
repeated review of all60 source photos. No additional human review is requested
before addressing these known technical holds.

Validation/test and the12 reserved training-check sources remain closed. No
new photos, preprocessing, masks, thresholds, calibration, training admission,
active assets or model-quality claims were introduced. The last full suite is
742 passing tests; this script-only data verification is recorded separately.

- [Complete60-source dispositions](../outputs/accepted_training_pair_audit_v1/source_pair_dispositions.json)
- [Summary](../outputs/accepted_training_pair_audit_v1/summary.json)
- [Verified evidence](../outputs/accepted_training_pair_audit_v1/verification.json)
- [Predeclared audit protocol](accepted-reference-audit-protocol.md)
