# Training-control leaf policy: development result

28 October2026. Completed the separately frozen
[clean-leaf protocol](table2-clean-leaf-policy-protocol.md). At any saved
nine-feature leaf containing a fitting identity control, replaced its output
with exact identity parameters. Distortion-only leaves keep their original
values. The rule uses training labels only; no held-source reference/target or
identity label enters policy construction. No splits were refitted or thresholds
searched. This is a changed experimental output policy, not ordinary
least-squares leaf regression or an adopted final method.

Same reviewed20pairs,10source/duplicate-group folds,9actual-inputfeatures including
ITA/MST, masks and scoring support as the prior chroma experiment. The prior
policy, model artifacts,5rejectedsourceIDs,21heldsources and51803minor-hole
concern remain preserved. Modified portable exports are separate local artifacts.

| Mean CIEDE2000 | No correction | Original chroma9 | Training-control leaf policy |
| --- | ---: | ---: | ---: |
| All20 | 10.577 | 8.898 | 8.538 |
| Ten unchanged | 0.000 | 3.488 | 2.767 |
| Ten distorted | 21.154 | 14.309 | 14.309 |

Five held predictions change, all clean controls:22211,62331,84364,51803,83205
become exact identity.53109,6236,67583,22454were already unchanged. All ten
distorted predictions and corrected pixels remain as before. Thus nine of ten
held unchanged controls are now preserved, but **the zero-clean-harm gate still
fails**. The overall-improvement gate passes. No active model or Android asset
was replaced, and no all-data release model was fitted.

The remaining failure is clean75027, whose CIEDE2000 remains27.672. In its held
fold6, leaf7contains only53109medium and67583medium fitting examples. It predicts
approximately gamma2.31236,red1.01631,blue0.91581; no fitting identity member
triggers the conservative policy. This is a serious failure, not a negligible
residual that can be omitted or waived. Training-control preservation does not
guarantee preservation of an unseen clean source.

All90fitting-control occurrences across ten folds output exact identity after
the policy. These are repeated appearances of the same ten-source controls,
not90independent subjects or generalization cases. The result gives limited
support to treating mixed leaves conservatively on this exposed cohort; it
does not validate a reliable correction/no-correction detector. It may withhold
useful correction on future distorted inputs. The unchanged light distortions
and visible distortion artifacts from the earlier experiment still apply.

Codex inspected all ten boards. Five newly preserved clean outputs now match
their inputs.75027still shows severe over-lightening, and the distorted images
retain the same patches/incorrect adjustments as the chroma9candidate. This is
qualitative inspection, not photographer MOS or new user approvals.

Scripts175/176save and independently replay the experiment. Verification uses
the original sklearn models to recompute fitting-leaf membership, checks every
portable split node is unchanged, verifies training-only output replacement,
all20held predictions,10exports,90fittingcontroloccurrences, independent RGB
pixels, metrics/gates, source/group separation, exclusions and original hashes.
All checks pass. No shared algorithm module changed; latest full suite remains
**695passed** from the prior chroma-feature stage, not a new full-suite run.

Keep this result experimental. Do not tune a special-case75027rule, relax the
identity gate or select another policy threshold from these outcomes. Any next
learning design must distinguish clean inputs arriving in distortion-only
regions using fitting-only evidence and then test on held sources. The current
result does not establish how to do that reliably. Clipping/approximate recovery,
photographic references, weak MST and absent dark-group/person-disjoint/final
validation remain limitations. Android is paused; CPM deferred.

- [Frozen policy and cohort](../outputs/table2_clean_leaf_policy_v1/plan.json)
- [Metrics and fitting-leaf membership](../outputs/table2_clean_leaf_policy_v1/summary.json)
- [Independent verification](../outputs/table2_clean_leaf_policy_v1/verification.json)
- [All comparison boards](../outputs/table2_clean_leaf_policy_v1/review.html)
