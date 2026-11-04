# Accepted-image exclusion audit (2026-10-19)

## Scope and evidence

Audited all 45 unique manually accepted images from the initial 30-image
review and the random-50 review. The sample CSV takes precedence over the
master's stale random-sample decisions. Original user decisions are unchanged.

`scripts/18_prepare_exclusion_audit.py` generated original/exclusion-overlay
pairs, individual PNGs, and five contact sheets. All 45 regenerated masks
matched stored pixel counts, coverage, mean Lab and ITA. Red overlay pixels
show exclusion regions, not selected skin. All five sheets were inspected;
eight suspect cases were additionally inspected individually.

Results and per-image notes are in
`outputs/accepted_exclusion_audit/audit.csv`. These are Codex visual audit
judgments, not a second human reviewer, ground-truth segmentation, or a
replacement for the user's accept/reject labels. The overlay audit alone
does not establish whether every unexcluded non-skin pixel survives the color
mask; that requires inspecting the final mask too.

## Findings

| Audit judgment | Count | Meaning |
| --- | ---: | --- |
| No obvious gross misalignment | 23 | Approximate feature locations look plausible; complete exclusion and overall mask quality are not certified. |
| Incomplete mouth exclusion | 12 | Visible upper mouth/lip/teeth lie outside the lower-mouth exclusion region. |
| Uncertain | 9 | Blur, shadow, profile, or glasses prevent confident boundary assessment. |
| Misplaced geometry | 1 | 83184 has exclusions over the forehead instead of the actual features. |

These categories apply only to this curated 45-image set. They are neither
population rates nor a validated acceptance rate for the 533 successes.
The 23 cases without obvious misalignment are not automatically training-ready.

The 12 incomplete-mouth examples are train/124, 17773, 21241, 26799, 30603,
47374, 62331, 6236, 67854, 7712, val/10480 and val/1728 (all `.jpg`).
The nine uncertain examples are train/12362, 27912, 41283, 5946, 79206,
42655, 76841, 82552 and 29559.

## Code inspection

`FEATURE_INDICES['lips']` in `landmark_exclusion.py` is described as an outer
lip ring but contains only 21 unique vertices, following lower outer/inner
segments. Inspection of the installed MediaPipe package's public
`FaceLandmarksConnections.FACE_LANDMARKS_LIPS` topology shows 40 unique lip
vertices; the current list omits upper-lip vertices including 0 and 13.
The resulting lower-mouth-shaped exclusion agrees with the visual findings.
This is a concrete polygon-definition issue distinct from the unreliable
landmark detection on 83184. Correcting it will not fix that detection failure.

## Decision and next experiment

Do not treat the existing accepted set as fully verified for anatomical
exclusion. Preserve V2 and original review labels; do not train yet.

The next focused experiment should replace the experimental mouth polygon
with the complete **ordered outer lip contour**, while leaving color masking,
eye/brow exclusions, thresholds, and measurement conventions unchanged.
Do not concatenate all 40 inner/outer topology vertices into an unordered
polygon. Compare on the same 80 development examples and verify that the
change removes selected mouth pixels without needless removal of useful skin.
Keep numerical validity and visual findings separate. Do not combine this
change with the rejected face-outline restriction or claim it solves glasses,
hair, lighting, occlusion, or the 83184 geometry failure.

The last full test-suite result remains 359 passed from the outline experiment.
The audit command completed on all 45 images with measurement checks; no
algorithm was changed during this audit.
