# Operator decision: one pre-power affine candidate, not another contrast retry

14 November2026. User authorized reviewing a minimal operator extension against
closed contrast studies and the FFHQ recoverability result. Select one bounded
generated algebra check only. No real-photo fit, learned predictor, production
renderer, output-schema adoption or paper edit is selected.

## What the existing evidence says

The November2 PPR10K candidate added one contrast control after gamma about
encoded midpoint0.5. It improved4/6initial check-block DE results, particularly
three wedding faces, but worsened two indoor results. The later eight-group
comparison and detail checks remain completed evidence, not a new training
cohort. Increased clipping and actual highlight flattening were observed; some
counts also reflected approximate-mask contamination. Smooth clipping reduced
endpoint flattening but did not recover absent source information or demonstrate
automatic parameter prediction. Do not restart these experiments or present
contrast as an untested solution.

The November14 FFHQ diagnostic instead showed substantial local-fit residuals
for directional composites under the current direct-gamma/three-control
renderer: mean RGB errors15.7–18.7codes for exposure/combined conditions despite
reference-informed controls. Alpha1core residuals and substantial input clipping
remain. These local fits do not prove a global lower bound, and neither their
RGB objective nor the earlier PPR experiment guarantees DE improvement.

## One candidate and its actual scope cost

Let y be normalized encoded input RGB. Propose only this mathematical family:

`T(y) = clip(max(0, a*y+d)**q * [r,1,b], 0,1)`.

Five scalar controls are q,r,b,a,d. Scale a>0, power q>0 and gains r,b>0;
d is finite and signed. Clip above1only after power/gains, rather than throwing
away an intermediate value that a later gain might bring back into range.
Existing correction alpha/protection would be applied after this transform,
with existing RGB8 rounding, if a later implementation is justified.

The current three-control transform is nested exactly at a=1,d=0. Full identity
is[1,1,1,1,0]. This is one affine-stage extension adding two independent scalars;
it is not the old single fixed-midpoint contrast control. Two scalars describe
independent input scale and offset in this family. This is not a proof that no
other four-parameter family could approximate the task or a globally minimal
operator over all possible designs. No matching completed pre-power/free-affine
implementation was found in the scoped correction/distortion/history search.

This is our proposed engineering family, not an attributed published method,
author-parity claim or claim of novelty. The old four-control family can still
approximate some changes and its positive results are retained.

**Five predicted controls depart from the paper's stated gamma/red/blue outputs.**
Keeping one decision tree and ITA/MST would not make this an unchanged method.
Adoption would require an explicit researcher scope decision, documented schema,
training/qualification and matching Android work. No adviser-response prerequisite
is imposed, but no paper/runtime change is silently authorized here. If exactly
three outputs must remain, reject this candidate for adoption; do not conceal
the extra controls as fixed preprocessing or a reference-informed inference step.

## Why the candidate addresses a demonstrated mechanism

The exposure-only forward function before clipping/quantization is
`y=c*x**p+t`, where c=1.08 for the fixed diagnostic row.
Underexposure has p=1/.70 and t=1-c-35/255.
Overexposure has p=.70 and t=35/255.

For an unclipped positive value, the inverse is
`x=((y-t)/c)**(1/p)`. The proposed family represents it with
q=1/p,a=1/c,d=-t/c,r=b=1. This is a known-forward-parameter construction,
not a fitted target or a way to infer those parameters from an unknown photo.
The mechanism removes the exposure scale/offset before undoing power.

The original green-channel family y**q lacks that independent affine stage.
This algebra explains why a different family is worth a small check; it does
not explain every residual of the local fits or prove old contrast cannot help.

Additive red/blue colour offsets are different. A shared d cannot simultaneously
subtract three different channel offsets before power. The retained r/b gains
do not generally make these channel offsets exactly invertible. Combined-case
residuals therefore remain explicit, not promised fixed by this extension.
The old wrong-axis learned predictions remain a separate problem.

Clipping remains irreversible. Distinct references can have the same clipped
input; one deterministic transform then gives them the same output. Lifting a
black patch can change its level without restoring its lost texture. No gain,
offset, soft clip or tree can be credited with reconstructing unspecified
clipped information merely because its output looks brighter.

## Bounded generated check fixed before execution

Use seven encoded-RGB triples formed by cyclic offsets0,2,4 through
v=[.35,.40,.45,.50,.55,.60,.65]. They are arithmetic probes, not people,
skin-tone categories or physical light measurements.

Exactly39records:

-21ideal records: seven triples each for identity, exposure-under and
  exposure-over. Apply the analytic controls above, not an optimizer.
-14combined records: the same seven triples with under/over plus[-10,0,10]/255.
  Apply the exposure-only analytic controls and disclose colour residuals;
  do not fit red/blue gains or add channel offsets to rescue them.
-4clipping records: underexposure of uniform0and uniform.05; overexposure of
  uniform.9and uniform1. Confirm each pair has equal clipped inputs and equal
  recovered outputs despite distinct references. Keep both members of each pair.

Record continuous forward values, clipping, recovery and errors; also record
recovery after quantizing the input to RGB8. Continuous ideal identity/exposure
error must be at most1e-12 and all outputs/parameters finite/in range as defined.
The clipped pairs must remain indistinguishable to the transform. Quantization
and combined residuals are descriptive; no post-hoc visibility cutoff or fit
threshold is introduced. Independent inverse arithmetic must agree with the
candidate on ideal exposure probes. Budget:0optimizers,0tree fits,0photo/mask
arrays,0ratings,0new sources. No solver bounds or real training roster selected.

Stop if the algebra/finite-value/nesting/collision checks fail. Do not tune a
bound, curve, channel offset or probe selection to obtain a pass. If they pass,
conclude only that the family expresses the intended unclipped exposure inverse.
Do not claim that it fixes combined colour, source transfer, fairness or user
usefulness. No real FFHQ/PPR re-fit follows automatically; the decision remains
whether a substantive five-output method change is acceptable and adequately
justified for the thesis before implementing a new target fitter.

## Preserved requirements

Darker-skin bias reduction remains central. Extra freedom can introduce unwanted
shadow lifting or shifts in accepted darker complexions; no reference-neutrality
or blanket brightening assumption is permitted. Independent eligible tone-label
evidence, clean/identity preservation and source-held usefulness remain required.
None is supplied by the generated probes or existing unlabelled FFHQ references.

All prior results, accepted supports, failed/closed recipes and ratings remain
intact. No source reacquisition, locked final24/older contents or manifests,
runtime/Android or manuscript access. Model unfinished; paper paused; November25
deadline retained.

Evidence: ppr10k-contrast-diagnostic-results-2026-11-02.md;
ppr10k-new-group-comparison-results-2026-11-02.md;
ppr10k-clipping-detail-results-2026-11-02.md;
ppr10k-smooth-boundary-results-2026-11-02.md;
ffhq-directional-recoverability-results-2026-11-14.md.
