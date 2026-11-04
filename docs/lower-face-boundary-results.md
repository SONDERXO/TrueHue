# Lower-face boundary experiment

23 October 2026. Follow-up to [added-region review](added-correction-region-review.md).
Status: isolated experiment; not integrated or used for fitting.

Later user requirement: [include visible neck skin in correction](face-and-neck-correction-requirement.md).
This facial-only boundary intentionally removes neck support and must not be
promoted as the final face-and-neck boundary. Historical findings remain intact.

## Fixed rule

Restrict YCrCb candidate correction support to the landmark face oval **below
the nose bridge, landmark168**. Leave rows above that point unchanged, avoiding
a full-oval cut across the forehead. Reuse input-only face detection/landmarks,
existing material/hair checks and feature exclusions. Estimation masks, ITA,
model inputs/targets and generated images are unchanged.

The candidate can only remove selected pixels. Reject the boundary explicitly
if less than75% of its input support would remain. This fixed development guard
is not validated landmark confidence; failure is reported, never silently
replaced by the original support. Full-oval area is also recorded as a diagnostic.

## Outcome

- All38 square development attempts had an available bounded support.
- All retained at least87.61% of the incoming support.
- All48 original-point clean/color-shift probes were available and selected
  exactly the same points before/after the boundary:12/12 skin,0/3 paint and
  0/5 other points in each variant; hair remains1/4 clean and0/4 shifted.
- Source83184 was checked separately at its original224 resolution, clean and
  globally shifted, without entering training. Its full oval retained only
  6.63%/6.13% of incoming support. The lower-face rule would retain10.26%/10.64%,
  so both were explicitly rejected by the guard. The geometry problem is not
  repaired or diagnosed by rejecting it.

Codex inspected all38 rows on eight boards. Visible clothing/collar/neck spill
is reduced in12288,22211 and62331. However, some side-face/lower-jaw skin is
trimmed too, including edges in51739 and6236. Upper-side and eye-rim errors
remain possible because this restriction deliberately leaves upper rows alone.
Preserving the selected skin points does not establish preservation of all skin.

## Coverage tradeoff

The boundary removes103,715 pixels across repeated variants:87,884 inside and
15,831 outside the generation regions. These counts are not independent samples
or annotated skin/non-skin areas. Generation support itself includes some
non-facial pixels, so neither count is a true-positive/false-positive measurement.

The same exploratory training retention screen falls from27 to19 passes.
This flags a substantial mismatch with the generation region; it is not by
itself proof of worse facial segmentation. Visual edge losses still prevent
automatic adoption. Do not remove hard cases to claim a better average score.

## Decision

Completed follow-up: [additions-only boundary](additions-only-boundary-results.md)
preserves all baseline support and retains useful recovery while limiting new
lower-boundary spill. Baseline errors remain; candidate is not integrated.

**Keep this candidate experimental.** It demonstrates that spill can be removed,
but the unrestricted lower-oval cut also removes some baseline facial coverage.
No mask, cohort, review label, runtime policy or correction model was replaced.

Next, test a separate **additions-only** boundary hypothesis: retain the original
HSV-and-YCrCb correction support, then constrain only the extra support proposed
by YCrCb-only masking. That preserves baseline support by construction while
testing how much useful extra skin can be retained without the new spill.
Existing baseline errors would remain explicit; this is not a complete mask fix.
Keep geometry rejection and hair/paint regression checks and do not describe
either rule as an approved thesis-method change.

## Evidence and verification

- [All comparison boards](../outputs/lower_face_boundary_v1/review-index.md)
- [Per-pair measurements and sentinel results](../outputs/lower_face_boundary_v1/summary.json)
- [Visual assessment](../outputs/lower_face_boundary_v1/visual_assessment.json)
- [Saved-mask checks](../outputs/lower_face_boundary_v1/verification.json)
- Script: `scripts/58_test_lower_face_boundary.py` (refuses overwrite).

Verified38 saved subsets, unchanged upper bands, removal counts,48 unchanged
point outcomes, both explicit sentinel rejections and tracked input/model/review
hashes. Six new tests check forehead preservation, anatomical holes, no additions,
large-loss rejection and invalid geometry. Full suite: **460 passed**.
