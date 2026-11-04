# Synthetic-pair technical pilot (2026-10-20)

## Purpose and implementation

Validate a shared operator and analytic correction targets before constructing
training data. No decision tree, final split, skin-tone group, or severity rule
is fitted or assigned. The five sources are development/pilot data, not an
untouched final evaluation set.

`src/distortion_generation/generate_distortions.py` now provides
`transform_rgb` and `inverse_parameters`, version
`encoded_rgb_gamma_then_gain_v1`. Historical uint8 helpers remain unchanged.
For normalized image-encoded RGB:

```text
distorted = clip([red_gain, 1, blue_gain] * reference ** (1/gamma), 0, 1)
correction_gamma = 1 / distortion_gamma
correction_gain = distortion_gain ** (-distortion_gamma)
```

Gamma greater than one brightens. Gamma acts first, channel gain second.
Transforms use float64; PNG export rounds once to uint8. Analytic inverse
targets are exact only without clipping/quantization. This is a mathematical
image simulation, not a calibrated camera or skin-color model.

Reproduce from the project root:

```text
venv/Scripts/python.exe scripts/21_synthetic_pair_pilot.py
```

Existing pilot outputs are protected from overwrite.

## Selection, scope and records

Seed 42 selects five IDs from the sorted 23 previously accepted images with
no obvious gross exclusion misalignment in the separate audit:
train/12288, 16611, 22211, 22454 and 7303 (all `.jpg`). This is a curated
technical sample, not representative of skin-tone groups or the whole pool.
The audit did not certify complete segmentation or reference color accuracy.

Each source receives the same three technical probes:

| Probe | Gamma | Red gain | Blue gain |
| --- | ---: | ---: | ---: |
| dark | 0.70 | 0.85 | 0.95 |
| bright_warm | 1.25 | 1.08 | 0.95 |
| color_shift | 1.00 | 0.85 | 1.15 |

These values are technical tests, not finalized training ranges or
tone-dependent severity. There is no brightness offset.

Generate the versioned source mask using `v2_complete_mouth_v1` and verify
its stored measurements. Apply distortion only on that binary source mask;
all other original pixels remain unchanged. The known-parameter correction
uses the same fixed source mask. This oracle mask is **not available from
an unknown clean source at deployment**; its role is generation and operator
verification, not inference. Hard boundaries and unchanged feature regions
are visible in the distorted probes; blending/realism are not validated here.

Separately rerun face detection, versioned masking and Lab/ITA on each saved
distorted full-frame PNG. These input features never use clean reference
statistics. Their outputs, including failures, are recorded independently
from oracle reconstruction metrics. Saving corrected images does not imply
the inference mask would match the fixed generation mask.

Local artifacts under `outputs/synthetic_pair_pilot_v1/`:

- `pairs.csv`: 15 source/variant records, targets, clipping and reconstruction metrics.
- `distorted_input_features.csv`: input-derived features and automatic exclusions.
- `summary.json`: selected IDs, versions, input/code/model hashes and aggregate results.
- Five generation masks, 15 distorted PNGs, 15 oracle-corrected PNGs,
  individual comparison strips and five source comparison sheets.

Comparison columns are reference, distorted input, and known-parameter
correction. Rows on each source sheet are dark, bright_warm and color_shift.
Raw source files, original manifests and reviews are not modified; hashes
are checked after the run. Pilot source grouping is recorded so all variants
of one source can remain together in any future development use.

## Results

- 5 sources x 3 probes = 15 pairs generated.
- Maximum unclipped float reconstruction error: 2.22e-16 on the [0,1] scale.
- Three bright_warm probes clipped: 1 pixel in 12288, 14 in 16611,
  and 2 in 22454. Clipping fractions and clipped-region errors are retained.
- Mean distorted skin-region RGB MAE: 0.088359 on [0,1].
- Mean saved oracle-corrected skin-region RGB MAE: 0.000290 on [0,1].
  These are unweighted means of the 15 per-pair MAEs on the fixed source masks.
- Distorted-input feature extraction: 13 successes, 2 exclusions.
  The color_shift variants of 22454 and 7303 had insufficient selected skin
  pixels. They remain in the records, rather than disappearing from counts.
- All five source sheets (all 15 comparisons) were visually inspected.
  Known-parameter reconstruction appears close; mask seams in the distortions
  and existing source-image limitations are visible.

The oracle metrics verify the operator and targets, not a learned correction
model, segmentation accuracy, fairness or real-world skin-color restoration.
Near-perfect inverse reconstruction does not establish that these ordinary
source photos represent true skin color. The 13/15 numerical feature success
rate is descriptive for this small curated pilot only.

## Verification and next step

380 tests passed, including analytic inversion across the three probe settings,
gamma/channel conventions, non-mutation, parameter/input validation and
irreversible clipping. The pilot also asserts unchanged pixels outside the
generation mask, baseline agreement and input-hash preservation.

The operator/target contract is ready for further development. Before full
pair generation, specify source eligibility, split/deduplication policy,
handling of distorted-input failures, and generation/correction scope and
blending. Full tone-dependent generation still requires an approved grouping
policy. Do not train on the 15 pilot pairs and present them as final results.
