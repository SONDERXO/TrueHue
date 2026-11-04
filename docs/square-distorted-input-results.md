# 256x256 check on existing development distortions

23 October 2026. Follow-up to [source-image preprocessing](square-preprocessing-results.md).

## Outcome

All 38 existing attempts were checked at native 224x224 and after resizing to
256x256. There were no new processing failures or recovered exclusions.

| Historical use | Attempts | Native passes | 256 passes |
| --- | ---: | ---: | ---: |
| Training | 30 | 30 | 30 |
| Development-validation (one source) | 3 | 3 | 3 |
| Clipped stress, kept separate | 4 | 4 | 4 |
| Previously excluded | 1 | 0 | 0 |

The excluded source22454/color-shift selected 231 native versus 387 resized
skin pixels; both remain below the fixed 1,000-pixel requirement. It remains
excluded. No source, partition, training target or review label was changed.

Native successful features reproduce stored values within 0.00011, allowing
for the table's four-decimal rounding. Both sizes use fresh face detection,
landmarks and complete-mouth estimation masks, with the same thresholds.
All saved mask shapes, counts, crop bounds and pass/fail outcomes were checked.
Input/model/table hashes remained unchanged. No model was loaded or fitted.

## Important limitation

Numerical processing success is not a mask-quality assessment. The largest
ITA shift is +8.0011 degrees for development source19/color-shift; its mask
agreement is 0.6882 IoU. Across the 37 paired successes, agreement ranges from
0.6882 to 0.9784. Agreement measures consistency, not accuracy.

Codex inspected boards for sources19,22454,12288 and62331. Substantial skin
loss remains in some color-shift examples and source22454/dark. Some baseline
hair inclusion also remains. The 256 resize does not fix these threshold-mask
limitations. No new human acceptance or claim of segmentation accuracy is made.
These boards show estimation masks, not the experimental hair-filtered
correction support or corrected outputs.

This experiment resizes **already distorted** images. A future 256 training
table must instead resize the clean source first, recompute its generation
mask, apply the fixed distortion, and then measure the saved distorted input.
Interpolation and distortion do not generally commute, especially at binary
mask boundaries. Do not use this report's resized probes as that new table.

## Artifacts and recommendation

Completed follow-up: [fresh square-resolution dataset](square-development-dataset.md).
Generation checks pass, but mask-quality concerns remain before retraining.

- [Review boards](../outputs/square_distorted_inputs_v1/review-index.md)
- [Full evidence](../outputs/square_distorted_inputs_v1/summary.json)
- Reproduction: `venv/Scripts/python.exe scripts/50_check_square_distorted_inputs.py`
  (refuses to overwrite its output directory).

A separate 256 development table is now reasonable as a software check using
the existing sources and fixed distortion settings. Preserve every attempt,
recheck clipping at the new generation resolution, retain exclusions and keep
stress outside fitting. Assess the resulting masks before any retraining;
the current mask holes must not be hidden by a successful status flag.
MST mapping, SCIN suitability and final-method approval remain unresolved.
