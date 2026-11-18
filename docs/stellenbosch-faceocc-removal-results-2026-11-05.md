# FaceOcc removal inspection — 5 November 2026

The saved before/after comparison shows **apparent visible-skin loss in several
difficult cases**, alongside plausible hairline/contour/neck trimming. The loss
is mostly from the model prediction, not the alignment-domain boundary. This
supports testing a recognition-input adaptation; it does not justify removing
the veto, lowering its threshold or admitting the current measurements.

## What was compared

Scripts444–445 followed the [frozen protocol](stellenbosch-faceocc-removal-protocol-2026-11-05.md).
All30cases from the one parser-appearance candidate remain. Twenty-five have
parent masks and FaceOcc predictions; five are unavailable before FaceOcc.
Original pixels, landmarks, aligned inputs, logits and logit>0rule are unchanged.
No new inference, photo, refit or candidate was executed.

For each available case, exact aligned-pixel replay and parent/intersection mask
replay pass. An all-positive aligned mask through the same validity/inverse warp
isolates mapping-domain coverage. Removed parent pixels outside that coverage
are counted as mapping-domain loss; other removed pixels are model-prediction
loss. These are software-stage counts, not numbers of actual skin pixels lost.

| Quantity, pooled normalized pixels over25available cases | Count |
|---|---:|
| Parent selected pixels | 332,755 |
| Final retained pixels | 252,696 |
| Removed pixels | 80,059 |
| Mapping-domain loss | 3,368 |
| Model-prediction loss | 76,691 |

Model prediction accounts for95.79%of removed pixels. This is not an error rate,
an accuracy measure, or an independent native-pixel sample. Three available masks
are empty; another is below the unchanged1000normalized-pixel minimum. Final
availability remains21/30, not25/30. The five unavailable cases have no fabricated
FaceOcc successes, losses or zero-removal claims.

## Visual findings

The assistant inspected all30five-panel boards with source scores hidden:
original; parent support; retained support; removed pixels in red; original
aligned image with positive model prediction. Red is a removal indicator, not
skin truth. Observations are qualitative and no dense annotations were made.

- Several easier cases mainly lose contour and hairline pixels; some removed
  regions include a hair lock or uncertain neck/boundary material.
- One case loses substantial apparently visible lower-face/chin skin in a warm
  condition. Other cases lose broad apparent cheek/chin skin while retaining
  forehead regions. The pattern changes across lighting conditions.
- Glasses/reflections are ambiguous. One warm glasses case loses most parent
  facial support, retaining only a small cheek patch. Of10,476removed pixels,
  1,123are mapping-domain loss and9,353are model-prediction loss.
- Some passing photos still have large parser-stage holes even where FaceOcc
  predicts broad visibility. Those holes cannot all be attributed to FaceOcc.
- In the highest sampled score interval, three parent masks reach FaceOcc:
  3,624→0,5,533→907and13,063→0pixels. Their mapping-domain loss is zero. The model
  rejects the existing forehead/broader facial support; the very dim source
  detail limits certainty, but removals overlap apparent visible skin rather
  than being confined to obvious objects. The other three cases fail earlier.

These results do not establish that every rejected pixel is real skin or that
the model has a demonstrated population-level skin-tone bias. Lighting, native
detail, alignment adaptation, subject appearance and prediction validity remain
confounded. No claim that FaceOcc is generally unusable follows.

## Selected repair direction

The specific next candidate is **one fixed appearance preprocessing step for
FaceOcc recognition only**, preserving the original alignment transform,
parent mask and original-pixel colour measurement. A separate frozen comparison
must include all available cases and object/glasses concerns, retain failures
and compare removed/added regions, rather than optimize pass counts.

This diagnostic does not execute that candidate. It does not authorise a sweep,
disable the veto, union geometry into the mask, change logit>0, expand the cohort,
fit calibration/trees or update Android. The current skin-validity/calibration
hold remains; image enlargement adds no native detail. Original MST scores and
the intended ITA/calibrated-MST/three-output correction design remain unchanged.

## Verification and private evidence

All bound input/source/history/artifact hashes remained unchanged. Twenty-five
exact alignment/mask replays and independent kept/removed/domain/model partition
checks pass; five pooled-count aggregates match. All30members and ten subject
keys remain. No new model forwards, fits, admissions, author contacts or dataset
transfers occurred.

Eleven focused coordinate, landmark-bridge, veto and development-service tests
passed in2.42seconds. No new full-suite or device test was needed for this saved
output inspection; these tests do not establish segmentation accuracy.

Private gallery: `outputs/stellenbosch_faceocc_removal_v1/review_PRIVATE.html`.
Notes and verification: `outputs/stellenbosch_faceocc_removal_assessment_v1/assessment_PRIVATE.json`.
Dataset images, identities, source scores and manifests remain ignored local
files under the author's research/noncommercial, citation and no-redistribution
terms. No app/runtime/measurement helper or submitted thesis was changed.
