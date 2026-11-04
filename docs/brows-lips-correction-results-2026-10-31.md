# Eyebrows and lips in correction only

31October2026. User requested a small experiment: include eyebrows and lips when
correcting, but exclude them from ITA/MST measurement. Implemented as an opt-in
correction-support extension. Existing defaults, model and calibration stay
unchanged. Neck support is retained. Beard-specific work remains on hold.

## Try it

Open `outputs/brows_lips_correction_v1/review.html` for the21saved comparisons.
Panels: original; new correction pixels in pink; existing face+neck operator
demonstration; same settings with eyebrows/lips included. These use fixed
illustrative settings, not model predictions or measured neutral-color targets.

Double-click `run_face_neck_features_preview.cmd` to choose your own photo and
preview the separate regions. Green is facial measurement support, cyan is
neck correction support and pink is brows/lips correction support. This picker
shows masks and saves measurements, not a learned corrected output. The usual
`run_face_neck_preview.cmd` keeps its original behavior.

## Behavior and evidence

Only predicted left/right brows and upper/lower lips inside the selected facial
mask bounds are added. Eyes, glasses, mouth-interior and hair classes are not
added. The mouth is not filled as one solid polygon; teeth/mouth interior stay
out where the parser labels them correctly. Explicit protected pixels remain
protected. Parser predictions are not anatomical truth.

The21saved face/neck frames and category maps were reused without new inference
or refitting.20cases have added brow pixels,20have added lip pixels. Missing
predictions are not filled with guessed shapes. Facial binary masks and Lab/ITA
statistics remain exactly unchanged, so this correction-only option does not
change ITA inputs or the matching MST measurement contract. No MST lookup is
called by this experiment. Correction pixels outside the additions reproduce
the baseline exactly; identity settings reproduce the original.

All21boards were visually inspected. The added regions often cover the visible
brows/lips and remove their untreated appearance under the illustrative
settings. This is not a quantified perceptual-quality result. Some examples
have partial/missing eyebrow support, and a wider-framed diagnostic labels part
of head hair as brow. The existing face-covering error is not repaired. Skin-
derived gains/gamma can also change natural lip pigment, lipstick and brow hair
in undesirable ways. Predicted-class exclusion does not prove real teeth, eyes
or hair were protected. No mask approval, quality guarantee or automatic
adoption follows from this preview, and no parameter sweep was performed.

Full Python suite: **866passed in13.32seconds**, cache disabled. Seven focused
tests cover unchanged measurement/input masks, allowed additions, excluded
classes, explicit veto, selected-face bounds and baseline parity outside added
pixels. The opt-in CLI smoke on25517 completed and saved a local preview.

Implementation: `src/skin_masking/correction_facial_features.py`, script337 and
the opt-in flag in script336. Evidence:
`outputs/brows_lips_correction_v1/{plan,records,verification}.json` and saved
per-case masks/baseline/experiment images. No tree training, calibration change,
current-demo switch or synthetic-data regeneration occurred. Any future training
or evaluation using this wider correction region must declare it separately
from the facial measurement and generation/scoring supports.
