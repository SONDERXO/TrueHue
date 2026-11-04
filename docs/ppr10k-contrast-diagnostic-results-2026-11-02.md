# One contrast-control comparison: strong wedding improvement, mixed indoor results

2 November2026. User explicitly authorised the proposed fourth-control
experiment. **Adding contrast improves four of six check-block colour errors,
especially all three wedding faces; two indoor cases worsen.** Keep this as an
experimental candidate, not an adopted replacement or a finished model.

Gallery: `outputs/ppr10k_contrast_diagnostic_v1/review.html`.
Script394; focused operator tests in `tests/test_ppr10k_contrast_diagnostic.py`.

## What was fixed

Same six exact source/editor-A pairs, saved float64 RGB16/RGB8-normalised sRGB
inputs, selected faces, approximate polygons and8x8 fit/check masks as script392.
Original source, three-control results, diagnosis and delivery snapshots preserved.
No new photos, masks, registration, parser/FaceOcc inference or replacement.
The masks include eyes/lips/makeup and may miss face edges; they exclude neck.
Diagnostic hard boundaries do not evaluate or replace adopted face+neck blending.

Protocol SHA256 `424193d25deb266278843c2abbe2a815bc3c88b286acabb74a7ee582cc1fc855`
was frozen before all six fits. One candidate only:

`clip((0.5 + contrast * (source**(1/gamma) - 0.5)) * [red,1,blue], 0,1)`.

Contrast1 reduces mathematically to the baseline operator. Gamma/red/blue bounds
remain[0.25,4], contrast[0.5,2], encoded midpoint0.5. One identity-start
least-squares run/photo, squared-sRGB fit-block objective, tolerances1e-12 and
maximum2000 evaluations. No bounds, objective, midpoint, start or model sweep.
All six converged without active bounds; global optimality is not proved.

## Results, including regressions

Mean relative CIEDE2000 on the saved check blocks, lower means closer to editor A.
These are image-appearance errors, not instrument-measured skin colour.

|Frame|Three controls|Four controls|Contrast|Clipped face channel samples: three -> four|
|---|---:|---:|---:|---:|
|1398_0|5.610|1.737|1.283|29 ->149 /11469|
|1398_1|5.310|1.598|1.296|35 ->119 /10854|
|1398_2|6.176|1.862|1.277|99 ->365 /12144|
|1487_0|2.968|2.997|0.995|0 ->0 /1884|
|1487_1|5.014|5.106|0.885|0 ->0 /3399|
|1487_2|3.680|3.255|1.051|0 ->25 /3630|

Equal-weight mean of the six image means:4.793 ->2.759 (42.4% reduction relative
to the saved three-control approximation). Only4/6 improve; wedding gains dominate
this average. Related photos from two groups are not six independent subjects.
No acceptable-error threshold, statistical significance or population accuracy
is asserted. RGB MAE, DeltaE mean/median/p95, clipping and signed residuals remain
in `results.json` for fit/check/all regions.

All six squared-RGB fitting errors decrease, but colour difference can worsen:
the fit objective is squared RGB, not CIEDE2000. In1487_1, check RGB MAE improves
7.986 ->7.611 while mean relative DeltaE worsens5.014 ->5.106. This is retained,
not used to justify a different objective run.

Clipping means out-of-range float channel samples before final clipping, not
merely final values equal0/1. This definition is identical for both operators
here. Earlier script393 endpoint counts used a different definition and must
not be compared directly with these clipping counts. Four photos gain clipping;
no claim that contrast preserves all detail. A target's intended black/white
values and possible lost information need consideration before interpreting it.

## Visual and residual findings

Assistant inspected all six four-column boards:

-1398_0/1/2: four-control faces are substantially closer visually to editor A;
the prior pink cast and flat tonal appearance reduce. Mean a* residuals change
4.08/3.66/4.60 ->0.01/-0.02/0.27. Darkest/brightest source-green quartile L*
errors previously about+4/-4 are now approximately+0.2 to+0.5. Lip/highlight and
local differences remain, with increased clipping disclosed above.
-1487_0: contrast near1 produces little visible improvement; check errors
slightly worsen. Small-face, hair and lighting concerns remain.
-1487_1: fitted contrast is below1, not above1 despite the earlier intensity
pattern. Pink residual increases (a*0.10 ->3.24), and dark/light residuals worsen.
This is evidence against assuming one contrast control fixes every scene.
-1487_2: modest check-error improvement; local warmth/shadow and face-edge
differences remain. New clipping is recorded.

Approximate regions, makeup/mixed features, tiny face detail, source quantisation
and unverified pixelwise alignment can affect these differences. These results
do not isolate all error as operator capacity. Enlarged crops use nearest-neighbour
display. Unchanged neck/background and hard polygon cutouts are temporary
diagnostic rendering, not production correction outputs.

## Verification and decision

Six outputs independently replay exactly from the explicit four-control formula;
stored check metrics/clipping counts recalculated; outside-polygon float pixels
unchanged. Protocol timestamps precede saved fits; all baseline artifact hashes
still match. Three focused candidate tests cover neutral-contrast equivalence,
hand-computed midpoint/clipping and synthetic four-parameter recovery. Combined
with existing operator tests:17passed/1.51s. No full-suite run claimed.

Six target-aware oracle fits occurred, zero MST/calibration or correction-tree
fits. This is not an automatic predictor: each target was used to choose its own
adjustments. Same-photo check blocks are not new-photo validation. Both groups
remain development-exposed publisher-validation photographs, with existing
TrueHue reserved roles unchanged.

The authorised single comparison is complete. Contrast is promising for one
represented editing style, with measured regressions and clipping costs. It is
not adopted as a fourth decision-tree output or Python/Android runtime change.
Do not expand the batch, tune these six, pick only the wedding group for training,
or treat fitted parameters as admitted correction labels automatically.
ITA + calibrated MST + facial statistics and the decision-tree family remain
retained; reliable mapping/automatic correction are still unfinished.
No submitted thesis edit, formal letter or panel approval follows from this
experimental authorisation. Dataset terms and prior source limitations remain.
