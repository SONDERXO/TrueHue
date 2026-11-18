# Matched facial-only versus scene-aware gate — 6 November 2026

The user authorizes one scene-aware gate comparison. Freeze settings before
fitting. Use only the completed whole-scene420attempts, original10publisher-key
folds, saved nested MST models and the saved face-plus-scene correction tree.
Compare five-feature facial gate versus12-feature facial+scene gate on exactly
the same data, feeding both to the same saved face-plus-scene correction controls.
This isolates gate features; do not compare differently trained correction trees
or import the older restricted-region gate as a matched baseline.

Use the existing fixed logistic gate procedure: C1,L2default,lbfgs,
max_iter1000,tolerance1e-4,seed42; equal fitting-key total/equal binary-class
weight within key, weights summing to fitting-row count. Standardize on training
rows with those weights. Decision strictly positive logit→apply correction;
zero/negative→exact unchanged input. No threshold/penalty/classifier sweep.

Twenty new gates, ten per method; zero new MST, correction-tree, mask, target
fits or distortions. Train on all397available facial-feature rows, including
synthetics without valid correction targets. Labels are original versus imposed
synthetic recipe, not real-world aesthetic correction need. Known natural
warm/cool source appearances remain clean references. No recipe, condition,
source label, target availability or original-image pixel enters inference.

Reconstruct each gate-training key's MST feature with both its own and outer
key excluded, using the saved55ridges. Held features reuse the corresponding
saved outer feature vectors. Append the fixed seven scene features only for
the scene-aware method; no new feature calculation policy or selection.

Preserve14original failures without support and nine undefined-ITA no-ops.
Unavailable decisions are not true negatives; retain all attempt counts.
Report both clean false corrections and synthetic missed corrections, per-layer/
condition counts, always-correct/always-unchanged baselines and operational
clean/core/stress errors, equal-key means and regressions. Use the same saved
scene-aware correction tree as an ungated operational comparator for both.

Verify20training memberships/scalings, nested exclusions and linear export,
all794held gate decisions and812scored rendered outputs. Inspect all29clean
and the two previously fixed core/stress cases for all30sources, with original
failures retained. Stop after this one paired test. No gate adoption, threshold
tuning, pruning/depth/feature combination sweep, new dataset or app change.
The borrowed-mask/studio/chart cues and private author terms remain limitations.
