# Table2 composite transform and recovery-target protocol

28October2026. User explicitly authorizes fullTable2distortions and approximate
three-parameter recovery targets. No study-image generation occurs before this
implementation and synthetic verification checkpoint.

Executable development convention (not a claimed editor-equivalent formula):
encoded floatRGB[0,1] → power `x**(1/gamma)` → contrast about0.5with multiplier
`1+contrast/100` → brightness offset `brightness/255` → additive red
`cyan_red/255` and blue `yellow_blue/255` (green unchanged) → single final clip
and nearest-even uint8encoding. Positive color values increase the namedRGB
channel; negative red/positive blue implements the paper's cool shift. No
intermediate clipping. Table2does not specify these units/order/pivot, so this
is a recorded implementation interpretation requiring thesis disclosure.

Fixed rows(light/medium/dark): gamma(.85,.70,.60), brightness(-20,-35,-45),
contrast(5,8,10), red(-6,-10,-14), blue(6,10,14). Reuse existing group convention
MST1–3/4–7/8–10with provenance. Group assignment and final eligibility remain
separate from defining the operator. No source labels fabricated.

Target fit: bounded nonlinear least squares in normalized encodedRGB, same
existing clipped power/gain correction, parameters(gamma,redgain,bluegain),
fixed initialidentity, bounds(.25,.25,.25)to(4,4,4), SciPyTRF, linear loss,
ftol/xtol/gtol1e-10,max_nfev500. Single fixed start, no parameter/bound search.
Objective is floatingRGB squared residual on explicitly provided fitting
support∩reference scoring mask. The caller must provide both supports; fitting
cannot imply final train admission. No reference enters inference.

Require at least100pixels and varying input intensities. Record convergence,
Jacobian rank, active bounds, input black/white channel fractions, selected
pixels, identity/fitRMSEand quantizedRGBMAE. Insufficient or rank-deficient fits
stay unavailable; do not substitute nominalinverse targets. A converged local
solution is not guaranteed global optimum. Quantization/clipping residuals are
reported, never treated as exact recovery. CIEDE2000remains a separate evaluation
metric, not this optimization objective. Reference-informed fits are target
construction/oracle capacity diagnostics, not learned correction performance.

Synthetic tests first: exact in-family recovery, composite residual/clipping,
identity, mask exclusion/invariance and invalid/degenerate cases. Study-image
generation, new eligibility, model fitting and runtime changes are not authorized
by passing software tests alone. Original artifacts/holds preserved; Android
paused and CPM deferred.
