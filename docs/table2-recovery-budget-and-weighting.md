# Recovery budget and fixed severity-weighting comparison

28 October2026. Audited the fixed15source/30paircohort before another training
change, then tested the [predeclared control/severity weighting rule](table2-severity-weighting-protocol.md).
No reviewed mask, MST mapping, source allocation, accepted concern or adoption
gate changed.

## Exact error accounting

Script204partitions the reference scoring region into selected application
pixels and missed pixels. The latter remain identical to the input under every
allowed correction. Per-image CIEDE2000andRGBMSE sum exactly from these two
regions when each contribution uses the same full-reference denominator.

| Distorted subset | Pairs | Missed reference fraction | Fixed-support CIEDE floor | Learned5 CIEDE | Saved fitted-target CIEDE |
| --- | ---: | ---: | ---: | ---: | ---: |
| All | 15 | 21.95% | 4.445 | 11.598 | 8.902 |
| Light | 4 | 5.22% | 0.675 | 9.478 | 1.382 |
| Medium | 11 | 28.03% | 5.816 | 12.368 | 11.637 |

The floor is the missed-region delta sum divided by reference-pixel count.
It is a genuine nonnegative bound for correction preserving pixels outside the
current application support, relative to this estimated reference region—not
an annotated whole-face skin bound. No segmentation adjustment follows here.
The saved fitted target minimizes bounded local RGBloss; it is not a globally
optimal CIEDE2000solution. Its difference from learned error is descriptive and
can be signed, not a causal or mathematically optimal model-error decomposition.

Light cases have a much larger empirical learned-versus-fitted gap; medium
cases combine limited support and substantial recovery residuals. All clean
targets remain exact identity with zero support floor, so model-induced clean
error is avoidable in principle even though unseen-source identification remains
unresolved. This accounting does not invent true source exposure/color labels.

## Training hypothesis and result

Using the same5features/depth3/seed42/minleaf1tree, weighted fitting controls to
half the loss and divided the other half equally across fitting severity groups
present in each fold. Counts use only28fittingrows. Reference-estimated severity
is training metadata only,never an inference feature. This changes source
influence across groups and is a separately labeled objective experiment, not
an approved final-method amendment or guaranteed class balancing on real MST.

Exactly15weighted regressors are fitted. A conservative fitting-control leaf
variant reuses their splits. No ratio,weight,depth,feature or source search.

| Mean CIEDE2000 | No correction | Original baseline5 | Weighted | Weighted clean-leaf |
| --- | ---: | ---: | ---: | ---: |
| All30 | 10.076 | 8.534 | 9.324 | 8.313 |
| Fifteen unchanged | 0.000 | 5.470 | 7.211 | 4.450 |
| Fifteen distorted | 20.153 | 11.598 | 11.436 | 12.175 |
| Harmed clean controls | 0 | 6 | 11 | 3 |

Weighted distortion error improves slightly but clean harm worsens. Its
conservative variant harms68453,62331,75027and does not beat the prior unweighted
conservative overall7.995with two harmed controls. **Both new variants fail the
clean gate.** Neither is activated, and no new weights are selected from these
outcomes. Per-target MAE remains separately labeled approximate-target error,
not skin-color truth or MST accuracy.

## Checks and disposition

Script204verifies90methodoutputs across30cases with exact CIEDE/MSE partitions,
independent full-reference metric recomputation and unchanged outside-application
pixels/hashes. Script205freezes the new objective before15fits and saves30exports/
60newcorrectedimages. Script206independently recomputes15fittingweightsets,
weighted leaf target means,60predictions and output PNGs with separate RGB
arithmetic,source/duplicate-group separation,metrics/gates and original hashes.
All checks pass. No new visual-quality inspection is claimed.

Six new weight tests cover an imbalanced fitting pool, absent severity handling,
input immutability and rejection of missing groups/unknown variants. Full suite:
**715passed in12.20seconds**, fresh workspace temporary directory/cache disabled.
The audit supports concentrating on light/clean ambiguity and treating medium
capacity limits explicitly, but this particular reweighting is not a successful
solution. Preserve prior models and negative results. No active model, lookup,
mask or Android asset changed. Photographer evaluation stays deferred until
model completion using the existing GoogleForm; Android paused;CPM deferred.

- [Exact recovery accounting](../outputs/table2_recovery_budget_v1/summary.json)
- [Accounting verification](../outputs/table2_recovery_budget_v1/verification.json)
- [Weighted comparison](../outputs/table2_severity_weighting_v1/summary.json)
- [Independent weighted verification](../outputs/table2_severity_weighting_v1/verification.json)
