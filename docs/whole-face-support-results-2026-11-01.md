# Whole-face correction and nostril-excluded measurement

1November2026. User explicitly requested everything inside the selected face
shape for correction, including hair across the face. Eyes, hair, eyebrows and
nostrils must be excluded from ITA/MST measurement. This supersedes earlier
correction cut-outs; lip/mouth/neck measurement exclusions are retained.

## Implemented behavior

The correction mask is the filled selected landmark face outline, plus retained
facial skin extending beyond it and the existing associated visible-neck support.
There are no anatomical/parser holes INSIDE the face outline. Therefore it also
corrects eyes, teeth, glasses, beard and objects crossing that area, as implied
by the requested whole-face policy. Explicit protected pixels can still override
correction. Hair outside the selected outline is not selected as whole-head hair.
The parser/landmarks can still produce boundary and identity errors.

Measurement is separate: predicted facial skin/nose with existing landmark
eye/brow/mouth and parser non-skin exclusions, plus a new conservative nasal-base
guard. The guard uses two supersampled nasal-base hulls from the installed
MediaPipe nose topology with a1pixel margin. It excludes nearby nose skin as
well as the estimated nostril area; it is not exact learned nostril segmentation.
No threshold or radius sweep was performed. Beard/hair misclassified as skin
can remain a limitation; no new beard-specific model was introduced.

New measurement contract:
`1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7`.
This is incompatible with the old semantic lookup. New reports explicitly leave
MST unavailable and block old-lookup reuse. A matching recalibration/evaluation
must precede MST-aware training or runtime adoption. No valid mapping or final
correction model is claimed by this support repair.

## Try the current version

Both `run_face_neck_features_preview.cmd` and `run_face_neck_preview.cmd` now
launch script350. The old script336 remains available for historical behavior.
Current gallery: `outputs/whole_face_support_v4/review.html`.

Panels: original, whole-face correction overlay, separate measurement mask and
fixed-setting operator demonstration. These are not trained-model predictions.
The source image is never overwritten. Detection/measurement failures produce
explicit reports; no old feature or lookup is substituted.

## Checks and results

-16staged references processed from saved images/category maps/landmarks. No
  new parser inference, calibration fit or correction-tree fit occurred.
- Every rasterized face-outline pixel is included in correction unless an
  explicit protection mask forbids it. Outside-support pixels remain unchanged.
- The conservative nasal guard removed382–669previously measured pixels per
  image. This is a pixel-count finding, not proof of exact nostril accuracy.
- All16contact-board rows were visually inspected. Hair/feature gaps inside
  the outline disappear, while eye and mouth/nasal measurement cut-outs remain.
  Background/other-person risks and existing reference-quality issues remain.
- Standalone CLI smoke on25517 completed with MST unavailable as intended.
- Full Python suite: **884passed in15.75seconds**, cache disabled. Three added
  tests cover whole-face inclusion, measurement exclusions, explicit veto,
  source-mask immutability and degenerate nasal-geometry failure.

An initial implementation snapshot was retained separately before strengthening
the measurement helper's explicit class/anatomy intersection. This was code
verification, not another model or threshold experiment.

## Data consequence

Earlier staged source-photo judgments still apply to the same photo bytes.
Earlier facial-mask and correction-mask approvals/features do not automatically
apply to this measurement/correction revision. Preserve old data and reports;
do not fit version2pairs or use the old lookup as though they represented
version4. The old review pages are historical. Do not request another broad
review until the current method and matching data are ready. No current desktop
or Android correction model/preset was switched.

Implementation: `src/skin_masking/full_face_support.py`,
`src/ita_estimation/nostril_measurement.py`, script350 and both neck preview
launchers. Evidence: `outputs/whole_face_support_v4/contract.json`, `records.json`,
`verification.json`; CLI smoke `outputs/whole_face_photo_7407173f62ab/`.
