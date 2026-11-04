# FaceOcc veto: one diagnostic completed

1November2026. User authorised one fixed FaceOcc comparison after aligned-input
inspection. Scripts368–370 completed the frozen protocol with no tuning, second
checkpoint, crop change, replacement images, calibration or correction-tree fit.

**Result: useful neck/clothing and face-covering removal, but not reliable
actual-skin measurement. Not adopted; stop this diagnostic cycle.**

## What ran

All25original attempts retained:17saved aligned inputs received one CPU forward
each; eight original failures remained without retry. Pinned weights and fixed
MediaPipe/template bridge were used. InputRGB/ImageNet normalisation, logit>0,
source-validity masking and nearest inverse mapping were frozen before prediction.
Candidate = preferred nostril-excluded parent measurement AND mapped visible face.
The rejected landmark-outline intersection was not used.

Candidate contract:
`03307d45c74807a4d85a534b826ee069807e20a0bb669c6faff4c8f934c69bc8`.
Active measurement remains parent1bdef31c; neither this candidate nor its features
can use the old MST lookup. Correction masks/rendering and baseline hashes are
unchanged. No Android claim or integration.

| Fixed-sample result | Value |
|---|---:|
| Attempt records | 25 |
| Original failures retained | 8 |
| FaceOcc outputs | 17 |
| Candidate technical measurements | 17 |
| Newly below1000-pixel minimum | 0 |
| Selected pixels removed across images | 10,838 |
| Median parent-pixel retention | 95.44% |
| Minimum retention, neck/garment spill case4 | 26.80% |
| Retention across other16cases | 73.98–99.20% |

Retention measures the old selection retained, not true-skin recall. The old
selection contains non-skin, so removing many pixels can be useful, destructive,
or both. No image was dropped on retention. Passing1000pixels is not quality.

## Prebound diagnostic marks and visual findings

Original sparse assistant diagnostic marks were bound before FaceOcc predictions.
Three of four selected non-skin marks were removed; one remains. Both of two
marked skin points remain. These are a handful of exposed diagnostic points,
not segmentation accuracy, independent ground truth or user approvals.

- Case4: marked neck(125,175) and garment(125,225) are removed. Marked cheek
  skin(100,140) remains. The large exterior spill is visibly reduced.
- Case14: marked worn face covering(115,150) is removed, while forehead
  skin(110,90) remains. Visual inspection shows substantially better covering
  rejection than the parent on this example; not proof every mask pixel is excluded.
- Case10: marked beard(125,140) remains selected. The binary visible-face target
  is not a beard-specific skin classifier. Dark illumination also limits visual
  assessment; there is no invented beard exemption or hidden row removal.

All17boards were inspected across five contact sheets. Facial coverage is largely
preserved compared with the rejected outline-only diagnostic, but hairline/upper
forehead and edge regions are removed in several cases, notably case17. This is
a qualitative exposed comparison, not an independent model-selection benchmark.
No dense skin annotation supports a precision/recall or exact skin-loss claim.

There is no dedicated prelabelled glasses diagnostic in this fixed sample, so
glasses improvement is **not established**. The earlier FairFace glasses-bridge
failure was not added after seeing outcomes. Profile alignment, reflected padding
and estimated landmarks behind a covering remain adaptation limitations.

## Verification and stopping decision

Saved logits are finite with exact expected shape. Script370 reconstructed masks
with direct source-validity/affine operations independently of the candidate
combination function, then reproduced all17pixel counts, statistics and endpoint
features.0added pixels and0selected forbidden parser/anatomical/nasal-guard pixels.
Baseline and saved correction/rendering input hashes unchanged. This verifies
construction, not the truth of predicted classes. No second inference for checks.

Seven focused mapping/bridge/veto tests passed in0.63s. Two new tests cover strict
threshold/removal-only/immutability and unavailable/nonfinite outputs. Broader
Python run:903passed in12.19s, excluding tests/test_demo_desktop.py because local
Tcl/Tk is unavailable. Not a full-suite pass.

Stop after this one run. The veto is a promising exposed occlusion diagnostic,
not reliable MST measurement, validated correction or runtime adoption. The
remaining beard contamination and unmeasured skin loss prevent a general claim.
Do not retune thresholds, swap models, fit a filtered subset or automatically
expand to new images. Beard-specific model work remains held. Independent
actual-skin/occluder evaluation, matching MST evidence and Android deployment
remain separate unresolved requirements. No new participant collection imposed.

## Evidence and panel record

Gallery: outputs/faceocc_diagnostic_v1/review.html. Panels are original, preferred
measurement, mapped FaceOcc prediction and combined measurement. The FaceOcc
prediction alone includes internal features; only the intersection retains the
parent anatomical/nasal exclusions. These are not correction masks.

plan.json binds input/code/checkpoint hashes and marks before inference;
inference.json/records retain all17forward outcomes; raw logits, mapped masks,
candidate masks and their hashes are saved. summary.json retains all25records
and features/unavailable states; verification.json records saved replay checks.

Panel register now records that a pretrained visible-face veto plus fixed
MediaPipe alignment was tested as a candidate beyond the original rule-based
masking stage. No panel approval or adopted amendment is claimed. If later used,
cite original FaceOcc and derivative checkpoint/source, retain attribution, and
verify affected submitted-paper sections before finalising the request letter.
