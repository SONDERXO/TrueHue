# One focused review instead of seven batches

Review completed and imported on 29 October 2026: all 24 decisions validated,
5 accepted (4 with concerns) and 19 rejected. No new review request or fitting
admission. [Import findings and next comparison](focused-mask-review-import-results.md).

29 October 2026. The immediate manual task is now **24 training photos**, showing
only the reference photo and its existing face mask. The old 418-source pages
and scientific artifacts remain available but are not the current review task.

The predeclared selection contains eight fixed-hash successful pair candidates,
four high-occupancy masks, four large input/reference mask-change cases, four
unavailable-reference-landmark cases, two empty/insufficient-skin cases and two
single-face failures. Occupancy and retention are risk proxies, not confirmed
hair, clothing or background contamination. This purposive sample supports
diagnosis and cannot estimate representative mask or model accuracy.

For each image, choose accept, reject or uncertain and add concerns. Decisions
apply only to the shown reference and mask, not every distorted variant or
training eligibility. Use Export reviews to save a portable JSON backup, or
Copy decisions to share text. Local browser saving is best-effort. The page
supports navigation, filtering and enlarged panels. The complete original
board is optional when investigating a mask-change flag; distortion approval
is not required in this first pass.

Twelve other training sources with disjoint duplicate groups are reserved for
a later check after a mask candidate is frozen. They are not displayed now and
are not independent final evaluation: they already have pipeline exposure,
and people are not verified disjoint. Validation and final test remain closed.
All 36 sources come from the existing duplicate-screen-clear training queue.
No new raw images, features, distortions or model fits were generated.

After annotations, identify recurring reference/mask problems, declare one
specific mask change and compare it against the preserved baseline on these
same 24 sources. Check a frozen candidate on the reserved training sources
before broader use. Additional manual requests should focus on ambiguous or
changed masks rather than returning to all 418 photos. Unreviewed sources stay
unapproved; exploratory correction experiments remain distinct from reviewed
evidence. No mask improvement or learned correction benefit is claimed yet.

- [Open the 24-photo review](../outputs/focused_mask_review24_v1/review.html)
- [Selection and reasons](../outputs/focused_mask_review24_v1/selection.json)
- [Predeclared selection and follow-up protocol](focused-mask-review-protocol.md)
