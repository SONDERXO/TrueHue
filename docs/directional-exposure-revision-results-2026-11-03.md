# Directional exposure revision — 3 November 2026

The user approved developing a documented departure from Table2, and explicitly
reaffirmed that changes outside the paper must be recorded. This authorises the
experimental implementation below, not final recipe adoption, model training,
dataset admission, runtime replacement or thesis-panel approval.

## Paper and implementation differences

Verified source: unchanged `Thesis Proposal Document.pdf`, PDF38/printed31
(direct gamma interpretation), PDF60/printed53 (under/overexposure and colour
errors), PDF62/printed55 (Table2), PDF63–64/printed56–57 (three outputs and
category-dependent severity). See the proposal scope validation for checksum.

| Item | Paper / existing interpretation | New experimental implementation |
|---|---|---|
| Exposure direction | Table2 has one row of values per group; executable under/over formula unspecified | Separate explicit underexposure and overexposure scenarios |
| Gamma | Table2 g=.85/.70/.60; paper describes direct exponent below1 as brightening | Effective direct exponent1/g for underexposure, g for overexposure; this is an explicit interpretation change |
| Contrast | Table2 +5/+8/+10; pivot/formula unspecified; earlier code used0.5 | Keep magnitudes as percentages; pivot1 for underexposure,0 for overexposure to preserve direction |
| Brightness | Table2 -20/-35/-45 | Retain negative offsets for underexposure; use positive magnitudes for overexposure, divided by255 |
| Colour | Cyan-red/yellow-blue slider values, conversion unspecified | Retain existing additive red/blue conversion divided by255; green unchanged before clipping |
| Scenarios | Exact decomposition not specified | Clean, colour-only, exposure-under, exposure-over, combined-under, combined-over; not an adopted training distribution |
| Region and rendering | Exact alpha/clipping/rounding order not specified | Supplied alpha; transformed float clipped once, blended, then RGB8 rounded once; zero-alpha pixels exact |
| Targets | Three correction outputs moving input toward original photo | Existing experimental three-control local blended fit; approximate residuals disclosed, never assumed exact inverse |

The original-reference photographic-restoration goal and ITA + calibrated MST +
facial statistics → decision-tree gamma/red/blue outputs are retained. These are
synthetic scenarios, not evidence that a particular skin group experiences these
numeric errors in real smartphone photography. Group labels identify severity
settings here; generated pixels have no subjects or MST labels.

## Exact formula and direction guarantee

Let x be encoded RGB/255, g the Table2 gamma, c its contrast/100, and
b=abs(Table2 brightness)/255. Before colour shifts and clipping:

- Underexposure: `(1+c)*(x**(1/g)-1)+1-b`.
- Overexposure: `(1+c)*x**g+b`.

For x in[0,1], the underexposure result is at most x and the overexposure result
is at least x. Their light→medium→dark settings are ordered in the same direction.
Clipping, fixed alpha blending and monotonic rounding preserve this weak order.
Equality is possible because clipping/quantisation can flatten differences.
These guarantees apply to exposure-only channels, not all channels after colour
shifts, perceptual lightness, or measured tone groups. Actual exposure severity
on photographs has not been validated.

## Fixed evidence and important limitation

Module: `src/distortion_generation/directional_exposure_recipe.py`.
Script403 saves generated arrays, parameters, clipping and residuals under
`outputs/directional_exposure_recipe_v1/`. One neutral RGB8 ramp, three severity
settings, six scenarios each:18 saved probes.15 local target fits, three exact
clean shortcuts; zero photos, model inference, tree/MST fits or admissions.

| Setting | Exposure-under target-fit error | Exposure-over error | Combined-under error | Combined-over error |
|---|---:|---:|---:|---:|
| Light | 8.362 | 7.289 | 8.567 | 7.516 |
| Medium | 19.343 | 15.684 | 19.605 | 16.112 |
| Dark | 29.860 | 23.665 | 30.231 | 24.296 |

Errors are average absolute RGB8 channel codes over all positive-alpha pixels,
including faded edges. They are target-aware local fit residuals on generated
data, not automatic predictions, CIEDE2000 or accuracy percentages. Clean error
is0 in all settings. Colour-only errors1.610/2.685/3.763 are retained.

**Direction is fixed, recoverability is not.** Strong exposure settings destroy
substantial ramp detail: dark exposure-under clips5,184 of11,904 selected channel
samples; dark exposure-over clips4,512. Colour/combined clipping and all residuals
remain in JSON. Do not describe this as a better correction model or a training-
ready recipe. No tuning, replacement or filtering followed these results.

## Verification and status

37 focused tests passed in2.59seconds across the new recipe, previous recipe,
direct gamma and blended targets. Tests cover every RGB8 level at alpha0/.05/.5/1,
direction and severity ordering, exact clean/outside-support preservation,
source immutability, independent formula arithmetic, additive colour conversion
and invalid scenario rejection. No new full-suite run is claimed.

All38 persisted arrays (reference, alpha,18 inputs and18 restored outputs)
round-tripped exactly. The seven script399 source hashes and seven parent
manifest hashes remain unchanged. Earlier recipes/evidence are preserved;
neither runtime nor submitted proposal changed.

Before real data generation, decide how recoverable distortions versus severe
clipping stress cases should be represented and evaluated. This result establishes
directional arithmetic only. No sample proportions, residual acceptance thresholds
or final distortion distribution have been invented. Source/support admission,
identity grouping, matching MST and evaluation adequacy still need resolution.
