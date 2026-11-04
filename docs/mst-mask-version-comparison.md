# MST mapping: mask-version comparison (21 October 2026)

## Plain-language result

The complete-mouth fix improves which mouth pixels are removed, but it does
not make ITA reliably identify one of the ten MST categories. We tested the
same mapping rules with subjects kept separate. No final lookup, FairFace
groups, or correction model was created. The approved thesis objectives
remain unchanged; this is evidence about implementation feasibility.

The run also exposed a reproducibility issue: the current face detector cannot
reliably process the original large MST-E images at native detector size.
That has to be distinguished from the effect of changing the mouth mask.

## Preserved native-detector attempt

The first attempt used the current pipeline directly on native-resolution
inputs. It was interrupted for diagnosis after 124 of the 418 reviewed sources:

- 123 had no detected face.
- One produced a V2 measurement but a degenerate complete-mouth polygon.
- No completed current-mask mapping comparison was obtained from that attempt.

This was an ordered partial attempt, not a random sample or a failure-rate
estimate for the whole dataset. Its rows and interruption status are preserved
under `data/manifests/mst_mapping_mask_comparison_v1/`.

On the first diagnostic source (3840x2880), native detection found no face;
detector inputs reduced to maximum sides 1024, 640 and 256 detected a face.
This establishes a scale sensitivity for that probe, not a validated optimum.
No detector confidence threshold was lowered or size tuned against mapping scores.

## Separate controlled detector-scale run

Script 27 was run with `--detector-max-side 1024`, selected after that detection
probe and before seeing the full mapping results. It reduces only the detector
input, maps box coordinates back using actual width/height scale factors,
and measures masks and Lab/ITA on the native image crop. It never upsamples
small images. Both regenerated V2 and complete-mouth variants share the exact
same detected crop; only their mouth exclusions differ.

This is explicitly **not** the proposal's full 256x256 preprocessing and is
not a silently adopted production detector change. The historical table has
no run hashes or saved face boxes available here, so historical preprocessing
cannot be faithfully reconstructed. Zero historical pixel-count/ITA pairs
matched exactly in this 1024-detector run. Do not attribute historical/current
differences solely to the mouth fix or claim the old run was reproduced.

The experiment attempted all 418 historically reviewed sources:

| Outcome | Images |
| --- | ---: |
| Both current mask variants numerically successful | 394 |
| No detected face | 22 |
| Multiple detected faces | 1 |
| Landmark exclusion unavailable | 1 |

All attempts remain in the comparison audit. Current numeric success does not
inherit the original masks' human quality labels. The paired mapping evaluation
uses the common 394 images from 15 subjects for **all three measurement versions**.
Thus the historical row below differs from the earlier 418-image result: its
training and test inputs are deliberately restricted to the identical common
cohort. Do not compare historical 418-image accuracy directly with new 394-image
accuracy as an isolated mask effect.

## Paired subject-separated results

Every subject is held out in turn. The same three fixed rules are refitted on
the remaining subjects for each measurement version, using the earlier protocol.
Exact accuracy is image-weighted; ordinal MAE is measured in MST-category steps.

| Measurements | Ordered ITA mapping: exact | Ordered mapping: MAE | Nearest-category rule: exact | Nearest rule: MAE |
| --- | ---: | ---: | ---: | ---: |
| Historical V2, common cohort | 6.3% | 2.46 | 17.5% | 2.95 |
| Regenerated V2, detector max 1024 | 11.4% | 2.19 | 14.7% | 2.67 |
| Complete mouth, same detected crop | 11.4% | 2.13 | 15.2% | 2.64 |

The constant training-subject-median baseline is identical across versions:
14.5% exact accuracy and MAE 2.84. The isolated mouth change slightly lowers
average category error; it does not improve ordered-mapping exact accuracy.
This is descriptive, not a statistically established improvement.

For the complete-mouth ordered mapping, within-one-category accuracy is 36.5%;
equal-subject exact accuracy is 12.4% and equal-subject MAE is 2.26. Equal-subject
results and per-label/per-lighting summaries are preserved in the CSVs rather
than relying only on photo counts.

Five categories still have only one reviewed subject. Their category is absent
from training when that subject is held out. Even limiting the already-generated
predictions to the 216 images whose labels were represented in training gives
only 13.9% ordered-mapping exact accuracy (27.8% for the nearest-category rule).
This is a descriptive support check, not another tuned classifier or final test.

## Mask changes and visual evidence

The mouth fix changed selected pixel counts in 363 of the 394 successful pairs.
Median absolute ITA change from that isolated fix was 0.276 degrees; maximum
was 3.153 degrees. There were no additional numerical failures caused by the
mouth change among the current-V2 successes in this completed scaled run.

Twelve diagnostic IDs were sampled with seed 42 before processing. Eleven
produced comparison grids; one failed and was not replaced. All eleven grids
were inspected: mouth coverage generally becomes more complete, while hair,
facial hair, glasses, occlusion and fragmented skin selection remain concerns.
This is a limited Codex visual inspection, not fresh human validation of 394
masks or evidence of segmentation accuracy. Historical reviews are preserved.

## Recommendation for the thesis

Keep the mouth fix as a narrow correction, but **do not export or use either
tested ITA-to-MST mapping yet**. The controlled results do not establish reliable
ten-category estimation, and past development use and subject scarcity remain.
This does not prove that all possible mapping approaches fail.

Before further calibration or full training, establish a reproducible final
preprocessing contract consistent with the approved 256x256 specification,
including detector input size versus measurement size, crop coordinate mapping,
and pixel-count meaning. Any alternative should be justified and discussed,
not introduced under the name of the old pipeline. Then decide whether more
independent labeled subjects or additional approved-method work is feasible.

Use these measured implementation difficulties in adviser consultation. No
automatic proposal revision, category relabeling, severity change or formal
approval claim is made. Continuing to tune lookup thresholds until this same
small inspected set looks good would not produce defensible final evidence.

## Reproduction and artifacts

```text
venv/Scripts/python.exe scripts/27_compare_mst_mapping_mask_versions.py --detector-max-side 1024
```

Existing outputs are protected. Data are under
`data/manifests/mst_mapping_mask_comparison_max1024_v1/`: all-image measurements
and failures, per-version subject-held-out predictions, paired mapping metrics
and a summary containing input/code/model hashes. Diagnostic grids are under
`outputs/mst_mapping_mask_comparison_max1024_v1/`. Original source images,
historical tables and review decisions were not changed.

399 tests passed. Checks cover paired-cohort selection, no historical-feature
imputation for failures, subject exclusion during fitting, nonfinite values,
detector-box remapping, edge clamping, and no small-image upsampling. Run-level
checks enforce that the mouth restriction never adds pixels and that input,
code and model hashes remain unchanged during the completed run.
