# Scene-aware gate: better clean preservation, unresolved misses and false corrections

6November2026. The authorized matched comparison is complete. The scene-aware
gate preserves23of29clean photos versus18with the facial-only gate, but still
wrongly corrects six clean photos and misses160of368available synthetic
distortions. **This remains an exploratory candidate, not an adopted model.**

## Matched design

Follow the [frozen protocol](scene-aware-gate-protocol-2026-11-06.md). Both gates
use the same whole-photo420attempts and the same saved face-plus-scene depth3
correction tree. Only gate inputs differ: five facial Lab/ITA/continuous-MST
features versus those five plus the seven fixed scene features. Do not interpret
the older restricted-region gate as the matched comparator.

Each method fits one logistic gate per outer held publisher key:20new gate fits.
Same fixed C1,L2default,lbfgs,max_iter1000,tol1e-4,seed42,weighted training-only
standardization and equal-key/equal-binary-class masses. The fixed rule applies
the shared saved correction controls only for a strictly positive logit;
zero/negative output is byte-identical unchanged input. No threshold search,
new correction/MST/target fits, masks or distortions.

All397available feature rows can supervise the gate, including40without usable
correction targets. The saved correction models keep their original357fitting
rows. Each gate-training MST feature excludes its own key and the outer key;
held vectors reuse outer-only estimates. No recipe, condition, source score,
reference image or target-fit status enters inference. Labels distinguish
originals from imposed synthetics, not aesthetic or physical correction need.

## Held-key detection

| Measure | Facial-only gate | Scene-aware gate |
| --- | ---: | ---: |
| Clean photos left unchanged /29 |18|23|
| Clean false corrections /29 |11(37.9%)|6(20.7%)|
| Synthetic distortions detected /368 |202|208|
| Synthetic distortions missed /368 |166(45.1%)|160(43.5%)|
| Core distortions missed /232 |119|144|
| Stress distortions missed /136 |47|16|

The overall synthetic miss reduction hides a trade-off: the scene-aware gate
detects more severe stress cases but fewer core cases. It misses62.1%of available
core distortions. A detection does not guarantee that the correction improves
the image, and no-op does not mean an imposed distortion was repaired.

Each method retains420attempts,397available decisions and23unavailable decisions.
The14original failures lack scoring support; nine undefined-ITA stress cases
are unchanged operational fallbacks, not detector true negatives. Always-correct
would yield29clean false corrections and zero available synthetic misses;
always-unchanged would yield zero clean false corrections and368synthetic misses.
These baselines are reported rather than ordinary imbalanced accuracy alone.

## End-to-end operational errors on fixed support

| Layer | Scored / attempted | Ungated shared corrector MAE | Facial-only gate MAE | Scene-aware gate MAE |
| --- | ---: | ---: | ---: | ---: |
| Clean |29/30|14.7037|5.4905|2.8495|
| Core |232/240|10.1152|14.7481|14.7630|
| Stress |145/150|25.5244|32.1345|26.3939|

RGB8MAE uses the0–255channel scale. Fourteen unsupported attempts receive no
fabricated numeric error; nine feature-failure outputs remain in the scored
stress denominator. Relative CIEDE2000 and equal-key summaries are saved with
the full results. Six clean corrections still cause harm. Gated regressions
versus unchanged input are31→20of232core outputs and18→14of145stress outputs
for facial-only→scene-aware gates. Lower harm counts can coexist with missed
useful correction and higher average error than the ungated corrector.

These are matched development descriptions, not significance, calibrated
probabilities, independent generalization, skin-tone fairness or final model
accuracy. All sources were already development-exposed. The tiny native faces,
borrowed masks, clipping, original lighting and source-score limitations remain.
Whole-scene statistics include the release's studio background and visible
chart pixels; transfer to unconstrained photographs remains untested.

## Verification and inspection

Script496fits and saves the paired gates. Script497checks3573nested training
traces,20weighted scaling/class-mass constructions,794independent held linear
logits and812saved renderer/metric outcomes, with no verification refits.
Independent confusion counts match both methods. Both gate-off outputs exactly
equal their distorted inputs; gate-on outputs use the same saved correction
parameters. Source and all bound parent artifacts remain hash-identical.

Existing gate/scene-feature/continuous-interface suites: **29passed in4.31seconds**.
No new full-suite, device test or scientific validation is claimed. All90fixed
inspection boards were viewed: clean and two predeclared core/stress cases per
original, including three original-failure contexts. Some clean outputs are now
preserved where ungated correction creates large patches; visible changes remain
in false-positive cases. Many core no-ops retain the imposed cast/darkening.
Severe stress shadow/detail loss remains even where correction is applied.
These are assistant development observations, not new reviewer labels or MOS.

Private models/results/images: `outputs/scene_gate_comparison_v1/`.
Private verification/boards: `outputs/scene_gate_assessment_v1/`.
No final refit, admission, runtime/Android update, dataset expansion, sharing,
external contact or conference submission. Author research/noncommercial,
citation and no-redistribution terms remain.

## Decision

The matched scene-aware gate improves clean preservation and severe-distortion
detection but does not provide reliable automatic correction across this
sample. Do not tune its threshold, sweep classifiers or treat23clean no-ops as
validation. Close the paired test. The remaining decision is an explicitly
justified operating scope or new inference evidence for clean-versus-distorted
separation; neither a manual app step nor a narrower final method is adopted
automatically. No further fitting task is activated by these results.
