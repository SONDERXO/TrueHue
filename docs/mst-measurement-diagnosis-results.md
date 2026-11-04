# Why the current MST calibration is blocked

28 October2026. Completed the authorized saved-data diagnosis. No new image
opened, calibration fitted, mask changed or label assigned. [Fixed protocol](mst-measurement-diagnosis-protocol.md).

Two different failures require different remedies:

- **Subject support:** MST4,5,7,9,10each has one measured subject. Holding that
  subject out removes its category. Five folds therefore cannot construct a
  supported ten-category lookup; adding more photos of those same people would
  not add independent subject support.
- **Measurement/category ordering:** the other ten folds pool category centers.
  Among100distinct-category subject pairs,66have the expected median ITA order
  and34are reversed. Five same-category pairs are counted separately. This is
  descriptive ordering, not classifier accuracy or a proof of impossibility.

All396saved ITA values reproduce from the saved rounded meanL*/b*; all396meanb*
values are positive. Thus negative-b quadrant ambiguity or a corrupted saved
formula does not explain this cohort's failure. This does not validate selected
pixels as skin or the source photos as calibrated color references.

The largest within-subject ITA range is121.645degrees (`subject_18`). Recorded
lighting groups also show large shifts:

| Subject | Official MST | Poorly-lit median ITA (images) | Well-lit median ITA (images) |
| --- | ---: | ---: | ---: |
| subject_18 | 1 | -34.796 (11) | 34.780 (22) |
| subject_6 | 5 | -67.146 (24) | 10.054 (33) |
| subject_13 | 2 | -72.136 (9) | -40.852 (16) |

Lighting labels are existing metadata, not controlled illumination measurements.
Pose, mask coverage, background/hair/glasses selection and capture conditions
are confounded. Earlier12board inspection showed those mask concerns; this
numerical audit does not identify a single cause or justify excluding poorly-lit
images after seeing their results. An application must face such conditions.

## Consequence for implementation

Retain MST as required, but do not create arbitrary gaps between pooled centers,
reuse historical thresholds or report a valid lookup. A larger correction tree
cannot repair an unvalidated upstream MST feature.

The next useful diagnostic is a predeclared comparison of measurement-region
quality on the already exposed fixed12board set: separate ordinary facial skin,
excluded anatomy/material and uncertain boundaries, using the original square
frames. It must preserve old labels and distinguish provisional development QA
from human/expert truth. Evaluate measurement changes only after references
are frozen; no mask/threshold sweep or lookup fitting follows automatically.
This would distinguish obvious region-selection defects from residual
photo-dependent variation more directly than another lookup fit. It is not
executed or counted as validated in this report.

Separately, a ten-category generalization claim needs additional independent
category support or an explicitly limited evaluation design. Do not equate
SCIN's case-level labels with known subject independence or usable facial masks.
Do not silently assign new MST-E calibration/evaluation roles. Both support and
measurement limitations remain, even if one is improved.

[All saved summaries/lighting groups/pairs](../outputs/mst_measurement_diagnosis_v1/summary.json) ·
[Subject CSV](../outputs/mst_measurement_diagnosis_v1/subject_summary.csv) ·
[Independent accounting](../outputs/mst_measurement_diagnosis_v1/verification.json).

Script140performs no fitting or image processing. Independent standard-library
arithmetic checks15subject medians/ranges and105subject pairs; input hashes
remain unchanged. Existing607-test result still applies; no runtime algorithm
changed during this report-only diagnostic. Original reviews/holds remain.
Android stays paused and CPM deferred. No handoff work was continued.
