# TrueHue correction-training contract

11 November 2026 | Specification only; no new model or dataset generated

**Objective:** finish a useful single-photo correction model, retaining one
three-output decision tree, ITA/MST, face/visible-neck correction and optional
manual refinement. Study decisions belong to the researchers; adviser approval
is not a prerequisite. This contract does not claim that the model is finished
or that the proposed training change will work.

## A. Keep the task and target types explicit

The paper asks for photographic restoration against the original reference,
not intrinsic skin-colour measurement. Keep gamma/red/blue outputs and the
uncorrected-input baseline. No new colourimeter, chart, perfectly invariant MST
or physical-camera model is required for development.

| Data lane | Forward operator | Supervised control target | Limitation |
| --- | --- | --- | --- |
| Identity | Original reference unchanged | Exactly[1,1,1] | Preserving the accepted photograph, not certifying physical colour |
| Known gamma/gain diagnostic | u**g*[r,1,b], clipping/encoding explicitly recorded | [1/g,r**(-1/g),b**(-1/g)] as nominal inverse | Correct before quantization/blending; final residual must be reported |
| Paper composite | Explicit gamma, brightness/contrast and red/blue operations | Best approximate three-control recovery under the actual renderer | Never label an additive/clipped composite with an exact gamma/gain inverse |

The composite implementation must record order, encoded-RGB units, contrast
pivot, slider conversion and severity assignment; Table2numbers alone do not
define them. Retain the previous declared interpretations and audits as evidence,
not unquestioned physical simulations. Do not execute or revise that lane under
this specification. Approximate targets must record local-fit method/bounds,
convergence, clipping and actual RGB8/DeltaE residual. They are neither global
optima nor learned predictions; references are supervision-only.

## B. Coverage completion is separate from model repair

The current11-source/44-case FFHQ diagnostic has identity, underexposure,
overexposure and one red-attenuation cast at one fixed strength. Blue targets
are constant1; no combined distortions exist. It cannot establish complete
three-output colour learning, strength generalization, fullTable2coverage or
performance across supported MST groups. Keep its48-role ledger, including the
four excluded29863roles, and all prior user appearance/support decisions.

A later full-task dataset must account for identity, exposure-only, red/blue
colour adjustment and combined conditions, with explicit strength/severity
provenance and observed target variation. Do not invent MST labels or add new
category boundaries. Available source grouping/labels and missing tone coverage
must be reported honestly. Real group counts, not variant counts, determine the
claimed sample size. Existing mask/support uncertainties remain disclosed.

This is a coverage checklist, not authority for a new recipe grid, acquisition,
annotation batch or repeat of the closed82-source/890-condition programme.
That programme already included warm and combined examples and failed. Filling
missing recipe names alone does not explain how unseen control choices improve.

## C. One distinct learning hypothesis: search versus greedy fitting

The target audit found correct inverse equations and low known-control residuals;
rewriting targets is unjustified. The saved16-input tree gives nonidentity
controls to95of110fitting-identity appearances, despite balanced fitting roles.
This motivates testing whether greedy partition search itself leaves avoidable
fitting error at the same model size. It does not prove that the features suffice
or that a better training solution generalizes.

Propose a bounded non-greedy search over the SAME axis-aligned, depth-at-most4,
three-output regression-tree class and the SAME unweighted raw squared-error
objective. Keep the saved16features/targets, not the failed18-feature extension.
Use each saved greedy tree as an initial feasible incumbent; do not refit it.
A candidate may explore a split with no immediate gain if its descendants reduce
error. No new classifier, gate, extra head, weights, output scaling, action
catalogue, leaf override, depth or input descriptor is added.

For a fitting subset S and remaining depth d, define leaf cost
L(S)=sum_i sum_j(y[i,j]-mean_S(y[:,j]))**2, with three raw control axes.
The exact recurrence is:
T(S,0)=L(S)
T(S,d)=min(L(S), min_split[T(S_left,d-1)+T(S_right,d-1)]).
Leaf outputs remain the raw control means. This recurrence evaluates descendants,
whereas the current greedy method selects immediate split improvements.

