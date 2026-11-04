# Frozen endpoint candidate: full-path JPEG check

30 October 2026. Reuse the exact 141 saved lossless/JPEG95/JPEG85 inputs from
the fixed-support sensitivity check. Rerun square-frame detection, original
HSV/YCrCb rule mask, required landmarks/complete-mouth exclusion, Lab/ITA,
experimental MST, endpoint features and direct-gamma correction. Use the same
source-held tree per pair. No training, threshold or recipe changes.

Keep the original reference scoring masks, so changing input support cannot
hide poorly corrected reference pixels. Save failures with their exact stage;
never reuse old features, masks or outputs after failure. Report successful
denominators alongside all 47 attempts per encoding. Count correction changes
relative to decoded input. Report detection/measurement failure separately
from clean overcorrection, and compare success subsets with their own unchanged
inputs. Do not silently count failed cases as safe successful identity outputs.

Measure original-mask agreement and parameter changes against fixed-support
results, but treat overlap as diagnostic agreement, not skin-mask accuracy.
Existing human approvals apply only to original saved masks. New compressed or
remeasured masks do not receive inferred approval or training eligibility.

Verify frozen hashes, replay face detection, reconstruct successful masks and
anatomical exclusions from captured frame-local landmarks, recompute features,
routes, output pixels and metrics, verify held-source separation and account for
all 141 attempts including explicit failures. No automatic demo replacement,
reserved data, new calibration, photographer evaluation or review request.
