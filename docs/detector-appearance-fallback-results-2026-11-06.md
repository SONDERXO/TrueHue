# Zero-face detector appearance fallback: results

6 November 2026. Completed the [single frozen comparison](detector-appearance-fallback-protocol-2026-11-06.md).
A contrast-normalized detector-only fallback recovers some unavailable images,
with modest average error gains, but also enables one new harmful correction.
Keep this as an experimental candidate, not a runtime or Android change.

## Fixed change and execution

The saved 61 failures included 30 source-anchor and 18 crop-redetection failures,
all with zero detected faces. Reprocess only those 48 cases. If original-BGR
face detection yields zero boxes, retry once on a separate Lab-L CLAHE copy
(clip2/grid8), at the same confidence0.85. Accept exactly one box; do not retry
multiple detections. Image coordinates are unchanged. Crop pixels, landmarks,
parser/FaceOcc policies, object/class exclusions, 1000-pixel guard, original-RGB
statistics, frozen MST/trees/gate and native224 renderer are unchanged.

An initial metadata assertion incorrectly assumed no clean case among the48;
it stopped before decoding/output creation. Saved records showed one previously
failed clean case among them; the assertion/protocol were corrected before the
comparison. No outcome-based selection occurred. Other288cases, including23clean
cases and13other failures, use cached records/outputs byte-for-byte. This is not
a fresh independent cohort, complete clean rerun or new model fit.

48targeted attempts: 74 original detector calls plus50 enhancement-copy retries;
26 retries accepted one box.24parser and17CPUFaceOcc forwards;16final measurements.
All17visibility calls succeeded; one final measurement then failed the pixel guard.
No MST, correction, gate or target fits, and no threshold/appearance sweep.

## Availability and colour error

| Layer | Attempts | Available before | Available after |
|---|---:|---:|---:|
| Clean |24|23|23|
| Core |192|177|182|
| Stress |120|75|86|
| Total |336|275|291|

Recovered16/48target cases: five core and eleven stress. The targeted clean case
still fails;45total cases remain unchanged failure fallbacks. Of32remaining
target failures:22source-anchor,2crop-redetection,6no predicted facial-skin overlap,
and2pixel-guard failures. Recovery of detection does not ensure usable skin support.

Matched gated RGB MAE (0–255 codes) on original native reference support:

| Layer | Previous input-derived pipeline | Fallback candidate |
|---|---:|---:|
| Clean |0.02774|0.02774|
| Core |17.7450|17.4263|
| Stress |37.7131|36.2272|

Reference-region scoring availability remains23/24,184/192,115/120. All paths,
including unchanged failure fallbacks, retain the same reference-region denominator.
No reference mask is invented for the originally unavailable source, even where
its distorted variants recover. These available-region errors are not skin accuracy
or a failure penalty. Native224 results must not be pooled with earlier256crop scores.

Candidate equal-key gated RGB MAE:0.02659/17.3312/36.0814 by layer;
relative CIEDE2000 means:0.03013/6.6957/14.3660. Ungated core/stress RGB MAE:
7.4392->7.1205 and38.1722->36.6863. No improvement claim beyond this exposed,
synthetically distorted sample and common imperfect reference support.

The gate acts on15newly available cases:4core and11stress. One recovered core
case is withheld. Clean preservation stays22/23measurable photos exact no-op;
the unavailable clean case stays unchanged too. Reference-region harm counts
remain1clean/2core/0stress, but that does not capture the new harm below.

## New harmful correction retained

A recovered mild-warm variant of the originally unavailable source has no original
reference mask, so it is excluded from reference-region means. Its full-scene
RGB error worsens2.01958->2.05803; core full-scene harm count increases2->3.
The gate logit is+0.33869; controls are gamma1.42785, red1.14691, blue0.84319.
On its own62selected native pixels, error rises1.1129->32.2258; that diagnostic
region is the candidate prediction, not human-confirmed skin truth. This records
an enabled correction error, not a reason to erase the case or fabricate support.
The sparse forehead/face patch and visible local darkening also concern visual review.

The other new gated corrections improve or preserve the full-scene RGB metric;
this does not establish good-looking output, complete facial coverage or material
protection. Full-scene means include mostly uncorrected background/clothes/chart:
core22.80362->22.80163, stress59.44117->59.42668. Their small changes are context
diagnostics, not facial success scores. Stress full-scene harm remains0.

## Visual scope and verification

Viewed all48targeted original/input/predicted-mask/old-output/new-output boards,
including all32unrecovered cases. Recovered masks can remain fragmented or cover
only parts of cheeks/forehead; glasses/reflections and extremely dark/clipped
features prevent confident material judgement. Corrected islands and strong
residual casts remain. No dense skin/object labels were added or inferred.

On reference-available new gated cases,24core and832stress native pixels change
outside the original mask (3core/11stress cases). This is neither verified skin
gain nor an object-error count. Existing parser/visibility exclusions are preserved,
but they cannot prove absence of object or facial-hair leakage in new masks.
No mask union/fill, smoothing or relaxed guard was used.

Verified288untargeted records and saved outputs exactly equal the prior pipeline;
74detector trace/input/appearance-copy hash replays;17visibility-service replays;
291feature/MST/gate/portable-control/native-projection checks and1680saved output/
metric replays.23cached clean records match the original pipeline; these are
consistency checks, not new inference.42focused tests passed in5.47seconds,
including two new fallback tests for no retry on existing/multiple detections,
exactly-one acceptance and original-image preservation. Scientific admission
flags remain false. No fitting or new subjects during verification.

Private outputs: detector_appearance_inference_v1, detector_appearance_merged_v1,
detector_appearance_correction_v1, detector_appearance_assessment_v1,
detector_appearance_comparison_v1 (review_PRIVATE.html and all48boards).
Scripts518–523 and detector_appearance_fallback.py preserve the isolated candidate;
previous outputs/model remain unchanged.

This closes one targeted repair. Do not adopt it on availability alone: the newly
enabled harmful gate/control action and incomplete/uncertain support still need
resolution. The next recommended evidence step is a saved-feature/route diagnosis
of that new false correction before choosing another intervention. No automatic
retry, threshold change, fit, cohort expansion or review task is activated.
Research-only/noncommercial/citation/no-redistribution conditions remain. No
runtime/Android change, contact, upload, sharing or submission occurred.
