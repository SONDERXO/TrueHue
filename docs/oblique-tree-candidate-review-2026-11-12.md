# Candidate found: one multi-output oblique regression tree

12 November 2026. **Recommended for a bounded engineering feasibility specification, not yet for a real-data fit.** The user asked to find a justified candidate under the accepted practical completion contract. No old model is rescored under the new policy. Paper work remains paused and the working model remains unfinished.

## Proposed model, in plain terms

Keep one decision tree, the existing input-derived ITA/MST and traditional features, and one constant [gamma, red, blue] vector per leaf. Change each branch from a test of one measurement to a test of a learned weighted combination of measurements. For example, a branch could depend jointly on facial lightness and scene colour rather than cutting only one of them. No actual coefficients or thresholds are selected in this review.

At inference each node evaluates w dot x + b and follows ONE child, reaching ONE leaf. No neural features, forest, soft averaging, separate correction predictor, linear leaf model, reference image, recipe ID or repeated rendering/selection is included. Face/visible-neck support, protected pixels and optional manual refinement stay. This is still a traditional decision tree, but a substantive branch/training change from the proposal's ordinary sklearn CART implementation; do not present it as the same existing trainer.

## Why this is a distinct hypothesis

The saved 44-case review found 44distinct input vectors and no exact conflicting full-vector targets, while 10of11original/cool pairs were routed to the same learned leaf and three source groups collapsed all four roles. Those are observed failures, not proof that an oblique boundary repairs them. The old bounded search changed optimization inside the SAME axis-aligned tree class. It reduced fitting error greatly without establishing held-source transfer. More time, depth or a new summary was therefore unsupported.

This candidate instead changes the shape of allowable partitions. Combinations of correlated measurements can be separated by one hyperplane even when a small axis-aligned tree needs a staircase of cuts. That is a geometric reason to investigate one different tree class at shallow depth. It adds no measured image information and may still fail if the relevant inference information is absent or source correlations do not transfer. Distinct vectors do not prove the needed boundary exists.

A scoped docs/src search found no implemented oblique/hyperplane/TAO correction trainer; the only hits for "oblique" described face poses. This is a local search finding, not research novelty. The closed target-scaling, weighted/regional loss, hard nonharm, binary control classifier, bounded axis search, spatialNSS and gray-pixel trials remain closed. This is not a new name for one of them.

## Primary-source basis and limits

