# Native-coordinate pipeline integration diagnostic — 9 November 2026

The user requests sustained progress toward the working model. This is a separate
bounded integration diagnostic, prepared before execution. The prior eight-photo
detector comparison remains FAILED and unadopted. This diagnostic does not reopen
its detection search or relax any quality gate.

## Design review

The software bridge now accepts native boxes explicitly, with 19 focused generated
tests passing. Cached native detections exist for all eight original source photos.
The missing question is whether the existing downstream measurement/support stages
can consume their exact native crops without coordinate or projection errors.
This cannot be established by the synthetic bridge tests alone.

Keep the original eight IDs/order and original source/editor-A files. Do not rerun
the anchor detector. Use each recorded sole native box exactly, including the
child box in904_0. That case remains a wrong-historical-person FAILURE regardless
of whether a technically valid child mask is produced. Do not switch to the adult,
drop the case, or claim all-eight cohort readiness. Record downstream technical
availability separately from correct-historical-person availability.

## Exact intervention and limits

- Only the anchor-to-crop coordinate input changes from the previous support
  screen. Use cached native anchors and the isolated `crop_native_anchor` fixed
  1.5-context helper, no alternative crop/margin/rounding policy.
- Recheck all sixteen inherited TIFF hashes, types, dimensions and sRGB profiles,
  cached detection/result/verification hashes, exact bridge and existing mask
  model/code bindings before any downstream call. Separate exclusive output
  directory; preserve partial artifacts and never blindly restart.
- At most one unchanged parent preprocessing invocation per crop, at most eight
  parent detector calls, eight dense-parser calls and eight FaceOcc calls. Record
  actual landmark helper/fallback attempts. No new anchor calls, enhanced input,
  model install/download or alternative parser. Stop on contract/hash mismatch.
- Use existing nostril measurement, raw-appearance alignment/visibility, strict
  FaceOcc veto, 1000-normalized-pixel guard, protected face/visible-neck support,
  uncertain glasses and identity controls. No target inference, calibration, tree
  learning, action/target fitting or rendering with learned controls.
- All eight stay in the attempt ledger; preserve source-selection mismatch and
  technical failures independently. New crops invalidate automatic reuse of old
  features/calibration/costs. Do not fabricate MST labels from these portraits.

## Verification and visual review

Independently replay cached measurement masks, native binary projection, native
alpha/protection, identity/output invariants and call/source accounting without
new model calls. Verify each crop is the exact declared original-source slice.
Review every available mask board and retained failure. Reuse the previous
all-eight source/target correspondence review only under exact original-file
hash equality; no fresh registration or dense skin validation claim.

Report both raw technical availability and correctly selected-person availability,
retaining904_0 as failed for the latter. Compare descriptive coverage/support
against the earlier support screen; no new dense-quality threshold or oracle
fit. A technically successful mask is not training admission or product readiness.

## Stop and subsequent boundary

Stop after this one integration diagnostic. No detector/parser/threshold/guard
rescue, successful-only fit, fourth contrast output, dataset expansion or final
holdout read. Use the actual result to identify the next genuine blocker. New
model learning still needs substantive design evidence, compatible ITA/MST and a
justified evaluation plan. No current failed candidate is promoted by this work.

All private files remain local/ignored. No runtime change, author contact, upload,
commit or push. The final eight-group/24-photo holdout stays byte-unread.
