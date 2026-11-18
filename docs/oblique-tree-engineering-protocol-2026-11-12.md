# Frozen oblique-tree engineering specification

12 November 2026. Authorized scope: ONE specification, implementation and GENERATED numerical verification. No real-source metadata fitting, pixel reads, held prediction, old-candidate rescoring or runtime adoption. New module/schema stays separate from portable_tree.py and the app.

## Predictor and numerical contract

One hard binary tree, at mostdepth4/31nodes, using at most16named input features and exactly3positive constant controls at each leaf: gamma/red/blue. Each internal node stores float64weights and intercept and follows RIGHT iff score>0; equality goes LEFT. Inputs are rounded tofloat32 once. Canonical score is math.fsum([intercept]+[weight[j]*float32input[j] in indexorder]). Training acceptance and serialized inference use this exact raw-coordinate evaluator. Invalid dimensions/nonfinite/overflow values, cycles, sharedchildren, unreachable nodes, invalid positive controls and excessive depth are rejected. No probabilities, softrouting, linear leaves, multiple trees or inference reference/recipe labels.

A new truehue_oblique_regression_tree_v1schema declares those semantics. Do not change/load through the old axis schema. Legacy axis tree conversion is exact: coefficient1atfeaturej, intercept=-threshold, old<=left preserved including ties. No initialtree is fitted by this trainer. Current generated fixtures supply their one initialtree; a possible later real study would name ONE saved ordinary axis initialtree prospectively, not choose among parents or restarts.

## Objective, scaling and branch solver

Keep raw unweighted3control fittingSSE. Constant-leaf updates use means of fitting targets reaching each leaf; empty leaves retain prior values. No targets standardized, roleweights, calibration, feature selection or identity override.

Fit one populationmean/std vector from provided fittingfloat32rows, zero std->1. Branch solver uses these standardized inputs; fold its learned weights/intercept algebraically into rawcoordinates at export. Never fit scaling on held rows. Algebraic folding may differ at exact floating boundaries from a separately evaluated standardizeddotproduct; rawcanonicalrouting is authoritative, and acceptance is checked AFTERfolding. Record this, do not claim arbitrary floating-point coordinate equivalence.

For each current branch, collect its fitting reducedset. Compute each row's left/right descendant3controlSSE with current subtrees. Pseudolabel is rightiff rightloss<leftloss. Weight is abs(leftloss-rightloss); exactties have zero weight and do not influence branch optimization. A zero-weight or single-label reducedproblem is skipped, not replaced by an arbitrary split. Normalize weights to sum1 for conditioning.

Use SciPyL-BFGS-B with an explicit stable logistic objective/analytic gradient and L2coefficient .01 on normalized-space slopes only (interceptunpenalized). Options maxiter100,maxfun1000,maxls20,ftol1e-10,gtol1e-8,maxcor10. Warmstart only from the current branch. This is an OWN regressionTAO-inspired adaptation: the paper uses L1, whereas this fixed L2surrogate supports a simple deterministic smooth implementation. L2is training-side branch conditioning, not an added penalty or axis weighting in the declared rawSSEacceptance objective. No claim of reproducing authorcode, paper hyperparameters, sparseweights or optimality.

A surrogate improvement is insufficient. Reject nonfinite/failed-optimizer proposals and proposals sending every reduced row to one child. For all others, calculate canonical FULL fittingSSE after folding. Accept only if improvement>1e-12*max(1,initialSSE); this is numerical tolerance, not photographic quality. Leaf updates must not increase rawSSE. Keep the current feasible tree on rejected proposals. Log solverstatus and rejection reason; do not silently retry with another solver/penalty.

## Order, resource caps and stopping

Breadth-first branch order, then update populated leafmeans. One pass=allcurrentbranches plus leafupdate. Max20passes,300branchsolverattempts,60seconds,1process, no restarts/budget increases. Check time before passes/branches and at each optimizer function/gradient evaluation; no asyncworker. A timeout inside solver discards that unfinished proposal and returns last accepted tree. This is a cooperative time cap, not a hard realtime guarantee; initialization/evaluation/solver nativecall overhead may overshoot, and actualelapsed is recorded. Do not call a capped result converged or globallyoptimal.

Stop if a fullpass produces no numerically strict rawSSEimprovement, or a cap is reached. Preserve status, completedpasses,proposals/accepted/rejected and initial/finalSSE. No pruning/growing or topological rescue in this implementation. A degenerate one-leaf initialtree stays oneleaf. Wholefittingloss decrease is diagnostic only; no current image or useracceptance condition is inferred.

## Generated verification and stop

Tests cover hand-computable diagonal geometry vsanaxisstump, three-output means, independent scalar dot/routing, standardizationfolding awayfromties and rawtie semantics, axisconversion, zero/single-label/tiedlosses, failed/nonfinite/empty/worseningproposals, deterministic budgets/time, constantfeatures/targets, graph/schema/numeric validation and JSONroundtrip. Finite-difference checks verify surrogategradient. Compare canonical scores/routing/SSE independently; no generatedexample is labelled photographic or trainingdata.

Expected engineeringevidence: traceable monotone rawSSEupdates and portableparity, including a generateddiagonal case showing a branch can use multiple coordinates. Generatedfailure means fix a correctnessbug transparently or stop, not tune hyperparameters to imitate realresults. Allfirstfailures preserved before correction. No realdatafit follows automatically even if alltests pass. Next selection would need a fixed training-only feasibility design with exact fittingroles and no held access; current44rolecoverage/MSTlimits remain. Accepted visual/numerical protocol still governs any later correctionstudy.

## Sources and effects

RegressionTAO basis: https://proceedings.mlr.press/v119/zharmagambetov20a.html (section3vectoroutputs/constantleaves and source updateacceptance option). Solver options: https://docs.scipy.org/doc/scipy/reference/optimize.minimize-lbfgsb.html. Existing SciPy1.18.1/NumPy/sklearn available; no authorarchive/package/weights installation. The new implementation is not proof of better correction or samecapacity as axis trees. Model-first/paperpaused; alloldfailures, existingevaluator, masks, mappings, outputs and final24/olderlocks preserved. Zero datasetphotos/realdatafits/runtime/Android/contact/upload/commitpush.
