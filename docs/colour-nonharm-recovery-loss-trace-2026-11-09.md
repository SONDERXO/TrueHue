# Why six underexposure corrections were lost

9 November 2026. **All six losses follow a changed root split, not a reserved-clean veto.** This is a saved-model diagnosis; no new fit or prediction.

## Exact finding

The old root compares scene median brightness with 29.607844. The constrained tree lowers this to 28.431373 in both affected fitting configurations. All six inputs cross from the old low-brightness branch to the new higher-brightness branch.

The six conditions are exposure-under, combined-cool-under and combined-warm-under for each of `case_01` and `eval_16`: two originals, not six independent photos. Their features and all fitting matrices, costs and actions remain unchanged.

| Configuration / affected original | Old correction leaf | New identity leaf | New leaf clean / colour rows |
| --- | ---: | ---: | ---: |
| Held-group development / case_01 | 72 fitting rows | 335 fitting rows | 79 / 215 |
| Full model / eval_16 | 68 fitting rows | 348 fitting rows | 82 / 222 |

Both new leaves select identity before postprocessing and are not vetoed. The old gamma≈0.700 action would harm clean and colour-only fitting rows in these new leaves. It also has substantially worse aggregate cost there: 10,061.05 versus 1,795.75 for identity in the development leaf, and 10,376.18 versus 1,916.36 in the full-fit leaf. Replacing those whole leaves with the previous correction would be unjustified.

There is a useful distinction in the **old** partitions: the old development correction leaf has zero fitting colour rows harmed by its previous action. The old full-model correction leaf has one. Thus some recovery loss is collateral from globally rebuilding the tree, while the full-model branch also has a genuine local constraint conflict. The constraint change is causal in the controlled comparison, but this descriptive trace does not establish a generally safe repair.

## What to compare next

One justified alternative is **fixed-structure constrained action reassignment**: preserve the previous candidate's tree thresholds and partitions, and choose the lowest-cost feasible existing action in each old leaf under the exact clean and colour-nonharm constraints. Keep all group roles, reserved-clean veto, facial exception, actions and costs fixed. This isolates local action protection from global repartitioning; it does not require searching new thresholds or increasing depth.

This may preserve the unaffected development branch, but cannot be assumed to preserve the full-model underexposure action: its old leaf has a real colour blocker. It may still lose useful corrections or fail generalisation. No such reassignment or evaluation was performed in this diagnosis, and it must be fixed as one comparison before execution. Do not remove the blocker, exempt a named case or relax the accepted clean protection.

Keep the colour-nonharm candidate frozen and unadopted. The original joint requirements remain; no final holdout access or automatic integration follows. A local alternative is not an assurance that the correction model is nearly finished, and mask fragmentation remains separate.

## Verification

Scripts 663–664; private `outputs/colour_nonharm_loss_trace_v1`. Exact six-case selection comes from the complete prior/current core benefit transition, not hand-picked losses. Independently replayed 12 routes, fitting row memberships, clean/colour blocker sets and scalar action-cost sums, with source hashes unchanged. All passed. Zero fits, inference, new predictions, rendering or image/holdout reads. DINO was not used.
