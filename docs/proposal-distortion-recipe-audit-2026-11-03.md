# Proposal distortion recipe audit — 3 November 2026

## Finding

The printed Table2 values are not a complete executable recipe. Under the
existing direct-exponent interpretation they also do not guarantee increasingly
strong underexposure across the light/medium/dark settings. Do not start training
and describe those properties as already established.

Verified proposal locations: PDF38/printed31 defines gamma<1 as brightening;
PDF60/printed53 describes simulated underexposure, overexposure and colour casts;
PDF62/printed55 lists Table2 values; PDF63–64/printed56–57 retains three correction
outputs and tone-dependent synthetic severity. These statements require an
explicit implementation interpretation. This is not a reason to abandon the
original-reference synthetic restoration goal.

## Fixed diagnostic

Script402 uses a generated neutral RGB ramp, not photos or labelled subjects.
It applies the existing three-variant recipe for each of the three existing
severity settings: nine combinations, no sweep or settings search. Each formula
is independently recomputed and checked. Exposure and colour variants are an
engineering decomposition, not a verbatim requirement of the paper.

The exact experimental order is direct gamma, contrast around 0.5, brightness
offset divided by255, additive red/blue offsets divided by255, clipping and
RGB8 rounding; then supplied alpha blending and another RGB8 rounding. Contrast
is interpreted as a percentage multiplier. This order and slider interpretation
are inherited engineering choices, not established image-editor equivalence.

| Setting | Exposure-only result for neutral input RGB[64,64,64] | Approximate recovery error, exposure-only | Combined error |
|---|---|---:|---:|
| Light | [56,56,56] | 3.956 | 4.269 |
| Medium | [59,59,59] | 6.109 | 6.552 |
| Dark | [65,65,65] | 7.388 | 8.070 |

Errors are average absolute RGB8 channel code differences over positive-alpha
pixels on this ramp, after target-aware local three-control fitting. They are
not model predictions, skin-colour measurements, CIEDE2000 or real-photo results.
The labels identify recipes, not the skin tone of generated pixels. Colour-only
residuals were also retained:1.610/2.685/3.763. All nine cases remain saved in
`outputs/proposal_distortion_recipe_audit_v1/results.json`, including clipping,
fitted parameters, bounds and residuals. Nine target fits, zero tree/MST fits,
zero photos, admissions or runtime changes.

## Recommended decision before data generation

Keep ITA + calibrated MST + facial statistics and the three correction outputs.
Document a revision to the synthetic exposure formula so its tested pixel-level
behaviour matches the intended exposure scenarios. Specify underexposure and
overexposure separately rather than assuming one Table2 row supplies both.
Retain the current Table2 audit as evidence; do not silently switch to reciprocal
gamma or describe a changed formula as unchanged printed settings.

This is a proposed next step, not an adopted formula, a new parameter search,
or authority to process a photo batch. The user should decide whether to permit
that documented departure from Table2 before it is implemented. Adviser/panel
agreement is not claimed, and academic change documentation remains necessary.
If exact printed settings are retained instead, describe their measured behaviour
honestly rather than promising monotonic underexposure severity.

Final source/support admission, identity grouping, compatible MST evaluation and
training/evaluation adequacy remain unresolved regardless of that choice.

Verification:49 focused tests passed in3.60seconds across the existing
three-variant recipe, Table2 contract, direct gamma and new blended target
construction. No new full-suite run is claimed.
