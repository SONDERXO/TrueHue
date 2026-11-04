# Control-aware partition training result

28 October2026. Returned to model improvement under the
[frozen control-partition protocol](table2-control-partition-protocol.md).
Photographer evaluation is deferred until the correction model is finished and
will use the user's existing Google Form. The local forms remain unused and
are not a prerequisite for development.

The tested hypothesis changes the training objective: fit Gini splits that
separate fitting identity controls from fitting distortions, then assign identity
parameters to any leaf containing fitting controls and fitting target means to
distortion-only leaves. The export is a single tree with three correction
outputs; no extra classifier is run at inference. This is an experimental
classification-induced partition, not ordinary squared-error regression or an
adopted thesis methodology amendment.

Same9inputfeatures including Lab/ITA/MST,20reviewedpairs,10source/known-duplicate
folds,18fittingpairs per fold,depth3/seed42/minimumleaf1/unweighted settings,
targets,masks,reference support and exclusions. No held-source labels enter
splits/leaf outputs. No source expansion, hyperparameter/feature search or
special handling of75027. Exactly ten candidate trees were fitted once.

| Mean CIEDE2000 | No correction | Previous clean-leaf policy | Control-aware partitions |
| --- | ---: | ---: | ---: |
| All20 | 10.577 | 8.538 | 12.815 |
| Ten unchanged | 0.000 | 2.767 | 9.770 |
| Ten distorted | 21.154 | 14.309 | 15.861 |

**Both adoption gates fail.** Four clean controls are harmed:62331,84364,75027,
51803. This is worse than the prior one-harmed-control policy, while distorted
error also increases. Preserve the negative result; do not replace the previous
candidate or tune the split objective/depth from these outcomes. Even the
previous candidate remains unsuitable for adoption.

Codex inspected those four harmed-source boards.75027remains severely lightened;
62331and51803acquire conspicuous clean-image over-lightening.84364's distorted
prediction receives little/no recovery compared with the previous brightening.
These are qualitative observations of four sentinel boards, not expert MOS,
new source labels or a new claim about reference correctness.

`src/model_training/control_partition_tree.py` is isolated experimental training
code. Four tests check label separation, analytic distortion-leaf target means,
indistinguishable fitting samples retaining identity, explicit boolean labels,
both-class support and rejection of nonidentity control targets. Full suite:
**705passed in13.29seconds**, fresh workspace temporary directory/cache disabled.
Script190independently reloads all ten saved classifiers and single-tree exports,
reconstructs fitting membership/leaf targets, verifies20heldpredictions, feature
splits, source/group separation, output PNGs using a separate RGB formula,
metrics/gates and original hashes. All checks pass. Software validity does not
make the candidate scientifically successful.

The experiment does not support the hypothesis that this change of split
objective fixes cross-source clean/distortion confusion. No active Python
model, Android asset, lookup, measurement policy or source eligibility changed.
Experimental MST, photographic references, clipping/approximate recovery,
absent dark-group coverage and unverified person separation remain limitations.
Do not create another post-hoc gate, depth sweep or automatic all-source fit
to conceal this failure. Photographer work remains deferred; Android paused;
CPM deferred.

- [Frozen fit plan](../outputs/table2_control_partition_v1/plan.json)
- [Metrics and retained failures](../outputs/table2_control_partition_v1/summary.json)
- [Independent verification](../outputs/table2_control_partition_v1/verification.json)
- [Comparison boards](../outputs/table2_control_partition_v1/review.html)
