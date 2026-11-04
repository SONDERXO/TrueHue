# Face and visible-neck support — 31 October 2026

A working, separately versioned face-plus-neck correction-support candidate is
implemented. It selects neck pixels beyond the facial mask and can apply the
same correction settings to both regions. Facial measurement pixels and ITA
remain unchanged. This is a preview, not adoption of a reliable correction model
or proof that neck coverage is complete.

## Open the result

- Fixed21-case gallery: `outputs/face_neck_support_v1/review.html`.
- Choose another photo: double-click `run_face_neck_preview.cmd`.
- CLI: `venv\Scripts\python.exe scripts/336_preview_face_neck_photo.py --image "photo.jpg" --open`.

The standalone tool shows facial support in green and neck support in cyan,
with separate binary files and a report. It runs no correction tree or MST
lookup and never overwrites the original. ITA statistics use only facial skin.
If detection, required landmarks or facial measurement fail, it saves a failure
report without inventing neck/body support. Canceling the picker exits.
The old face-mask preview and both correction demos stay unchanged.

## What was implemented

The existing parser already has a neck class. A new helper associates its neck
components with the selected lower face using the geometry declared in the
[fixed protocol](face-neck-support-protocol-2026-10-31.md). It does not expand
generic skin into a larger rectangle, fill forbidden classes or use the clean
reference at runtime. Neck pixels remain separate from facial measurements.

Predicted clothing, jewelry, hair, ears and background classes cannot become
new neck pixels. Explicit protected pixels are excluded from correction. A
missing associated neck produces a recorded unavailable status and face-only
support, rather than a body-skin fallback. Single-face selection is required.
The parser has no separate beard/paint/tattoo class. Pixels it mislabels as neck
can still be included. No additional beard model was enabled.

## Fixed check and honest limits

21 already exposed frames were used: six accepted reference masks and15 fixed
MST-development diagnostic attempts. Six category maps were reused;15 were
computed for this new neck step. These were not new calibration/correction
training examples, and no reserved evaluation pixels were opened.

All21 produced a nonempty candidate neck region. That is availability, not
21approved masks or proof that visible neck is always present. No-neck and
multiple-person behavior were tested synthetically; this set does not establish
real-world absence detection. All21 contact-board rows were visually inspected.
Visible neck is selected below the jaw in wider-framed examples and narrow neck
strips in several tight crops. Hair/clothing boundaries often appear useful,
but conservative horizontal bounds can omit lateral neck skin; no guarantee of
complete neck coverage follows. Tattoos remain selected in subject_0's neck.
The existing subject_7 facial face-covering error also remains. These are
assistant observations, not new user decisions or ground-truth scores.

The gallery compares face-only and face+neck application using exactly the same
fixed direct-gamma/red/blue settings (.85,1.05,.95). These are illustrative
operator settings, not learned predictions, reference-fitted settings, a proposed
default or proof of improvement. Face/neck lighting differences and hard support
boundaries can remain visible. No smoothing, reconstruction or neck-to-face
color matching was introduced. No parameter/geometry sweep followed inspection.

The existing paired dataset has facial generation support only. Applying
correction to an undistorted neck would not provide a valid neck-reconstruction
experiment. Future paired preparation must separately bind reviewed neck
generation/scoring support before claiming neck improvement. The six facial
approvals are not neck approvals. No additional review is requested here.

## Verification

- Full Python suite: **859 passed in12.93seconds**, cache disabled.
- Thirteen new focused tests cover extension below the face, unchanged
  measurements, predicted non-neck exclusions, disconnected unrelated neck,
  explicit protected pixels, no-neck fallback, multiple-face failure and shared
  operator behavior.
- All21 facial masks and Lab/ITA statistics remain exact. Identity settings
  reproduce inputs; outside-support pixels remain exact; face-only and shared
  correction produce identical corrected facial pixels.
- The standalone CLI smoke on25517 reproduces the batch face and neck masks
  exactly. Saved source/code hashes and semantic measurement contract match.

Implementation: `src/skin_masking/face_neck_support.py`, scripts335–336,
`tests/test_face_neck_support.py`. Evidence: `outputs/face_neck_support_v1/plan.json`,
`records.json`, `verification.json` and separate per-case masks/images.
Semantic measurement contract remains
`f128f543377efab22930e5c60b4c20efd4c5f386d951a645818ca5c2a6265828`.
No calibration fit, tree fit, lookup change or deployed-model switch occurred.

## Next boundary

Include separate reviewed face and neck correction support in the next declared
paired-data/evaluation design. Preserve facial-only ITA/MST, region-specific
outcomes, unavailable necks and existing reference/occlusion holds. The neck
requirement remains unfinished until mask quality and corrected neck outcomes
are established; a working preview does not satisfy it by itself. Changes and
results are recorded without imposing an adviser-request prerequisite.
