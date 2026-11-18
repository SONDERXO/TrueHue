# Photographic support save controls and draft recovery — 10 November 2026

The user reported completing review, then clarified there was no visible Save
button, that some masks had been painted while others were unchanged, and that
the edited windows were closed. Actual support annotations and worker jobs both
numbered zero. This records **user-reported review work without persisted edited
masks**, not a claim that the user did not do the work.

The old research editor packed Save and confirmation controls after an enlarged
image and other controls. That layout allowed the actions to extend below the
visible window. The user's old window geometry was not captured, so its exact
clipping is not asserted. Earlier hidden GUI checks exercised save callbacks but
did not verify on-screen button bounds; they did not catch this failure path.

## Fix

Research Save/unjudgeable buttons and both review confirmations now appear at
the **top**, before the image, in a compact two-row action layout. Research
display starts at1×, and its initial window is bounded by the screen with an
explicit on-screen position. Ordinary desktop mode retains its default behavior.
The queue now also warns before skipping an unsaved role and labels the editor
button explicitly. Restart the whole reviewer to load the corrected code.

Research strokes, undo/reset and notes now write an atomic local **draft**, bound
to the exact base manifest. Closing also checkpoints pending edits. Reopening
offers to restore a matching unsaved draft, with both final review confirmations
reset. Drafts are explicitly unapproved and are not counted as support reviews,
training data or admission. Successful saves mark the current draft saved and
retain the immutable annotation and prior revisions. Worker failure leaves the
draft intact. Draft files are dedicated mutable working files, not overwritten
original images or scientific artifacts.

Real draft root: `outputs/photographic_support_drafts_v1`. Existing sessions used
the old code and wrote no drafts; this feature cannot recover their closed-window
memory. No unavailable stroke history was reconstructed or fabricated. Painted
changes from those closed sessions need repainting; unchanged existing masks can
be explicitly confirmed and saved without repainting.

## Checks

**24 focused tests pass in8.26s**, covering the support and existing refinement
backends plus unsaved navigation, atomic draft/reset behavior and ordinary-mode
draft isolation. The independent new GUI check is script741, with generated
inputs and outputs isolated in `outputs/photographic_support_visibility_check_v1`.

The actual Python3.13 Tk check maps the controls and verifies Save, unjudgeable
and both confirmation widgets lie fully inside the client window under a
simulated720pixel screen height, a450pixel-high window, and a restored-draft
window. It then paints, closes, restores the draft, confirms both masks and invokes
the visible Save button through the project worker. Saving and progress pass.
Ordinary-mode constructor/render/cancel smoke also passes. These are measured
widget-bound and interaction checks, not a screenshot or a universal visual
layout guarantee. The old GUI checks remain preserved.

No actual support annotations were created by QA; no real user drafts or reviews
were fabricated. The user's prior30calibration reviews, eight reference choices,
all immutable tasks/decisions/annotations and closed assessments are preserved.
No model calls, calibration/target/tree fits, original TIFF/holdout reads,
downloads, contact, uploads, commit, push or predictor/Android changes.
