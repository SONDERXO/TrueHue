# Correction prototype results — 21 October 2026

Follow-up: [correction boundary experiment](correction-boundary-results.md)
tests smoothing with the model fixed and identifies substantial coverage loss.

The decision-tree prototype runs successfully, but the corrected images still
have visible color and mask-boundary errors. This is an implementation check,
not a final thesis experiment or an approved methodology change.

## Setup

Training used 16 unclipped image pairs from seven source images. Development
validation used three variants of one separate source image (FairFace 19).
Source IDs and duplicate groups were checked for separation. The tree used
maximum depth 3 and random seed 42, fixed before evaluation, without tuning.

Inputs are the distorted image's mean Lab values and continuous ITA, selected
explicitly from the table. Outputs are gamma, red gain and blue gain. Metadata,
known distortion settings and reference-image measurements are excluded from
model inputs. This prototype does not establish the proposal's MST grouping.

Correction uses the mask inferred from the distorted input. All methods are
scored against the clean reference on the same original generation mask.
The constant baseline uses the training targets' mean parameters only.

## Development-validation results

Lower values mean less reconstruction error. RGB MAE uses values from 0 to 1;
color difference is CIEDE2000 under an sRGB assumption.

| Method | Mean RGB MAE | Mean color difference |
| --- | ---: | ---: |
| No correction | 0.09350 | 10.666 |
| Training-mean parameters | 0.09704 | 10.433 |
| Decision tree | 0.06295 | 7.609 |
| Known parameters, input mask (diagnostic) | 0.01546 | 2.607 |
| Known parameters, source mask (oracle diagnostic) | 0.00023 | 0.073 |

The tree reduced color error on all three validation variants. Its parameter
MAEs were 0.16952 for gamma, 0.05442 for red gain and 0.08188 for blue gain.
These measure parameter prediction separately from image reconstruction.

All three validation comparison sheets were visually inspected. The color-shift
example retains conspicuous patches, including with known parameters and the
input-derived mask. Mask mismatch therefore contributes error independently of
parameter estimation. The oracle uses information unavailable at inference and
must not be reported as learned performance.

Four clipped stress pairs were evaluated separately. Their mean color error
increased from 7.227 without correction to 13.916 with the tree. They are not an
independent test set and demonstrate that correction can worsen an image.
The original failed pair remains excluded with its reason; no features were
imputed. There were no additional evaluation failures.

## Artifacts and verification

- Runner: `scripts/28_train_correction_prototype.py`.
- Saved model and schema: `models/correction_prototype_v1/`.
- Metrics, predictions, tree rules, summary and comparison images:
  `outputs/correction_prototype_v1/`.
- Input tables: `data/manifests/controlled_training_v1/`.

Run from the project root with
`venv/Scripts/python.exe scripts/28_train_correction_prototype.py`.
The runner refuses to overwrite an existing run. The first run completed the
model and numerical evaluation before a NumPy-integer JSON serialization error.
The reports were recovered from the saved artifacts without refitting or tuning;
this is recorded in `summary.json`.

405 tests passed. Checks cover feature selection, mask-only correction,
nonmutation, identity correction and fixed-region scoring. Model persistence
round-tripped without changing predictions; artifact hashes are recorded.
Prediction-only desktop timing is about 0.34 ms; it excludes face detection,
masking and image correction and is not an Android performance result.

Only one validation source and three settings shared with training were used.
These results cannot establish generalization, fairness, physical skin-color
accuracy or final thesis performance. No final test set was used. Before scaling
training, the correction application needs to address the visible mask-boundary
artifacts and retain these comparisons as regression examples. Mapping research
remains paused, and the approved proposal remains the target implementation.
