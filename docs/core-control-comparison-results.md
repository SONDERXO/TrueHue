# Core control-aware training comparison

27 October2026. Completed the user-authorized fixed comparison. **Adding
unchanged/mild controls helps against the older recipe, but still loses to
no correction and does not solve overcorrection. The runtime model is unchanged.**

[Comparison gallery](../outputs/core_control_comparison_v1/review.html) ·
[Aggregate CSV](../outputs/core_control_comparison_v1/aggregate.csv) ·
[Decision gates](../outputs/core_control_comparison_v1/readiness.json) ·
[Independent verification](../outputs/core_control_comparison_v1/verification.json).

## Fixed design and eligibility

The [protocol](core-control-comparison-protocol.md) preceded fitting. Reviewed
the earlier control-recipe experiment before designing this comparison; this
is not a claim that controls had never been tested. Earlier script61used
hair-clean256inputs/expanded application support. This comparison uses the
current core runner's native224inputs, four Lab/ITA features and fixed legacy
measurement/application masks, all already replayed in the core check.

The prior22screen-pass IDs form a **conservative fitting-ID gate**, mapped via
their explicit `parent_pair_id` to the original core rows. All eight previously
held IDs stay out of every fit. The old256screen is not silently reinterpreted
as native224mask accuracy or a new quality approval. The original30training-
source probes remain the diagnostic universe; no row is promoted or reassigned.
Three external-development, four clipped-stress and the original failed attempt
retain their existing roles and do not enter these fits or new model selection.

Seven source/known-duplicate groups are held out in turn. Six groups contain
the22primary eligible probes. Source12288has no eligible fitting rows; its
additional fold diagnoses four held rows using the remaining eligible pool.
All variants and known duplicates of each evaluated source remain outside
that fold's fits. The eight held probes are reported separately, never pooled
into primary accuracy. Subject identities remain unverified.

Each fold fits two depth3/seed42/minimum-leaf1regressors, with no weighting,
feature/target scaling or search:

- Older recipe: eligible dark/color-shift/bright-warm variants only.
- With controls: the same eligible pool plus unchanged/mild variants.

Fourteen experimental fold trees were saved under the ignored output directory;
none replaces the runtime or becomes a final production model. The extra12288
diagnostic fold fits the six-source eligible pool, not a newly admitted source.
All14verification refits are replay checks, not extra candidate settings.
No new source, image, synthetic pair, mask or reference target was created.

## Source-held-out results

Mean CIEDE2000 on each fixed historical source-generation region; lower is better:

| Primary probe type | Pairs | No correction | Older recipe CV | With controls CV |
| --- | ---: | ---: | ---: | ---: |
| Dark | 4 | 12.304 | 14.509 | 8.074 |
| Color shift | 3 | 7.190 | 13.233 | 9.595 |
| Bright/warm | 3 | 8.377 | 7.660 | 6.656 |
| Unchanged | 6 | 0.000 | 7.369 | 6.756 |
| Mild | 6 | 2.820 | 6.939 | 4.906 |
| All primary probes | 22 | 5.129 | 9.389 | 6.865 |
| Equal-source mean | 6sources | 4.746 | 9.002 | 6.774 |

Controls improve the average versus the older recipe, but12/22primary probes
still worsen relative to no correction, including6/6unchanged and2/6mild.
The older recipe worsens18/22, including6/6unchanged and5/6mild. Lower average
error does not establish nonharm or consistent source-level improvement.

Only75027has all five eligible variants. On that source, no correction scores
5.540, older recipe9.347 and with controls9.726. This tiny sensitivity subset
does not support generalization; it is an important counterexample to uniformly
better behavior. Per-source scores and sensitivity are saved separately.

The eight held-ID diagnostic probes score8.866without correction,9.115older
recipe and8.065with controls. Their masks/reference status remain held;
an attractive diagnostic average cannot justify their admission.

## Current frozen runtime comparator

The requested current-tree comparison is retained explicitly as **seen-source
history**, separate from CV. All seven sources occurred in its original fit,
even when a particular control variant did not. On the same22primary inputs
its mean is6.294(pair-weighted),6.828(equal-source). These reproduce the saved
core results exactly. They are not equally source-held-out and must not be
ranked as a fair generalization comparison with the two refitted recipes.

The fair primary comparison uses an older-recipe tree refitted with each source
held out, rather than allowing the frozen runtime's source overlap to give a
misleading baseline. All frozen parameters/source-model hashes remain intact.

## Inspection and explanation

Codex inspected all seven source boards, covering30probes with both held-source
recipe outputs and visible primary/held labels. Controls help some dark/color
or mild examples, but unwanted identity corrections persist.51739's unchanged
output is substantially brighter with controls than with the older recipe;
22454unchanged/mild remains warm/bright.75027also worsens overall. Hard mask
patches remain because the mask policy was deliberately fixed. These are
technical observations, not user approval or expert MOS.

After the frozen comparison, a separately labeled post-hoc trace checks24
primary unchanged/mild predictions across the two fitted recipes. Every leaf
prediction matches the mean of its actual training members' inverse targets;
none contains the held source. This confirms real routing/leaf averaging,
not leakage or a parameter-application bug. It does not prove all four-feature
methods are impossible or justify tuning a skip threshold on these probes.

The finding is consistent with the earlier control comparison: adding controls
alone is insufficient on this small exposed, appearance-dependent dataset.
This new result concerns the current core mask/input path and must not be
substituted for the earlier256results or described as independent confirmation.

## Verification and decision

Scripts120–122freeze folds before fitting, record exact fitting/evaluation IDs,
save models, independently rebuild membership without the planning helper,
recompute known inverse targets, refit all14models with fixed settings, and
replay120parameter/transform/metric records plus44aggregate rows. All original
runtime/input/source/review/reference/ledger/mask hashes remain unchanged.
Pixels outside application support stay identical. Final checks verify15local
gallery links, seven inspected source boards and24post-hoc leaf means.
**546tests passed in11.44s**, including9new tests for eligibility partitions,
held-only diagnostic folds, source exclusion, failed/clipped/external rows and
inconsistent duplicate groups.

The declared revised-versus-old mean-error gate passes; revised-versus-no-
correction, unchanged nonharm and mild nonharm fail. **No runtime replacement,
final all-pool production fit or new data admission follows.** No source,
feature, depth, weight or correction cutoff was adjusted after seeing results.

Keep this negative result. Further core model work needs a specific data/
measurement rationale addressing the repeated control failures before another
fit; simply repeating control additions on these same few sources is not a
demonstrated solution. The model remains a decision-tree regressor for gamma/
red/blue, without a fabricated MST category. The four-feature/control-variant
development recipe, selected22IDs and source-based CV remain distinctions from
the paper's final MST-conditioned data/method requirements. No sample-size,
fairness, intrinsic skin-color, expert-review or final-accuracy claim is made.
CPM stays deferred; paint/makeup, face/visible-neck, operational MST, finaldata/
reference/splits/evaluation, expert MOS and Android remain recorded limitations
or unfinished requirements. Existing approvals, holds and fold plans are kept.
