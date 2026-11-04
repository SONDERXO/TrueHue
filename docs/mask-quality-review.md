# Facial Skin Mask Quality Review Policy

## Purpose

This policy identifies whether a facial skin mask is suitable for ITA
calculation, ITA-to-MST calibration, and later model-development use.

The review is a quality-control step on the *algorithm output*. The person in
the photograph is never assessed, categorised, or described.

## Where the label is recorded

The MST-E workflow below retains its existing labels and storage. For the
current FairFace candidate pool, use the separate review procedure at the end
of this document; do not overwrite automated processing results.

The review label lives in the `quality_review` column of
`data/manifests/mst_e_ita_calibration_results.csv` (written by
`scripts/05_run_mst_e_ita_calibration.py`). The permitted values are:

| Value | Set by | Meaning |
|-------|--------|---------|
| `pending` | script, then reviewer | Written automatically for every measured image. Replace it with `good`, `acceptable`, or `poor` during review. |
| `good` | reviewer | See "Good" below. |
| `acceptable` | reviewer | See "Acceptable" below. |
| `poor` | reviewer | See "Poor" below. |
| `auto_failed` | script only | Automatic failure. Never assigned by a human. |

Whenever a row is excluded, `exclusion_reason` must state why in plain words
(for example "mask covers background instead of facial skin"). Two columns must
never disagree: a row with `quality_review = poor` or `auto_failed` must not be
used in the calibration statistics.

In addition to the minimum conditions above, the script records these
automatic failures: unreadable image, an empty face crop, a missing
ground-truth MST label in the inventory, and Skin Mask V2 feature exclusion
being unavailable so that a V1 fallback mask was produced instead.

## How to review an image

1. Open the face crop, its mask, and the mask overlay produced by
   `scripts/02_batch_face_and_skin_test.py` (or the 2x2 diagnostic grid from
   `src.skin_masking.skin_mask.save_mask_visualization`).
2. Judge only the mask: which pixels were selected as facial skin.
3. Assign one of `good`, `acceptable`, or `poor` from the criteria below, and
   write a short `exclusion_reason` whenever the label is not `good`.
4. Review the crop and the mask, not the whole photograph, and do not consult
   the ground-truth MST label while labelling: seeing it first biases the
   review. Label first, then join the label.

The criteria under "Manual mask-quality labels" are qualitative, by design:
they are written for a human looking at a mask, not for a script. Confirm them
with the supervisor before the full review pass, and record any change in this
file so every reviewer uses the same policy.

## Automatic minimum condition

An image fails automatically when:

- No face is detected.
- The face crop is empty.
- The skin mask is empty.
- The final skin mask contains fewer than 1,000 pixels.
- CIELAB/ITA computation fails.

## Manual mask-quality labels

The three labels describe mask reliability only. `pending` means the mask has
not been reviewed yet; it is the state every measured image starts in.

### Good

- Cheeks, forehead, nose, and chin are substantially represented.
- Eyes, eyebrows, lips, and obvious hair/background are mostly excluded.
- The selected region is reasonably continuous.
- No major false-positive region dominates the mask.

### Acceptable

- Some small holes or incomplete cheek regions are present.
- The selected region still covers enough representative facial skin.
- No major background, hair, eye, eyebrow, or mouth contamination is present.

### Poor

- The mask is highly fragmented.
- Large facial-skin regions are missing.
- Hair, background, eyes, eyebrows, lips, or clothing are substantially included.
- The selected pixels do not appear representative of the facial skin region.

## Use decision

- Good: eligible for ITA processing and calibration.
- Acceptable: eligible, but retain the review label for sensitivity analysis.
- Poor: exclude from ITA-to-MST calibration and model-development input tables.
- Automatic failure: exclude.

## Important note

The review label assesses whether the mask is suitable for this image-based
pipeline. It does not classify the person or determine their actual or
permanent skin tone.

Specifically, a `good`, `acceptable`, or `poor` label never states anything
about:

- a person's identity, or whether two images show the same person;
- race, ethnicity, or national origin;
- medical or dermatological status, or any skin condition;
- a person's permanent or natural skin tone.

It states one thing only: how much the selected mask can be trusted as
"facial skin pixels" for the ITA measurement taken from that image. A `poor`
mask says the measurement is unreliable, not anything about the person.

