# Reviewed-source semantic mask candidate

Completed candidate review: 12 accepted, 11 rejected, 1 uncertain. Eight baseline
rejections became accepted; 66413 regressed from accepted to rejected due to
facial hair. Exact concerns remain preserved; no promotion or reserved-check
access. [Paired review findings](focused-semantic-mask-review-results.md).

29 October 2026. Implemented a separate semantic mask candidate to address
the reviewed background/clothing spill and inadequate facial coverage. The
existing local 19-class face parser selects predicted skin/nose only inside
the unchanged single-face detector box. It excludes the parser's other classes
and does not require MediaPipe landmarks. A removal-only arm intersects those
same predictions with the saved baseline to distinguish spill removal from
coverage additions. No hole filling or threshold tuning was performed.

| Candidate outcome | Reviewed sources |
| --- | ---: |
| At least 1000 selected pixels | 21 |
| Below 1000 pixels: 13718, only 84 selected | 1 |
| Single-face failures remain excluded: 31367, 20653 | 2 |
| Total | 24 |

These are technical support counts, not suitability approvals or accuracy.
All five previously accepted masks change and need regression review. Original
decisions and qualified concerns remain intact. The candidate can generate
support on reference landmark-failed cases, but it cannot retrospectively
turn the baseline's failed ITA/features into valid measurements.

Visual inspection of selected boards shows plausible gains: 32903 loses much
of the previously selected background/clothing, and 12559 gains substantial
facial support missing from the color-threshold mask. However, 9149 selects
mostly chin pixels beneath glasses (4481 pixels), demonstrating that passing
the pixel minimum does not ensure adequate coverage. The grayscale/occluded
55166 image also illustrates why recovered mask support is separate from a
suitable photographic correction reference. No human candidate labels or
pixel-level ground truth establish an improvement rate yet.

The comparison page displays reference, saved baseline, removal-only diagnostic
and semantic candidate. Review the **rightmost candidate**, keeping the exact
original note visible. Accept/reject/uncertain applies only to candidate
reference-mask suitability. Reviewing these same sources adds no new unique
photos to the 96-photo development budget. The 12 reserved training-check
sources remain uninspected for candidate design; validation and test remain
closed. Do not expand to the remaining 418 sources or promote by area alone.

The parser and candidate have frozen model/dependency hashes and a separately
versioned support definition. **The existing MST lookup is not calibrated for
these different pixels.** No candidate ITA/MST calls, distortion regeneration,
correction-tree fits, automatic admissions or active-model changes occurred.
Any later adoption requires a new measurement contract and calibration checks.
The dense parser's Android cost/portability remains unresolved.

Scripts 216/217 retain all 24 attempts and reconstruct both candidate arms from
saved categories for the 22 parser-available cases, verify no additions in the
removal-only arm, count changes and check unchanged source/dependency hashes.
All checks pass. Seven new guard cases bring the full suite to **731 passed
in 34.43 seconds**. Mock-DOM checks verify comparison labels, scoped decisions,
saved notes and export. Boards were visually inspected as local images;
interactive browser QA remains unavailable.

Next: annotate the candidate comparison, freeze or reject this candidate based
on observed spill/coverage regressions, and only then open the separately
reserved training check. No new review of the full seven batches is needed.

- [Compare the same 24 photos](../outputs/focused_semantic_mask_comparison_v1/review.html)
- [All candidate records](../outputs/focused_semantic_mask_comparison_v1/attempts.jsonl)
- [Summary](../outputs/focused_semantic_mask_comparison_v1/summary.json)
- [Verification](../outputs/focused_semantic_mask_comparison_v1/verification.json)
- [Predeclared protocol](focused-semantic-mask-protocol.md)
