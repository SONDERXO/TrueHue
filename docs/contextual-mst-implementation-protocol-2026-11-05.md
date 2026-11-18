# Authorised contextual MST software experiment — 5 November 2026

User explicitly selected “Test ITA + Lab mapping candidate” in response to the
method-choice question. This supersedes retention of an ITA-only lookup only
for the isolated experimental comparison defined in the method-choice document.
It does not authorise production/category replacement, real unadmitted-data
fitting, adviser approval or removal of ITA/MST from the correction pipeline.

Implement the predeclared four-feature ridgealpha1 candidate, fixed ITA-only
ridgealpha1 ablation and fitting-subject median constant. Use exact decimal
strings as targets, preserved in results; no integer rounding. Each fitting
subject has total weight1, shared across that subject's available photos, in
both weighted population-variance standardization and regression. Ridge objective
is sum_i w_i(y_i-intercept-z_i beta)^2 + sum_j beta_j^2. The intercept is unpenalized.
Use exact constant-column detection and scale1 to avoid roundoff masquerading
as nonzero variance. Store fitting means/scales, coefficients and intercept.

Hold all photos of one subject out together. Fit only available measurements
from the other subjects; no fitting features/labels from held subjects. A fold
without any fitting measurements produces unavailable predictions, not guessed
scores. A fold with very limited support may execute mathematically; this is not
an adequate-cohort claim, so actual subject/row support stays in fold reports.

Use the four original-pixel feature names exactly; reject extra reference or
lighting features, missing admission declarations, mixed contracts, conflicting
subject scores, duplicated IDs and invalid/nonfinite values. A true admission
flag is a declaration, not independent evidence: real cohort eligibility and
the admission report still require verification before any real invocation.

Predictions retain raw values and explicitly clip diagnostic scores to1–10.
No integer-category/MSTindex export or production artifact is supplied. Include
image/equal-subject MAE, unavailable counts, condition breakdowns, descriptive
score intervals and per-subject prediction ranges. Baselines share exact rows.

Validation now uses generated arithmetic fixtures only: six fictional subject
IDs with three fictional reporting conditions each. Their numeric features are
software fixtures, not simulated skin/physical lighting or real label admissions.
No Stellenbosch measurement rows may be fitted, no cohort split is assigned,
and no image/model inference is needed. Save a deterministic fixture replay with
source/protocol hashes in a new ignored package. Keep old lookup/calibrator,
tree/Android interfaces and all private dataset packages unchanged.