Zharmagambetov and Carreira-Perpinan2020, section3, formulate hard regression trees with vector-valued outputs, oblique branch tests and either constant or linear leaves. Their Tree Alternating Optimization (TAO) updates branches using downstream regression losses and updates constant leaves to fitting means. They explicitly distinguish the single-tree algorithm from the bagged forests used later. We propose only a SINGLE constant-leaf tree and no forest. Their published forest improvements do not establish TrueHue or single-tree correction accuracy. [Paper and metadata](https://proceedings.mlr.press/v119/zharmagambetov20a.html), [section3 PDF](https://proceedings.mlr.press/v119/zharmagambetov20a/zharmagambetov20a.pdf).

The author's TAO page explicitly supports single-tree use and lists a2026Python release. The archive was not downloaded or executed; actual code compatibility, vector-output support and licence inside that archive are not verified. No third-party package is installed or selected. An independent published-equation implementation is a possible engineering route; it must be identified as ours, not author-code parity. [Author's project page](https://faculty.ucmerced.edu/mcarreira-perpinan/research/TAO.html).

The inspected generic obliquetree.Regressor documentation specifies scalar y shaped(n_samples,). It is not a verified drop-in three-output implementation. Training three separate trees would violate the retained one-predictor requirement; do not use that shortcut. [Package's own regressor documentation](https://obliquetree.readthedocs.io/en/latest/api/regressor.html).

## What training would mean, without hiding another predictor

Propose keeping the SAME16inputs, raw3control squared-error targets, depth-at-most4 and constant leaves for the first engineering design. No loss scaling, new recipes, data expansion, masking/calibration change or extra descriptor is bundled. The new model class necessarily requires a compatible trainer; a future comparison would test that branch-class/trainer package, not isolate the causal effect of branch orientation alone.

TAO's branch update is a fitting-only binary routing subproblem: for each fitting example, compare its losses through the current left and right subtrees and learn a hyperplane favoring the lower-loss child. Those routing pseudo-labels are not exposure/identity/recipe classes. The training-side weighted logistic solver is a way of learning a tree branch; inference exports only branch coefficients and leaf controls, with no independent logistic/quality/correction output. This distinguishes it from the old failed control-partition classifier.

The paper notes surrogate updates can increase actual tree loss. Any implementation proposed for this project must check the actual declared fitting objective and reject worsening updates rather than claim a surrogate guarantees improvement. Fitting mean/std scaling, solver, regularization, initialization, numeric routing/ties, budget, stopping and empty leaves still need one frozen specification before fitting. Use fitting roles only; no new penalty/depth/seed grid or held-error-based selection. Lower fitting SSE will remain a diagnostic, never the acceptance decision.

The 2018TAOpaper is primarily classification; it is not sufficient on its own to claim our three-output implementation. The2020vector-output regression formulation is the relevant basis. We do not copy forest tuning, linear leaves, random ensembles or multiple-start selection from related work.

## Resource and compatibility assessment

For16features at depth4, a prediction follows at most4branches: at most64coefficient products plus additions/comparisons, followed by3constant leaf values. A complete tree has at most15branches and16leaves:255branch coefficients/intercepts plus48leaf values,303numeric scalars (2424bytes atfloat64, before metadata). This is a static upper-bound count, not an actual trained model, export size or phone latency. It omits the unchanged image-processing costs.

This is lightweight inference in arithmetic terms, but **more free parameters** than an axis-aligned tree of the same depth (at most78corresponding feature-index/threshold/leaf scalars). Oblique coefficients increase flexibility and overfit risk; equal depth is not equal capacity. Forty fitting rows from10sources cannot be assumed adequate. No guaranteed generalization or training-speed advantage follows.

Current portable_tree.py accepts a single feature index and threshold at a branch, not a coefficient vector. A new separately versioned evaluator/export contract and parity checks would be needed; do not alter the current runtime or silently load these nodes through the old schema. Fold any fitting-only normalization into exported coefficients/intercepts so no separate learned preprocessing head is required at runtime. Preserve old model exports/evaluators byte-for-byte.

## Rejected alternative directions in this search

- Another generic gamma/histogram/gray-pixel summary would need new transfer evidence and risks repeating closed descriptor work; not selected.
- Pairwise/ranking objectives can use within-source relationships, but a new loss alone does not resolve the already observed zero-fitting-error/held-failure case. Enhancement-ranking systems using ensembles or neural representations do not satisfy this candidate's output/inference constraints. No ranking system or pairwise loss is selected.
- Contemporary hinge/model trees can use linear predictors at leaves or additional tuning; they are not automatically the retained constant three-control predictor. No package is imported merely because its name says "tree".

## Recommended next deliverable

Prepare ONE engineering feasibility specification for a multi-output, constant-leaf oblique tree based on regressionTAO: explicit objective, branch solver/regularization, fitting-only scaling, single initialization, maximumdepth4, fixed computation caps, safe update acceptance, empty-node/tie rules and a new portable schema. Bind the accepted visual/numerical evaluation protocol. This is the next bounded deliverable, not authorization to refit old comparisons or promote rejected models under new criteria.

Then verify on GENERATED numerical fixtures first: exact dot-product routing/export parity;3output leaf means; an analytically diagonal boundary distinguishable by an oblique branch; zero/equal downstream losses; rejected worsening updates; scaling fold-in; invalid/empty nodes; deterministic stopping and budget exhaustion. Fixtures are not scientific data. Do not use generated success as evidence of skin-tone correction.

No real-data search/fit, photo extraction, model comparison or review queue is selected here. After engineering feasibility, a separately specified grouped diagnostic could test whether this candidate actually improves input-relative correction under the new contract. The existing11source diagnostic has incompleteblue/strength/combined/MSTcoverage; a result there alone would not finish the model. Independent final evidence and a compatible final pipeline still matter, and final24/olderlocks remain byte-unread. No claim that this is the best algorithm or a promised fix.

## Evidence and effects

Source/diagnosis/contract hashes and the static count are recorded under outputs/oblique_tree_candidate_review_v1. No dataset or cached photo/reference/mask bytes, model weights, dependency downloads, fits, predictions, old-candidate rescoring, contacts, uploads, commit/push, runtime or Android changes occurred. Preserve manual refinement, tree/ITA/MST, lightweight traditional single-photo correction and the user's model-first priority. PPR remains paused and the neural-feature route declined.
