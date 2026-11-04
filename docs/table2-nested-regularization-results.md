# Nested minimum-leaf-size comparison

28 October2026. Completed the
[predeclared regularization protocol](table2-nested-regularization-protocol.md)
on the unchanged15reviewedsourcegroups/30pairs. This tests model complexity
selection rather than adding more output guards or selecting settings from
outer held-source results.

Candidate minimum leaf sizes are exactly1,2,4; depth3,seed42,fiveLab/ITA/MST
features,unweighted targets,masks and the existing training-control leaf policy
stay fixed. No depth/feature search,class weighting,new sources or gate changes.

Each outer fold's14fittinggroups supply14inner held-group folds per size.
Each inner model fits26pairs/13groups; its held pair and the outer held source/
known duplicate group are excluded.630inner trees produce1260inner predictions.
Setting selection uses only these inner results, with the unchanged strict
overall-improvement and zero-clean-harm gates. Ties,if any,favor larger minimum
leaf size. Outer decisions are saved before scoring the held source.

## Result

No candidate size is eligible in any of the15outer folds: every setting retains
at least one harmful inner clean prediction. Minimumleaf4is not automatically
accepted simply because it sometimes reduces the number of harms. All15folds
select identity,with zero outer model refits.

| Outer held cases | Pairs | No correction CIEDE2000 | Selected procedure CIEDE2000 | Changed inputs |
| --- | ---: | ---: | ---: | ---: |
| All | 30 | 10.076 | 10.076 | 0 |
| Unchanged | 15 | 0.000 | 0.000 | 0 |
| Distorted | 15 | 20.153 | 20.153 | 0 |

The clean gate passes but strict overall improvement fails. This is safe
abstention,not useful correction or model completion. Do not relax the gates,
add extra sizes after seeing this result or report an inner model's best score
as held-source performance. The result does not prove that every regularized
tree or larger dataset must fail; it tests this fixed design and candidate set.

No active model,Android asset,source allocation,mask,MST lookup or accepted
concern changed. Historical exclusions and holds remain in the frozen plan.
The earlier range-guard's narrow cohort pass remains separate: it corrected
only one distorted input and failed the light-severity stress mean. Neither
that result nor this identity-only selector establishes broadly effective
correction. Repeated hypothesis development on the same sources also prevents
claiming independent final validity,even with correct nested partitioning.

## Verification and consequence

Script200saves all630raw/policy portable model pairs,inner partitions,predictions
and15selection records. Script201independently reconstructs leaf target means
and control overrides,checks1260inner predictions with separate RGB arithmetic,
recomputes candidate eligibility/tie rules and all15training-only decisions,
verifies30outerPNGoutputs/metrics/gates,source/duplicate separation and original
hashes. All checks pass. No shared algorithm code changed; latest full suite
remains705passed from the control-partition stage,not a new full-suite run.

This comparison provides no evidence for adopting a different minimum leaf
size under the current clean-preservation requirements. Preserve the simpler
baseline and failed candidates as development evidence. Further work needs a
new,predeclared data/representation/training hypothesis rather than an enlarged
search on these same errors. Weak experimental MST,photographic references,
clipping/approximate recovery,accepted hair/body/background contamination,
absent dark-group coverage and person-separation limitations remain explicit.
Photographer evaluation is deferred until the correction model is finished,
using the existing Google Form. Android remains paused;CPM deferred.

- [Frozen setting-selection plan](../outputs/table2_nested_leaf_regularization_v1/plan.json)
- [All predictions,decisions and scores](../outputs/table2_nested_leaf_regularization_v1/summary.json)
- [Independent verification](../outputs/table2_nested_leaf_regularization_v1/verification.json)
