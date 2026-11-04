# Fixed Table2 input-mask robustness comparison

29 October 2026. Executed the predeclared two-by-two rule comparison on the20
technically usable human-accepted original-mask training sources, using both
their saved references and their actual Table2-distorted inputs. Severity,
distorted pixels, reference generation support, detector/landmark rules,
threshold bounds and morphology were held fixed. No source geometry or mask
was copied into distorted-input inference.

| Input mask policy | Available / ≥1000 pixels | Existing support-screen passes | Total pixels outside frame-local oval |
| --- | ---: | ---: | ---: |
| HSV AND YCrCb, original component order | 20 / 20 | 3 | 63,250 |
| YCrCb-only, original component order | 20 / 20 | 4 | 92,707 |
| HSV AND YCrCb, oval before component | 20 / 20 | 1 | 0 |
| YCrCb-only, oval before component | 20 / 20 | 1 | 0 |

YCrCb-only adds one screen-passing case,34458. It also increases aggregate
outside-oval selection. Inspected34458 shows more facial support alongside
selection beyond the contour; screen success is not proof of a clean mask.
Oval restriction removes outside-oval pixels by construction but reduces
retention against the existing reference generation support. Neither metric
alone establishes improvement: reference masks include prior concerns and are
not annotated skin truth, while the oval is predicted anatomy rather than
perfect contour ground truth.

All40 original-arm masks reproduced the previously saved reference/input masks
exactly. The support-loss problem is therefore reproducible under the unchanged
measurement, not a missing-image or reference-feature substitution bug. The
existing .5/.8 whole/quadrant support screen remains exploratory and is not
silently redefined to make a candidate pass. All20 inputs already exceed the
pixel minimum; larger area alone does not resolve misplaced or missing support.

**No tested candidate is justified for promotion by this evidence.** Keep
the original measurement contract, lookup and active model unchanged. The19
clipped inputs remain clipped under every mask policy; segmentation changes
cannot restore lost channel values. Do not count increased mask support as
successful color recovery or admit those pairs into an unclipped primary set.
The accepted16033 hair concern and every other original note remain preserved.

Saved geometry/color candidates permit independent reconstruction of all160
masks across40frames and four policies. Script228 verifies each mask, source
hash, original-arm parity, anatomical exclusion, support metric and aggregate
summary. The original algorithm modules and contract remain unchanged; the
last full suite remains742passing tests. This script-only experiment uses
artifact reconstruction as its specific verification rather than claiming
new correction quality from that test count.

No reserved training-check, validation or final-test source was opened. No
candidate ITA/MST lookup, threshold tuning, parser substitution, target optimizer,
correction-tree fit, training admission or new user review occurred.

The result narrows the next decision: the currently specified Table2 stress
recipe and available rule masks do not yield enough supported unclipped pairs
for a defensible new primary fit. Any change to augmentation interpretation or
masking/calibration needs its own declared, paper-aligned policy, not another
undisclosed mask expansion or a relaxed success gate. Retain these failed
comparisons as evidence rather than replacing them with favorable examples.

- [Comparison boards](../outputs/table2_input_mask_robustness_v1/review.html)
- [Summary](../outputs/table2_input_mask_robustness_v1/summary.json)
- [All frame/policy measurements](../outputs/table2_input_mask_robustness_v1/attempts.jsonl)
- [Reconstruction verification](../outputs/table2_input_mask_robustness_v1/verification.json)
- [Predeclared protocol](table2-input-mask-robustness-protocol.md)
