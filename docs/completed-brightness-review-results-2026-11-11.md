# Completed brighter-capture review audit — 11 November 2026

All thirty actual user reviews are saved: 32 immutable revisions, 30 distinct
captures, ten publisher subjects and all three 1200 conditions per subject.
All thirty latest records explicitly review the selection and have valid
measurements; there are no missing cases, unjudgeable latest records or failed
save jobs (32 successful jobs). All six historical unavailable cases now have
valid manual records, including the three empty starts. No further user reviews
are needed for this queue. Unchanged selections 01, 03 and 17 have explicit saves.

Script 765 verifies every revision's bundle/task/label/group provenance, stroke
replay, exact mask, changed-pixel and stroke counts, Lab/ITA and job-result joins.
All checks pass. Independent direct OpenCV Lab means and scalar ITA calculations
agree with saved statistics. The minimum latest selected count is 9,556 normalized
pixels; the original 1,000-pixel guard is unchanged. All 32 revisions are retained.
Private results: `outputs/brightness_annotation_audit_v1`.

All six contact sheets / thirty comparison panels were viewed. User selections
provide broader facial support than many fragmented automatic seeds, including
formerly empty cases. Low original image detail, facial-hair/hairline boundaries
and glasses remain uncertainties. User review is not independent dense pixel
truth, official MST-category validation or proof of prediction accuracy.

The actual reviewed L* range is 14.3583–61.5026. Seven of the fourteen photographic
roles remain above this maximum. Thus the manual data improve available reviewed
brightness coverage relative to the previous set but do not establish full
photographic transfer. No MST labels are inferred for photographic inputs.

The new queue method is
`9a9ff905dd774e24deb7f368de18301ea332daf8c222f796fa736eb6435b3798`.
Its upstream screen identity differs from the older 600-condition queue. Next
work should verify shared measurement computation and prepare a compatible
sixty-row, ten-subject grouped validation design. All six conditions of a subject
must stay together; the additional thirty images are not thirty independent
subjects. Freeze a prospective comparison before any new fit; do not reuse old
coefficients, rerun closed assessments or admit brighter photographic
extrapolation on the basis of marginal ranges. No new fit is selected by this
audit.

Zero original-photo reads, image-model calls or fits occurred. Scientific
admission flags remain false. The demo and final decision-tree requirement are
unchanged. All prior artifacts and reviews are preserved. Final 24 and older
locked images remain byte-unread; no acquisition, contact, upload, commit or push.
