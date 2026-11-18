# Split exposure and colour predictors improve the development comparison

6November2026. The authorized split-predictor comparison is complete. Separate
gamma and joint red/blue-gain trees reduce error substantially versus the old
shared three-output tree. With the frozen benefit gate, average clean RGB8error
falls1.4822→0.0558, but three clean images still change and mild-cast failures
remain. **This is an experimental improvement, not runtime adoption.**

## One architecture comparison

Follow the [protocol](split-control-predictors-protocol-2026-11-06.md). Use the
same12facial+scene features,357trainable rows,10publisher-key folds, saved nested
MST estimates, targets, whole-photo distortions and borrowed measurement masks.
Both heads use unweighted per-target fitting-only normalization and fixed
depth3/seed42/minleaf1. Twenty new head-tree fits form ten paired predictors.
No new gate/MST/target fits, masks or distortions.

The gamma head has one output and the colour head has two; the renderer still
receives gamma/red gain/blue gain in the same order. Both heads train on the
same rows, not recipe-specific subsets. This changes splitting objectives and
increases capacity from one tree to two (up to eight leaves each), so the result
cannot be attributed exclusively to decoupling the outputs.

The benefit gate's held decisions are reused exactly. It was trained to predict
benefit of the old joint corrector, not the split predictor. This is explicitly
a frozen-gate transfer test, not newly matched benefit calibration. Gate-off
remains exact unchanged input; no thresholds or inference labels change.

## Four matched operational paths

| Layer | Scored / attempted | Joint ungated | Split ungated | Joint + frozen gate | Split + same gate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Clean |29/30|14.7037|1.3254|1.4822|0.0558|
| Core |232/240|10.1152|3.5612|14.2060|13.5119|
| Stress |145/150|25.5244|22.8556|25.4913|23.7582|

Values are RGB8MAE on the0–255channel scale, not accuracy percentages. All
420attempts remain. Fourteen original failures lack scoring support; nine
undefined-ITA outputs are unchanged fallbacks within the145scored stress cases.
The matched paths have identical availability and fitting roles.

Ungated clean harm remains29/29, although average magnitude decreases. With the
same gate,26clean images are exact no-ops and three still worsen. Smaller harm
must not be reported as zero harm. Core harms versus unchanged input fall63→38
ungated and12→9gated; stress harms26→3ungated and4→1gated.

Equal-key split MAEs are1.6742clean,3.7433core,22.7333stress ungated and
0.0595clean,13.2667core,23.5491stress gated. Relative CIEDE2000 means are
0.8440/1.7595/9.5317ungated and0.0744/5.2405/9.9859gated. No significance,
independent generalization, physical colour truth or expert quality claim.

## Mild colour casts and exposure trade-offs

| Recipe | Input MAE | Joint ungated | Split ungated | Joint gated | Split gated |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pure cool cast,29available |1.0684|13.6457|2.5426|2.7391|0.9887|
| Pure warm cast,29available |0.6056|14.0991|1.9246|1.9327|0.6614|
| Exposure under,29available |25.2495|13.6158|5.0623|24.9874|24.7806|
| Exposure over,29available |29.9499|4.1618|2.7288|11.6442|10.3310|

The split predictor reduces severe cast overcorrection but does not solve every
mild case. Ungated cool-cast harms fall29→2, but its mean error still exceeds
unchanged input because those failures are large. Ungated warm casts still harm
all29; gated warm harm remains3/29and mean error0.6614still exceeds input0.6056.

Cool/warm predicted gamma ranges are0.6698–1.4286and0.9988–1.4286respectively,
versus fitted target gamma near1. Thus the gamma issue is reduced in typical
outputs, not bounded away in every case. Controls still equal the paired clean
prediction for28/29cool casts and29/29warm casts. These small perturbations remain
difficult for the fixed partitions. Reference-aware targets remain local fitted
supervision, not runtime truth.

The frozen gate suppresses much of the improved exposure correction: for
underexposure, split ungated MAE5.0623becomes24.7806with the old gate. This is
evidence of operating-policy mismatch after changing the corrector, not proof
that retraining a gate will necessarily solve it.

## Verification and visual findings

`src/model_training/split_control_candidate.py` is isolated from default fitting
and runtime interfaces. Script502fits the paired heads; script503independently
checks6426head fitting routes,160raw leaf means,20head normalization contracts,
406frozen gate records and812saved renderer/metric outputs without refitting.
Source and parent artifact hashes remain unchanged.

Three new split-predictor tests plus existing target-scaled/portable tests:
**35passed in4.70seconds**. New tests cover cross-head target independence,
scalar/paired export ordering, duplicate-vector raw means, constant axes and
invalid schema/targets. This is not a full-suite or device check.

All70preselected boards were inspected: all30clean contexts and four fixed
recipes on the first case ID per publisher key. This includes the original
failure and is not a full420-output visual review. Clean outputs are often
closer to their references and many exaggerated mild-cast changes shrink.
Some ungated exposure corrections remain conspicuous, while gate-off exposure
cases retain darkening. Severe stress shadow/detail loss and borrowed-mask
boundaries persist. These are assistant observations, not new reviewer labels.

Private artifacts: `outputs/split_control_comparison_v1/`.
Verification/boards: `outputs/split_control_assessment_v1/`.
The small development-exposed sample, native detail, studio/chart cues,
source-score/calibration shift and unverified material support remain. All
admission flags remain false. No runtime/Android update, final refit, source
sharing, contact or conference work. Author research/noncommercial, citation
and no-redistribution terms remain.

## Decision

Retain this as a stronger experimental corrector for a subsequent explicitly
specified comparison, without adopting it in the app. The next compatible
decision experiment would regenerate nested benefit labels from split-head
inner correctors, rather than assume the previous joint-corrector gate remains
appropriate. It must preserve subject exclusions and report clean/mild-cast
harm and lost exposure corrections. No such retraining, sweep or acceptance
of the remaining risk is activated by this completed architecture test.
