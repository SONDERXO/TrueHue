# Post-check face-containment development comparison

29 October 2026. The frozen YCrCb-only policy received4accept/16reject on its
separate training check and remains unpromoted. Tested one new, fixed geometric
refinement on those **now-exposed development cases**, preserving that outcome.
These sources cannot serve as untouched validation for the new candidate.

The new version constrains existing YCrCb color support to the frame-local
landmark face oval before largest-component selection, then applies the same
anatomical/complete-mouth exclusions. Color thresholds, morphology, detector,
landmark framing and minimum pixel count remain unchanged. No semantic parser,
per-image tuning, erosion radius, new hole filling or geometry fallback is used.
The contour is an implementation refinement, not a claim that the paper
explicitly specifies every landmark detail.

| Diagnostic | Earlier YCrCb policy | Contour candidate |
| --- | ---: | ---: |
| Available reference measurements | 18/20 | 18/20 |
| Available color-probe measurements | 18/20 | 18/20 |
| Reference pixels selected outside predicted oval | 120,595 | 0 |
| Color-probe pixels selected outside predicted oval | 80,637 | 0 |

The outside-oval result is a construction invariant, not measured semantic
accuracy. Across both frames,201,500previously selected pixels are removed,
including component-order differences. Removed pixels are not all confirmed
background or hair; a predicted oval can also miss valid facial skin.
All four earlier accepted source pairs change, so their labels cannot be
transferred to the new masks without regression review.

Local visual inspection shows reduced selection beyond the jaw/sides on38620
and20196, but also concrete remaining limits. On57961, part of a hand overlaps
the facial contour and remains selected. On38620, hair inside the predicted
contour can still be included. The method cannot distinguish all same-colored
occluders using containment and fixed color thresholds. Missing landmarks,
holes, eye/glasses boundaries and source blur are not automatically resolved.
Do not call a technically available mask suitable or a larger region correct.

Packaged the candidate under its own dependency-bound measurement identity.
No existing MST thresholds are applied to its changed pixels. Replayed all40
earlier candidate reports exactly before comparing. Independent reconstruction
verifies37geometry-available masks, retains3missing-geometry frames, accounts
for all40frames and preserves all20old decisions/notes. Insufficient support
remains a failure even when geometry exists. The full suite passed
**768 tests in21.32seconds**.

No new human labels were inferred, no active mask/model was replaced, and no
calibration, target fitting, regression training or final validation/test access
occurred. No new full20-photo review is requested merely from pixel removal.
The candidate still needs semantic/source-suitability evidence before promotion.

Next development should explicitly distinguish clear facial references from
occluded/foreign-object cases and retain fail-closed fitting exclusions. A
geometric boundary is useful for containment but cannot justify admitting known
hand/hair contamination. Any further candidate tuned on these notes must be
reported as development and evaluated separately before a calibrated model is
claimed. The thesis's ITA/MST/decision-tree architecture remains unchanged.

- [Development comparison boards](../outputs/postcheck_contour_development_v1/review.html)
- [Full measurements and unchanged prior labels](../outputs/postcheck_contour_development_v1/attempts.json)
- [Summary](../outputs/postcheck_contour_development_v1/summary.json)
- [Verification](../outputs/postcheck_contour_development_v1/verification.json)
- [Frozen experiment protocol](ycrcb-contour-development-protocol.md)
