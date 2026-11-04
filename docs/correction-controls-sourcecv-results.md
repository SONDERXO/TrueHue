# Correction controls: source-held-out comparison

Completed24 October2026 (Asia/Manila). Development experiment, not a deployed
replacement or final thesis evaluation. Follow-up to
[the fixed-mask output comparison](corrected-mask-comparison-results.md).

## What was tested

Used only the existing22 screen-pass training IDs from six sources. The eight
held rows stayed out. Features were recomputed on the already-saved hair-clean
256 inputs; the four-column baseline Lab/ITA schema and three known inverse
targets stayed fixed. No source eligibility, correction mask or target recipe
was changed. All inputs were unclipped and feature-valid.

For each of six source/known-duplicate-group folds, exclude all variants of the
held source, then fit two decision trees with the same depth3/seed42 settings:

- **Older recipe:** original distortion types only,10 eligible probes in total.
- **With controls:** those probes plus six unchanged and six mildly brightened
  inputs,22 probes total. Each fold uses only its non-held subset.

Both predict the same held-source probes. Correction uses the fixed additions-only
mask and common generation-region metric. This is a data-recipe ablation, not
a depth search. The older-recipe comparator is newly fitted per fold; it is
**not** the original frozen runtime model. Its scores cannot be directly equated
with earlier in-sample/frozen-model or one-source validation results.

No external development-validation source, stress case or reserved-test source
entered fitting or this evaluation. Subject identity independence remains
unverified; known source/duplicate separation is checked, not inferred identity.

## Results

Mean CIEDE2000 on source-held-out probes; lower is better:

| Probe type | Pairs | No correction | Older recipe | With controls |
| --- | ---: | ---: | ---: | ---: |
| Dark | 4 | 12.375 | 14.571 | 8.095 |
| Color shift | 3 | 7.284 | 13.814 | 9.800 |
| Bright/warm | 3 | 8.391 | 7.758 | 6.680 |
| Unchanged | 6 | 0.000 | 7.392 | 6.767 |
| Mild brightening | 6 | 2.818 | 6.984 | 4.956 |
| All22 probes | 22 | 5.156 | 9.512 | 6.916 |

Equal-source means are4.771 without correction,9.120 for the older recipe and
6.828 with controls. Report both: unequal variants per source affect pooled means.

Controls improve the average against the older recipe, but **do not solve
overcorrection**. The revised recipe remains worse than no correction overall,
worsens all six unchanged probes, and worsens two of six mild probes. It beats
no correction on only two of six per-source means, and improves against the
older recipe on four of six. An aggregate gain is not consistent reliability.

Unchanged references are synthetic reconstruction controls, not calibrated proof
that an ordinary photo can never need real-world adjustment. Still, the known
zero-distortion target must not be hidden when evaluating this training task.

## Failure traces and visual check

All22 held-source rows were visually inspected by Codex on six source boards.
Examples of persistent errors:

- Unchanged51739 and75027 receive gamma1.4286 and non-neutral gains, the same
  setting as a dark-distortion inverse; they become strongly overcorrected.
- Unchanged22454 receives a color-shift inverse instead of identity.
- Several other unchanged inputs improve but still receive non-neutral settings.

Script63 traced all12 control probes to actual training-leaf members and checked
that predictions equal their mean targets. The held source never appears in
those leaves. This identifies misrouting/averaging across different input
appearances; it does not prove all four-feature methods are impossible, assign
MST labels, or establish a physical explanation for lighting/skin variation.

## Decision and next work

Completed follow-up: [training-source coverage audit](training-coverage-audit.md)
screened18 previously unexposed training-pool images.17 processed successfully,
but only20555 is promising for follow-up; none were admitted. Worst control
errors occur inside marginal feature ranges, so brightness-range expansion alone
is not a demonstrated fix.

Do not replace the runtime model or expand these correction settings onto neck
skin. Preserve both fixed recipes and their negative findings. Six selected
sources provide very limited training coverage; adding two variants per source
is useful but does not create additional independent faces.

The next step is a bounded audit of training-source/feature coverage and a plan
for more varied suitable development sources before another model revision.
Keep controls and no-correction comparisons; report per-source/variant failures.
Do not clamp gamma, special-case reviewed IDs or tune on the external one-source
development set to make these examples look better. Final MST, dataset and
methodology questions remain in [the thesis record](thesis-method-alignment.md).

The requested [face-and-neck support](face-and-neck-correction-requirement.md)
remains recorded. This study concerns facial measurement/correction strength;
it does not implement or evaluate neck correction.

## Evidence and checks

- [Held-source corrected-image boards](../outputs/correction_controls_sourcecv_v1/review-index.md)
- [Full scores, predictions and fitting provenance](../outputs/correction_controls_sourcecv_v1/summary.json)
- [Fold verification](../outputs/correction_controls_sourcecv_v1/verification.json)
- [Control-leaf traces](../outputs/correction_controls_sourcecv_v1/control_failure_traces.json)
- Derived table/folds: `data/manifests/correction_controls_sourcecv_v1/`.
- Scripts61/62/63 refuse to overwrite their existing outputs.

Twelve experimental fold models are saved under this output directory, not as
a replacement runtime model. No final all-source model was exported. Verified
all44 learned held-pair predictions (plus22 no-correction controls), exact model
replay, source/duplicate separation, declared feature/target columns, fixed
screen IDs, zero clipped fitting inputs and unchanged original artifacts.
The full suite after scripts61/62 was **464 passed**; script63's subsequent
read-only leaf checks also passed without further model fitting.
