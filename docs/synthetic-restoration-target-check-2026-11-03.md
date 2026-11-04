# Paper-aligned synthetic restoration: first target-consistency check

3 November 2026. User authorised starting data/target preparation after verifying
the proposal's photographic-restoration scope. Script400 checks generated arrays
only, without new source photos, fitting, calibration, inference or adoption.
The original photographic appearance is the intended target; intrinsic-colour
reference qualification is not a requirement for this claim.

## Implemented and checked

Three deterministic RGB ramp cases: neutral, gamma1.4/red0.85/blue1.05 and
gamma0.7/red1.5/blue0.8. These are arithmetic probes, not adopted Table2 settings,
MST-stratified distortions, photographic results or generated training labels.
Use explicit direct-exponent paper convention x**gamma followed by gains.
Its inverse is reciprocal gamma and gains raised to -1/gamma. Do not interchange
with the legacy reciprocal-exponent implementation or the frozen4-control formula.

- Exact baseline inverse on non-clipped float RGB checked within1e-12; observed
  maximum error2.23e-16. Source arrays and relevant source hashes unchanged.
- Clipping/8-bit encoding cause residual errors, even with inverse parameters.
- Applying the same inward alpha at distortion and correction does not make
  reciprocal parameters an exact inverse at feathered boundaries. Mean fractional-
  edge errors for the two non-neutral probes were0.00451 and0.02667 in normalized
  RGB; these synthetic numbers are not photo-quality acceptance thresholds.
- Neutral baseline parameters preserve the generated uint8 image exactly through
  actual apply_blended. Outside-alpha pixels remain unchanged in all probes.
- The frozen experimental soft-boundary function at neutral parameters changes
  3,456 channel codes in this particular generated ramp. This is not an image
  alteration rate for real photographs; it confirms the known nonidentity issue.

The baseline test uses synthetic square support and is not actual face/neck mask
validation. Four-control candidate stays frozen and unadopted; no fifth control,
new no-change classifier or alternative soft-width experiment introduced.

## Practical implication and next preparation

Keep original photographs as targets. Before generating a training table, choose
and document the exact distortion/correction composition and scoring support,
including colour ordering, alpha, clipping and quantisation. Parameter labels must
be verified against that composition; do not copy old analytic inverse labels or
target-aware PPR oracle parameters into the new model's training labels.

The source-reference/support, person/role grouping and matching-MST gaps remain.
No repeat same-person fit, further small review or new dataset-processing queue
activated by this arithmetic check. Reliable automatic correction is not claimed.
A qualified photographic source need not be certified intrinsic skin colour.

Outputs: outputs/synthetic_restoration_target_check_v1/protocol.json, results.json
and sha256.json. Checks are deterministic numerical assertions including source
immutability, baseline identity, no outside change and explicit counterexamples
to a false blended inverse. No pytest run or runtime/source module edits.
This verifies a preparation issue under the paper's existing scope; it is not a
new adopted method or panel change. Existing snapshots/proposal unchanged.
