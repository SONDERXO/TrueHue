# One zero-face detection fallback comparison

6 November 2026. User authorises one targeted mask-reliability change after the
input-derived check. Saved evidence: 30 source-anchor and 18 crop-redetection
failures all report zero faces; the other 13 failures are not detection failures.
Freeze a fallback ONLY when the existing original-BGR detector returns zero boxes:
apply existing fixed Lab-L CLAHE clip2/grid8 to a separate 256 BGR copy, retry the
same detector once at confidence0.85, accept exactly one box, otherwise fail.
Never retry multiple-face detections, lower thresholds, fill masks, change parser,
landmarks, FaceOcc, pixel guard, measurement pixels, gate or correction model.
Boxes from the appearance copy refer to the same unwarped coordinates.

Reprocess only the 48 preselected zero-face failures from the same exposed
336-case batch. Other 288 cached cases, including 23 clean cases and 13 other
failures, stay byte-identical/reused. One originally failed clean case is among
the 48 targets and is rerun; this is not a fresh full clean inference run.
The initial metadata assertion assumed no clean target and stopped before any
pixel decoding/output creation; corrected from saved records before execution.
Both detector stages may use the identical zero-face fallback rule. Record calls,
original and enhanced boxes/input hashes, original-colour measurements and all
failures. No replacements, tuning or additional cases after results.

Use the same fixed correction bundle and direct native224 renderer, compare
unchanged / old input-derived / fallback input-derived on common original-native
reference regions and full scenes. All 336 attempts retained; failed correction
returns unchanged. Original failure reference stays unavailable, even if detection
recovers. Gains in availability or overlap are not skin/object accuracy.
Inspect all 48 targeted original/input/mask/output comparisons, including failed
recoveries. Audit original vs candidate support and changes outside original
support (not automatic object truth), geometry consistency, originalRGB features,
portable predictions, output/metric/hash replay. Existing exclusions remain; no
new human labels or false admissions. No fitting or Android/runtime adoption.
Dataset private research/noncommercial/citation/no redistribution terms retain.
Stop after this single comparison, even if negative.
