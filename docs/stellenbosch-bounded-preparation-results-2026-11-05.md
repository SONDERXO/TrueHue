# Bounded preparation: decimal scores preserved; current whole-frame path fails

5November2026. The authorised30-image preparation is complete. **The delivered
sample has small faces within full scenes, and none passed the unchanged current
measurement guard.** This is a concrete preprocessing/measurement limitation,
not evidence that the entire dataset or ITA-to-MST task is unusable.

Private local gallery:
`outputs/stellenbosch_bounded_preparation_v1/review_PRIVATE.html`.
Do not publish/share its pictures, scores or per-person manifests without author
consent. Only aggregate findings and generic code are recorded here. Research-
only/noncommercial and source-paper citation conditions remain in force.

## Decimal-score policy and fixed selection

The [protocol](stellenbosch-bounded-preparation-protocol-2026-11-05.md) fixed the
source-target policy before image pixels: preserve supplied decimal MST scores
within1–10, including raw values/types and exact decimal representations. No
rounding, integer-only subset or invented category labels. For this development
preparation the source target is a decimal MST score, not a calibrated prediction
or an assumption that score differences are physical/perceptual distances.

A future justified calibration candidate would retain ITA as measured predictor
and the supplied score as target, with subject-balanced/held-subject score-error
and fitting-subject median-baseline evaluation. No integer-category accuracy
can be claimed from that definition. The old integer-only calibrator and final
runtime MST interface were NOT changed, adapted or fitted in this preparation.
No final feature/output-schema adoption follows from accepting decimal source data.

Ten publisher subject keys were selected by fixed SHA256 ordering: two from
each of five descriptive score intervals [1,3),[3,5),[5,7),[7,9),[9,10]. These
are sampling strata, not five new MST classes. Each subject supplied the same
three front-facing filename conditions F_cool_600/H_warm_600/L_warm_600. All30
selections were recorded before pixels/inference; all failures remain, with no
replacement. The other275subjects, other poses and other conditions were not
activated. No fitting/evaluation split or cohort adequacy claim was created.

## Actual processing and failure denominators

| Stage | Successful / attempted |
|---|---:|
| Current detector/landmark/parser/nostril parent measurement | 21/30 |
| Fixed CPU FaceOcc forward on available alignments | 21/21 |
| Final preferred measurement meeting unchanged1000-pixel guard | 0/30 |
| Calibration/training admission | 0/30 |

Of nine parent failures, six had insufficient selected skin and three had no
predicted facial skin overlapping the selected face. The21FaceOcc outputs were
finite and saved, but every final candidate had fewer than1000selected pixels
(range0–977). Thus technically successful model inference is not a usable
measurement. No valid MST predictions or calibrated ITA-to-MST results were
fabricated from those failed measurements.

This run used the unchanged whole-frame224→256 INTER_LINEAR path, .85 single-face
guard, existing ordered landmark helper, parser/anatomical/nostril exclusions,
pinned alignment and strict logit>0 validity veto. No crop/margin/threshold/model
search or installation. The existing landmark helper's own fixed fallbacks were
retained, not extended. Main project environment remains separate from PyTorch.

## What the visual check established

The assistant inspected all30private boards. Their first panels show native224px
originals padded only for display; the model input is separately resized to256.
Other panels show parent overlay, preferred overlay and selected pixels. Source
scores were not displayed on boards; no strict blinded clinical/skin assessment
is claimed. No human annotation workload was created.

The sampled images include torso/background and a chart above the subject. Faces
are much smaller than the face-filling FFHQ frames: detected face boxes are only
28–35pixels wide and35–46pixels high in the working256frame. This is not a native
high-resolution face crop. Upsampling does not create new facial detail.

Parent masks visibly include hair, neck and sometimes clothing; one selects a
large part of a light shirt. FaceOcc removes much of that contamination but can
also leave sparse or absent facial patches. Glasses, varying colour appearance,
low facial signal and unresolved skin-loss boundaries remain. The fixed whole-
frame contract therefore does not transfer cleanly to these delivered samples.
Framing, resolution, light and segmentation effects are not causally isolated
by this single diagnostic.

## Verification and next technical step

All21saved service/mask/feature reports replayed exactly with saved logits, with
no additions outside parent support. Independent saved-statistics checks passed
for all21candidate masks, including their invalid status.30CSV/JSON score records
preserve exact decimals; deterministic selection was recomputed identically.
Selected source JPEGs, label files, metadata, archive and prior historical inputs
remain byte-identical.21focused tests passed in5.88seconds for selection, labels
and service behaviour; not a full-suite pass or scientific validity claim.

Private result/assessment packages:
`outputs/stellenbosch_bounded_preparation_v1/` and
`outputs/stellenbosch_bounded_preparation_assessment_v1/`.
They retain per-person provenance and pictures locally and carry artifact hashes.
Scripts430–432 refuse overwrite; no failed cases were silently repaired.

**Decision:** do not fit calibration on this run or relax the1000-pixel guard to
force a success. The next justified technical investigation is a single fixed
face-first framing bridge on these same30cases, recording source-to-crop geometry
and native-resolution support. That would be a new preprocessing contract and
must preserve this failed baseline, rather than replacing its masks or claiming
more independent pixels after resizing. It is not implemented or activated here,
and may improve parser framing without resolving low native detail or all light/
occlusion concerns. No automatic broader processing or dataset rejection.

No calibration/threshold/isotonic/tree fits, synthetic variants, lookup export,
runtime change, contacts, public dataset/gallery or submitted/working thesis edits.
The earlier nineteen-subject study stays complete and unchanged. The panel
register records decimal-target policy and the observed frame mismatch without
claiming adoption, panel approval or a finished model.
