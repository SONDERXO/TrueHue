# Direct-gamma tree with fitting-control leaf protection

30 October 2026. Tested one fixed conservative output rule on the saved
direct-gamma trees. If a leaf contains any unchanged **fitting** photo, return
identity[1,1,1]. All splits and other outputs remain fixed. Held-photo labels
never decide whether to apply the rule. The same policy previously had limited
success with old gamma coordinates; this experiment tests the newer partitions
and does not claim a novel algorithm or general clean-image detector.

## Same-cohort held-source results

The original historical15-source/30-pair development cohort, five ITA/MST/Lab
features, masks, folds and exact source concerns are retained. No newer rejected
or unreviewed mask rows enter fitting. Lower CIEDE2000 is better.

| Method | All30pairs | Unchanged15 | Distorted15 | Harmed unchanged photos |
| --- | ---: | ---: | ---: | ---: |
| No correction | 10.076 | 0.000 | 20.153 | 0 |
| Direct-gamma tree | 7.628 | 3.464 | 11.791 | 5 |
| Protected direct-gamma leaves | 7.132 | 1.870 | 12.393 | 1 |

The protected policy reduces pooled error approximately6.5%relative to the
unprotected direct-gamma candidate and reduces held-clean harm5→1. It also
reduces correction interventions on distorted inputs13→11of15and worsens their
mean error. Report that trade-off, not uniform improvement or a near-perfect
model. These percentages are descriptive on repeatedly exposed development
sources, not statistical significance or independent final validation.

The remaining unchanged failure is75027, with CIEDE2000about28.05. It reaches
a leaf containing only distorted fitting examples, so this fixed control-leaf
rule cannot protect it. No source-ID special case, feature cutoff or identity
fallback tuned to this held case was added. The necessary zero-clean-harm gate
therefore still fails, despite overall improvement versus no correction.

Verified15modified tree exports with unchanged split nodes and correct
fitting-only membership. All210fitting-control occurrences return identity.
Independently reconstruct all30held outputs/metrics and preserve source/group
separation. The full suite passed **776 tests in12.53seconds**. No new
regression fits were needed; the saved direct-gamma trees supplied partitions.

The demo preset remains unchanged and the candidate is not activated. Prior
quality gates, historical accepted mask concerns, approximate/clipped targets,
weak experimental MST and absent dark-severity coverage remain disclosed.
No new calibration, source review, image generation, validation/test access
or deployment fit occurred. Do not use the in-training identity property as
proof of safety on new clean images.

Next work must address unseen clean inputs that resemble distorted fitting
examples while preserving measurable correction benefit. Another hand-chosen
skip rule for75027would not establish a reliable solution. Keep this candidate
and the previous failed policies as matched baselines, and do not replace the
working demo merely because the overall average improved. No further human
photo review is requested here.

- [Matched before/after gallery](../outputs/direct_gamma_clean_leaf_v1/review.html)
- [Complete predictions and leaf evidence](../outputs/direct_gamma_clean_leaf_v1/predictions.json)
- [Summary and failed safety gate](../outputs/direct_gamma_clean_leaf_v1/summary.json)
- [Independent verification](../outputs/direct_gamma_clean_leaf_v1/verification.json)
- [Frozen protocol](direct-gamma-clean-leaf-protocol.md)
