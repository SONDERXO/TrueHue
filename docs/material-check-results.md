# Input-relative color check — 22 October 2026

Next artifact: [24-point human review](material-point-review-guide.md), prepared
with blank labels to check retained skin and unwanted materials separately.

The added color check rejects much of the vivid face paint and some new hair
coverage while preserving the original example's improvement. It also blocks
recovery on another ordinary face. Keep it experimental: color consistency
does not reliably distinguish skin from other materials.

## Method

Only proposed additions to the guarded correction mask are checked. The input's
existing skin pixels supply a robust Lab center (channel medians) and scale
(1.4826 times the median absolute deviation, with floors of 12, 6 and 6 Lab
units). An addition must have standardized Euclidean distance at most 3. The
rule was fixed before this run, without a parameter sweep. It uses float OpenCV
Lab from normalized BGR. These are engineering choices, not calibrated material
probabilities or validated skin thresholds.

At least 1,000 input skin pixels are required; inadequate support fails explicitly.
The check uses no clean reference or distortion parameters, has no absolute
light/dark cutoff, and does not guarantee equal behavior across skin tones.
Existing baseline mistakes are preserved, including baseline hair inclusion.
Estimation masks, input Lab/ITA, saved tree and predictions are unchanged.

## Fixed-model comparison

All seven earlier pairs completed. On the three development variants of one
source, mean color error was 7.609 originally, 6.483 with unrestricted fill,
6.621 with the previous guard, and 6.622 with the color check. The original
color-shift patch improvement is visually retained.

Mean extra-region pixels were 350 originally, 673 unrestricted, 355 guarded,
and 350 checked. Checked outside-region RGB MAE matches the original 0.00109
on these three pairs. This does not imply perfect skin segmentation: the scoring
region is only the original generation mask.

Four nonindependent clipped stress pairs still perform poorly: mean color error
13.967 checked, versus 13.916 originally. The check cannot repair incorrect tree
predictions. Outside-region RGB MAE falls from 0.00240 guarded to 0.00177 checked
(original 0.00156). No final test images were used.

## Broader check, including unavailable cases

The same 46 development sources were attempted clean and color-shifted. Of 92
attempts, 83 completed: 46 clean and 37 shifted. Nine shifted cases are unavailable:

- Landmark failures: 21241 and 83184, also failed in the earlier run.
- Insufficient seed pixels: 7712, 47374, 48136, 22454, 79206, val/7058 and 7303.

These seven new abstentions must not disappear from reliability reporting.
They concern color-check availability; the ordinary pipeline also requires at
least 1,000 skin pixels for valid features. The broader earlier mask-only check
did not enforce that feature requirement. Rejected 29962 remains rejected;
original review decisions and training eligibility are unchanged.

Compare the same 37 successful shifted cases, rather than the previous 44:

| Mean diagnostic | Original | Guarded | Color checked |
| --- | ---: | ---: | ---: |
| Generation-region coverage | 61.9% | 73.0% | 72.2% |
| Extra-region pixels | 367 | 960 | 603 |
| Added pixels | 0 | 3,806 | 3,190 |

These conditional coverage figures do not include failures. The clean mask is
only used to generate the synthetic shift and score support, never to choose
input additions. Clean-input coverage is 100% by construction and is not an
accuracy result. Extra-region pixels can be skin or non-skin, so this table is
not segmentation precision/recall. There are no learned-model performance claims
for the broader mask-only cohort.

The original color-shift pair and shifted 16798, 29962 and val/10480 were visually
inspected, along with their combined review board. Much vivid paint is blocked
in 16798, but some colored regions still pass. New hair support shrinks in 29962
without eliminating hair already in the baseline. In val/10480 the check blocks
much of the prior recovery on facial skin. Most broader outputs are not manually
reviewed. No expert annotation or aesthetic rating is claimed.

## Artifacts, verification and decision

Run from the project root:

```text
venv/Scripts/python.exe scripts/32_check_correction_materials.py
venv/Scripts/python.exe scripts/32b_summarize_material_check.py
```

Both refuse to overwrite their existing results. Artifacts are in
`outputs/material_checked_support_v1/`: pair comparisons, mask overlays,
per-case metrics, failure ledger, hashes and `common_cohort_comparison.json`.
`material_review_board.png` shows input / previous guarded / color checked for
paint, hair and an ordinary face. Cyan marks additions; green shows baseline
support. This board makes both benefits and lost recovery visible.

422 tests passed. New tests cover recovery relative to different seed brightness,
synthetic vivid-paint/dark-material rejection, exclusions, nonmutation, inadequate
seeds and image-size mismatch. Fixed-model pair outputs reproduced the previous
baseline exactly; saved model, features and run input hashes were checked.

Do not promote either fill/filter to a general default or tune thresholds on
these examples to claim final performance. The next justified step is a small
independently reviewed skin/non-skin regression set, with hair, paint, ordinary
skin and darker/shaded skin explicitly represented. Use it to assess a stronger
input-only material mask and report retained skin as well as unwanted coverage
before scaling training. Existing estimation and approved thesis scope remain
the target; this experiment does not introduce a new final method.
