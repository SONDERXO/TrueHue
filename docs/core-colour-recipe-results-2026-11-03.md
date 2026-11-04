# Normal colour-error candidates — 3 November 2026

User authorised defining/checking normal colour-error examples on generated
images after the exposure/core/stress separation. The bounded check is complete.
This establishes an experimental recipe and its arithmetic behaviour, not
training admission, real-photo validity, a final sampling distribution or panel
approval. Submitted proposal and runtime are unchanged.

## Recipe and explicit differences from the paper

The proposal's Table2 (PDF62/printed55) gives cyan-red and yellow-blue slider
values but not an executable conversion. Earlier experimental code interpreted
them as additive red/blue shifts, which clip on full-range generated ramps.
Those examples and all15 earlier clipping stress cases remain unchanged.

This new normal-candidate recipe uses attenuation instead:

- Cool: red gain `1-abs(cyan_red)/255`; green and blue gains1.
- Warm: blue gain `1-abs(yellow_blue)/255`; red and green gains1.
- Corresponding light/medium/dark gains are249/255,245/255,241/255.
- Colour-only exponent1. Combined underexposure exponent1/g; overexposure g,
  retaining the previously declared .85/.70/.60 gamma magnitudes.
- Apply power, then channel gain, then supplied alpha blending, then a single
  RGB8 rounding. No additive brightness, extra contrast or channel offsets.

Reducing red or blue changes their relative balance without increasing any
channel above range. This also reduces brightness: it is not a pure chromaticity
change, calibrated white-balance simulation or equivalent to the paper's
additive sliders. The warm direction is an explicitly added counterpart to the
previous cool-direction examples. Combined overexposure plus attenuation need
not brighten every channel; direction guarantees apply to the exposure component.

These are documented development interpretations. Keep the photographic-
restoration goal and ITA + calibrated MST + facial statistics → decision-tree
gamma/red/blue outputs. Existing clipping-stress evidence is not replaced by
these easier examples. The proposal's scope/limitations remain as verified in
`proposal-scope-validation-2026-11-03.md`, with unchanged source-PDF checksum.

## Fixed check and saved results

Module: `src/distortion_generation/core_colour_recipe.py`.
Script405 writes its protocol before fitting: three severity settings × two
casts × three exposure options(none/under/over), exactly18 probes plus one clean
control. No sweep, replacements or adjustment after seeing residuals.

Input is one fixed16×256 generated chromatic ramp with channels R=x,G=255-x,
B=(37*x)%256; application alpha is reused from the preceding generated check.
This is not a face, actual skin, independently sampled subjects or tone coverage.
The group names identify severity settings only.

Evidence: `outputs/core_colour_recipe_v1/` contains protocol, JSON/CSV results,
40 arrays, source checksums and artifact checksums. All18 probes have zero
forward clipping and remain core candidates, not automatically admitted cases.
The clean image and its neutral correction remain bit-identical.

| Severity setting | Colour-only target-fit error, cool/warm | Combined-under error, cool/warm | Combined-over error, cool/warm |
|---|---|---|---|
| Light | 0.008 / 0.009 | 0.059 / 0.059 | 0.063 / 0.065 |
| Medium | 0.015 / 0.013 | 0.151 / 0.149 | 0.148 / 0.147 |
| Dark | 0.022 / 0.019 | 0.273 / 0.269 | 0.220 / 0.219 |

These are average absolute RGB8 channel code differences over positive-alpha
pixels after target-aware local three-control fitting. They are not learned
predictions, CIEDE2000, percentages or real-photo performance. A different
generated reference was used here than the preceding neutral ramp, so these
numbers are not a controlled comparison proving superiority to earlier recipes.
All18 fits converged with full-rank Jacobians and no active parameter bounds.
There were no outside-support mismatches.

Clipping-free is not lossless. RGB8 quantisation produced384 new endpoint
channel samples summed across the18 probes; these are repeated diagnostic
samples, not unique facial pixels or a recovery percentage. Boundary blending
also prevents assuming the simple unblended inverse is an exact target.

## Verification and stopping decision

98 focused tests passed in2.51seconds across the new recipe, role rules, existing
recipes, Table2 contract, direct gamma, old/new targets and seamless blending.
This is not a full-suite run. Tests cover both casts and all exposure options
on full-range RGB inputs, fractional/protected alpha, clipping, source immutability,
channel effects, ordered colour severity, independent formula arithmetic,
target construction and invalid recipe rejection.

18 independent arithmetic replays and40 exact array roundtrips passed. All24
parent cases remain saved and were not refitted. Parent artifact/source hashes
and the script399 seven source/seven parent-manifest hashes remain unchanged.
18 new local target fits and one clean shortcut were performed; zero photos,
ML inference, tree/MST fits, admissions, runtime changes or contacts.

Stop this generated recipe check. Normal exposure, colour and combined
development candidates now have explicit arithmetic definitions, alongside
clean/stress roles. This does not activate real-image generation or final
training. Next substantive work is a single integrated recipe/admission plan
using these saved definitions: actual source/support/person eligibility,
matching MST inputs, final case proportions and justified evaluation criteria
remain unresolved. Do not repeat formula sweeps, process a new photo batch or
fit a tree automatically. All failures and stress cases must remain reported.
