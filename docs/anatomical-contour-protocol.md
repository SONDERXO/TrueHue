# Fixed anatomical-exclusion and contour protocol

26 October 2026. Fixed before candidate execution. Development ablation only;
no runtime adoption, synthetic regeneration, training admission or fitting.

Diagnosis on the two annotated clean256 references found no selected pixels
inside the recomputed existing feature exclusions. All805/1059 selected
reference-exclusion pixels lie outside those polygons. Full-frame remapping is
consistent with the saved generation masks. Landmarker feature boundaries are
narrower/misaligned relative to the supplied broader eye/brow references; this
is not evidence of a crop-coordinate bug. Landmarked oval and detector/color
constraints also restrict the cheek. No annotations enter candidate inference.

Two arms, fixed once with no parameter sweep:

1. **E, exclusions only:** retain existing feature/mouth exclusions and add an
   elliptical margin to each eye/brow polygon. Radius is ceil3% of inter-eye
   center distance, minimum1pixel. Apply removal to source generation, input
   measurement and correction. Mouth rule unchanged.
2. **EC, exclusions plus contour:** E for measurement. For generation/correction,
   union additions no farther than ceil2% of the larger detector dimension from
   existing support, within the same margin of the landmark oval, and inside
   the detector rectangle padded by that amount. Require predicted face-skin
   class3 and the existing relative-Lab distance<=3 with scale floors12/6/6,
   using at least1000 E-filtered measurement seeds from the actual input.
   E exclusions override all support. Existing material/semantic removals
   remain; added pixels deliberately bypass absolute HSV/YCrCb thresholds.
   This is a substantive experimental policy change, not threshold tuning.

Reuse the prior geometry gate: at least75% of padded YCrCb+semantic candidate
support must lie in the unexpanded oval. Missing landmarks/single-face failures
or failed geometry/seeds give explicit unavailability; no eligible fallback.
E may still be measured separately where EC is unavailable. New geometry is
predicted from each actual input, never transferred from its reference.

Fixed scope: exact32 saved candidate inputs across9 sources, nine clean
generation sources, original24 labeled point probes across clean/global-shift
native frames (48 observations), three completed polygon references, and83184
clean/shift geometry sentinels. Include historical failures explicitly; no
replacement sources, new exposure, reserved data, label edits or silent folds.
Native paint frames stay224; all other frames retain their saved dimensions.

Score both arms against the unchanged reference classes, with full and
one-pixel-interior sensitivity. Report removal of labeled skin separately from
reduced exclusion overlap, and new labeled exclusion/unlabeled additions.
Retain native hair/paint point results at generation/measurement/correction,
including unavailable denominators. Check all32 measurement statistics and
frozen brightness features, masks, original-generation retention, and saved
input/source/model/ledger/human-decision hashes. Review all changed source/input
boards. Pixel additions are not assumed to be valid skin.

Inputs remain those generated with the OLD masks: compare prospective source
generation masks and saved-input measurement/correction diagnostically. No
claim of a consistently regenerated training set follows. Old decisions and
technical holds stand. No pass threshold is invented from these3 references;
report tradeoffs and failure cases before proposing further work. Neck remains
unlocalized, MST/final data/split/expert/Android requirements unresolved, and
this protocol does not amend the thesis proposal.
