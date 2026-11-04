# Facial-hair cleanup checkpoint — 30 October 2026

The fuller semantic face mask remains the preferred preview. A manual exclusion
brush is implemented for beard, moustache and other mistakenly selected objects.
Automatic beard removal is not reliable in the two bounded checks below and is
disabled by default. This does not finish automatic facial-hair segmentation.

## Use

Double-click `run_face_mask_preview.cmd`, choose a photograph, then paint over
facial hair with **Exclude hair**. Adjust Brush size for fine edges. **Restore
original skin** reverses painted exclusions without adding pixels outside the
original preferred mask. Undo (also Ctrl-Z) reverses a stroke; Reset clears edits.
**Save edited mask** creates a new `edits/edit_<id>/` inside that photograph's
preview folder. It saves mask, inward edge alpha, exclusion map, overlay and a
hash-bound `edit.json` containing replayable strokes. Original preview files
remain unchanged. Saved edits are not automatically admitted as training labels.

The editor uses the existing Python/Tk environment; no new package is needed
for the normal launcher. Controller tests and the photo-preview CLI passed;
interactive pointer operation has not yet been checked by a person.

## Bounded automatic check and stopping decision

The existing 19-class parser has no beard class. We investigated EasyPortrait
because its annotation policy excludes beard from skin; sparse stubble remains
ambiguous. See the [upstream project](https://github.com/hukenovs/easyportrait)
and [paper](https://arxiv.org/abs/2304.13509). The downloaded assets are
[third-party ONNX conversions](https://huggingface.co/sadzip/EasyPortrait-ONNX),
not newly trained TrueHue models. Their eight output classes have no separate
beard label. Background disagreement is only a possible exclusion suggestion.

Both checks used the same twelve previously exposed training sources: six
visible-facial-hair examples and six reviewed clean references. Reserved
evaluation data was not accessed. The fixed rule suggested only existing skin
pixels below the selected nose where the auxiliary model predicted background.
No darkness threshold, threshold search, fitting or replacement mask approval
was used. This rule intentionally could not cover upper moustache regions.

| Candidate | Input | Removed selected pixels on clean reference 63509 |
|---|---:|---:|
| FCN MobileNetV2 | 384 | 7,312 |
| FPN ResNet50 | 512 | 6,292 |

Visual inspection shows substantial unwanted cheek/chin skin loss. These are
selected-pixel removal counts, not beard accuracy scores: dense beard ground
truth is unavailable. Neither candidate is adopted. Do not repeat these checks
or tune the same rule on this set. Galleries and records are in
`outputs/facial_hair_suggestions_v1/` and
`outputs/facial_hair_fpn_suggestions_v1/`.

Both assets are pinned to repository revision
`19e22b9d1bfd87e67b82e4b2749405686aeecba2`:

- MobileNet SHA256: `f649f30a4f000ea3d8c5f4593b01c140b3c50659388c6d2997a6f546a451c434`.
- FPN SHA256: `cc5e9ce11c8e51b00b2975ba24c560b82d298d428b8c4ee4d15e9d005d567d15`.

Input preprocessing follows the converter: raw BGR, per-channel mean
143.55267075/132.96705975/126.94924335 and standard deviation
60.2625333/60.32740275/59.30988645, then NCHW. OpenCV and isolated ONNX Runtime
1.31.1 agree on every MobileNet output class for reference 63509 (maximum
logit difference 0.0001983643). The observed failure is reproduced across these
two runtimes. The isolated runtime lives under the ignored model directory;
project requirements and the default brush runtime were not changed.

The research-only `--suggest-facial-hair` CLI flag remains explicitly opt-in;
its suggestion is not applied automatically. The default launcher does not
request or run either auxiliary model.

## Verification and pipeline boundary

`scripts/312_verify_facial_hair_checkpoint.py` exactly replays all 24 saved
auxiliary masks/alphas and checks removal-only behavior, runtime parity and
unchanged preferred photo-preview mask. Evidence:
`outputs/facial_hair_brush_verification_v1/verification.json`.

Full suite: **833 passed in 11.62 seconds**, cache disabled; JUnit evidence in
`outputs/facial_hair_brush_verification_v1/tests.xml`. Sixteen new tests cover
brush replay, save provenance, source mutation rejection, undo/reset, restore,
invalid strokes and removal-only behavior.

This is a standalone mask preview/editor. No correction demo switch, tree fit,
ITA/MST computation or old-mask replacement occurred. ITA + calibrated MST +
facial-statistics decision-tree correction remains retained. Any adoption still
requires matching mask-dependent calibration and consistent data preparation.
