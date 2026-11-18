# Actual skin-patch measurements — 6 November 2026

The user's completed export was found in the private v2 review directory and
imported, with exact schema, six-case membership, reviewer, manifest/image hashes,
status, integer coordinates and simple nondegenerate polygon checks. All six
photos are marked; 36 polygons cover a union of3156native pixels. Overlaps are
counted once. No annotation was invented or modified.

Private final measurements: `outputs/stellenbosch_skin_patch_import_v2/`.
Original export bytes are preserved as `actual_export_PRIVATE.json`. Raster
contract: native integer polygon union using OpenCV fillPoly, boundary pixels
included. Original native BGR pixels enter the retained OpenCV Lab/ITA formula.
No resizing or appearance enhancement enters these measurements.

## What the actual references show

| Comparison | Available paired photos | User-selected pixels | Selected by automatic mask |
| --- | ---: | ---: | ---: |
| Frozen baseline | 5 | 2551 | 987 (38.7%) |
| Isolated ResNet34 | 5 | 2551 | 1558 (61.1%) |

The sixth image has605user-selected pixels but no automatic prediction because
of the retained landmark failure. It is not treated as all-negative and does not
enter the paired2551pixel denominator. All six manual colour measurements are
arithmetically available, which does not qualify them for training.

All six original/patch/baseline/ResNet34 boards were inspected. The actual marks
include visible neck regions despite the face-only instruction. Preserve those
regions and the user's skin interpretation; do not relabel, silently trim them
or call their omission a face-mask error. Therefore the table measures selection
of the user's actual patches, not face-only recall. Several patches also lie
close to facial-feature and beard boundaries in these small images; no dense
material-purity or full-face truth claim follows from the outlines.

The glasses case and warm fragmented case gain substantial selected patch
coverage with ResNet34; the dim cool case remains sparse. Broader automatic
coverage still does not establish beard/object protection, whose regressions
remain in the completed sparse-point experiment. This skin-only patch review
cannot measure unwanted inclusion outside its polygons.

Manual patch ITA values in review order are63.576, -58.9142,83.2078,-72.5989,
84.3756 and-81.8176degrees. These are image/region-dependent original-colour
statistics, not MST labels, intrinsic skin colour or six independent subjects.
Different patch locations and face/neck mixture prevent a simple accuracy or
within-person lighting conclusion. Review04and06share a publisher key; no new
independent people are created by patches.

## Guard correction and verification

The first import package (`stellenbosch_skin_patch_import_v1`, script475)
correctly recorded geometry/overlap but accidentally inherited the automatic
1000pixel default for statistics. It returned unavailable colour measurements.
It is retained as an intermediate record, not the final measurement result.
Script476writes the separate v2 package with an explicit one-pixel arithmetic
minimum for this manual-reference diagnostic. That setting is not a scientific
adequacy threshold, automatic guard reduction or training-admission rule. The
automatic pipeline and its1000normalized-pixel guard are unchanged.

Fifteen new strict-import/geometry/raster tests pass in0.48seconds. Six native
Lab means were independently recomputed from original pixels and match retained
statistics exactly after rounding. Final artifact hashes and all bound source,
mask and prior package hashes were checked; earlier evidence remains unchanged.
No new inference, calibration, tree fit, admission, runtime change or sharing.

## Decision

The reference measurement diagnostic is complete; do not request another
automatic repeat review or tune masks to these exposed regions. We now have
actual human-selected-region statistics and quantified automatic coverage
limitations. We still do not have a qualified real contextual MST cohort or
person-held correction experiment. The six development references are not a
calibration substitute. Retain the November8 paper-scope decision: further work
should assemble the supported conference findings and limitations, while any
new real-data fit requires substantive justified measurement/cohort evidence.
No final paper-scope change, adviser approval or conference submission is assumed.

The dataset, original user polygons, source IDs, measurements and boards remain
private under research/noncommercial, citation and no-redistribution terms.
