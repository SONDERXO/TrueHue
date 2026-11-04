# Whole eyebrow-area skin during correction

1November2026. User clarified that the whole surrounding skin area should be
included for correction, because it is skin. The earlier narrow peribrow band
was insufficient. This revision restores eligible skin across the full
anatomical eyebrow-exclusion polygons, not a progressively enlarged band.

The correction helper adds predicted skin/nose inside those complete polygons
and the selected facial outline, with a separate eye-landmark veto and explicit
protected-pixel exclusion. Brow hairs and lips remain in correction support;
neck behavior is unchanged. Parser mistakes can still omit true skin or label
an object incorrectly; “all eligible pixels” refers to this explicit rule,
not ground-truth proof of every actual skin pixel.

ITA/MST measurement masks stay byte-identical. No lookup or calibration was
changed. The preview colors the surrounding skin GREEN as part of facial
correction support; brows/lips remain pink and neck cyan. Green is a correction
overlay, not a claim that every green pixel enters measurement. The separate
facial measurement mask is saved unchanged.

Run `run_face_neck_features_preview.cmd` as usual. Current16-reference comparison:
`outputs/complete_brow_area_v3/review.html`. Its panels are original, updated
correction overlay, previous operator output and updated operator output. Fixed
illustrative settings are used, not a learned model prediction.

All16available staged references gained coverage beyond version2. Saved parser
maps were reused; landmarks were rerun and independently reproduced all16old
semantic facial masks exactly. Every eligible brow-area skin pixel is now in
correction support, and output differences stay within newly added pixels.
The six-anchor contact sheet was visually inspected and shows the previous
brow-area gaps covered. There is no new user mask approval or quantitative
perceptual-quality claim. The standalone CLI smoke on25517 also completed.

Full Python suite: **881passed in22.50seconds**, cache disabled. Two new tests
cover skin far from the predicted brow hairs across the full exclusion polygon,
unchanged measurement support, eye protection and protected pixels.

Earlier version1/version2cohort, pair and review artifacts remain historical.
Their source/facial judgments remain scoped-useful; correction-support
decisions do not transfer to this version3mask. The current review page is
labelled as the previous correction version. Do not train with old version2pairs
as though they used version3. No pair-generation/training/calibration loop was
repeated for this repair. A later data update should use this fixed design and
preserve source/facial choices rather than ask for those judgments again.

Implementation: `src/skin_masking/complete_brow_area.py`, script349 and the
existing photo-picker script336. Evidence: `outputs/complete_brow_area_v3/`.
The previous narrow-band implementation is retained as history. Both correction
demos, model presets, reserved data roles and beard-specific hold remain.
