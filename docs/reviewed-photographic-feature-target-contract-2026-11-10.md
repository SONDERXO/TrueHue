# Reviewed photographic feature and target contract — 10 November 2026

## Frozen preparation scope

Define and prepare input features and correction-control supervision for the
reviewed photographic data. Retain the final decision tree, ITA/MST, the existing
16feature definitions and the previous full green-parent catalogue of14actions,
in exact order. The parent is a failed development comparator, not adopted as
a model. Only its fixed feature/action definitions are inherited; no coefficients,
old predictions, calibration or old mask-dependent costs are reused.

No new calibration fit or tree fit is included. New target-aware categorical
action selection from the frozen catalogue is explicitly permitted by this
control-target preparation: evaluate14actions per14available roles, without
continuous optimization, new recipe/depth/weight/threshold/guard searches. These
are supervision/oracle labels, never automatic model predictions or accuracy.

## Measurement and pipeline identities

Introduce a shared **computational measurement core**: exact cached native
anchor1.5square context,256×256linear-resized uint8BGR, an explicit user-reviewed
binary facial measurement mask, at least1000selected normalized pixels, the
existing OpenCV Lab encoding conversion/float32 means/four-decimal rounding,
and the retained ITA atan formula with rounded means and b*epsilon. Bind code
hashes and numerical library versions. Source identity, mask bytes, automatic
seed provenance, label and review history belong in per-instance records.

Replay all30labelled native-manual inputs and all14photographic role inputs
through that same core, requiring exact saved four-statistic parity. Add the
core identity alongside the original method/instance identities; do not rewrite
them. This proves computational agreement on these supplied inputs, not outer
pipeline equivalence, image-quality validity or empirical cross-dataset MST
transfer. Keep JPEG assumed-sRGB versus historically ICC-checked PPR TIFF-toRGB8
producer provenance explicit; no originals are reopened or recoloured.

## Input features

Preserve the exact order of the16parent features. Four input Lab/ITA statistics
come from each role's own normalized image and reviewed measurement mask. Four
green summaries use that same own input/mask and the existing linear percentiles
and log contrast. Seven scene summaries use that role's own full-frame RGB8
input, not the target frame. No paired delta, reference label, target mask or
editor image enters a source feature.

Prepare these15available values per role. Keep `input_mst_score=null`, with a
required-mapping reason; reject model use while missing rather than fill with
zeros, a source label, an old prediction or an average of old folds. Thus there
are zero complete16-input vectors at the end of this preparation.

## Compatible MST execution plan, not executed here

The external labelled cohort remains30images/ten publisher subjects/three
conditions, with exact decimal scores. Its prior tenfold isotonic assessment is
closed and remains limited developmental evidence (not a passing calibration
declaration). No old mapping is rebound to the new core or photographic method.

A later separately authorized execution would fit **one fresh** subject-balanced
nonincreasing isotonic map on the30frozen labelled rows, bind its new core and
producer/application contract and preserve all prior validation limitations.
It would generate14input-only photographic MST scores with fitting-support and
endpoint-clipping flags. PPR labels remain missing, so no PPR mapping accuracy
could be asserted. That external mapping would be fixed across PPR publisher-held
folds; no PPR target, choice, control loss or held-pair image would fit it. New
core identity alone does not qualify its empirical transfer. No ensemble,
condition-specific map, sign/formula change or extra candidate is selected.

## Rendering and target costs

Use the prepared original-grid RGB8 arrays, each role's reviewed native alpha
and retained protection. For positive controls gamma/red/blue:

`candidate = clip((input /255)**gamma *[red,1,blue],0,1)`

`output = round_to_even(255*((input /255)*(1-alpha)+candidate*alpha))`

Use the existing native blended-cost helper and verify direct integer output
parity. Gamma is the **direct exponent**, not the historical reciprocal. Score
RGB-code absolute error over every native pixel with positive application alpha,
allthree channels. No target-mask intersection filter or region subsampling.
Protected and zero-alpha pixels must remain equal to the input for every action.
Do not claim global editorial reproduction outside local correction support.

For each source, reference the user-accepted editor-A image at the declared same
publisher pixel coordinates, without a warp. Correspondence remains a dataset
assumption, not independently proven registration. For each target role, its own
editor frame is its defined photographic identity reference. Identity action0
must have exact zero target-role cost. This defines an identity control for that
photographic objective, not physical neutrality or an arbitrary source-clean flag.
Near-unchanged330source remains a source; let its costs describe the desired edit.

Evaluate the14fixed catalogue actions, record all14costs, then select the first
minimum in catalogue order, with identity first. Export direct gamma/red/blue
values, action index, cost and identity-relative oracle gain. Target selections
and evaluation scores are target-aware diagnostics/supervision; they may never
be reported as predicted restoration accuracy. Do not add their controls to a
new action catalogue or tune the catalogue after inspecting outcomes.

## Groups, missing roles and later tree boundary

Keep all16attempted roles/eight publisher groups. Fourteen reviewed roles are
available;904source/target remain failed and unscored, not successful identity
predictions. Retain1188and its disclosed native-detail uncertainty; no new pixel
cutoff or favorable-case removal. Source and target from a pair stay in one group.

Prepare eight leave-one-publisher-group-out role allocations, retaining the
failed904evaluation fold. With904held,14roles from seven groups are available
for fitting, with two unavailable evaluation roles. For another group held,
12available fitting roles and two available evaluation roles remain; the904
failures remain in that fold's full attempt ledger. Original publisher groups
are known; independent real-world identities are not newly certified. These are
exposed development comparisons, not a blind final test or deployment gate.

This step does not fit a tree, predict correction, freeze a tree-comparison
protocol or claim admission. A later fixed comparison would need the fresh
mapping artifact, exact input provenance, current target-cost rows, the retained
depth4tree/action-loss/clean-preservation constraints and full failure accounting.
Held targets/controls/costs may score evaluation, never choose a training split or
training action. No full-PPR release fit follows automatically. Existing joint
quality gates remain unchanged; success on these pairs would not substitute for
those gates, broader support/evaluation evidence or a specific final-holdout
access decision. All original/holdout images and prior artifacts stay preserved.
