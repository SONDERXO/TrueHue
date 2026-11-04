# Single-factor YCrCb color-cast refinement

Review complete: six accepted, two rejected; four acceptances have notes.
14418 is rejected for background inclusion despite its retention gain. Preserve
foreign-object, holes, earrings and source-blur concerns. No global adoption
or calibration transfer. [Exact review findings](color-cast-ycrcb-review-results.md).

29 October 2026. Investigated the20color-only input failures from the new
three-variant cohort. On14418,99.9%of the original reference support passes
the existing YCrCb bounds after the color shift, but only25.7%passes HSV.
Other sources show the same direction of gate loss. Reference support supplies
diagnostic evidence only, not candidate construction or input features.

Tested one fixed refinement: remove the extra HSV intersection and use the
paper's detailed face-constrained YCrCb-only rule. Keep detector boxes,
frame-local margin landmarks, existing Cr/Cb thresholds, morphology, largest
component and complete anatomical exclusions unchanged. No parser, threshold
search, per-image tuning, extra filling, oval constraint or reference fallback.

| Color-input diagnostic, same20sources | Baseline HSV AND YCrCb | Candidate YCrCb only |
| --- | ---: | ---: |
| Existing support-screen passes | 5 | 14 |
| Total pixels outside predicted facial oval | 58,904 | 97,052 |

Nine sources change from screen-fail to screen-pass; none changes in the
opposite direction. However, predicted outside-oval selection increases, so
retention gains cannot be called segmentation accuracy or automatic acceptance.
The oval is diagnostic predicted anatomy, not human ground truth. Original
reference masks and their accepted concerns are also not perfect pixel labels.

Both the reference and color-input frame were processed for every source,
using their own geometry. All40baseline masks replay exactly. All40candidate
masks, raw color masks and anatomical exclusions are saved and reconstructed
independently. Original reference notes remain visible. 14418regains facial
support in the inspected candidate, while66413still illustrates facial-hair
and side-boundary risk. Neither observation overwrites the user's old labels.

## Small review packet

Prepare8existing photos, not a new source batch: six fixed-hash retention
gains plus two risk cases from the predeclared selection rule. IDs:
14418,75166,20648,72595,34227,68073,75898,66413.
This purposive subset is not a representative validation sample; all20results
remain recorded, and all unreviewed masks remain held.

Each page item shows six panels: reference photo, reference baseline,
**reference YCrCb candidate**, color input, input baseline, **input YCrCb
candidate**. Accept only if both candidate masks are usable; otherwise reject
or choose uncertain and specify the failing panel/concern. Export reviews to
preserve a portable backup. Existing acceptances apply only to old pixels and
are not transferred onto the new candidate references.

Candidate review is the prerequisite to freezing this policy. After a justified
freeze, run the separate training check and verify a matching measurement
contract/MST calibration before using new masks in correction training. The
old lookup is not calibrated for this candidate definition; no candidate ITA,
MST, target fitting or tree fitting occurred in this step. Active masks/models,
the12reserved sources, validation and final test remain untouched.

Artifact checks verify40candidate reconstructions,40baseline parity comparisons,
all8selected IDs and six-panel labels. Mock-DOM checks cover scoped annotation,
notes/navigation and export. No algorithm module changed; the last full suite
remains762passing tests. Boards were inspected locally; no interactive-browser
visual check is claimed.

- [Review the8changed/risk cases](../outputs/color_cast_ycrcb_refinement_v1/review.html)
- [Full20-source results](../outputs/color_cast_ycrcb_refinement_v1/summary.json)
- [All frame measurements](../outputs/color_cast_ycrcb_refinement_v1/attempts.json)
- [Verification](../outputs/color_cast_ycrcb_refinement_v1/verification.json)
- [Frozen single-factor protocol](color-cast-ycrcb-refinement-protocol.md)
