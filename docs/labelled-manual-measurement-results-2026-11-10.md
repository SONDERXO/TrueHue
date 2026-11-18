# Labelled measurement editing preparation — 10 November 2026

The requested labelled-refinement path is ready for actual user annotations.
Launch `review_labelled_measurements.cmd`; see the separate usage guide. No
calibration or decision-tree fit has been performed or selected.

## Cohort and preparation

Scripts723–727 implement an isolated research queue/editor/worker/verification.
All30 existing development records from ten Stellenbosch publisher subjects are
retained, with their exact original decimal MST scores, groups, three conditions,
source hashes, native bridge metadata and historical outcomes. Scores are hidden
in the editor. Labels remain publisher references, not inferred labels for FFHQ.

Historical cached artifacts were checked against the existing artifact hash
inventory before copying. All30 have a saved normalized input. Twenty-five have
a saved measurement mask, copied exactly; five start explicitly empty. The queue
retains all nine historical unavailable cases, including five without a saved
mask. No substitute parser/parent mask, research points or polygons become human
annotations. No source original, later/final image or additional cohort was read.

The separate `truehue_native_manual_measurement_method_v1` binds native1p5crop
geometry, the automatic starting contract, full manual facial-skin annotation,
Lab/ITA implementation and library versions. It is incompatible with the
whole-image desktop square method unless independently justified; sharing a
formula does not establish calibration transfer. No correction or brightness
controls enter this annotation editor. This adds manual annotation from scratch
for saved research images, not failed-run rescue in the correction demo.

## Annotation behavior

The UI displays original and green selected-skin views. It offers add/remove/
restore, undo/reset, optional notes, previous/next and explicit reviewed-selection
or unjudgeable saves. Source tasks are immutable. Every save binds its task
manifest and records strokes, mask, statistics, exact label/group provenance,
automatic failure history, generated status and admission flags. Revisions stay
separate, with the same source/task key; they cannot be counted independently.

Invalid or fewer-than1,000-pixel selections may be preserved as unavailable;
they cannot become usable measurements by saving. An unjudgeable review always
remains unavailable even if its mask has sufficient pixels. Reviewed measurements
are only pending admission: calibration/training flags remain false, allocation
null, and old lookup compatibility false. Painting is not proof of anatomical
correctness or representative support.

## Checks

- **22 focused tests pass in2.60s**, covering the new annotation worker plus
  existing refinement behavior. Generated fixtures stay in test temporary paths.
- Actual Python3.13 hidden Tk interaction check passes: draw/undo/reset,
  project-Python worker save, resume, navigation and unjudgeable recording.
  Its two generated annotations are isolated under
  `outputs/labelled_measurement_gui_check_v1`, never the real annotation root.
  No screenshot or visual-layout review is claimed.
- Independent script727 passes all30 exact provenance/label/group joins, cached
  image/mask hashes, all21 historical available Lab/ITA replays, nine retained
  unavailable cases and five empty starts. New user annotations: **zero**.

Private queue/evidence: `outputs/labelled_measurement_queue_v1`.
Preparation and independent verification refuse overwriting earlier versions.

## Current user review and next work

The user's latest FFHQ29863 response approves the facial measurement after manual
hair exclusion and reports the corrected appearance too bright. This is retained
in a scoped hash-bound review receipt. Correction-support approval was not
explicitly answered. Earlier pending-review records remain preserved rather than
rewritten. That one approved measurement has no reference MST label or verified
subject group; it is not a labelled calibration record.

The next required input is actual user review/annotation of the labelled queue.
Afterward inspect real outputs and failures, measurement support, all condition/
score/group coverage and revision deduplication. Define subject-disjoint roles
before fitting a matching calibration; do not fit the21automatic successes alone.
Correction targets and a separately frozen bounded tree comparison remain
additional prerequisites. This cohort supplies labelled measurement evidence,
not correct exposure or expert photographic targets.

Decision tree, ITA and calibrated MST remain required. No new model calls,
original-source image reads, fits, downloads, contacts, uploads, commit or push.
The correction demo, Android, active model assets and old experiments are
unchanged. Final eight groups /24 photos and older locked allocations remain
byte-unread. No repeat of665 or713–718; all prior artifacts preserved.