Dynamic-programming regression-tree search has published precedent:
[Van Den Bos et al.,2024](https://proceedings.mlr.press/v235/van-den-bos24a.html).
Our three-output additive-cost adaptation is a proposed implementation, not a
claim that their software directly supports this contract or validates TrueHue.
Optimal tree training can be computationally expensive. No package/model download,
installation, linear leaf model or change of final predictor family is selected.
This is a declared training-algorithm departure from the proposal's sklearn
trainer; the ordinary sklearn tree remains the matched paper-method baseline.

Prior local depth/weight changes, binary control-partition classification,
normalized regression, split predictors, rendered-action losses and nonharm
constraints remain closed. A repository search found no implemented global
regression-tree search in the reviewed modules/reports; that is a scoped code
finding, not a literature novelty claim. Optimizing the same raw objective may
still prioritize gamma and may overfit. We deliberately do not bundle a loss
change into this test. A better fitting tree is not a working correction model.

## D. Fixed implementation and computational feasibility stage

Next deliverable: implement and verify the search on generated fixtures before
any real-data fit. Compare tiny cases with independent exhaustive enumeration,
including an interaction needing a zero-immediate-gain split, pure leaves,
constant targets, exact ties, float32 routing and budget exhaustion. Generated
fixtures must stay outside scientific data and annotations.

Candidate thresholds use fitting-only sorted float32 values, midpoint between
adjacent values separated by more than1e-7, matching the existing verification
convention. Do not choose bins or cuts using held data. Preserve the incumbent
unless training SSE improves by more than1e-12*max(1,rootSSE); this is a numerical
comparison tolerance, not a photographic-quality gate. Do not change targets
or scale axes. An exact-rational or independently checked stable cost calculation
must distinguish genuine improvements from rounding noise.

After generated verification, one training-only feasibility search is specified:
use the first existing fold, held groupffhq_source_16061, and ONLY its40fitting
rows, fixed16inputs, targets and saved greedy incumbent. No held features,
reference pixels or held errors enter search or termination. No image reads or
new target/measurement/MST fits are required. This first search counts toward,
not in addition to, any later11-foldcandidate budget; preserve it without refit.

Resource limits are60seconds and5,000expanded subset/depth states, whichever
comes first, one process. These are fixed computation caps, not tuned model
parameters. No automatic budget increase/restart. Record seed/input hashes,
expanded/completed states, elapsed time, feasible incumbent objective and sound
lower bound. Interrupted states must never be cached as exact optima. If search
finishes, report its certificate within the stated finite tree class. If capped,
say best-found/budget-limited; never label it globally optimal. Failure to improve
at this budget is inconclusive about global optimality, not evidence all trees fail.

No photographic search is executed by this document. Review feasibility evidence
before selecting a full correction comparison. If the search cannot deliver a
verifiable improvement within the resource cap, stop this candidate rather than
starting a budget, depth, loss or threshold sweep.

## E. Prospective validation if feasibility supports proceeding

Reuse all11known photo-group folds,40fit/4held each, same44cases and the saved
16-input baseline; no parent refits, all-data fit, ensemble or source mixing.
Maximum11candidate searches total, including the feasibility fold. Preserve each
fold's40trainingrows and absence of held-source variants. Photo grouping is not
verified person independence. Keep current masks, fixed external MST artifact,
rendering, all alpha-positive scoring pixels and user-protected removals.

Primary reporting: RGB/standard CIEDE2000 before/after, each recipe and identity
separately, all individual harms, direct-coordinate parameter MAE and coverage.
Training SSE and identity-control fit are separate diagnostic outcomes, not
substitutes for held-photo image quality.

Prospective comparison checks: complete44prediction/48attempt accounting;
protected/zero-alpha pixels unchanged; each distorted recipe's meanRGBandDeltaE
better than uncorrected input and no worse than the saved16-input comparator;
all11held identity outputs unchanged. Report all results if any check fails.
Exact identity preservation is an engineering check here, not a newly invented
universal paper criterion. No posthoc relaxation or outcome-based case removal.
A failure closes this candidate, with no automatic refinement variant.

## F. Conditions before calling the correction model finished

Even a passing44-case development result would not complete the full paper or
qualify runtime promotion. It must be followed by the declared full-task coverage
and compatible target evaluation, honest MST/group claims, and independent
validation under a frozen final method. Keep final24/older allocations byte-unread
until a separately justified final-evaluation stage. Photographer/MOS and Android
work retain their project roles; this contract does not fabricate those results.

All existing reviews are complete. No new masks, user annotation, adviser action,
contact, acquisition, upload, commit/push or runtime/Android changes are needed
for the next generated solver implementation. The working-model goal remains
active; the proposed experiment is a testable hypothesis, not a promised fix.

Evidence: [target audit](correction-training-target-audit-results-2026-11-11.md),
[learning diagnosis](ffhq-correction-learning-review-2026-11-11.md),
[baseline](reviewed-ffhq-restoration-results-2026-11-11.md),
[historical broad-coverage failure context](training-exposure-colour-audit-2026-11-09.md).
