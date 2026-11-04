# Fitting-only target-scale comparison

28 October2026. Executed the [frozen experiment](table2-target-scaling-protocol.md)
to test whether unequal numeric scales of gamma/red/blue targets were limiting
the five-feature regression. Same15sources/30pairs,15held-source/known-duplicate
folds,28fittingpairs each,fiveLab/ITA/MSTfeatures,depth3/seed42/minimumleaf1,
unweighted targets and unchanged masks/scoring support.

For each fold, computed only fitting-target means and population standard
deviations, standardized the three targets and fitted one tree. Exported the
learned splits with raw-unit fitting target means in each leaf. Constant target
axes use scale1. The second output policy uses the existing fitting-control
identity override on the same splits; it requires no extra fit. Exactly15fits,
no weights/scale/depth/feature search and no held-label target statistics.

| Mean CIEDE2000 | No correction | Raw baseline5 | Standardized targets | Standardized + clean leaves |
| --- | ---: | ---: | ---: | ---: |
| All30 | 10.076 | 8.534 | 10.133 | 9.320 |
| Fifteen unchanged | 0.000 | 5.470 | 7.816 | 5.477 |
| Fifteen distorted | 20.153 | 11.598 | 12.450 | 13.163 |
| Harmed clean inputs | 0 | 6 | 11 | 3 |

The standardized-target tree fails both quality gates. Its conservative policy
passes only overall improvement against no correction and fails clean preservation.
It is also worse overall than the previous conservative five-feature policy,
which scored7.995andharmed2cleancontrols. Equalizing target scales therefore does
not improve the required reconstruction/safety outcomes in this fixed comparison.
Do not select another target weighting from these outcomes or replace earlier
models. A mathematical change to loss units is not evidence of perceptual quality.

The conservative standardized variant harms1398,68453,75027clean. No source was
removed because of this result. All accepted hair/body/background concerns,
7rejectedsourceIDs and74holds remain unchanged. Separate gamma/red/blue MAE is
recorded against approximate fitted recovery targets; these errors are not MST
label accuracy, calibrated skin-color accuracy or photographer opinions.

## Verification

The isolated`target_scaled_tree.py`training helper has four tests covering
constant axes, exact raw-unit exports, repeated-feature leaf means, inference
not changing fitting statistics, positive targets and feature schema. The full
suite passes **709tests in14.42seconds**, using a fresh workspace temporary
directory and cache disabled.

Script202saves fitting statistics,15normalized models and30portable exports
(ordinary/conservative). Script203independently recomputes all15fitting statistics,
normalized and raw leaf means,checks inverse-scaled predictions,source/duplicate
separation,60newcorrectedPNGs with separate RGB arithmetic,metrics/gates and
original hashes. All checks pass. No active Python model,Android asset,mask,
MSTlookup or default inference path changed. No new visual-quality review is
claimed; verification is numerical and artifact-based.

This unsuccessful objective experiment is retained alongside the earlier
comparisons. The simpler unscaled baseline remains the comparison reference;
none of these results establishes a finished broadly effective model. The
range-guard's narrow cohort pass and weak intervention/stress performance also
remain qualified. Existing reference/clipping/MST/person/category limitations
persist. Photographer evaluation waits until model completion using the existing
GoogleForm; Android remains paused; CPM deferred.

- [Frozen fitting plan](../outputs/table2_target_scaling_v1/plan.json)
- [Per-case scores, target MAE and statistics](../outputs/table2_target_scaling_v1/summary.json)
- [Independent verification](../outputs/table2_target_scaling_v1/verification.json)
