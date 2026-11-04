# Focused paper color-rule diagnostic

29 October 2026. Compare the existing HSV AND YCrCb color rule with the
detailed proposal's YCrCb-only rule on the already reviewed 24 training sources.
Use the exact existing Cr133..173/Cb77..127 bounds from script 56, same 5x5
ellipse open/close/close, and the saved oval/anatomical exclusions and face
boxes from rule_mask_ordering_v1. No new threshold selection or landmarks.

Both arms constrain color support before selecting the largest component and
apply anatomy exclusions afterwards. Missing saved geometry yields unavailable,
not a rectangle or parser fallback. Record reference-source exclusions and
all mask counts. No reserved, validation or test sources; no ITA/MST, targets,
model fits or adoption. Greater area is not accuracy and may add non-skin.
The existing MST lookup does not apply to changed measurement pixels.

Save both arms and added-pixel maps, reconstruct the old arm exactly and
retain original evidence. Diagnose missing masks by stage rather than calling
every failure "no face". This is a fixed diagnostic, not a newly approved
masking policy or correction-quality evaluation.