ITA itself is an image-derived quantity computed from the camera's rendering of
the scene under its lighting. It is not a measurement of a person's real or
permanent skin colour.

## Dataset roles

This review applies to every dataset inventory produced by
`scripts/04_build_dataset_inventory.py`:

- FairFace and SCIN are training sources (`intended_use = training`).
- MST-E is an evaluation/calibration dataset (`intended_use =
  evaluation_only`). Its rows must never enter a model-training, validation, or
  test split, and its images must never be used to fit the correction model.

## FairFace candidate screening procedure (2026-10-19)

### Scope and review unit

Screen all 533 rows with `processing_status = success` in
`data/manifests/fairface_candidate_processed_manifest.csv` before calling them
visually screened candidates. Retain all 650 source rows for accounting,
including the 117 automated exclusions. SCIN remains paused. This review does
not assign MST labels, create a data split, or establish training readiness.

The unit is one original image and its final V2 mask. Keep the existing
detector, mask configuration, processing resolution, CIELAB conversion, ITA
formula, and minimum-pixel condition unchanged during this baseline review.

The 30-grid pilot is complete: 7 accepted and 23 rejected. Seven rejections
were already automated exclusions; 16 were automated successes. Thus 23 of
the 533 successes have been reviewed and 510 successes remain to review.
The sample combines random and extreme-coverage examples; its acceptance
fraction must not be reported as a full-pool acceptance estimate.

### What the reviewer sees

Show the original face crop, final binary mask, and preferably a mask overlay
at matching scale. In the existing grids, white in **Final** means selected
measurement pixels; white in **Exclusion** means pixels intended for removal.
Inspect the Final panel rather than treating the Exclusion panel as the mask.
Enlarge unclear images without changing the measurement image or mask.

Hide ITA, source demographic attributes, any estimated groups, and model
outcomes during review. Review in a fixed image-ID order, in manageable
batches (for example 25), with a progress record. Do not prioritize images
because their ITA values look convenient or remove difficult lighting cases
solely to improve the apparent distribution.

Only 30 grids currently exist. Before reviewing the remaining successes,
prepare matching grids through the existing visualization helper in
`scripts/13_fairface_smoke_test.py`, reused by script 14. Any regenerated
mask must use the recorded frozen configuration and matching local model
assets. Check it against stored skin-pixel counts and ITA before reviewing;
if it differs, investigate and label a separate run rather than silently
replacing baseline evidence. Do not rerun or overwrite the original manifests.

### Decisions and criteria

Use `pending`, `accept`, `reject`, or `unsure`. These FairFace decisions are
separate from the MST-E `good` / `acceptable` / `poor` labels above.

| Decision | Criterion | Required action |
| --- | --- | --- |
| `accept` | Selected pixels visibly provide useful facial-skin coverage with no substantial non-skin contamination. | Record a short reason and any residual concern. |
| `reject` | Substantial contamination or loss of useful facial-skin coverage makes the measurement unreliable. | Record reason codes and a specific observation. |
| `unsure` | The grid cannot support a confident decision. | Inspect enlarged crop and overlay; obtain a second review where available. Keep ineligible until resolved. |
| `pending` | No completed visual review. | Keep ineligible until reviewed. |

Acceptable masks can have small holes, omit the chin, or lack complete
forehead/cheek coverage. They need not select every facial-skin pixel or form
one solid region. Reject contamination that materially changes the selected
measurement region, such as large hair/background regions, glasses, clothing,
or an inadequately excluded open mouth. Substantial facial-hair inclusion is
a concern; a reviewer must assess the actual selected region.

Coverage percentage alone is neither an acceptance nor a rejection rule.
Do not invent a percentage threshold from these examples. Note uneven or
poor lighting as a limitation; reject only with a documented mask-suitability
reason. Visual acceptance does not establish accurate skin color or ITA.

Use these reason codes, with multiple codes separated by `;` where needed:

