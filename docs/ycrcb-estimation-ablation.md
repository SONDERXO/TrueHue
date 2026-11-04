# YCrCb-only estimation comparison

23 October 2026. Development experiment; no runtime adoption or model fit.
Follow-up to [hair-clean generation](hair-clean-generation-results.md).

## Fixed comparison

Tested all38 saved hair-clean square-generation attempts. Both methods see
exactly the same image, face box and complete-mouth anatomical exclusions.
The candidate removes only the HSV intersection, retaining Cr133–173,
Cb77–127, the existing5x5 elliptical open/close/close and largest component.
The material check and hair veto for correction support remain unchanged.
No threshold tuning or held-case-specific fallback was introduced.

This is closer to the proposal's detailed face-constrained YCrCb method,
but retains YuNet, landmark exclusions and experimental correction helpers.
It is not a claim that the whole proposed pipeline is now implemented.
The abstract/scope and detailed method still differ in their masking wording.

## Coverage findings

The same exploratory generation-retention screen passes27 of30 training
candidates, compared with25 for the paired HSV-and-YCrCb baseline on these
hair-clean inputs. This baseline is distinct from the original22-row selection.

Two previously failing cases now pass: source22211/dark and source62331/color.
Three still fail: source12288/color, source22211/color and source22454/dark.
All three source19 development variants pass the candidate screen, but remain
development-only. The historically excluded source22454/color now exceeds the
pixel minimum; its coverage remains visibly sparse. It was not promoted.

**More coverage also admits extra regions.** Codex inspected boards for12288,
22454,22211 and62331. Upper/side-face recovery improves in places, but candidate
support sometimes reaches farther toward neck, clothing or surroundings.
For source62331/color, support outside the generation region rises from119
to2,138pixels; source22211/dark rises from790 to2,403. Outside-generation pixels
are not automatically non-skin, and these are not annotated false-positive
counts. They do show why the coverage screen alone cannot approve this change.

## Labeled regression

Original24 reviewed points, six original224 images and exact original coordinates
were checked on clean images and a fixed **global** color shift (gamma1,
red0.85,blue1.15). There are48 observations per method,96 total; all available.
The shifted labels are reused development annotations, not new independent data.
These global probes differ from the masked-generation square dataset.

| Selected correction-support points | Baseline clean | Candidate clean | Baseline shifted | Candidate shifted |
| --- | ---: | ---: | ---: | ---: |
| Skin,12 reviewed | 12 | 12 | 9 | 12 |
| Hair,4 reviewed | 1 | 1 | 0 | 0 |
| Paint,3 reviewed | 0 | 0 | 0 | 0 |
| Other,5 reviewed | 0 | 0 | 0 | 0 |

No reviewed paint regression was observed. One clean hair point remains selected.
These selected pixels do not measure area accuracy or guarantee exclusion of
paint, hair, clothing or background elsewhere. No corrected-output performance
or fairness result is claimed.

## Decision and next step

Completed follow-up: [added-region visual review](added-correction-region-review.md)
confirms recovered skin mixed with clothing/collar/border spill. Candidate remains
unadopted; the next experiment should test an input-derived facial boundary.

Keep the candidate separate. Do not integrate it, refit the old model against
new features, or promote held/excluded rows on the strength of these results.
The unchanged22-row manifest, original tables, model and review labels remain
intact. The five prior mask-loss cases remain held in the adopted development
record; two have a promising experimental recovery only.

The next useful check is a focused review of **newly added correction regions**
to distinguish real facial skin from surrounding material. Preserve this fixed
candidate for that review instead of repeatedly widening thresholds. Any later
boundary restriction needs a separate version and checks on both gained skin
and hair/paint errors. This does not resolve MST mapping or the dataset policy.

## Evidence

- [Comparison boards](../outputs/ycrcb_estimation_ablation_v1/review-index.md)
- [Full measurements and point observations](../outputs/ycrcb_estimation_ablation_v1/summary.json)
- [Outside-generation diagnostics](../outputs/ycrcb_estimation_ablation_v1/outside_generation_diagnostics.json)
- Script56: `scripts/56_compare_ycrcb_estimation.py` (refuses overwrite).

Baseline masks reproduce the previous experiment exactly. All152 saved square
masks/counts and96 point availability records were checked. Tracked input/model/
review hashes match after execution. Existing **454 tests passed**.
