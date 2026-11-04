# Blended correction-target construction — 3 November 2026

The proposal's goal is synthetic photographic restoration toward the original
photograph, not restoration of measured intrinsic skin colour. This work builds
an isolated target-construction tool for that goal. It does not train or adopt
a correction model, admit photographs, or resolve ITA-to-MST mapping.

## What was implemented

`src/model_training/blended_recovery_targets.py` fits gamma, red gain and blue
gain against a supplied reference using the supplied application alpha. The
renderer uses direct-power gamma, channel gains, clipping, inward blending and
RGB8 rounding, matching `apply_blended` for these controls. It is separate from
the existing reciprocal-gamma target builder and the frozen four-control
contrast/soft-boundary experiment. No runtime caller was switched.

There is one bounded local least-squares fit starting at neutral, with each
parameter bounded to [0.25, 4], maximum 500 function evaluations and tolerance
1e-10. These are explicit experimental solver settings, not paper-mandated
augmentation limits or adopted training criteria. Optimisation minimises float
encoded-RGB squared error; actual rounded RGB8 residuals are reported separately.
This is not a global optimum guarantee or a CIEDE2000 optimisation objective.

The caller must supply a nonempty boolean scoring region inside positive alpha.
Unchanged scored pixels receive exact neutral parameters without optimisation.
Degenerate inputs or unsuccessful/rank-deficient fits receive no usable target.
Reference differences outside application support are reported, including on
the neutral path; they cannot be fixed by this operator. Every result explicitly
remains not admitted for calibration or training. Quality acceptance remains a
separate decision; solver convergence does not certify a good correction.

## Generated-array diagnostic

Script401 saves evidence in `outputs/blended_recovery_target_check_v1/`.
It uses one deterministic generated RGB8 array (48×48), a square support with
fractional boundary alpha, and three probes. No real photos or model inference.

| Probe | Input average absolute channel error | Fitted output error |
|---|---:|---:|
| Unchanged control | 0.000 | 0.000 |
| Blended gamma/red/blue distortion | 25.078 | 0.253 |
| Illustrative contrast/brightness/gamma distortion with clipping | 44.380 | 15.267 |

Errors are RGB8 channel code values, averaged over all positive-alpha pixels.
They are not percentages, colour-difference units, model accuracy or population
results. The complex probe deliberately lies outside the three-control family;
its formula is recorded in the JSON and is not adoption of a Table2 policy.
Clipped cases and their substantial residuals were retained.

Two target fits plus two deterministic repeat fits were performed. The clean
case took a neutral shortcut. All three resulting renders matched independent
calls through the existing `apply_blended` function exactly. Outside-support
pixels and input arrays were unchanged. The prior analytic-inverse comparison
is also saved for the matching distortion, without claiming exact inversion.

## Verification and next boundary

37 focused tests passed in 2.00 seconds across the new module, seamless blending,
direct gamma and existing recovery targets. This is not a new full-suite run.
The frozen script399 sources and parent manifests are checked separately; no
historical diagnostic is rewritten.

This resolves an implementation gap for experimental three-control blended
targets, not the whole training-readiness plan. Before real training, specify
the final distortion recipe/convention and scoring policy; admit suitable
ordinary photographic sources and face/neck support; preserve identity and
evaluation roles; establish matching MST inputs and evaluation adequacy. Do not
use this diagnostic to turn PPR oracle parameters into labels or justify a
clean-only refit. A fourth contrast output remains experimental and requires an
explicit method decision before it can replace the paper's three outputs.
