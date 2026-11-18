# Linear-leaf engineering passes; source-colour confusion remains

13November2026. User authorized implementing and executing the [fixed generated-only design](linear-leaf-generated-feasibility-protocol-2026-11-13.md). **28tests PASS in1.19s. Engineering PASS; affine mechanism PASS; real photographic fit NOT QUALIFIED.** Evidence: outputs/linear_leaf_generated_v1, including original design/code bindings, fixtures, eight generated fitted-tree artifacts, independent checks, source-confound results and a deliberately failed empty-leaf attempt preserved without retry.

Implemented src/model_training/portable_linear_leaf_tree.py, linear_leaf_generated.py, linear_leaf_scalar_check.py and linear_leaf_fixtures.py; scripts/check_linear_leaf_generated.py; tests/test_linear_leaf_generated.py. The existing constant-leaf runtime is unchanged. No additional package was installed. Generated fixtures have an explicit generated-only provenance flag; the fitter refuses scientific records without that flag. No real photo metadata or feature vectors were loaded.

The fixed two-coordinate affine leaf uses nine coefficients, raw three-control targets and ridge0.01 on standardized slopes, with intercept unpenalized and a single direct2x2solve per leaf. Coefficients are folded to raw-input form. Independent scalar sufficient statistics/inversion and inference checked234values with maximum difference1.96e-15, within1e-12. Input rounding, JSON roundtrip, immutable artifact copies, branch ties, malformed graphs/schema/values, constant/neutral/exposure behavior, correlated and zero-variance inputs, identical-conflicting targets, empty-leaf refusal and no-overwrite/failure preservation were verified. Standard-library runtime/scalar imports do not load NumPy or sklearn.

## Mechanism result

On the nine-record affine toy, the constant-mean analytical comparator has rawSSE0.0192 and the linear leaf has0.00000188217. Own-axis slopes have the expected sign and cross-axis slopes are numerically zero. All four interpolation predictions agree with independent inference. This establishes that a reached leaf can produce different red/blue responses instead of a common averaged vector. The toy targets are artificial affine relationships, not exact inverses of the photographic edit operators or observed evidence of transferable cues.

Neutral and fixed-exposure fixtures preserve their target controls within the specified arithmetic tolerance. Identical-input/conflicting-target examples retain irreducible residual rather than falsely separating labels. The x5=10extrapolation produces a nonpositive control and is explicitly rejected before rendering. The x5=-10probe returns approximately[1,2.9802,1], which is numerically valid but not evidence of a safe or desirable correction. No clipping, identity fallback or new confidence gate was added.

## Source-confound result

The fixed nuisance study has36records: four fitting cases from offset(0,0), then32cases at eight different source offsets. Seven float32coordinate groups contain conflicting targets across the36examples. The learned leaf confuses source offsets with edits: all eight unchanged-source probes receive non-neutral controls, reaching roughly2%gain changes for the fixed0.1offset examples.

Unseen-offset rawSSE is0.01882514 versus0.0352for the analytical fitting-target mean. Therefore the affine model carries some edit signal across these artificial offsets, but improved aggregate error does not remove its source-colour sensitivity. These are mathematical source-offset examples, not eight people, skin-tone labels or eight unwanted visual changes. The controls may or may not be visually acceptable; no human ratings were collected.

The coordinate collisions concern the two leaf measurements, not a proof of impossibility for all281features or all model trees. The toy's other colour-branch inputs provide no additional source information; a differently justified branch/cue policy could change that. However this result does not justify a post-result feature/penalty/topology sweep or claiming a real fit is ready.

## Disposition

Keep this as engineering-correct, mechanism-demonstrated and photographically UNQUALIFIED. The fixed compact leaf inputs do not establish separation of source colour from edit colour, the earlier baseline remains frozen, and no real fitting roster or user review is selected. Do not infer the linear-leaf family impossible, mark the blue-axis candidate accepted, or claim that matching nominal controls will resolve the earlier visual preferences.

A further model proposal must justify inference-available source context or a distinct leaf/branch input mechanism before another fitting experiment; simply making these slopes larger or choosing another penalty is not supported. No automatic next experiment is launched from this result.

Final hashes/probe accounting were checked unchanged. All fitting and inference here were artificial-only. No photographic arrays/masks/NPZs, raworiginals/lockedholdouts, real fits/predictions, runtimeAndroid or manuscript changes occurred. Historical artifacts, approved59807manual/ears, all ratings and darker-skin priority retained. Independent tone-qualified bias evidence remains unestablished. Modelunfinished/paperpaused/November14complete-deliverytargetatrisk/exacttimeunspecified.
