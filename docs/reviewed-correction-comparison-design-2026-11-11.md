# One reviewed-data correction comparison — 11 November 2026

**Prepared, not executed.** The question is whether the existing reviewed
photographic supervision lets the retained decision tree improve held-pair
correction while preserving the defined reference/identity examples. It is a
small exposed-development diagnostic, not the final paper experiment or a model
promotion. No new dataset, calibrator, mask review or model family is required.

## Data and one intervention

Use the existing fourteen complete source/target development vectors, seven
reviewed source/editor-A pairs, and verified native action costs. Keep all sixteen
attempted roles: the two904 roles remain unavailable because the intended-person
pairing failed. Do not add images, replace failures or treat arbitrary source
photos as clean. Source330 is not a clean input; its reference was accepted as
near unchanged. Keep1188 despite limited native detail.

The single intervention relative to the closed synthetic-development cycle is
**reviewed photographic correction supervision**. Inherit the same sixteen input
definitions, fourteen fixed gamma/R/B actions and depth4; no new feature search,
actions, weights or mapper. The existing external thirty-row isotonic mapping
artifact and its fourteen scores are fixed. No calibration rerun, contextual
model substitution or fold selection. Its MST column is constant4.494736842105263,
so this diagnostic cannot demonstrate learned MST conditioning. Retain and report
that limitation rather than making a new source hunt a prerequisite.

## Candidate and folds

Use the existing `image_loss_action_tree.fit_action_tree`, depth4. Each leaf
selects a gamma/red/blue tuple from the frozen fourteen-action catalogue. It
minimizes the sum of saved native RGBMAE action costs with equal role weights.
Each available fitting pair contributes one source and one identity role, so
pairs receive equal total weight. Fitting editor-target roles require zero
identity cost; no source colour-only labels or extra nonharm veto are invented.
Use the implementation's deterministic action/split tie rules unchanged.

This is the existing clean-feasibility action-tree learner, not a new classifier
or another variant of the old global colour guard. The prior source colour-only
flags have no matching meaning on these photographic references. The declared
learning objective and the photographic supervision change must remain visible.

Seven folds each hold out one publisher group's source and reference together:
six pairs/twelve roles fit, one pair/two roles evaluate. The eighth ledger entry,
904, has two unavailable evaluation roles and **no fit**. Training on all fourteen
with nothing to evaluate would be an unnecessary all-data fit. Maximum execution:
seven trees and fourteen held-role predictions. No release/all-data tree.
Publisher groups are not certified independent people, and these images have
already been reviewed; do not claim blind validation.

## Baseline, outputs and checks

Compare each held source output with the **uncorrected input**, against its
accepted editor reference on exactly the same native pixels with alpha>0. Use
all channels and pixels; no target-mask intersection or region shrinking.
Render with the existing direct-exponent gamma, red/blue gains, clipping, native
alpha blend and rounding. Save all fourteen outputs and the blocked-role ledger.

The prospective development checks are deliberately task-matched:

1. Fourteen held predictions, with all sixteen attempts retained and904 failures
   distinct from learned identity.
2. Seven-source equal-publisher mean RGBMAE **and** mean CIEDE2000 strictly improve
   over uncorrected input (comparison tolerance1e-12).
3. All seven held reference/identity outputs remain pixel-identical to their
   inputs; all protected and zero-alpha pixels remain unchanged for every role.

Report every source's RGB/DeltaE change, benefits/harms/ties, worst harms,
controls, identity edits and missed available catalogue benefit. Summarize source
cases by the saved oracle gamma direction to expose brightening/darkening
behaviour; do not call those physical exposure labels. Inspect all held outputs
against input/reference with labels hidden. Saved best-catalogue costs are
target-aware representability context, not predictive accuracy. Parameter
comparison to catalogue minima can only be described as catalogue-supervision
agreement, not error against known physical correction controls.

These checks do not require every source to improve, invent an accuracy target,
or replace old gates after failure. Individual harms must remain visible even
if averages improve. Passing supports another development decision only; it
does not permit a blanket safety/fairness claim, runtime deployment or final
holdout access. The earlier frozen synthetic/calibration comparison outcomes and
their acceptance rules remain unchanged; their numeric errors cannot be pasted
onto this different target cohort.

## Stop and paper alignment

Execute this candidate once, then close the comparison regardless of outcome.
No depth/action/weight/feature/guard/calibration repair, alternate cohort or new
annotation round follows automatically. Independently verify fitting splits,
tree arithmetic, renders, metrics and invariants without refitting.

The paper's primary study remains synthetic distortion versus original targets,
with ITA/MST, the decision tree, per-tone evidence, baseline improvement, actual
expert MOS and Android verification. This photographic-editor experiment is an
explicit development extension. It does not resolve the constant-MST limitation,
registration assumption or missing independent photographic tone labels, and
must not be presented as a completed skin-tone-conditioned final model.

Scripts785–786 package and independently check the specification in
`outputs/reviewed_correction_comparison_design_v1`. All fourteen vectors/costs
are unchanged, pairs never cross fitting/evaluation, the904 fit is skipped and
all old mapping/actions remain bound. This preparation reads metadata only:
zero image bytes, fits, predictions or app changes. No new acquisition/contact,
uploads, commits or pushes. Final24 and older locked images remain byte-unread.
