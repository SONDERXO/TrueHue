# Fitting-leaf support guard: narrow gate pass, limited recovery

28 October2026. Executed the [frozen range-guard protocol](table2-leaf-support-protocol.md).
The five-feature conservative tree keeps all original splits. Each leaf stores
float32 minima/maxima from its fitting inputs on all five axes. A query outside
any reached-leaf range receives identity; otherwise the existing conservative
output is used. Ranges come only from the28fittingpairs in each held-source
fold. No new tree fit, threshold margin, source selection or mask change.

This auxiliary policy adds input-range metadata beyond the bare tree. It is an
experimental support heuristic, not standard regression, calibrated confidence
or a guarantee of joint/distributional support. No final method amendment or
active-model replacement follows.

## Prespecified15source/30pair development cohort

| Mean CIEDE2000 | No correction | Previous conservative5 | Range-guarded5 |
| --- | ---: | ---: | ---: |
| All30 | 10.076 | 7.995 | 9.796 |
| Fifteen unchanged | 0.000 | 3.664 | 0.000 |
| Fifteen distorted | 20.153 | 12.326 | 19.592 |

Both prescribed gates pass on this repeatedly exposed development cohort:
overall error is strictly lower than no correction and no held unchanged input
is harmed.1398and75027are now preserved. **This is a narrow pass:**21of30queries
trigger the support guard, and only one of15distortedinputs is actually changed.
The other14distortedinputs remain unchanged, either through abstention or an
identity leaf.83205mediumprovides the entire gain,23.189to14.776CIEDE2000.

The strict gate therefore does not establish sufficiently broad correction.
Do not call the model finished, claim independent validation, promote it or hide
the very low intervention coverage. The poorer mean relative to unguarded
correction reflects the cost of conservatism. Repeated hypotheses on these
exposed subjects also remain a source of development-selection bias.

## Frozen-rule stress check

Without changing the rule, script199applies it to the pre-existing24all-severity
probes from eight accepted sources, using each source's prescribed15sourceheld
fold. Saved actual-input features/masks are used; no new reference features or
targets enter predictions. All23valid probes are scored;75027darkremains the
known measurement failure without fallback.

| Counterfactual severity | Successful / attempted | Changed inputs | No correction | Guarded |
| --- | ---: | ---: | ---: | ---: |
| Light | 8 / 8 | 3 | 12.694 | 13.746 |
| Medium | 8 / 8 | 1 | 23.488 | 22.437 |
| Dark | 7 / 8 | 0 | 30.117 | 30.117 |

Light recovery is worse on mean than doing nothing. Dark probes receive no
correction at all. These findings prevent treating the cohort gate pass as
general evidence of safe, effective correction. The stress probes are also
historically exposed, not a fresh final holdout; dark distortion severity is
not dark-complexion coverage. No pooled mean across unequal scopes is used.

## Verification and disposition

Script197saves the frozen policy,15range sets and30outputs. Script198independently
uses original sklearn leaf routing and NumPy float32 fitting arrays to reconstruct
all ranges and decisions, checks all30RGBoutputs with separate arithmetic,
metrics/gates and original hashes. Script199also independently checks sklearn
range decisions and pixels on23successful stress cases and preserves the failed
case. Both verification records pass. No shared algorithm module changed;
latest full suite remains705passed from the earlier control-partition stage,
not a new full-suite run.

Retain this as a conservative baseline for future training design, not a release
model or a reason to tune the range margins on these cases. The next design must
improve the fraction of genuinely distorted inputs corrected without introducing
clean harm, and demonstrate that beyond repeated exposure to this cohort.
All accepted hair/body/background concerns,7rejectedsourceIDs,74heldsources,
weakMST/clipping/photographic-reference/person/category limitations remain.
Photographer evaluation is deferred until model completion using the existing
GoogleForm. Android remains paused; CPM deferred.

- [Development cohort results](../outputs/table2_leaf_support_guard_v1/summary.json)
- [Independent guard verification](../outputs/table2_leaf_support_guard_v1/verification.json)
- [Frozen-rule stress results](../outputs/table2_leaf_support_stress_v1/summary.json)
- [Stress verification](../outputs/table2_leaf_support_stress_v1/verification.json)
