# Correction boundaries — 22 October 2026

Follow-up: [input-only coverage experiment](correction-support-results.md)
diagnoses color-gate losses and tests a separate correction support candidate.

Smoother boundaries soften abrupt edges, but do not fix the large patches.
Keep this experimental; do not replace the current correction automatically.

## What was tested

The saved decision tree, its predictions, input features and binary masks were
held fixed. The hard correction was reproduced pixel-for-pixel before comparison.
One inward feather rule was tested: a smoothstep ramp over a width equal to
3% of the smaller face-crop dimension, with a minimum of two pixels. There was
no parameter sweep, refitting or mask expansion. Excluded pixels remain unchanged.

The three development-validation pairs and four separate clipped stress pairs
were attempted; all seven succeeded. Original failed pairs remain excluded in
the earlier training table. Scoring used the same fixed source-generation region
as the previous run. That region is a diagnostic reference, not human ground-truth
skin segmentation, and does not enter correction or prediction.

## Results

| Mean color difference (lower is better) | Validation: 3 pairs, 1 source | Clipped stress: 4 pairs |
| --- | ---: | ---: |
| No correction | 10.666 | 7.227 |
| Hard correction | 7.609 | 13.916 |
| Inward feather | 7.870 | 13.179 |

The correction-residual jump across mask edges fell from 0.05505 to 0.00492
on validation. This measures the correction's abruptness, not overall image
quality: no correction has a zero residual jump by definition. The validation
RGB MAE increased from 0.06295 to 0.06503. Stress results still worsen the input
despite a modest improvement over hard correction; this set is not independent.

All three validation sheets were visually inspected. Narrow boundaries are
softer, but broad patches persist. Input-mask coverage of the original distorted
region varies strongly even though these variants share one source:

| Variant | Coverage | Missed pixels outside face crop | Missed inside crop, outside feature exclusions |
| --- | ---: | ---: | ---: |
| Dark | 91.4% | 2,061 | 334 |
| Bright/warm | 99.6% | 0 | 0 |
| Color shift | 35.6% | 486 | 20,274 |

Another 385, 121 and 133 missed pixels respectively overlap feature exclusions.
This separates crop changes, anatomical exclusions and the remaining mask loss;
it does not establish which internal threshold or cleaning step causes every
missing pixel. Most loss in the color-shift example is inside the crop and away
from eye/mouth exclusions. Feathering cannot recover those areas.

## Artifacts and next step

Run `venv/Scripts/python.exe scripts/29_compare_correction_boundaries.py` from
the project root. It refuses to overwrite an existing experiment.
Outputs are in `outputs/correction_boundary_v1/`: comparison sheets, inferred
masks, feather alpha maps, per-image metrics, failure ledger and a hashed summary.
Comparison sheets show reference/input/coverage above hard/feather/alpha.
Coverage colors: green shared, red missed source region, blue extra input region.

411 tests passed. Tests verify support preservation, full correction in the
interior, unchanged input, image-border handling, identity behavior and invalid
width rejection. Evaluation checked unchanged hashes, saved predictions and
exact reproduction of the previous hard-correction images and scores.

Next investigate color-sensitive mask coverage with input-only information,
keeping estimation and correction requirements explicit. Do not fill missing
regions from clean reference masks during inference. Any changed estimation mask
would require regenerated features and a separately versioned training run.
This development comparison does not establish generalization, approve thesis
methodology changes or use the reserved final test set.
