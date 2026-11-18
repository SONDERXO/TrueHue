# Split-corrector benefit gate retrained: no overall RGB improvement

6November2026. The user-authorized retraining and matched comparison are
complete. New benefit labels were generated from subject-held split predictors.
The retrained gate misses fewer useful corrections but increases mean RGB error
in clean, core and stress groups versus the previous frozen gate. **The retrained
gate does not replace the previous development benchmark.** Neither version is
adopted for the app or scientifically admitted.

## Fixed nested experiment

Follow the [protocol](split-benefit-gate-protocol-2026-11-06.md). Keep the12input
features, same420whole-photo attempts/10publisher keys, saved357correction-fitting
rows,397gate-feature rows and targets/masks. Each inner label-corrector excludes
outer key H and label key S. Its fitting key T receives MST estimated with H,S,T
excluded. Label S uses MST excluding H,S. Strict positive RGB8MAE reduction gives
benefit1; equal/worse error gives0. References enter supervision/evaluation only.

Fit45inner split pairs (90new head trees) and10new logistic gates. Reuse all175
saved MST artifacts (55one/two-key-excluded and120three-key-excluded) and20outer
split head trees. Zero new MST, outer-corrector, target, mask or distortion fits.
The fixed gate settings, key/class masses, fitting-only scaling and zero-logit
decision rule remain unchanged. All keys have both benefit classes; gates
converge in25–28iterations. No threshold or setting retry.

## Matched operating results

| Layer | Scored / attempted | Split ungated RGB8 MAE | Split + previous frozen gate | Split + retrained gate |
| --- | ---: | ---: | ---: | ---: |
| Clean |29/30|1.3254|0.0558|0.0950|
| Core |232/240|3.5612|13.5119|13.7272|
| Stress |145/150|22.8556|23.7582|25.7359|

RGB8MAE uses the0–255channel scale. Fourteen original failures remain without
scoring support; nine undefined-ITA outputs remain unchanged within the scored
stress denominator. No availability or fitting-row filter was changed.

Clean harmed/changed photos increase3→6of29. Two previous clean harms persist,
one disappears and four previously preserved clean photos change. Their mean
magnitude remains small but is not reported as zero. Core harmed cases fall
9→8of232, while stress harmed cases rise1→3of145. Equal-key retrained MAEs are
0.0974clean,13.4748core and25.5176stress. Relative CIEDE2000 means are
0.1432clean,5.1804core and10.5123stress. Core perceptual mean improves slightly
from5.2405even though core RGB mean worsens; this is a metric trade-off, not
uniform superiority or statistical significance.

## Fewer missed useful corrections does not guarantee lower error

Using the same saved outer split corrector to define evaluation benefit:

| Useful corrections blocked by gate | Previous frozen gate | Retrained gate |
| --- | ---: | ---: |
| Core |130|120|
| Stress with available features |27|16|

The retrained gate permits more useful corrections by count, but the sizes of
their benefits and the harm introduced also matter. A binary benefit label does
not model improvement magnitude. These results support that limitation; they
do not prove it is the sole cause. Inner label-generating correctors use eight
keys, whereas outer correctors use nine, so benefit-proxy transfer also remains.

Cool-cast mean error improves0.9887→0.9082with zero harmed cool cases. Warm-cast
error worsens0.6614→0.7007and warm harms rise3→6. Underexposure mean error improves
24.7806→21.8395, but overexposure worsens10.3310→14.7262. The corrector still needs
careful clean/mild-cast and exposure reporting; the average gate result is not
enough to judge those behaviors.

There are397available gate decisions and23unavailable attempts, including14
original failures and nine undefined-ITA decisions. Synthetic no-ops are150core
and16stress, but synthetic membership is not the benefit objective. Unavailable
cases are not true negatives. No real-world aesthetic correction need, physical
skin colour, calibrated probability or independent generalization is established.

## Verification and inspection

Script504fits the new inner heads/gates. Script505independently checks120reused
ridge membership/scaling/normal equations,12852inner fitting feature traces,
90head normalization/raw-leaf constructions,3573rendered held benefit labels,
397outer logits and406operational image/metric replays. No verification refits.
All bound source and previous artifact hashes remain unchanged.

Existing split/gate/target-scaled/portable suites: **41passed in6.27seconds**.
This is a focused check, not a full-suite, device or validation result. All90
fixed clean/core/stress boards were inspected, including three original-failure
contexts. Some exposure cases are now corrected where the frozen gate left them
unchanged, but visible regional changes and severe stress shadow loss remain.
No new human labels, expert ratings or complete420-image visual review.

Private outputs: `outputs/split_benefit_gate_v1/`; independent verification and
boards: `outputs/split_benefit_gate_assessment_v1/`. Private author research/
noncommercial, citation and no-redistribution terms remain. No source transfer,
runtime/Android update, final all-data refit, admission, contact or submission.

## Freeze and next boundary

Freeze this comparison and preserve the split predictor with the previous
frozen gate as the prior development benchmark. Its gate-transfer limitation
and repeated-sample model selection remain disclosed. The new retrained gate
is retained as a negative comparison, not promoted merely because its label
generation matches the split architecture.

The checkpoint contains fold-specific development artifacts, not a single
deployable model or an ensemble. There is no all-data fitting step or newly
untouched evaluation cohort in this task. Before broader evaluation, specify
the final fitting procedure and fixed candidate, source/publisher-key roles,
measurement contract and failure policy before inspecting new outcomes.
Repeatedly tuning this exposed sample cannot create independent evidence.
No new threshold, loss, gate, subject batch or evaluation is activated here.
