# Native-anchor coordinate preparation — 9 November 2026

## Outcome

User requested the recommended next work after the fixed native-anchor result.
Reviewed the existing face-selection scope and implemented an isolated native-
coordinate bridge with generated-image checks. No further private-image/model
processing was started, and the failed eight-source comparison remains failed.

`docs/implementation-plan.md` specifies gallery input with a single face; the
current measurement service requires exactly one detected face. Adding automatic
group-photo subject selection is therefore not a prerequisite established by that
plan. However, one detected face is not proof that a scene contains only one
visible face: 904_0 demonstrates that distinction. Its child detection still
fails the fixed historical adult-selection task. Do not redefine that result,
remove it from the denominator, or describe native detection as adopted.

## Concrete implementation

New experimental `src/skin_masking/native_anchor_bridge.py` provides the explicitly
named `crop_native_anchor(image, native_box=...)` entry point. It accepts integer
coordinates measured on the original image, uses the existing 1.5-times context
policy, takes an exact square source slice and shifts it at image edges without
padding. Invalid or unfittable crops fail; there is no retry or alternate margin.

The report explicitly identifies original-native coordinates and a new version.
It contains bounds, source dimensions, scale and edge shift needed for the existing
normalized-to-native mask/alpha projection routines. The old 256-coordinate bridge
is unchanged. New detections must never be fed to its 256-coordinate input by
assuming the coordinate systems coincide on rectangular photographs.

The new helper neither detects nor selects a face, invokes any model, creates a
skin mask, changes protection or fits an MST/correction model. It is not imported
by application runtime or current experiment scripts. Compatible geometric fields
do not imply compatible calibration, fitting costs or validated correction;
report flags explicitly withhold those claims.

## Verification

Command:

```powershell
venv\Scripts\python.exe -B -m pytest tests/test_native_anchor_bridge.py tests/test_fixed_face_input_bridge.py -q -p no:cacheprovider
```

**19 tests passed in 0.70 seconds**: eleven new generated-image cases and eight
existing bridge cases. Checks cover orientation-independent native geometry,
known exact source slices, no source mutation/aliasing, edge shifting without
padding, binary mask projection at known locations, alpha/protected-pixel
invariants, coordinate parity when the source really is256-square, and rejection
of invalid or oversized crops. These are software checks, not extra research
photos or detector/correction accuracy results. No broader suite/device run is
claimed for this isolated preparation.

## Remaining decision before further real-image processing

A downstream feasibility design would have to bind this new coordinate contract,
retain all eight earlier outcomes, and distinguish an original single-face scope
from a post-hoc favourable subset. It must preserve 904_0's selection failure and
must not silently change to the child, use historical manual crops as inference
inputs, rerun only the seven favourable faces, or lower gates to adopt native
input. The completed detector protocol authorises no downstream model calls.

Any separately reviewed applicability study needs source-only eligibility rules
fixed before correction outcomes and an honest evaluation design. Existing photos
remain exposed development evidence. Mask quality, compatible ITA/MST, operator
limits, learning decisions and independent evaluation remain unresolved.

No new next model experiment has been selected or run. This work removes a
coordinate implementation gap; it does not constitute correction-model progress
or satisfy the user's working-model objective. All original artifacts and prior
source hashes are preserved. No source-image byte reads, detector/parser/
landmarker/FaceOcc calls, fits, downloads, final-holdout reads, runtime changes,
contacts, uploads, commits or pushes occurred.

- [Fixed native detector result](ppr10k-native-anchor-comparison-results-2026-11-09.md)
- [Original implementation scope](implementation-plan.md)
- [Completion requirements](completion-specification-2026-11-09.md)
