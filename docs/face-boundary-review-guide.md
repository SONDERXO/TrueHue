# Facial-boundary reference review

25 October 2026. Prepared a small offline annotation set before further mask-rule changes. It contains40048's clean256 reference (missed cheek),16798's original224 paint example and60162's clean256 reference (face/background boundary). These are known development sources, not new independent evaluation images. No labels or polygons are prefilled.

## How to mark the images

Open [the local annotation page](../outputs/face_boundary_review_v1/review.html) in a browser. It works offline and embeds its images, so no server is required.

1. Choose green **Facial skin**, click around the visible face and press **Finish polygon**. Include actual missing cheek skin; multiple regions are allowed.
2. Choose red **Keep excluded** and draw separate polygons for eyes, eyebrows, lips/mouth, hair, paint or other non-skin inside your outline. Exclusions override skin polygons.
3. Use yellow **Uncertain** for ambiguous edges. Leave the neck unmarked in this facial-boundary set; unmarked does not mean non-skin or rejected neck coverage.
4. Review the outline, mark that image complete and move to the next. Zoom changes display only, not stored image coordinates.
5. Download `truehue_face_boundary_review.json`, preferably into Documents, and return its file path. Draft exports and importing a saved JSON are supported.

Undo removes the latest draft point; Cancel discards only unfinished draft points. Saved polygons have individual Delete buttons so you can redraw. Switching images or exporting is blocked while a polygon is unfinished. Only finished polygons are saved in browser storage; download a draft before closing. All images must have skin and exclusion polygons and a completion check for the export to be marked non-draft.

Exclusion takes priority over uncertain, then skin. Pixels outside all polygons remain unlabeled rather than automatically becoming negative samples. The annotations guide coverage experiments; they are not calibrated skin-color truth, a final evaluation mask set or proof of annotator accuracy. We should inspect the returned polygons before rasterizing them or using them to judge candidate masks.

## Verification and limitations

Native annotation frames are preserved:256x256,224x224,256x256. Embedded images match exact source pixels, saved image hashes and manifest dimensions;16798's prior point-label frame is not resized. The new review has its own manifest hash and does not replace earlier24 point labels or user decisions. No additional source exposure was introduced and no mask/model/training data changed.

Used the browser skill to attempt an interactive check, but the browser runtime reported no available browser. JavaScript syntax and Node mock-DOM logic checks passed for blank initial state, zoom-to-original coordinates, completion requirements, draft/export protection, deletion, self-crossing rejection, manifest/coordinate import validation and storage failure. These are logic checks, not interactive browser QA or a visual user test. If the page behaves unexpectedly, preserve any downloaded draft and report the problem before continuing.

After user annotation, verify IDs/hash/dimensions/coordinates and completion. Preserve uncertain regions, inspect boundaries, and then compare generation/correction coverage against these explicit reference regions before another rule change. No automatic mask-rule update, refit or runtime adoption follows from creating this page. Operational MST, visible-neck support and final thesis/data/reference/evaluation requirements remain unfinished.

[Review manifest](../data/manifests/face_boundary_review_v1/review_manifest.json) | [Verification](../outputs/face_boundary_review_v1/verification.json) | [Prior padded-crop findings](padded-correction-crop-test.md)

Existing Python suite after preparation: **464 tests passed**.


## 26 October 2026: completed import

The reviewer confirmed40048 was complete despite its unchecked export box. Exact chat confirmation is linked to the archived original draft hash; the original export and all polygons/notes are unchanged. All three frames have now been visually inspected, rasterized with label priority/unlabeled regions preserved, and used for saved-mask diagnostics. See [reference results and limitations](face-boundary-reference-results.md) and [local comparison gallery](../outputs/face_boundary_reference_v1/review.html). No re-export is needed for this confirmed snapshot; any future coordinate edits require a separately validated/versioned import. This completion does not adopt a pipeline mask or authorize final training admission.

## 27 October 2026: material-reference caveat

The [cached failure audit](material-protection-design-checkpoint.md) flags mixed
paint/skin-boundary ambiguity at particular16798witness pixels. Completion and
structural validation do not establish material-label accuracy. Original export,
confirmation, polygons and rasters remain unchanged. Any actual clarification
must be a separate, provenance-preserving adjudicated version; model agreement
or Codex provisional labels cannot substitute for it. No required application
user annotation workflow or new training admission follows.
