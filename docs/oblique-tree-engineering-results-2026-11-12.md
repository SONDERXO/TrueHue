# Oblique correction tree: generated-only engineering results

12 November 2026. **Implementation verified on generated numerical fixtures; no real-data correction result or adopted model.** User authorized freezing and testing the new tree implementation. The model-first priority remains; paper work is paused.

## What changed

Added two separate experimental modules:

- src/model_training/portable_oblique_tree.py: versioned hard-routing oblique tree, exactly3positive constant leaf controls, float32inputs/float64coefficients, canonical scalar summation, strict numeric/topology validation and lossless conversion of compatible old axis branches.
- src/model_training/oblique_regression_tao.py: one bounded constant-leaf multi-output regressionTAO-inspired trainer accepting one supplied initial tree. No file access or initial-model fitting inside the trainer. It updates branches from downstream fitting losses, folds fitting-only standardization into exported raw coefficients, and accepts only strict decreases of canonical raw fittingSSE. Leafmeans may update only without increasing thatSSE.

Current portable_tree.py, the old bounded search, app code and scientific artifacts were not changed. Hash verification confirms preservation. The new schema cannot be silently loaded by the old evaluator; no runtime integration occurred. This is still a proposed single correction tree, not a forest, neural extractor, probability-weighted output or separate control classifier.

The frozen protocol uses maxdepth4,20passes,300branch-solverattempts and60seconds, one process/no restart. It uses one fixed L-BFGS-B branch solver with an analytic weighted-logistic gradient and L2=.01on slopes, zero weight for routing ties, and explicit empty/single-label/failed-solver handling. Its L2surrogate, normalized fitting-side weights and guarded rawSSEacceptance are OUR declared adaptation; they are not a reproduction of the paper's L1implementation. No penalty or axis-weight change enters the declared raw3control objective. No global optimum, sparse solution or improved photograph is claimed.

The time budget is cooperative, checked during solver evaluations and between stages, not a hard realtime deadline. The report records elapsed optimization-phase time; argument validation/float32input conversion precedes that timer. Solver/nativecall or evaluation overhead can overshoot a check. There is no phone timing claim.

## Tests and independent evidence

- **31new generated-only tests passed** (1.42seconds in the final new-test run).
- **59focused tests passed** (7.18seconds) when the28existing portable-tree tests were included. These existing tests use generated data, not photographs. No full-suite run is claimed.
- The tests check three-output leaf means, diagonal geometry, explicit equation/gradient finite differences, scaling fold-in, scalar routing/JSONroundtrip, rawfloat32tie handling and axisconversion, all-zero/single-label branch losses, unchanged empty leaves, invalid/cyclic/shared/unreachable/deep graphs, nonfinite/overflow inputs and losses, nonpositive/wrong-width controls, deterministic results, unchanged initial models, failed optimizer/no-retry and time/proposal/pass caps.
- Separate script843 verifies72canonical scalar routes and4three-output leafmeans after JSONserialization on generated2feature and16feature versions of the same diagonal fixture. Independent predictions match the known generated targets and recomputedSSE matches reports. Preserved source/module/document hashes pass.

| Generated engineering example | Rows | Initial fittingSSE | Final fittingSSE | Result |
|---|---:|---:|---:|---|
| Two-coordinate diagonal boundary |36|1.04845|0|Uses both coordinates in one branch; known three-control targets recovered|
| Same boundary with14constant extra columns |36|1.04845|0|Constant columns remain defined;16feature export/routing verified|
| Symmetric four-point plateau |4|0.1613|0.1613|No strict gain; algorithm stops without restart or optimality claim|

These are numerical fixtures, not skin photographs, source subjects, newly generated correction-data recipes, independent validation or training admission. The diagonal's zero error is an engineering check, not correction accuracy. The two diagonal runs are declared dimensionality checks of the SAME toy problem, not a feature-selection trial.

The plateau is important: the fixed solver/tree can stop without finding a better arrangement. Branch pseudo-labels depend on current descendants and may provide no informative update. Correct code does not imply this initialization/objective will work on actual fitting rows, much less on unseen photographs. No solver/depth/penalty/restart rescue was added. No failed generated test run occurred; additional defensive schema/overflow and16feature/plateau checks were added before final verification.

## Numeric/export conventions and limitations

All runtime branch decisions use math.fsum over the stored intercept and coefficient products on float32rounded inputs, with score>0right and equalityleft. Solver output is folded into rawcoordinates before any acceptance check, so serialized routing and training decisions use the same evaluator. A separately evaluated standardized-space dotproduct may differ at floating boundaries; algebraic folding is not a claim of universal bitwise equivalence. Such borderline differences cannot be hidden by using a different evaluator for reporting.

A depth4/16feature tree allows at most64coefficient products along one path and303stored numeric parameters before metadata. More coefficients mean more flexibility and overfit risk than an axis tree of equal depth. Generated success, lower fittingSSE and small export arithmetic do not establish generalization, conservative visual behaviour, useful MSTconditioning or Android delivery. RawcontrolSSEstill has the previously recorded unequal numeric scales; no new target scaling or weighting experiment is bundled.

## Decision and next bounded step

The implementation is ready to be CONSIDERED for one separately specified training-only feasibility check. It is not yet qualified for a real-data comparison or final evaluation. The next specification should identify exactly one already existing fold's fitting rows, one saved ordinary axis initialization, all immutable feature/target/source/contract hashes and the unchanged caps. A fitting-only check must not read held features/labels/pixels or choose among initializations. No new masks, calibrator, targets, sources, arbitrary confidence gate or all-data fit follows from engineering success.

A feasible fitting improvement would still need a prospective source-held correction comparison under the accepted practical visual/numerical protocol. A non-improving or capped/invalid training check is recorded honestly, with no automatic increase, new penalty or alternate initialization. The existing44casecohort has constantblue targets, limited strengths/combined conditions and no independentMSTlabels; even a passing diagnostic alone cannot complete the whole task. No previously failed candidate is rescored under new requirements or promoted.

No real-data training-only check is selected/executed by this result. Keep final24/olderlocks unread, alloldtrials closed, PPRpaused and the neuralfeature route declined. Retain ITA/MST/traditionalfeatures/onefinaltree/singlephoto/face-neck/manualrefinement. No model, runtime or paper-quality completion promise.

## Artifacts and preservation

Frozen design: docs/oblique-tree-engineering-protocol-2026-11-12.md. Tests: tests/test_oblique_regression_engineering.py. Independent generated receipt: outputs/oblique_tree_engineering_v1/generated_verification_PRIVATE.json; generated_models_ONLY_PRIVATE.json contains toytrees only, not admitted/deployed models. Original input hashes are in preserved_inputs_PRIVATE.json.

No dataset source, cache, image/mask/reference, final24 or older locked image bytes were read. No real-data fits/predictions, old-model rescoring, external code archives, weights, installs, acquisition/contact/upload/commit/push, runtime or Android changes. Libraries used were already installed. Existing user reviews remain complete.
