# Face-outline restriction experiment v1 (2026-10-19)

## Question and method

Can intersecting the frozen V2 mask with the MediaPipe face-oval polygon
reduce outer hair/background contamination without damaging useful masks?

The experimental module is `src/skin_masking/face_outline_experiment.py`.
Run `venv/Scripts/python.exe scripts/16_compare_face_outline.py` from the
project root. The command refuses to overwrite an existing experiment folder.
It preserves baseline code, models, manifests and manual review decisions.

The development set comprises the initial 30 grids plus the reviewed random
50: 80 unique images, with 45 baseline accepts and 35 baseline rejects after
normalizing `Accept` and `deny`. The random-50 CSV overrides stale master
decisions for those IDs; the initial master review is retained for the others.
No inference about full-pool acceptance rates is made from this mixed set.

Reuse the existing single-face YuNet detector, score 0.85, V2 mask helper,
crop-margin landmark cascade, feature exclusions, and 1,000-pixel condition.
Regenerated successful baselines must match stored pixel count, coverage,
mean Lab and ITA; excluded baselines must match stored pixel count.
Repeated landmark detection must reproduce V2's exclusion mask geometry.
The sole experimental operation is `V2 AND face_oval`. It can only remove
selected pixels; it cannot restore missed skin or fill holes.

Original image pixels remain the source of CIELAB/ITA. No distortion,
correction-model training, MST grouping, or independent evaluation occurs.

## Outputs and numerical results

Local outputs: `outputs/face_outline_experiment_v1/` contains `comparison.csv`,
`summary.json` (including input/model hashes), and 80 comparison grids.
The CSV includes fields for a future experimental visual review; these remain
pending and do not replace the baseline decisions.

- 80/80 baselines compared; no blocked comparisons.
- 73/80 masks changed.
- Median fraction of V2 selected pixels retained, among nonempty masks: 0.8405.
- No previously valid ITA output became invalid under the numerical rule.
- Input manifest, review files and model hashes were unchanged after the run.

These metrics describe geometric change and numerical validity, not improved
segmentation accuracy or increased visual acceptance.

## Targeted visual inspection and decision

Seven grids were inspected directly: train/29962, 25368, 124, 48136, 7147,
79424 and 83184. This is a targeted inspection, not a completed independent
review of all 80 experimental masks.

Outer selected regions shrink in examples such as 29962 and 25368. Hair
inside the boundary remains; beard/occlusion and poor color-threshold
coverage are not solved. In 7147 the method cannot recover missing facial
skin. Overlapping faces in 79424 remain a source of contamination.

Importantly, **83184 is a severe regression**: the baseline was manually
accepted, but the oval leaves only approximately 6.7% of its selected pixels
and visibly misses most of the face. It still passes the numerical minimum.
This demonstrates that pixel-count validity does not protect against a bad
outline. The cause needs investigation of landmark framing, correspondence
and coordinate remapping; no specific cause is established by the grid alone.

**Do not promote this experiment to the default pipeline.** Keep V2 as the
baseline. Before any adoption, resolve the 83184 geometry failure and check
the same change against accepted examples as well as rejected ones. A fresh
sample would only be appropriate after development choices are fixed.

## Validation

The full suite passed: 359 tests, including new checks that the restriction
preserves original inputs and holes, never adds selected pixels, keeps an
empty baseline empty, and rejects degenerate/nonfinite geometry.

## Follow-up: 83184 landmark trace

`scripts/17_diagnose_outline_landmarks.py` reproduces the trace without
altering baseline or experimental results. Evidence is saved locally in
`outputs/outline_landmark_trace_83184/trace.json` and annotated images.

- Original image: 224 x 224. YuNet crop: x=60, y=0, width=164, height=224.
- No landmarks are detected in the tight crop.
- The 50% margin reaches the full 224 x 224 image. The 150% margin and explicit
  full-frame options also reach exactly that same image; they are not three
  independent successful detections.
- All three return the same misplaced mesh. The oval spans approximately
  x=35.60..103.47 and y=-21.43..62.13 in the tight crop, visibly concentrated
  over the forehead instead of enclosing the face.
- Two coordinate paths agree with maximum absolute error zero:
  `raw_frame_landmarks + frame_origin` and
  `remapped_crop_landmarks + face_crop_origin`.
  The misplaced contour is present in original-image coordinates too.

The observed failure is therefore in the detected landmark geometry, not an
extra translation introduced by the crop remapping. The exact model-level
cause is not established. Trying still larger framing on this image supplies
the identical input and cannot independently resolve it.

This is sufficient to rule out adopting the current unconditional oval
restriction. No geometry threshold or special-case fallback was tuned to
rescue this one image. A gate based only on the 1,000-pixel condition would
miss this failure. A gate based on a small retained fraction could catch this
example, but would require independent development and validation before use.

The baseline V2 mask also uses this landmark geometry for feature exclusion.
Its manual acceptance is preserved as the reviewer's recorded decision, but
should not be cited as verification of correct eye/eyebrow/mouth placement.
Coverage, landmark correctness, and reference-image suitability are distinct
checks. Before using a screened subset for training, revisit examples with
suspect feature placement, including 83184, rather than treating earlier
coverage-based acceptance as unquestionable ground truth.

Recommended development direction: retain V2 for comparison and use a
documented screened subset for a feasibility prototype, subject to resolving
the landmark-quality concern and adviser agreement on the methodology.
That route is manual curation, not evidence of fully automatic reliability.
Changing landmark models or adding a validated geometry gate would be a
separate experiment; the current failure does not justify silently changing
the frozen pipeline or starting training immediately.
