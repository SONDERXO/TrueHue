# Paper-aligned nominal-control baseline ? frozen 11 November 2026

The proposal describes a DecisionTreeRegressor predicting gamma/red/blue gains.
The current rendered-cost action tree differs from that method. Test one direct,
unweighted three-output squared-error regressor on the current controlled data,
not another catalogue loss change. Earlier direct-gamma and balanced-parameter
regressions failed on different historical data; those experiments stay closed.

Reuse exactly 35 prepared rows and the seven saved publisher-held folds: each
fits 24 rows (six identities plus 18 controlled derivatives), predicts five, and
never fits original photographic sources. All five 904 unavailable roles remain
in the 40-role ledger. No new data, features, masks or calibration.

For a known forward transform v=u**g*[r,1,b], the nominal inverse parameters are
[1/g, r**(-1/g), b**(-1/g)]. These are engineering targets before RGB8 rounding,
clipping and alpha blending, not optimized pixel targets or physical colour truth.
Identities have [1,1,1]. Actual recorded forward recipes supply targets; no held
photographic reference is used to fit or infer them. Original source parameters
are unknown and excluded from parameter-MAE evaluation. Blue gain is always one
in these three recipes: this baseline cannot demonstrate learned blue correction.

Keep the 16 float32 inputs and fixed external mapper (constant MST disclosed),
depth4, random_state42, min_samples_leaf1, sklearn squared_error/best splitter,
no weights or target scaling. Positive leaf means are direct controls, without
action quantization, identity feasibility constraints, post-guards or fallback.
This is a declared learner/target change, not a matched objective-only ablation.
Maximum seven fits and35 predictions; no all-data fit, grid or further variant.

Keep native direct-gamma rendering, all alpha-positive RGB/DeltaE scoring, protected
and zero-alpha equality, and the same existing development checks: every recipe
improves mean RGB and DeltaE over input; original-source means <=32.002887577242504
and12.031091229086034; all seven held identities unchanged; coverage/protection.
Report raw parameter MAE by known-target role separately; it is not a promotion
criterion or comparable to reciprocal-gamma MAE. Compare saved candidates without
refitting them. Verify leaf means/routing, portable parity, native renders/metrics,
fold exclusion and target provenance. Inspect outputs before conclusions.

This baseline informs paper-method fidelity and correction feasibility. It does
not complete the paper's dataset/validation requirements or demonstrate intrinsic
tone recovery, fairness or MST conditioning. Preserve old artifacts and all locks;
no original photos, image models, acquisition, contact, upload, runtime or Android.
