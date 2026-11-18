# Fixed native-input YuNet anchor comparison — 9 November 2026

Status: proposed, NOT executed. One detector-input representation change; no
training, parser or mask experiment. Existing acceptance gates remain unchanged.

## Membership and preflight

Use the exact eight original source TIFFs in the original frozen sample order:
787_0,330_0,767_0,1117_0,1188_0,990_0,904_0,455_0. All are already exposed.
No targets enter inference. No acquisition, replacement photos or extra examples.
Use a new exclusive output directory, preserving partial artifacts on failure.

Before any forward, bind the historical sample, original source hashes, previous
screen/verification, this protocol, detector wrapper, OpenCV version and exact
existing YuNet model. Verify all eight inherited source hashes/dimensions/types/
profiles and the model's prior bound hash. Do not permit automatic download.
Decode sourceRGB16 and convert with round(source/257), then RGB-to-BGR as in
script703. No CLAHE, sharpening, exposure adjustment, crop or orientation search.

## Exactly one candidate construction

- Existing model; full native image input size, either360×540 or540×360.
- Confidence .85, NMS .3, topK5000; no other thresholds or parameter alternatives.
- Exactly one YuNet detector call per source (eight total), no retry if it fails.
- Capture returned raw candidates (including score/keypoints when returned) and
  derive clamped integer boxes with the existing helper's filtering/sorting logic.
  Do not lower the threshold to expose rejected candidates. Original rejected
  square256 candidates remain unknowable; do not invent their scores.
- If OpenCV/model cannot accept the declared native size, preserve that failure
  and stop; no padding/resizing fallback. Distinguish API errors from zero faces.
- Zero skin-parser, landmarker, FaceOcc, MST or correction-model calls. No target
  parameter fit, distortions or correction rendering. No app changes.

## Comparison and review

Reuse saved square256 detections as the comparator; do not rerun them. Map those
saved boxes back to native coordinates using their original separate x/y scales
for display only. Candidate boxes remain native coordinates. Save overlays for
all eight, with the historical source-only polygon shown as a locator, not skin
truth or a proposed crop. Review which person is selected without viewing target
edits or correction quality.

Record zero/one/multiple faces, each score and box, historical-face correspondence
and unintended detections. Keep the existing exactly-one-face eligibility rule:
do not choose the historical person manually from multiple detections. Group
frames and count repeated conditions correctly; no new person-independence claim.

Technical advance requires preserving all four earlier correct single-face
detections and recovering at least one earlier miss as the correct single face,
with no newly observed definite wrong detection. This is a local feasibility
criterion, not a new correction acceptance gate or dense detector benchmark.
Any remaining/multiple/wrong detections remain failures. Sparse manual locators
cannot certify detector precision across arbitrary images.

Verify source/model hashes unchanged, raw-record-to-box filtering and coordinate
calculations independently without repeating inference. Review every new overlay.
Report all eight outcomes even if the criterion fails. Do not tune thresholds,
try another resolution, switch detector or drop the difficult photos afterward.

## Interpretation and stop

A better result would support native/aspect-preserving input as a preprocessing
direction, not prove which sampling/aspect factor mattered. A worse result would
close this candidate. Either way, stop after this comparison. Even success would
not qualify automatic skin/neck support, MST, source-target registration, learned
correction, training admission or runtime integration. A separate coordinate-
compatible downstream plan would be needed before further model calls.

All photos/derivatives remain private under existing terms. Final eight-group/
24-photo holdout stays byte-unread. No contacts, uploads, account/form submission,
commit or push follows from this protocol.
