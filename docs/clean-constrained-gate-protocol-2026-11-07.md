# Clean-constrained signed-benefit gate: fixed protocol and acceptance rule

7 November 2026. User authorises explicit clean-photo protection. Freeze one
constraint intervention before fitting. Reuse signed-benefit target,alpha1,
12features,key/class weights,scaling,original split controls and all masks/folds.
Minimize the same weighted ridge squared-error objective subject to a nonpositive
action score for EVERY fitting clean row. Clean means no additional synthetic
distortion, not a declaration of physically neutral lighting or perfect skin.

Use score <= -1e-6RGBcodes as a fixed numerical feasibility margin (not a learned
risk threshold or perceptual tolerance); inference still applies iff score>0.
The1e-6margin prevents tiny optimizer roundoff from turning an active training
constraint into a positive action. No threshold selection from held clean scores.
Initialize feasible constant -1e-6, solve one convex quadratic per fold/fullmodel
with analytical gradients,SLSQP,ftol1e-10,maxiter2000,objective divided by fitting
weight sum without changing its minimizer. No solver/alpha/margin/feature sweep.
Fail and preserve outputs if solver/feasibility checks fail; do not silently tune.

Ten outer gates use existing504nested split traces and corresponding saved
unconstrained534gates/weights/scaling. Apply constraints only to their fitting
clean rows:261fold occurrences of the same29development originals, not261people.
One full gate uses the same397own-key-held fitting rows and29clean constraints.
No held-key or later eight-key rows/labels/pixels enter constraints, scaling orfit.
Total11QPgate fits; no other predictive fits or image-model inference.

Compare retained frozen gate, prior unconstrained signed gate and new constrained
gate across420working256held-key attempts and3x336native224conditions (borrowed,
actual-input,detector-fallback). Retain binary comparator as context only. Keep
all failures, unavailable-feature no-ops, fixed correction controls and references.
Do not pool conditions or count repeated photos as independent. Later eight keys
are exposed development evidence, not newly untouched validation. Original
reference-unavailable photos remain facial-region-unscored/fullscene-scored.

Necessary further-development screen: ZERO changed pixels on every reference-
available clean held-key photo (29) and later clean photo (23); lower core RGBMAE
than the retained frozen baseline in BOTH held-key256 and fallback-native224.
Report all harms/stress/availability even if this screen passes. This is a strict
observed-sample criterion, not proof of population safety or deployment approval.
Training feasibility alone cannot satisfy it; no accepted extra-clean-harm budget
is inferred. Do not select models/thresholds using these exposed outcomes.

Verify training constraints/objective/KKT residuals/source hashes/nested row
identity, unchanged upstream/control artifacts, gate/render/metricselection and
independentRGBreplays. Inspect29fold+23native clean boards, focal and fixedfirst
core/stress per native condition; additionalworst-harm boards outcome-selected.
Stop afteronecomparison,includingnegative generalization. No automaticfurther
weights/loss/gate/alpha/margin/features/depth/subject/review/runtime/Androidchanges.
Private research/noncommercial/citation/no-redistribution conditions retain.
