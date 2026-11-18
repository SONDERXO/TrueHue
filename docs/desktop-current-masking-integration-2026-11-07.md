# Current masking in the Python desktop demo

7 November 2026. The user explicitly requested adopting the existing masking
method in the Python demo and adding a simple proposal comparison to the adviser
briefing. This supersedes the earlier meeting update's statement that current
masks are not integrated. Android is unchanged.

## Behaviour

- Default **current** mode reuses the existing parser, nostril-excluded skin
  measurement, pinned FaceOcc visibility and object-protected correction preview.
  It includes face/visible-neck support, correction-hole filling and inward
  blending. No new segmentation policy, threshold or detector fallback was tuned.
- **Correction area / Facial measurement** switches the green overlay. Exports
  contain separate measurement, correction and protected masks plus blending
  alpha, images, report and manifest.
- **Clear / Opaque / Uncertain** controls existing glasses handling. Clear lenses
  retain visible facial areas through their interiors with approximate rim
  protection; uncertain/opaque keeps predicted glasses protected. There is no
  automatic glasses-type classifier or exact frame segmentation claim.
- **Legacy** mode preserves the old demo path. Changing masking/glasses clears
  stale results and requires another run. Failed current masks produce no
  correction; there is no silent fallback to old masks or fixed controls.

## Measurement compatibility

The baseline5/fold1 model and its MST lookup still receive only their original
measurements. The displayed current skin ITA is separate and never fed into that
lookup. Controls from the historical model are applied to the new correction
region, converting reciprocal gamma to direct exponent with the existing
`legacy_to_paper_parameters` utility. Old features, mask/report, MST source and
original control values remain recorded alongside the new mask and renderer
parameters. This mixed combination is explicitly unvalidated; the baseline's
failed quality status remains visible. No newer correction model/gate is adopted.

Current masks come from the reusable preview's established full-frame256 path,
not an adoption of every later mask experiment or recognition fallback. The
research cohorts and scientific admission flags remain unchanged. Full-face
rendering quality is not established by the restricted-region research metrics.

## Checks

- Focused demo integration/service/clear-lens/preview tests check separate
  feature provenance, reciprocal gamma, outside/protected pixels, rejection of
  image mismatches/missing controls and no legacy fallback on current-mask failure.
  **24 tests passed in 1.73 seconds** in the recorded run.
- A real historical example completed current parser/FaceOcc inference and
  correction. Its correction overlay, measurement overlay and output were viewed;
  the old model's unnatural correction remains visible, not claimed fixed.
- The real Python3.13 compatibility window and Python3.14 worker passed processing,
  both overlays, export, no-face handling, corrupt-file stale clearing and source
  preservation. `outputs/desktop_current_masks_gui_20261107_v1/verification.json`.
  No window screenshots were captured; GUI visual layout review remains limited
  to checked widget bounds/behaviour. Output images were inspected separately.
- Private integration outputs: `outputs/demo_current_mask_integration_20261107_v1`
  and `outputs/desktop_current_masks_*`. Existing experiment artifacts retained.

The short briefing compares proposal source-bound text (PDF2,12–14,59–65) with
current development. The original proposal PDF remains untouched. The method
register records desktop adoption without implying panel approval. No fitting,
parameter search, dataset search, annotation task, Android integration, external
sharing/contact, commit or push occurred.
