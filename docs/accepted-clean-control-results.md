# Reviewed clean-photo training comparison

30 October 2026. Adding eleven accepted original photos reduces unwanted changes
to clean photos, but weakens correction of distorted photos. It does not satisfy
the zero-clean-harm requirement. Keep the existing demo and research baseline.

The [frozen protocol](accepted-clean-control-protocol.md) compares three fixed
five-feature decision trees: historical fitting data, extra copies of historical
clean controls, and genuinely additional clean sources. All retain input Lab,
ITA and experimental calibrated MST, direct-exponent gamma/R/B targets, depth 3,
seed 42 and fitting-control leaf protection. No settings were selected from
these results.

Only original references and their exact masks accepted without recorded notes
were admitted: 85815, 56839, 75166, 68073, 75898, 62105, 20648, 72400, 34227,
34458 and 29880. Their target is unchanged `[1, 1, 1]`. Source 66413 remains
held because the user subsequently described the photo as too blurry. Other
accepted references with concerns remain held; their decisions are preserved.
No new distorted mask or target is approved by this experiment.

There are 26 source/duplicate-group-held folds, 78 fitted trees and 123 held
predictions. Each historical source contributes its clean and distorted pair;
each new source contributes one clean photo. A held source never appears in
its fold's fitting data. Repeated controls in the count comparator are weighting,
not additional independent sources.

Lower CIEDE2000 is better. The historical 30-pair comparison is kept separate
from the additional eleven easy clean cases.

| Method | Historical 30 error | Historical distorted 15 error | Historical clean changed /15 | New clean changed /11 | Combined 41 error |
|---|---:|---:|---:|---:|---:|
| No correction | 10.076 | 20.153 | 0 | 0 | 7.373 |
| Historical fitting data | 7.132 | 12.393 | 1 | 3 | 7.303 |
| Repeat old clean controls | 8.531 | 12.630 | 3 | 4 | 8.504 |
| Add eleven clean sources | 8.091 | 16.181 | 0 | 2 | 7.314 |

Additional clean sources protect all fifteen historical clean photos in this
comparison, including 75027, without a source-specific rule. They still alter
held clean sources 29880 and 68073. Distorted-photo error worsens from 12.393
to 16.181; distorted photos changed fall from eleven to seven. Changed does
not necessarily mean improved. Combined error also remains slightly worse than
the historical-only comparator, despite narrowly beating no correction.
Thus this is evidence about a tradeoff, not a successful overall upgrade.

Verification: `scripts/255_verify_accepted_clean_controls.py` independently
refits all 78 trees, reconstructs fitting-control leaf protection, checks
source separation and reviewed admissions, replays all 123 image outputs and
metrics, checks unchanged pixels outside application masks, and reproduces
the previous historical baseline to numerical tolerance. Evidence lives in
`outputs/accepted_clean_control_comparison_v1/verification.json`. The last
full core suite remains 780 passing tests; this script-only experiment uses
the focused replay verification rather than claiming another full-suite run.

These are exposed development sources, with experimental MST calibration,
limited tone coverage and existing synthetic/clipping assumptions. No reserved
validation/test images were opened in this experiment. Human acceptance of a
reference mask does not establish true skin color or final model accuracy.

The next justified model step is to inspect why unseen clean sources reach
distortion-only leaves and evaluate a predeclared tree-training change using
the same source-held comparisons. More copies of clean rows and broader
brightness features have now both failed; neither should be treated as the fix.
Keep source-specific exceptions and threshold invention out of the model.
