# Ten-source training-design audit

28 October 2026. Completed the next saved-data design audit after the reviewed
ten-source comparison. No model was fitted, feature changed, source selected,
mask edited or quality gate relaxed. Script 172 checks all 20 saved routes and
leaf target means and compares the original 16 pair IDs on identical evidence.

## Expansion did not improve the original cohort

| Same original pair IDs | Pairs | Earlier eight-source folds | New ten-source folds |
| --- | ---: | ---: | ---: |
| All | 16 | 10.729 | 10.794 |
| Unchanged | 8 | 6.524 | 6.460 |
| Distorted | 8 | 14.935 | 15.128 |

Values are mean CIEDE2000; lower is better. Images, masks, features, targets and
scoring regions match exactly for these pair IDs. Fitting pools differ, since
the expansion adds two source groups. Four old pairs improve, three worsen and
nine are unchanged. This is a descriptive comparison, not a significance claim.

The ten-source overall result of 9.643 remains correct, but its comparison with
the old 10.729 average mixes model changes with a changed evaluation cohort.
It must not be reported as evidence that expansion improved the original eight
sources. Within the ten-source cohort, the no-correction comparison still
improves overall while failing the clean-control gate.

## Why clean controls fail

Of seven harmed unchanged inputs, five route into mixed identity/distortion
leaves and two into distortion-only leaves. None routes into an identity-only
leaf. The regression averages the fitting targets within each leaf; including
identity examples in a fitting set does not guarantee an identity prediction
for an unseen clean photo. Source-dependent photographic color/exposure and
the synthetic recovery task remain entangled in these small fitting sets.

For three of the seven harmful controls, a distorted fitting input is nearer
than every identity fitting input in standardized Lab3 distance. This becomes
four of seven using all five model features. Conversely, several failures have
a nearer identity example but still route to harmful targets. Both representation
proximity and finite-tree partitioning deserve attention; neither alone explains
every failure. Distance uses each fold's fitting-only population standard
deviations and is descriptive, not a confidence or perceptual score.

Both light distortions (6236/22454) and medium-distorted 67583 still reach
identity-only leaves and receive no correction. This is the same qualitative
failure as before expansion. There are no exact identity/distortion feature
collisions after float32 conversion, so this audit does not prove mathematical
nonidentifiability or that every possible tree must fail.

Across ten saved trees, split counts are L*:12, a*:10, b*:23, ITA:14, MST:2.
These counts are not importance estimates or validation of category-aware
correction. ITA and the experimental MST mapping derive from the same pooled
color measurements; retaining MST satisfies the required development path but
does not supply an independent exposure reference. Keep the mapping's existing
weak-accuracy, no-MST10 and limited-evaluation disclosures.

## Implementation decision

The current development recipe is not eligible for runtime promotion. Stop
small source-expansion/refit cycles on these exposed examples and retain the
current five-feature MST tree as a documented unsuccessful development candidate.
No arbitrary identity cutoff, deeper-tree search or gate relaxation is justified
by these results. The recent all-severity capacity experiment also shows that
clipping and approximate three-parameter recovery remain independent limits.

Before another learning experiment, freeze a representation/training hypothesis
that specifically addresses clean-versus-distorted ambiguity. Any richer facial
statistics must be input-derived, retain ITA and mapped MST, avoid reference
features, and be assessed with source-group separation. Earlier ten-feature
brightness experiments already failed on different data; do not present another
brightness summary as an established solution. A new design needs its own
predeclared comparison, with original no-correction and clean-control outcomes
reported separately and all past negative results retained.

This audit does not supply calibrated references, independent final subjects,
dark-complexion coverage or an operationally validated MST model. Expert MOS,
final evaluation and Android correction integration remain unfinished. Android
remains paused; CPM remains deferred. No new approval is inferred from software
verification or from an overall average improvement.

## Verification

[All 20 routes and descriptive neighborhoods](../outputs/table2_training_design_audit_v1/summary.json) |
[Leaf membership table](../outputs/table2_training_design_audit_v1/review-index.md) |
[Checks](../outputs/table2_training_design_audit_v1/verification.json).

Verified 20 float32 routes and leaf means, 40 independently recomputed distance
sets, exact input/feature/target agreement on 16 matched pair IDs, held-source
and known-duplicate-group separation, and unchanged tracked hashes. The latest
full suite remains 692 passed from the earlier application-mask stage; no new
full-suite result is claimed for this script-only audit.
