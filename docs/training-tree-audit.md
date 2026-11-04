# Training and tree audit — 23 October 2026

Implemented follow-up: [exposure and identity data revision](exposure-identity-training-revision.md)
adds14 checked inputs and prepares source-grouped folds. No learner fitted yet.

The frozen tree is learning from **incomplete exposure coverage and mixed-target
branches**. This explains specific wrong brightness adjustments. The audit did
not retrain or tune the model, change masks, or alter dataset routing.

## Training coverage

| Synthetic variant | Training | Development validation | Clipped stress | Excluded input |
| --- | ---: | ---: | ---: | ---: |
| Darkened | 7 | 1 | 0 | 0 |
| Bright/warm | 3 | 1 | 4 | 0 |
| Color shift | 6 | 1 | 0 | 1 |

Training still consists of16 pairs from seven sources. Validation is three
variants of a single separate source. Four bright/warm probes are excluded from
training because they clipped; they remain stress-only, not new training data.
There are no full identity targets `[gamma=1, red=1, blue=1]` in training. Color-
shift examples have neutral gamma but non-identity color gains, so they are not
unchanged-image controls.

The three eligible bright/warm training inputs have mean L*37.25–47.32. Their
source reference mean L* spans28.15–37.90, whereas the four clipped bright/warm
sources span43.38–64.04. The clipping rule leaves this bright/warm training subset
without the latter source range. Reference values are audit metadata only, never
model features, MST labels, demographic groups or calibrated skin truth.

All four stress inputs fall outside at least one overall training-feature
range. The validation examples are within each marginal range, but that does
not establish coverage of their joint feature combinations.

## Exact tree behavior

The saved depth3 tree has four leaves. Thresholds below are rounded for reading;
the artifacts retain exact values and sklearn-compatible float32 routing.

| Branch | Training support | Predicted gamma |
| --- | --- | ---: |
| L* ≤25.17 | 3 darkened examples | 1.4286 |
| L* >25.17, b* ≤23.44, a* ≤9.98 | 2 darkened +4 color-shift examples | 1.1429 |
| L* >25.17, b* ≤23.44, a* >9.98 | 3 bright/warm +2 color-shift examples | 0.8800 |
| L* >25.17, b* >23.44 | 2 darkened examples | 1.4286 |

The last leaf contains only darkened51739 and6236. Their bright/warm stress
variants also take that branch: b*31.04 and30.05 exceed23.44. It therefore
predicts gamma1.4286, although both require inverse gamma0.8. The error is
reproduced directly from the saved model and training rows; it is not an inverse-
formula bug. Adding depth alone does not supply missing bright targets to a
branch with identical dark-only targets.

Bright/warm22454 reaches the mixed dark/color leaf and gets gamma1.1429 instead
of0.8. Thus three of four bright stress cases brighten when they should darken.
The fourth stress case,12288, gets gamma0.88: the right direction, imperfect
magnitude and color parameters.

The bright/color leaf averages incompatible adjustment vectors. Its five
training targets have gamma `[0.8,0.8,0.8,1,1]`, giving0.88. It also predicts red
gain1.0156, while bright/warm examples require0.9083. This is a concrete compromise
that can adjust color in the wrong direction even when gamma direction is right.

All six training color-shift cases receive non-neutral gamma although their
known gamma is1. Direction mismatches here mean unnecessary gamma adjustment,
not an opposite brighten-versus-darken command. Training has zero opposite-gamma
cases; validation has zero, while stress has three. Gamma, red and blue errors
are recorded separately in the per-pair traces.

ITA is passed as the fourth declared feature, but this tiny fitted tree never
selects it for a split. That is not evidence to remove ITA or claim the thesis
MST mapping is solved. Target variances differ (gamma0.06536, red0.00927,
blue0.00737); no target rescaling was tested or assumed to help.

## Mask limitations remain separate

The audit attaches the prior known-parameter/current-mask residual to every
successful pair. The severe22454/dark and12288/color-shift failures are still
visible. Better learning cannot correct pixels excluded by the application mask.
No case was silently relabeled, deleted or newly approved for training.

## Recommended next controlled revision

Before increasing tree depth or collecting another review batch:

1. Create a separately versioned development table with mild exposure-only
   brightening and unchanged-image controls using the same reviewed training
   sources. Exposure-only gain settings can avoid the red-gain clipping that
   removed the original bright/warm probes. Verify actual saved-input clipping
   and inference success for every attempt rather than assume availability.
2. Preserve the current source partitions, input-only feature schema and mask
   option. Keep clipped stress examples and the reserved final test out of fitting.
   Record failures and source/variant coverage explicitly.
3. Use source-grouped checks within the training sources for any model choices.
   Do not tune repeatedly against the one-source development set and call that
   fresh validation. Identity controls mean no synthetic transform, not that the
   ordinary source photo is calibrated real-world ground truth.
4. Keep the known mask-limited cases explicit and assess input-quality handling
   before expanding the source pool. More examples alone are not a mask fix.

The linked follow-up implements the data revision for development only. It is
not a promise of improved performance or approval of final methodology.

## Artifacts and verification

Open the [coverage/routing figure](../outputs/training_tree_audit_v1/coverage_and_routing.png)
or its [standalone SVG](../outputs/training_tree_audit_v1/coverage_and_routing.svg).
`outputs/training_tree_audit_v1/` also contains exact paths, leaf membership and
target means, pair traces, source routing, feature-range flags and input hashes.
Nearest-training-row distances are descriptive in standardized training-feature
coordinates, not an alternate predictor or evidence of generalization.

Reproduce from the project root:

```text
venv/Scripts/python.exe scripts/44_audit_training_tree.py
venv/Scripts/python.exe scripts/45_plot_training_audit.py
```

442 tests passed, including gamma/identity distinction and float32 threshold
routing without model mutation. Every leaf value matches the mean of its actual
training targets; sample counts match all16 rows. Traces for all23 successful
pairs reproduce saved predictions and features. Original model, table and audit
input hashes were checked. The plot was rendered and visually checked.

No correction output, training manifest, frozen human label, reserved test,
Android file or approved thesis scope changed. The same prototype weights remain
in use; this audit introduces no new learned-model score.
