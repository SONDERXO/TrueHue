# Signed-benefit gate: action-cost audit and results

7 November 2026. Completed the [fixed protocol](signed-benefit-gate-protocol-2026-11-07.md).
An amount-aware gate improves average ordinary-distortion reconstruction error,
but applies far too many corrections to clean images and does not prevent the
focal false correction. **Not adopted.** Previous frozen gate/model remain unchanged.

## Why this comparison

Saved action-cost audit533 separates a gate's excess RGB error, relative to the
retrospective better of unchanged/corrected, into harmful-action cost plus missed
benefit. This retrospective comparison is diagnostic only, never an inference
input or a newly admitted accuracy target.

The prior matched binary gate missed fewer useful stress cases (16vs27for the
frozen gate), yet mean missed benefit was2.8803vs1.2301RGBcodes, and harmful-action
cost.3825vs.0551. Counts alone hid the sizes of the mistakes. This justified one
fixed test of signed-benefit prediction rather than another threshold adjustment.

## What was fitted and frozen

Signed benefit = input RGBMAE minus inner predicted-correction RGBMAE. Weighted
ridgealpha1 predicts that value from the same12input features. Scaling and key/
positive-benefit-class balancing match the binary comparator. Intercept is
unpenalized; target/output are not standardized or clipped. Apply the existing
split controls only if predicted gain>0; otherwise return unchanged. Correction
strength itself is unchanged.

10outer held-key signed fits reuse504saved nested split-corrector traces, with
outer/label keys excluded from the inner corrector and MST. Their fitting-row MST
also excludes its own key. Outer evaluation gains are NOT training targets.
One full-development signed gate uses397saved own-key-held split predictions and
MST features; one matched full binary comparator is fitted on exactly those rows,
features, sign labels and weights. The frozen full baseline used joint-corrector
labels, so this matched comparator is needed to distinguish the objective change.

Total12new photographic gate fits:11signed ridges +1fullbinary logistic. No new
corrector/gamma/gain/MST/target/mask/distortion fits or image-model inference.
The unadopted gamma-restriction candidate is NOT used. The earlier comparison
manifest supplies only saved original contexts and original-control paths;
verification independently matches controls to the original split models.

## Original held-key working256 comparison

RGBMAE in0–255codes, on saved original measurement support:

| Layer | Frozen gate | Matched binary gate | Signed-benefit gate |
|---|---:|---:|---:|
| Clean |0.0558|0.0950|1.2955|
| Core |13.5119|13.7272|9.6297|
| Stress |23.7582|25.7359|23.0411|

Reference-scored29/30clean,232/240core,145/150stress.397feature decisions;
9undefined-ITA cases stay unchanged,14original failures remain unscored and in
attempt counts. Clean harms rise3->27/29versus the frozen gate (matched binary6).
Core harms9->37/232; stress harms1->3/145. Average core improvement therefore does
not establish safer decisions or acceptable clean behavior.

The signed gate predicts clean benefits ranging-2.4525to18.3900codes and applies
27clean corrections. Predicted positive gain is not a calibrated guarantee.
Core mean missed-benefit cost falls10.3542->6.0699versus frozen, while mean harmful-
action cost rises.02382->.42585. Stress costs become.18550missed benefit +.38247harm,
versus1.23008+.05506frozen. This is the measured trade-off, not a universal property
of regression or proof that another architecture cannot work.

## Later exposed eight-key native224 comparisons

Each cell lists frozen / matched-binary / signed RGBMAE. Supports and renderers
remain separate; do not pool with working256 or across native conditions.

| Condition | Clean | Core | Stress |
|---|---:|---:|---:|
| Borrowed support |0.0277 /1.2523 /3.2351|15.4275 /14.2927 /8.3345|24.1107 /27.9182 /24.6431|
| Actual-input support |0.0277 /1.2523 /3.2351|17.7450 /16.3503 /11.9652|37.7131 /40.0725 /38.1722|
| Detector-fallback support |0.0277 /1.2523 /3.2351|17.4263 /16.0315 /11.6465|36.2272 /38.5866 /36.6863|

All23reference-available clean photos are changed and harmed by the signed gate;
the matched full binary harms7, frozen baseline1. The unavailable clean photo
stays unchanged. Signed clean predictions are all positive,1.8043to23.7174codes.
Those23clean outputs are exact duplicates across native support conditions;
they are23photos, not69independent tests.

Core reference-region harms: frozen2, signed27with borrowed support or28with
actual-input/fallback support. Stress harms: frozen0, signed4borrowed or3actual/
fallback. Reference availability remains23/24,184/192,115/120; feature availability
318borrowed,275actual-input,291fallback. All unavailable-feature cases retain
unchanged fallback. Full-scene native errors, CIEDE2000, equal-key means, decision
ranges and costs remain in results_PRIVATE.json; reference-unavailable cases are
not assigned invented facial-region scores.

The recovered focal mild-warm case is still corrected: signed predicted gain
+20.5572; matched full binary logit+.46564. Its controls/output remain the harmful
original split prediction, with full-scene error2.01958->2.05803. The original
reference mask remains unavailable. Its gate forecast uses the training mask-
measurement scope and cannot be compared directly with a diluted full-scene MAE
as though those were the same prediction target.

## What we learned and what remains open

This fixed objective change reduces missed high-benefit corrections, but does
not reliably separate already acceptable photos from distortions. Minimizing
average signed-benefit prediction error does not, in this experiment, preserve
clean images. The result does not isolate whether linear capacity, inputs,
inner-to-outer corrector differences, mask contamination or training distribution
is the dominant cause. It does not justify choosing a new threshold from these
exposed clean predictions or treating their range as a validated safety bound.

No acceptance of extra clean harm was requested, and the prior model already
has known errors. Keep both as experimental evidence; do not claim a finished
or safe automatic correction model. A future intervention needs an explicit
clean-preservation objective/acceptance policy and evidence that it can generalize;
merely improving the global mean or repeating earlier class weights is insufficient.
No further fit, threshold/loss/alpha sweep, annotation task, source expansion or
runtime integration is activated by this result.

## Verification and review

Verified11weighted signed normal equations/scaling/weights,3573nested signed-gain
arithmetic checks and12852inner fitting-key exclusions;1281original-control/action
replays and2828saved render/action/metric-selection replays with independent RGB
errors. Every chosen output is byte-identical to either its already validated
unchanged or original ungated source, binding inherited CIEDE2000 values to exact
pixels; no claim of a second independent CIE implementation. All controls, masks
and pixels outside application support are unchanged. Source/model hashes match.
35focused tests passed in5.65seconds, including3new signed-gate tests.

Viewed61fixed boards (29fold clean,23native clean,9native context/focal) plus4
explicit outcome-selected worst extra-harm boards. Visible changes to acceptable
clean photos, hard patch boundaries and residual casts reinforce the failure of
clean preservation. No new human labels or blind/dense skin assessment. Full-
face/neck quality, object protection, highest-range coverage and real-world
validation remain unresolved.1428records are repeated conditions on54originals,
not independent accuracy observations; later subjects were already exposed.

Private artifacts: correction_action_cost_audit_v1, signed_benefit_gate_models_v1,
signed_benefit_gate_comparison_v1, signed_benefit_gate_assessment_v1,
signed_benefit_gate_review_v1. Scripts533–537 and isolated signed_benefit_gate.py.
Scientific admissions remain false. No Android/runtime change, contact, sharing,
publication or submission. Research/noncommercial/citation/no redistribution retain.
