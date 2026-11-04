# Seamless whole-face support: one fixed implementation

User authorized filter-like contour/edge improvements while retaining separate
ITA/MST measurement. Keep the current whole-face binary contour, associated
neck and nostril-guarded measurement unchanged. It already has no anatomical
holes inside the face. Do not fill holes outside the permitted contour into
hair/background/clothing merely to make a smooth-looking overlay.

Use one inward-only distance-transform alpha on the COMBINED face/neck support,
with smoothstep across max(2,ceil(3%facewidth))pixels. No width sweep. Opacity is
zero outside permitted support/protected pixels and full-strength in the
interior. Do not feather face/neck independently, which would create a seam at
their join. Keep original binary support, measurement mask and alpha as separate
artifacts. A face mesh/parser can still put the contour in the wrong place;
feathering does not validate its placement or repair color-parameter errors.

Compare hard and soft application on the same16staged reference frames with
the same illustrative parameters(.85,1.05,.95). Reuse saved whole-face masks;
no source re-selection, parser inference, MST/calibration/tree fit or parameter
sweep. Report geometry/gaps remaining honestly. Identity and outside-region
pixels must be exact; measurement contract stays unchanged. Default photo
preview may show the new blended operator clearly labelled as demonstration.
Existing model demos remain unchanged. Previously fitted hard-mask targets and
generation/scoring assumptions cannot be silently declared blended-operator
targets; future training must record the alpha/operator contract explicitly.
