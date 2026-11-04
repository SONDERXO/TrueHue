# R1 review imported and enclosed correction holes repaired

1 November 2026. User completed R1 and explicitly requested correction-hole
improvement. This authorises the correction-only repair despite the earlier
freeze on unsolicited mask sweeps. No measurement redesign or calibration.

Script357 imported the actual export in outputs/reference_readiness_r1/ with
exact manifest, membership and file verification. Original export, all decisions
and notes are preserved under outputs/reference_readiness_r1_import/. Preliminary
structured counts:10 photographic candidates,6 holds/rejections,2 technical holds.
These are not final eligibility or training admissions. Narrative concerns below
also remain unresolved even where a structured field says accept. Ten lighting
claims have no independently verified capture evidence; remarks such as "The
photo's great" do not establish calibrated lighting. No true-colour references
are verified by this audit. No user decision was rewritten.

| Source | Disposition / retained concern |
|---|---|
| 2434 | Source retained; masks accepted; covering marked present, contamination absent |
| 25517 | Source retained; masks accepted |
| 39083 | Hold measurement: facial-hair contamination marked present, despite acceptable appearance |
| 63509 | Correction rejected for eye/brow holes; enclosed holes repaired, no new approval inferred |
| 42965 | Accepted with eye-hole note; enclosed hole repaired, changed correction not automatically approved |
| 77101 | Accepted with forehead-edge gap note; outer notch remains unresolved |
| 62000 | Source and masks accepted, photographic candidate only |
| 29321 | Source and masks rejected; mouth/shadow concern retained; hole repair does not qualify it |
| 70911 | Accept fields but dark-reference concern: hold reference qualification pending evidence |
| 37251 | Accept fields but too-blurry note: hold reference qualification |
| 71429 | Source rejected as too bright |
| 9654 | Source and masks accepted, photographic candidate only |
| 69407 | Source and masks accepted, photographic candidate only |
| 35986 | Both masks rejected in fields; note says measurement good/correction lip hole; preserve conflict, hole repair is not approval |
| 74882 | Source/measurement rejected for glasses bridge selected as skin; no measurement repair or relabeling |
| 37071 | Accept fields but too-bright note: hold reference qualification |
| 59172 | Original semantic-association technical hold, no replacement |
| 67581 | Original104-pixel measurement technical hold, no replacement |

## Correction repair

New continuous_correction.py fills all enclosed background components in the
combined binary correction support. A padded exterior flood fill uses fixed
4-connectivity; there is no hole-size threshold, colour rule, outer dilation or
parameter search. Explicit protected pixels override filling. Measurement and
neck arrays are copied unchanged. The whole-face/nostril measurement module was
not edited; its code-hashed contract remains
1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7.

Script350 applies this correction wrapper before alpha/rendering, so both preview
launchers use it. New cohort paths use continuous_face_support_v6_* to preserve
old outputs. Desktop/Android correction models and runtime lookups are unchanged.
Old correction approvals and targets are not transferred to changed support.

Script358 replayed the16 exact saved R1 cases without inference. Six changed,
588 pixels filled. All16 pass idempotent fill, original-support retention,
positive interior alpha, clean identity and outside-final-support preservation.
Removing a hole also removes its artificial feathered boundary, so rendered
changes may extend around the filled hole within permitted correction support.
No unprotected enclosed holes remain by the declared4-connected criterion.
This does not prove the outer contour or every selected object is appropriate.

Evidence/gallery: outputs/continuous_correction_r2/review.html; all four contact
sheets visually inspected. The eye/lip holes are filled; external notches and
the forehead coverage concern remain. Filling an enclosed area can cover an
object inside the chosen whole-face region, as the adopted correction policy
intends; it is never a reason to add that object to measurement.

## Decision and next work

R1 is complete as an audit with unresolved evidence, **not ready for training**.
Keep all18 dispositions and conflicting notes. No replacement sources or fit.
Actual-skin reliability remains limited by glasses/beard contamination; a separate
justified measurement proposal would be needed before modifying exclusions.
No beard-specific model work is resumed. A forehead/outer-boundary repair must
use selected-face evidence rather than indiscriminate expansion into background.
Independent labelled support at categories7/10 and qualified lighting references
remain missing. The retained MST mapping cannot be promoted by these repairs.

Verification: nine focused tests passed (three new continuity cases plus existing
whole-face and review-import tests). Broader Python run:894passed/12.31seconds,
with tests/test_demo_desktop.py explicitly excluded due to the previously
confirmed unavailable Tcl/Tk init.tcl environment. This is not a full-suite pass.
No calibration, correction fitting, reserved-pixel access or professional contact.
