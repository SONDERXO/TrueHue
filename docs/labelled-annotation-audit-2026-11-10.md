# Saved labelled annotation audit — 10 November 2026

The user reported finishing all30 cases. Read-only inspection found **31 saved
revisions covering26 distinct cases**. Four cases have no saved annotation or
editor-worker job: **case_13, case_16, case_21, case_22**. All31 worker jobs have
successful results; no worker failure or lost saved output was found. Viewing a
case or pressing Next did not record a review in the original editor.

## Verification and coverage

Script728 audits all31 actual annotation bundles, all30 immutable queue tasks
and their provenance. Membership/size/hash checks, task/report/payload binding,
exact brush replay, saved-mask equality, changed-pixel/stroke counts, statistics
and separate Lab/ITA arithmetic checks pass. The 31 revisions are retained;
latest revision selection follows the editor's annotation-file mtime rule with
no ties. There are five additional revisions across cases11,15,19,30. These do
not count as additional independent examples.

All26 latest saved records are explicit reviewed selections with valid ITA and
more than the unchanged1,000 selected normalized pixels. There are no saved
unjudgeable outcomes. Allten publisher subjects have at least one saved review;
six have allthree. Allnine historical automatic failures now have saved, valid
manual measurements, including allfive empty starts. The four missing reviews
were historically automatic successes; their old masks are not silently treated
as approved. No approval or new strokes are fabricated for them.

Allsix contact sheets were viewed, covering all30 photo/seed/manual-or-missing
panels. Actual manual selections are substantially broader than sparse seeds
in many cases, with eye/mouth and hair exclusions. Low native detail, colour
casts and uncertain boundaries remain. These views are not independent pixel
ground truth, measured segmentation accuracy, validated calibration or proof that
all selected pixels are skin. No edits were made on the user's behalf.

Private audit: `outputs/labelled_annotation_audit_v1/audit_PRIVATE.json`, preserving
all revisions, exact tasks/labels/groups/conditions, jobs, missing cases and
input hashes. Cached queue images and masks were read; no original-source image,
later/final photo, model or external service was accessed. No fits were run.

## Editor completion fix

The editor now displays the number of **distinct saved reviews**, marks the
current case SAVED REVIEW or NOT SAVED, opens at the first missing review, and
offers **Go to first unsaved review**. Moving away from an unreviewed case now
prompts even when the mask and note were unchanged. Saving an unchanged reviewed
mask remains valid; saving unjudgeable counts as a completed review but not a
usable measurement. Existing files, methods and annotation records are unchanged.

The progress helper verifies saved evidence and deduplicates by task identity.
**10 focused tests pass in1.20s**, including distinct-case counting, duplicate
revisions, first-missing selection, unjudgeable completion and tampered-evidence
rejection. A fresh generated-only Python3.13 hidden Tk check also passes painting,
undo/reset, real project worker saves, resume/navigation, completion counts and
the unsaved-review prompt. Generated records remain isolated in
`outputs/labelled_measurement_gui_check_v2`. The original GUI check is preserved.
No screenshot or visual-layout review is claimed.

## Required input and calibration status

Reopen `review_labelled_measurements.cmd`; it starts at case13 with26/30 reviews
saved. Review cases13,16,21,22 and explicitly click **Save reviewed selection**
even if no painting is needed, or **Save as unjudgeable** when appropriate. Use
**Go to first unsaved review** to move among remaining cases. The other saved
cases need not be redone.

Calibration remains pending completion of saved-review coverage and eligibility
assessment. Do not fit on the26 successes while treating the four unsaved cases
as completed or silently dropping them. No old MST coefficient transfer or
automatic training admission occurred. The decision-tree/ITA/MST requirements
remain. No correction brightness fix or new tree comparison is claimed.

Final eight groups/24 photos and older locked allocations remain byte-unread.
No new inference, acquisition, upload, contact, commit or push. Previous outputs
and all actual user annotations are preserved.
