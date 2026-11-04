# Existing-subject skin study: review ready

2 November 2026. User explicitly answered Yes to preparing the 15 additional
simple checks. This activates the frozen membership in
outputs/mst_subject_skin_study_plan_v1/plan.json and protocol
mst-subject-skin-study-protocol-2026-11-02.md, not calibration or correction fits.

## Result

- 19 fixed existing people/photos retained, including all four actual prior
  reviews and the category9 facial-hair hold. No repeat answers requested.
- 15 additional fixed attempts: 14 technical successes ready for human review;
  subject_17's preserved parent face-detection failure retained with no replacement.
- 14 fixed FaceOcc CPU passes, all successful; zero new parser/detector/landmark
  model passes. Reused hash-verified parent masks/landmarks from the older saved
  measurement cycle. No old features treated as FaceOcc features or old lookup used.
- Raw source hashes verified, original full-frame 256 INTER_LINEAR decoding
  reproduced, parent L/a/b statistics matched exactly before alignment. These
  decodes are new authorised source access, not claimed saved-image-only work.
- 14 candidate masks/features/aligned arrays independently reproduced through
  the reusable development service from saved logits. Zero pixels added beyond
  the parent measurement support. Exact contract matches the previously verified
  development service. MST remains unavailable and all admission flags false.

Review page: outputs/mst_subject_skin_study_v1/review.html.
It includes original, green overlay and selected pixels alone, the same three
yes/no/cannot-tell questions, optional notes and no drawing. Four prior answers
and original notes displayed read-only. The failure needs no answers. All 19
remain in membership and outcome reporting.

Browser saving uses a manifest-specific key. Progress-copy export available as
backup; incomplete copies cannot be imported as completed reviews. Export completed
answers as truehue_mst_subject_skin_decisions.json, then tell the assistant its
saved filename/location. Do not prefill human answers from assistant notes.

Importer:

    venv\Scripts\python.exe scripts/388_import_subject_skin_review.py PATH_TO_EXPORT

It checks full manifest binding, completion, exact membership/order, image/mask
checksums, valid answers, original inputs and all saved display artifacts. It
preserves all 19 outcomes, actual prior answers and failures, and the original
new export; refuses overwrites. No automatic calibration/training admissions.

## Assistant inspection, separate from human judgments

All 14 new original/overlay/selected boards inspected. Beard/stubble remains a
concern in subjects12/14/15/5/8; subject13 has glasses and dark eye-region
uncertainty; subject7 has a small selected chin extension needing review.
Subject18 has a straight outer-side mask cutoff. Other cases still need their
own skin-boundary/lighting judgment; bright, profile and downward poses are not
silently removed. These are qualitative assistant observations, not dense truth
or actual human answers. Hair elsewhere on a face is not itself a measurement
failure; selected hair is the relevant question. Expected anatomical exclusions
are not holes to fill in measurement.

This is an eligibility study, not a correction-reference or lighting validation.
It cannot establish ten-category independent-person support: official categories
7/10 each have one person. Existing category9 concern remains. Stop after this
fixed review, preserve uncertainty and report support before any new research
decision. No replacement, radius/model/feature sweep or small clean-only fit.

## Verification and evidence

Scripts386/387 prepare fixed parents/alignment and reuse the frozen CPU inference
implementation; script386 finalises with independent saved-service replays.
Outputs include plan.json, baseline.json, inference_plan.json, inference.json,
manifest.json, verification.json, 14 logits and per-case input/mask/display files.
Prior inputs/masks copied exactly; source evidence hash checks passed before/after.

Seven focused importer tests passed in 0.38 seconds; one pytest cache-permission
warning, no test failure. JavaScript syntax passed. Isolated synthetic UI harness
resolved all new controls, blocked incomplete submission and permitted complete
export without saving human answers. This is a synthetic harness, not a real
browser interaction test. No broader pytest claim. All four contact sheets visually
inspected. No actual new review export yet. No calibration/tree fit, correction
mask/model/runtime change, reserved correction data, participant contact or new
dependency install. The isolated existing inference environment was reused.

Panel tracking: user-authorised expanded visual eligibility procedure and exact
reuse of parent artifacts, not dataset/model adoption or panel approval. Preserve
original-paper comparison for a future letter, and ITA + calibrated MST + facial
statistics to decision-tree gamma/red/blue correction.
