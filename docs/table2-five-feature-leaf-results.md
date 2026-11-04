# Five-feature conservative leaf policy

28 October2026. Executed the [fixed protocol](table2-five-feature-leaf-protocol.md)
on the15source/30paircohort. Reused baseline5splits and parameters; only leaves
containing fitting identity controls receive exact identity outputs. No fitting,
mask/feature/MST changes, source selection or threshold/depth search. Fitting
membership is computed separately in every prescribed held-source fold.

| Mean CIEDE2000 | No correction | Original baseline5 | Conservative baseline5 |
| --- | ---: | ---: | ---: |
| All30 | 10.076 | 8.534 | 7.995 |
| Fifteen unchanged | 0.000 | 5.470 | 3.664 |
| Fifteen distorted | 20.153 | 11.598 | 12.326 |

Six predictions change. Clean harms decrease from6to2, but distortion recovery
weakens. **Overall gate passes; zero-clean-harm gate still fails.**1398and75027
remain harmed. No active model or Android asset changes. This does not justify
relaxing the gate or adding source-specific rules. The earlier conservative9
feature policy also harms these two controls; the problem is not resolved by
changing the mean/split schema or post-processing mixed leaves.

Script196independently checks original sklearn training-leaf membership against
all15modified portable exports and verifies all210fitting-control occurrences
produce identity. These are repeated controls across folds, not210people.
All30heldoutputs are reconstructed with independent RGB arithmetic, checked
after PNG roundtrip and scored against unchanged reference support. Original
artifact/input hashes remain unchanged. The completed experiment includes its
own verification record; no new shared algorithm changes or full-suite run.
Latest full suite remains705passed from the control-partition stage.

This is a conservative output-policy experiment, not ordinary regression leaf
means or a validated final-method amendment. Retain all accepted mask concerns,
rejected sources/holds, experimentalMST, approximate-target/clipping and
photographic-reference limitations. Repeated exposure to these sources prevents
independent final-performance claims. Photographer evaluation remains deferred
until model completion using the existing Google Form; Android paused,CPMdeferred.

- [Frozen policy plan](../outputs/table2_five_feature_clean_leaf_v1/plan.json)
- [Parameters, leaf membership and metrics](../outputs/table2_five_feature_clean_leaf_v1/summary.json)
- [Verification](../outputs/table2_five_feature_clean_leaf_v1/verification.json)
