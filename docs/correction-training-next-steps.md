# Correction-model preparation after mouth-fix integration

**Current checkpoint, 23 October 2026:** this document contains historical
preparation guidance. A small development tree and revised training table now
exist. Before expanded training or model selection, follow
[thesis-method-alignment.md](thesis-method-alignment.md), which records unresolved
differences from the proposal and the recommended order of work.

Current controlled-development configuration: source suitability and scope
for an eight-source software run are fixed in
`docs/controlled-development-policy.md`. This is separate from final thesis
eligibility and does not approve a change to tone-conditioned severity.

Status: implementation checklist and proposed transform contract; no training
has been performed and no grouping-method change has been approved.

Update 2026-10-20: the float operator and a five-source, 15-pair technical pilot
are implemented and verified. See `docs/synthetic-pair-pilot.md` for actual
parameters, scope, clipping and input-pipeline failures. The full training
prerequisites below remain unresolved; the pilot is not final training data.

Source-selection statuses, duplicate screening, provisional source-level
allocations and pair failure policy are now implemented; see
`docs/source-selection-splits-and-failures.md`. Allocation is not a claim of
final source eligibility. Reference/current-mask suitability and the final
group-dependent severity/scope decisions still require resolution.

## Current input

Use the explicit `v2_complete_mouth_v1` feature manifest under
`data/manifests/v2_complete_mouth_v1/`. Old manifests and review labels remain
baseline evidence. Computation success is not training eligibility. Image
83184 remains flagged for misplaced landmarks.

## Next implementation milestone

Build a small synthetic-pair pilot and verify correction targets before full
generation. This pilot is separate from final training/evaluation. The
existing gamma helper uses `x ** (1/gamma)` and both existing transform helpers
return uint8; composing them introduces intermediate quantization.

Shared float RGB operator, now implemented as `transform_rgb` (feature
preparation itself still does not generate pairs):

```text
x = RGB float in [0, 1]
T(x; gamma, red_gain, blue_gain) = clip(gain * x ** (1/gamma), 0, 1)
gain = [red_gain, 1, blue_gain]
gamma > 1 brightens; gamma < 1 darkens
```

For an unclipped distortion, inverse targets for that same operator are
`gamma_c = 1/gamma_d` and `gain_c = gain_d ** (-gamma_d)`, not generally
reciprocal gains. Clipping loses information; quantization introduces error.
Record both, and do not claim perfect restoration of clipped pixels. Do not
add an offset distortion outside the three-output model's representational
capacity. Treat image-encoded RGB transforms as a simulation, not a physical
camera model. Parameter ranges, scope/blending and clipping handling remain
to be specified; three variants per source are proposed in the thesis.

## Before full training-data generation

1. Establish source suitability and handling of known landmark failures.
   Preserve attempted/rejected counts; do not inherit old acceptance as
   proof that a newly versioned mask is correct.
2. Deduplicate originals and split before creating variants, preserving
   FairFace source split information. All variants of an original stay in one
   split. Use subject grouping where IDs exist; disclose unavailable identities.
3. Record split sizes and tuning boundaries. MST-E development/calibration use
   must remain disclosed; already inspected data are not wholly untouched.
4. Specify generation/correction scope and inference-equivalent input features.
   Model inputs must come from distorted images, not clean reference features.
   Distinguish masks used for generation/evaluation from inference masks.
5. Resolve group-dependent severity with the adviser. No official FairFace MST
   labels or validated broad-group rule exists here. A group-independent
   technical pilot is possible but does not implement tone-conditioned severity.

## Training and evaluation

Compare no correction, a simple baseline and the decision tree using held-out
reconstruction error, CIEDE2000 on a documented region, failures and latency.
The existing train helper's training-set parameter MAE is insufficient for
this comparison. Reference photos are relative reconstruction targets, not
calibrated true skin color. Android integration and expert assessment remain
later milestones.
