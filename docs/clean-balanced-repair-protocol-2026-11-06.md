# One fixed clean/core/stress balance repair — 6 November 2026

After the user requests clean-harm diagnosis and a targeted repair, test one
objective change on the saved nested experiment. Read-only diagnosis shows
clean rows contribute about8.1%of fitting rows; every held clean route mixes
nonclean targets, with raw leaf means reproducing all29control drifts. No exact
float32feature duplicates with conflicting targets were found in any fold.
Nearest-neighbour overlap does not prove irreducibility or identify weighting
as the sole cause. This is a hypothesis test, not a guaranteed repair.

Use exactly the saved357trainable rows,10outer folds, inner/outer MST artifacts,
feature vectors, targets, fixed supports and420attempts. No new images,
distortions, target fits, MST fits, source labels, masks or availability changes.
Keep five continuous-schema features and three outputs, depth3/seed42/minleaf1.

Change only the fitting objective: give every training publisher key equal total
weight and within each key give clean/core/stress equal total weight. Within a
key/layer divide its weight equally among its available fitting rows. Require
all three layers per training key; fail rather than invent a missing layer.
For Ktraining keys and n(key,layer)rows, weight=1/(K*3*n(key,layer)). No free
hyperparameter, clean multiplier search or outcome-based threshold.

Use these weights in target means, population standard deviations, tree fitting
and raw leaf means. A constant target axis uses scale1. Normalize only fitting
targets. Reuse identical held feature vectors and MST predictions. One candidate
tree per outer fold,10new fits. No identity detector/gate or clean inference label.

Evaluate all420attempts with the same availability/fallback policy. Show matched
baseline/candidate clean/core/stress MAE, equal-key error, regressions, clean
changed outputs and nonclean trade-offs. Report clean failure even if mean
clean harm decreases. No automatic deployment/readiness claim or further fit.
Preserve baseline hashes and save objective weights, trees, normalization and
predictions privately; verify weights, raw leaf exports and renderer replay.
This remains a borrowed-mask restricted-region development experiment.
