# Clean-image harm: diagnosis and one balance comparison

6 November2026. The user's requested diagnosis and targeted repair comparison
are complete. The evidence shows mixed-leaf target averaging, a heavily
distorted fitting population and nearby clean/distorted feature vectors. One
fixed objective-balancing intervention reduces mean clean harm but does not
preserve clean images and worsens core results. **Neither candidate is adopted.**

## Read-only diagnosis

Script482used only the saved nested features, targets and trees. All29held
clean predictions exactly replay as raw means of their fitting leaf's targets.
Every such leaf contains nonclean rows; no held clean image reaches a clean-only
leaf. A per-layer decomposition exactly reproduces all29non-neutral control
drifts. This is a concrete explanation of what these fitted trees output, not
evidence that weighted training must fix the problem.

Clean examples account for8.10–8.18%of fitting rows across folds. Twenty-seven
of29held clean vectors have a nonclean nearest fitting vector after training-
only feature standardization. This is an exploratory proximity diagnostic,
not a fitted nearest-neighbour model, distance threshold or impossibility proof.
No exact float32feature duplicates with conflicting targets were found within
any fold. Inner/outer MST estimates come from different legitimate fitting sets,
so feature distances should not be treated as exact colour-identifiability tests.

All29original-versus-clean-output boards were inspected. Some changes are subtle;
others produce pronounced dark/bright regional patches. Hard borrowed-support
boundaries and ordinary recorded lighting remain confounders. These are
assistant development observations, not new human annotations or quality ratings.

Private diagnosis: `outputs/clean_correction_diagnosis_v1/`. It performs zero
fits and verifies source hashes,29leaf means and29drift decompositions.

## One fixed repair tested

The [protocol](clean-balanced-repair-protocol-2026-11-06.md) was frozen before
the new fit. Reuse exactly the original357trainable rows,420evaluation attempts,
10folds, saved nested MST predictions, five continuous-schema features, targets
and restricted fixed supports. Do not retune depth, add a gate, change features,
recompute target fits or use held labels. Keep depth3, seed42, minleaf1.

Each fitting publisher key receives equal total weight, and its clean/core/
stress layers each receive one-third of that weight. Rows share their key/layer
weight equally. The same weights enter fitting-target means/scales, tree loss
and raw leaf means. This is one objective change, not a clean-weight sweep.
There were10new correction-tree fits, zero new MST or target fits.

| Layer | Scored / attempts | Unchanged-input MAE | Original tree MAE | Balanced tree MAE |
| --- | ---: | ---: | ---: | ---: |
| Clean |29/30|0|10.369|8.010|
| Core |232/240|20.739|18.843|22.447|
| Stress |145/150|52.565|34.035|31.950|

RGB8 MAE is on the0–255channel scale. The14original failures remain unavailable
without invented scoring support; the nine stress feature failures remain
unchanged operational outputs in the145scored stress denominator. All matched
baseline and candidate denominators are unchanged.

The balanced candidate still changes and harms all29scored clean images.
Core RGB regressions versus unchanged input increase from98to142of232; stress
regressions increase from28to41of145despite lower mean stress error. Equal-key
candidate MAEs are7.801clean,22.370core and31.948stress, so equal-key summaries
do not rescue the decision. Candidate relative CIEDE2000 means are2.925clean,
8.100core and12.254stress. This is a trade-off, not a solved correction model.

All29clean original/baseline/balanced comparisons were viewed. Several formerly
large changes shrink, but some conspicuous regional changes remain. No favorable
case selection, new subjective labels or full420-output visual review is claimed.

## Verification and implementation

`src/model_training/layer_balanced_tree.py` is isolated from the default fitter.
Script483checks per-key weights, weighted raw leaf means and portable predictions
against inverse-normalized fitting-model predictions. An independent no-refit
check replays all406saved candidate images and metrics, including outside-support
invariance and held portable predictions. Baseline/source hashes remain unchanged.

Three new weighted-objective tests plus32existing target-scaling/portable tests:
**35passed in4.46seconds**. Tests cover weighted leaf means rather than unweighted
means, constant axes, invariance to duplication within a key/layer, and rejection
of missing layers. No full-suite or device test is claimed.

Private fitted artifacts: `outputs/balanced_correction_comparison_v1/`.
Verification and clean comparison boards: `outputs/balanced_correction_assessment_v1/`.
Original experiment and its MST/target artifacts remain preserved. No inference
model download, source expansion, scientific admission, runtime/Android change,
sharing or external contact occurred. Research/noncommercial, citation and
no-redistribution terms remain.

## Decision and next question

Close this one balance comparison. Do not continue adjusting clean weights,
depths or identity thresholds until the exposed sample looks good. The remaining
problem is separating normal recorded facial colour from imposed distortions
with the available inference features. A subsequent feature intervention should
be justified from input-only image information and fixed before fitting; neither
this result nor the earlier clean-only MST result establishes that more skin-tone
mapping alone can resolve that distinction. Preserve clean harm and nonclean
trade-offs as required outcomes of any later candidate.
