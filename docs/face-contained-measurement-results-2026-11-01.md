# Face-contained measurement candidate: diagnostic result

1 November 2026. User authorised implementation and one replay of the frozen
proposal. Implemented in an isolated face_contained_measurement.py module;
the active measurement pipeline, correction masks, preview launchers and demos
were not changed. No MST lookup, calibration or tree fitting.

## Result and stopping decision

**Outside-face containment passes; actual-skin reliability remains unresolved.**
Do not adopt this as a reliable measurement/MST solution or train on a subset.
Stop this diagnostic cycle. No alternative polygon/radius or recovery rule was
tried. No additional images or subjects were processed.

The candidate is exactly current nostril-excluded mask AND original landmark
face outline, using the unchanged square256 frame and1000-pixel minimum.
New isolated candidate contract:
`9e4c91973ab19dca2e3c3b17383742f509c83854d1d48b6840a050e163ad5868`.
Active parent contract remains
`1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7`.
No parent lookup/features/approval is transferred to this candidate.

| Fixed diagnostic denominator | Result |
|---|---:|
| Original attempts retained | 25 |
| Original failures retained without inference/retry | 8 |
| Saved successful masks replayed | 17 |
| Candidate technical successes | 17 |
| Newly below minimum / unavailable | 0 |
| Changed masks | 17 |
| Total selected pixels removed across images | 23,207 |
| Smallest retained fraction | 18.19% |

Every candidate has0pixels outside the exact outline,0added pixels, and0selected
forbidden predicted/anatomical/nasal-guard pixels. All17 independently
reconstructed mask comparisons and Lab/ITA/endpoint feature replays passed.
Source and parent evidence hashes, saved correction support and saved rendering
hashes are unchanged. Failure outputs carry no stale features. No new inference.

## Actual-skin and coverage observations

All17 comparison boards inspected across five contact sheets. The case4
neck/garment spill is visibly removed. Its retained mask is much smaller: this
is improved containment, not proof every removed pixel was wrong or every
remaining pixel is skin. Multiple profile/downward-pose cases lose visible
forehead, nose or cheek support. No per-pixel skin ground truth exists here,
so the loss is documented visually rather than scored as accurate segmentation.
Retaining1000pixels is a technical availability threshold, not a quality pass.

Sparse diagnostic locations were frozen in plan.json before candidate generation
from original/current-mask inspection, with image hashes, coordinate frame,
assistant annotation identity and uncertainty. They are not user approvals or
full segmentation labels:

- Case4: neck/garment marks(125,175) and(125,225) are no longer selected;
  cheek mark(100,140) remains selected.
- Case10: beard mark(125,140) is removed, but visual inspection still shows
  beard-adjacent lower-face selection. Removing one marked point does not
  establish complete beard exclusion. The dark cheek point was uncertain and
  is not treated as a clear-skin annotation.
- Case14: face-covering mark(115,150) remains selected. This is a clear
  contamination failure despite passing all geometric/programmed checks.
  Forehead skin mark(110,90) stays selected.

No claim of actual-skin precision/recall, illumination robustness, mapping
improvement or untouched subject generalisation follows. The25photos and their
four subjects are exposed development diagnostics.312same-subject unsampled
photos are not independent validation; they remain unprocessed.

## Evidence and implications

Run script362 only into a new output if reproducing; it refuses overwrite.
Evidence/gallery: outputs/face_contained_measurement_candidate_v1/review.html.
plan.json freezes membership, contract, sparse marks and input hashes; summary.json
retains all25statuses, pixel retention, features, sparse point results and
candidate mask hashes. All original source/review/failure artifacts are intact.

Nine focused tests passed in1.81s, including two new tests for spill containment,
parent immutability and unavailable features after insufficient pixels/bad geometry.
Broader verification:896passed in44.79s, excluding tests/test_demo_desktop.py
because the local Tcl/Tk setup is unavailable. This is not a full-suite pass.

The next decision is a measurement-validity strategy for ambiguous landmarks
and within-face occluders, with an independent evaluation scope; this diagnostic
does not authorise another incremental mask/calibration sweep. Beard-specific
model work remains on hold. Correction coverage/rendering remains separately
adopted; reliable automatic measurement, MST and correction remain unfinished.
