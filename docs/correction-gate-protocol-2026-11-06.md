# One fixed synthetic-distortion gate — 6 November 2026

The user explicitly authorizes a two-stage experimental extension. Freeze this
protocol before fitting. Labels distinguish unchanged originals from imposed
synthetic distortions; they do not establish real-world aesthetic quality or
whether a naturally lit photograph should be corrected. A source photo under
warm/cool lighting is still the clean reference for its own synthetic sequence.

Use the existing420attempts and saved nested MST models, original five-feature
depth3correction trees, targets and borrowed supports. No new correction tree,
MST fit, mask, distortion, dataset or qualified admission. Do not use the later
unlimited-depth, balanced or chroma-feature models. Fourteen original failures
have no scoring support; nine feature failures remain unchanged operationally.

For each held publisher key, train one logistic gate on all available input
feature rows of other keys, including synthetics whose correction target fit
was unavailable. Their synthetic/clean membership is still known. Training
labels use recipe membership only for supervision; inference sees only the
five Lab/ITA/continuous-MST values. Thus gate training can use397available rows,
while the existing correction trees remain fitted on their original357rows.
Do not silently conflate those roles.

For every gate-training key, reconstruct its MST feature using the saved ridge
that excludes both that key and the outer held key. Held features reuse the
saved outer-only estimator. No subject score, reference colour, condition,
recipe, clean identifier or target fit status enters inference. Gate feature
mean/std are fitted on training rows only.

Fixed logistic regression: C1, L2 default objective, solverlbfgs,
max_iter1000,tolerance1e-4,seed42. Each fitting key has equal total weight;
within key, clean and synthetically distorted classes receive equal weight.
Normalize weights to sum to the fitting-row count, fixing the effective C
convention. Use those weights in feature standardization and logistic fitting.
Constant features use scale1. No threshold or hyperparameter sweep.

Decision: strictly positive linear logit→apply the original saved depth3
correction controls; zero/negative→exact unchanged input. The fixed probability
boundary is0.5; no held outcomes select it. A gate-off output is not a new
correction prediction or evidence that distortion was repaired. Missing features
remain unavailable decisions/unchanged outputs, not detector true negatives.

Report clean false-positive corrections and synthetic false-negative no-ops,
per-condition and core/stress confusion counts, available/attempt denominators,
and majority baselines always-correct/always-unchanged. Compare ungated/gated
operational RGBMAE, relative CIEDE2000, equal-key means, clean harms and distorted
regressions with the same support/failure policies. Do not report ordinary
accuracy alone under class imbalance. Even an exact clean no-op policy can
fail if it leaves most distortions unchanged.

Fit ten gates once; retain raw logits and all models/memberships/weights.
Check convergence, nested exclusions, training-only scaling, exported linear
prediction replay and all406rendered outcomes without refitting. Inspect all29
held clean comparisons. Stop after this diagnostic, even if it fails; no tuned
gate threshold, automatic follow-up classifier or runtime adoption.
