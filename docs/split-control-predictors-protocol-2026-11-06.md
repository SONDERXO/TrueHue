# One split exposure/colour predictor comparison — 6 November 2026

User authorizes the architecture comparison. Fit a scalar gamma tree and one
joint red/blue-gain tree instead of the shared three-output tree. Both heads
receive the same12facial+scene input features and use depth3/seed42/minleaf1,
unweighted per-target fitting-only normalization. This changes the split
objectives and increases total tree capacity (up to eight leaves per head);
the result must not be attributed to output decoupling alone.

Keep all existing whole-photo420attempts,10publisher-key folds,357trainable
rows, saved nested MST features, targets and fixed borrowed supports. Twenty
new head-tree fits (two per fold), no new gate/MST/target/mask/distortion fits.
Gamma and gain heads train on the same rows, not separate recipe subsets;
recipe/condition/source labels do not enter inference. Three positive output
controls retain the existing renderer semantics and order.

Keep the previous benefit gate's exact held decisions. Those gates were trained
to estimate benefit of the old shared corrector, not these new heads. This
comparison explicitly tests frozen-gate transfer; no claim of matched benefit
calibration for the changed corrector. Gate-off remains exact unchanged input.
No new gate labels, threshold adjustment or post-hoc activation policy.

Evaluate four matched paths: old joint ungated, old joint benefit-gated, split
ungated and split with the same gate. Report clean/core/stress MAE/CIEDE2000,
equal-key means, harm counts and no-op availability. Separately report both
pure colour-cast recipes: gamma target/prediction ranges, same-control-as-clean
counts and errors/harm. Include exposure-only results so improvement on casts
cannot hide lost exposure correction. Preserve all14unsupported originals and
nine undefined-ITA fallback outputs.

Verify same training membership, feature vectors and gates, fitting-only head
normalization, raw leaf means, portable control replay and all812new rendered
operational outputs without refitting. Inspect all30clean contexts (29scored,
one failure), plus cool cast, warm cast, exposure-under and stress-combined-under
for the first case ID of each publisher key:70fixed boards. This deterministic
subset is not a full420-output visual review or new human annotation task.

Freeze protocol/code hashes before fits. Stop after this single architecture
comparison, retain unfavorable outcomes and private dataset terms. No head/depth/
weight/feature/gate sweep, scientific admission, final refit or app adoption.