| Code | Meaning |
| --- | --- |
| `representative_skin` | Useful facial skin selected; acceptance reason. |
| `minor_coverage_gaps` | Small holes or omitted regions retained as an acceptance caveat. |
| `hair_or_facial_hair` | Material hair contamination. |
| `background_or_clothing` | Material background/clothing contamination. |
| `eyes_brows_or_glasses` | Inadequate exclusion of these features. |
| `mouth_lips_or_teeth` | Inadequate exclusion of the mouth region. |
| `insufficient_representative_skin` | Extensive missing skin or fragmentation leaves an unsuitable measurement region. |
| `empty_mask` | No selected pixels visible. Check against automated status. |
| `unclear_visualization` | Evidence insufficient; requires further inspection. |

### Review record and preservation

Store one row per original candidate in a separate local CSV:
`data/manifests/fairface_candidate_mask_quality_review.csv`.
Script `15_prepare_fairface_mask_review.py` creates this review artifact without
overwriting existing packages. Run it from the project root with the project
virtual environment and `--workbook` pointing to the original review workbook.
It reads that workbook, applies the user's final eight resolutions, and
verifies regenerated measurements before saving new grids. It does not assign
human decisions to unreviewed images. The package records model/input SHA-256
hashes and library versions in `fairface_mask_review_provenance.json`, plus
per-image verification in `fairface_mask_review_regeneration_audit.csv`.
Use this schema:

```csv
image_id,processing_status,automated_exclusion_reason,visual_review,reason_codes,review_notes,reviewer,review_date,review_source,visualization_path,review_protocol_version
```

The prepared CSV also includes `review_batch` and `evidence_status` to track
grids stored under `outputs/fairface_mask_review/batch_NNN/` (25 images per
batch, with a shorter final batch). `blocked` evidence must be investigated
before review. Existing reviewed grids remain in their original folder.
Historical `reason_codes` remain blank where only free-text reasons were
supplied; retain those notes rather than inventing coded reviewer judgments.
Historical dates remain blank when the actual review date is unknown; the
final eight decisions' confirmation date is recorded in the notes/provenance.

Copy automated fields unchanged from the processed manifest and join by exact
`image_id`, not row number or basename. Use ISO dates and protocol version
`fairface_mask_review_v1`. For automated exclusions without visual review,
leave `visual_review = pending`; automation already makes them ineligible.
Preserve reviewed automated exclusions and their decisions as diagnostic
evidence. Never replace their automated reason with a manual reason.

Seed the review record with the 30 completed decisions from the supplied
workbook plus the user's final resolution recorded in `docs/expirement-log.md`.
Those final decisions override the workbook's eight original unsure values.
The accepted IDs are `fairface__train/124.jpg`, `fairface__train/4214.jpg`,
`fairface__train/22057.jpg`, `fairface__train/27912.jpg`,
`fairface__train/48136.jpg`, `fairface__train/53224.jpg`, and
`fairface__train/75027.jpg`; the other 23 reviewed IDs are rejected.
Record the user's decisions as manual review; do not claim a second human
review or invent reviewer agreement. Preserve the original workbook.

Review-only eligibility is derived, never inferred from a numeric ITA:

```text
mask_screen_pass = (processing_status == success) AND (visual_review == accept)
```

This is not final training eligibility. Grouping policy, reference suitability,
source-level split/leakage checks, and distortion targets remain separate.

### Completion checks and reporting

Before finalizing screening:

1. Verify 650 unique review IDs match the source manifest exactly, with no
   missing or extra IDs and unchanged automated fields.
2. Require every automated success to have a resolved accept/reject decision;
   pending or unsure successes prevent calling screening complete.
3. Check every rejection has a reason, every acceptance has a brief supporting
   observation, and review source/date/reviewer are recorded without guessing.
4. Reconcile automated success counts: accepted + rejected + unsure + pending
   must equal 533. Report the 117 automated exclusions separately and avoid
   counting rejected automated failures twice.
5. Report manual rejections by reason (codes may overlap), final included count,
   and any reviewed lighting/coverage concerns. State that no official FairFace
   MST labels or validated broad groups are available; do not substitute race
   for a skin-tone label or infer tone-specific rejection rates.
6. Keep all failures in the audit table. Performance on retained images is
   conditional on this screening and does not measure unscreened app reliability.

If useful candidates are insufficient or systematic contamination persists,
document a separate segmentation-improvement experiment. Version the change,
compare it on the same diagnostic examples, and regenerate affected features
consistently. Do not tune individual masks to preferred ITA values, combine
incompatible pipeline versions, or describe manually screened performance as
fully automatic deployment performance.
