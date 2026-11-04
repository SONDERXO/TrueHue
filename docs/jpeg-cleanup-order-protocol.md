# Fixed cleanup-order application-support comparison

30 October 2026. Stage tracing reconstructs all 141 full-path masks. At JPEG95,
12,122 original selected pixels are removed by morphology; JPEG85 loses 11,150
there and another 11,588 through component selection. HSV-only rejection also
contributes substantially. This motivates one fixed order comparison, not a
threshold or kernel search.

Compare original open/close/close with close/open/close. Retain the exact HSV
AND YCrCb ranges, ellipse 5x5 kernel, total two closes/one open, largest connected
component and current required anatomical/complete-mouth exclusions. Initial
closing may bridge narrow color-qualified regions before opening removes them;
it can also add non-skin, so no correctness guarantee is assumed.

This candidate changes correction application support only. Original full-path
measurement masks, Lab/ITA/experimental MST, endpoint features, frozen source-
held tree parameters and original reference scoring masks remain fixed. A new
estimation-mask/lookup contract is not created or silently reused. Candidate
support must have the existing 1000-pixel minimum; failure produces no candidate
output, never a fallback. Apply exactly the original direct-gamma parameters.

Use all 141 existing inputs, current face boxes and captured geometry. Report
lossless/JPEG95/JPEG85 separately, including successful denominators, corrected
and unchanged errors, support lost/added against baseline, reference-mask missed
pixels and additions outside reference support. These are agreement diagnostics,
not human skin labels. Do not infer acceptance or train on new masks.

Verify both cleanup paths by explicit reconstruction, identical color gates,
anatomical exclusions, frozen features/parameters/source separation and output
pixels/metrics. Inspect largest support changes. No model fitting, feature/
threshold/order search, source exception, reserved data or demo replacement.
The order change is an engineering development hypothesis, not a recipe quoted
from the proposal. Retain failed outcomes and existing clean-safety gate.
