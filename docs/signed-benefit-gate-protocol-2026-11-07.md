# Signed-benefit correction gate: fixed development comparison

7 November 2026. User authorises progress on specific correction mistakes.
Saved action-cost audit533 finds binary counts conceal magnitude: matched binary
stress gate misses16useful versus27for the frozen gate, but mean missed benefit
is2.8803 versus1.2301RGBcodes and harmful-action cost.3825versus.0551. Freeze one
signed-benefit gate comparison before fitting, not a threshold/feature sweep.

Use original split correctors, NOT the unadopted gamma-restriction candidate.
Change the action estimator from binary logistic benefit to ridge regression of
signed RGBMAE reduction: input_mae minus predicted-correction_mae. Same12actual
input features, key/class-balanced weights and weighted feature scaling as the
matched split binary gate. Fixed ridgealpha1, unpenalized intercept, no target
clipping or target standardization. Apply original saved controls iff predicted
signed benefit>0; otherwise unchanged. No strength adjustment or new blend rule.

Ten outer held-key fits use ONLY504saved inner split-corrector training traces:
label key and outer key were excluded from inner corrector and upstream MST;
its fitting-row MST excluded that fitting key too. Reuse exact saved features,
controls/errors and weights, not outer evaluation gains. Compare against both
saved frozen joint-benefit gate and saved matched binary gate across420attempts.
No correction, target, MST, mask or distortion fits/inference.

Also fit one full-development signed gate on397saved own-key-held split predictions
and own-key-held MST features. Fit one matched full binary comparator on exactly
these rows/features/signlabels/weights, since the frozen full gate used joint
rather than split benefit labels. Thus11signed fits plus1fullbinary fit; all other
fitted models unchanged. This is a bounded objective comparison, not reuse of the
previous binary-gate experiment as a newly successful model.

Evaluate three336attempt native224conditions from saved borrowed, actual-input
and detector-fallback masks. The later eight publisher keys are already exposed;
no fit uses them, and this remains development evidence, not a new independent
test. Keep original source references/failure behavior and native/256scope separate.
Report RGB/CIEDE2000/equal-key means, clean harm, missed useful/harmful action
cost/regret, denominator/feature availability and unclipped predicted-benefit ranges.
Retrospective best of unchanged/corrected is diagnostic only, never an inference
input or a target fitted on held-key outcomes. No skin-truth/admission invention.

Inspect29fold clean and23native clean boards, focal recovered false correction,
and first available core/stress per native condition. Identify extra outcome-
selected harm boards separately. Verify training equations/weights/nesting/hashes,
portable gate actions, frozen controls and saved renders/metrics. Keep all failures.
Stop after one comparison; no automatic loss/alpha/threshold/feature sweep/refit,
new subjects, mask changes, runtime/Android adoption, contacts or sharing.
Private research/noncommercial/citation/no redistribution conditions remain.
