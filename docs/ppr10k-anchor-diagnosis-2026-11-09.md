# PPR10K anchor miss diagnosis — 9 November 2026

## Finding

Saved evidence identifies a concrete input-geometry concern, but cannot establish
why each detection failed. **All four successful photos are 360-wide × 540-high;
all four misses are 540-wide × 360-high.** Script703 stretches each original to
256×256 before the anchor detector, without preserving aspect ratio.

That widens portrait faces by 1.5 relative to their original proportions and
narrows landscape faces by 2/3. This is existing research preprocessing behavior,
not a new claim of a detector implementation bug. Shape, scene content, pose and
face size are confounded in these eight sources; the orientation association
does not prove causation or population performance.

## Saved-record diagnosis

Script705 verified historical metadata and the completed screen's verification
binding, then mapped each existing source-only polygon bounding box into the
square anchor frame. These are approximate face-size proxies, not annotated
detector boxes, newly selected crops or inference features.

| Pair | Native frame W×H | Approximate polygon W×H at square256 | Existing outcome |
| --- | --- | --- | --- |
| 787_0 | 360×540 | 62.58×37.93 | Available |
| 330_0 | 540×360 | 19.44×32.71 | Zero anchor faces |
| 767_0 | 360×540 | 58.31×45.51 | Available |
| 1117_0 | 360×540 | 25.60×23.23 | Available |
| 1188_0 | 540×360 | 15.64×25.60 | Zero anchor faces |
| 990_0 | 360×540 | 24.18×19.44 | Available |
| 904_0 | 540×360 | 20.39×39.82 | Zero anchor faces |
| 455_0 | 540×360 | 21.81×41.96 | Zero anchor faces |

Small size alone cannot explain the pattern: the successful 990_0 proxy is smaller
in height than several failed proxies. This is descriptive, not a controlled
size experiment. Prior visual observations include profile/downward faces in
330_0 and1188_0, eyewear/multiple people in904_0, and styling/rollers in455_0.
They are plausible contributors, not proven causes or blanket exclusions.

The helper configures YuNet at .85, NMS .3 and topK5000 and returns only clamped
integer boxes, sorted by area. Detector scores, rejected candidates and raw
landmarks are not retained by that API. The original zero-box records therefore
cannot distinguish threshold rejection from absence of candidates. No saved
confidence values can be reconstructed by inspecting the files. The crop bridge,
skin parser, landmarks and FaceOcc were never reached on these four failures;
their masks cannot be blamed for the anchor failure.

## One bounded comparison selected for proposal

Change only the anchor detector's input representation from stretched square256
to the existing RGB8 source at its native 360×540/540×360 dimensions. Keep the same
YuNet model, .85 confidence, .3 NMS and topK5000. Test all eight once, not just the
four misses. This jointly changes input sampling and aspect preservation; do not
claim it isolates which component caused any improvement. No resolution ladder,
letterbox alternative, confidence sweep or enhanced input is bundled with it.

This is **detector-only**, not a new full-pipeline run. Native boxes cannot be
fed directly to the old 256-coordinate crop bridge. Any later bridge integration
requires an explicit coordinate contract and support/measurement compatibility
checks. No old calibration, masks or correction costs are automatically reused.

See the [fixed protocol](ppr10k-native-anchor-comparison-protocol-2026-11-09.md).
It is prepared but not executed. The user's approval for diagnosis and a proposed
bounded change is not treated as an instruction to run an unreviewed variant.

## Verification and boundary

Receipt: `outputs/ppr10k_anchor_diagnosis_v1/diagnosis_PRIVATE.json`, eight geometry
rows and bound metadata/code hashes. Algebraic aspect-ratio checks pass; original
bindings remain unchanged. No image byte reads, detector/parser/FaceOcc forwards,
correction fits, holdout access, runtime changes, downloads or contacts occurred.
All prior outputs remain preserved. This is diagnosis, not model improvement.
