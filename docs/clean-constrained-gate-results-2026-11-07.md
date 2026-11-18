# Clean-constrained gate: results and acceptance decision

7 November 2026. Completed the [predeclared comparison](clean-constrained-gate-protocol-2026-11-07.md).
The gate now preserves every fitting clean example, and improves substantially
over the previous unconstrained signed gate on held clean photos. It still alters
7/29held-key clean photos and3/23later clean photos, failing the zero-change
screen. **Not adopted; the retained frozen gate/model remain unchanged.**

## Explicit requirement and one implementation

The objective remains weighted signed-benefit ridgealpha1 with the same12features,
weights,scaling,targets and original split controls. Add one constraint: every
fitting clean example must have action score <= -1e-6. This fixed numerical margin
prevents optimizer roundoff from crossing the unchanged inference rule(score>0).
It is not a tuned confidence threshold, allowed colour change or perceptual margin.

Clean means no additional synthetic distortion, not physical illumination neutrality.
No clean status is supplied at inference. Only fitting rows constrain each model;
held subject keys and the later eight keys do not enter fitting or constraints.
Known clean vectors and their convex combinations can be protected by these affine
inequalities; arbitrary future vectors are not guaranteed to be protected.

11convex QP gate fits, with fixed SLSQP settings and analytical gradients:
10nested held-key models +1full397row model.261fold clean fitting occurrences
plus29full-model clean rows=290constraints, repeated across the same29originals,
not290independent people. Every fitting constraint passes. No solver retries,
margin/alpha/threshold sweep, extra predictive fits, upstream changes, image-model
inference or new subjects. Previous signed/binary gates are reused comparators.

The necessary further-development screen was fixed before fitting:
zero changed pixels on29available held-key clean photos and23later clean photos,
AND lower core RGBMAE than the retained frozen baseline on both held-key256 and
fallback-native224. Both core improvements pass; both clean requirements fail.
Passing would still not mean deployment approval or population safety.

## Held-key working256 results

RGBMAE in0–255codes on the original saved measurement region:

| Layer | Retained frozen gate | Previous signed gate | Clean-constrained gate |
|---|---:|---:|---:|
| Clean |0.05580|1.29554|0.89681|
| Core |13.51194|9.62971|11.25878|
| Stress |23.75824|23.04107|23.17349|

Changed/harmed clean cases:3/29frozen,27/29previous signed,7/29constrained.
Core harms:9/232frozen,37/232previous signed,15/232constrained.
Stress harms:1/145frozen,3/145previous signed,2/145constrained.
The constrained gate trades some of the previous signed gate's core improvement
for better preservation, but clean behavior remains worse than the retained gate.
Mean error alone does not override the predeclared clean requirement.

Availability remains29/30clean,232/240core,145/150stress reference-scored;
397feature predictions,9undefined-ITA unchanged cases and14original failures.
Unavailable originals remain in attempts without fabricated numerical colour scores.

## Later exposed native224 comparisons

Each cell lists frozen / previous signed / constrained RGBMAE. Keep these support
conditions separate from one another and from the working256 table.

| Condition | Clean | Core | Stress |
|---|---:|---:|---:|
| Borrowed original support |0.02774 /3.23507 /0.72605|15.42751 /8.33446 /11.04477|24.11074 /24.64308 /24.12117|
| Actual-input support |0.02774 /3.23507 /0.72605|17.74503 /11.96519 /14.37973|37.71315 /38.17219 /37.58630|
| Detector-fallback support |0.02774 /3.23507 /0.72605|17.42631 /11.64646 /14.06100|36.22723 /36.68627 /36.10039|

Native clean changes fall23->3/23versus the previous signed gate; retained frozen
changes1/23. The23clean outputs are identical across all3support conditions, not
69independent clean tests. The one unavailable clean source stays unchanged but
cannot establish successful facial measurement.

Constrained core reference harms:5/184for each condition, versus2/184retained
frozen. Constrained stress harms:1/115borrowed,0/115actual-input/fallback;
retained frozen0/115. Feature availability remains318/275/291by condition;
reference availability23/24clean,184/192core,115/120stress. All original failure
and undefined-feature fallbacks remain. Full-scene metrics, CIEDE2000, equal-key
means, decision ranges and action costs are retained in results_PRIVATE.json.

The focal recovered mild-warm photo still receives correction: predicted benefit
+8.95655, with unchanged original split controls. Its original reference mask is
unavailable, so it remains outside facial-reference means. Its full-scene error
still increases2.01958->2.05803. A lower positive forecast than the prior gate is
not a corrected decision or evidence of calibrated uncertainty.

## Interpretation and verification

Training protection is genuine but does not generalize fully in these saved
conditions. This is not a solver success being mistaken for a successful model.
The evidence does not establish that all features are intrinsically insufficient,
that more data are necessarily required, or that a new threshold would solve it.
No further alteration is selected from these exposed evaluation outcomes.

Independent verification checked11convex-QP feasibility/KKT residuals and frozen
scaling/weights, all290training clean constraints,3573nested benefit labels and
12852inner fitting-key exclusions.1281original-control/action checks and2828saved
render/action/metric-selection replays, with independent RGB errors; inherited
CIEDE2000 values bind to exact previously validated unchanged/ungated pixels.
The correction controls, upstream models/masks and outside-mask pixels are fixed;
source hashes match.38focused tests passed in6.86seconds, including3new constraint
feasibility/frozen-specification/objective-bound/invalid-index tests.

Viewed61fixed boards (29held-key clean,23native clean,9native context/focal) and4
explicitly outcome-selected extra-error boards. A worst-extra-error selection can
be equal-error where no additional harm exists; it is not automatically a new
harmful case. Visible unwanted clean edits, partial forehead regions, residual
casts and hard mask boundaries persist. No new labels, dense skin/object truth or
independent/blind visual assessment.23native clean duplicates were verified.

1428records are repeated conditions on54original photos, not independent samples.
Later publisher keys are already development-exposed; groups are not externally
verified identities. Mask contamination, low native resolution and absent untouched
highest-range coverage remain. No facial/full-scene accuracy measures are pooled.

Private outputs: clean_constrained_gate_models_v1 (including per-fold solver
artifacts), clean_constrained_gate_comparison_v1, clean_constrained_gate_assessment_v1
(acceptance_PRIVATE.json), clean_constrained_gate_review_v1. Scripts538–541;
isolated clean_constrained_gate.py. All scientific admissions and adoption remain
false. Close this one constraint experiment without automatic refitting, weights,
loss/alpha/margin/threshold/features/depth sweeps, new subjects or review tasks.
No runtime/Android change, contact, sharing, publication or submission. Dataset
research/noncommercial/citation/no redistribution conditions retain.
