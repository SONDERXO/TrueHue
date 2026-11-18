# Combined reviewed calibration comparison — 11 November 2026

The fixed expanded-data candidate **fails the frozen development advancement
checks**. It improves brighter-capture estimates but degrades all three original
conditions and their maximum error. It is not admitted for application or runtime.

Scripts 768–769 execute exactly ten ITA+Lab standardized ridge-alpha1 fits,
each using 54 reviewed captures from nine subjects and evaluating the six
captures of the tenth. Each fitting subject has weight1, row weight1/6. All
scaling, intercepts, coefficients and median baselines use fitting subjects only.
The unchanged ten saved 600-only models supply sixty comparator predictions,
with no comparator refit. All sixty candidate predictions are available.

| Evaluated captures | Expanded candidate MAE | Frozen 600-only comparator MAE |
|---|---:|---:|
| All sixty | 1.289663486 | 1.478602283 |
| Original thirty, 600 | 1.254087965 | 0.619323827 |
| New thirty, 1200 | 1.325239006 | 2.337880739 |

The fitting-subject median MAE is 2.99. Combined maximum absolute error improves
from 4.869108959 to 3.061046362, but original-capture maximum worsens from
2.112654232 to 3.061046362. Candidate raw scores span 1.907333308–8.755391199,
with zero clipping. Thirty-five cases improve and twenty-five worsen against
the frozen comparator; seven of ten subject-average errors improve. These
descriptive comparisons do not override failed preservation checks.

| Condition | Candidate MAE | Comparator MAE |
|---|---:|---:|
| F_cool_600 | 1.216937137 | 0.731678305 |
| H_warm_600 | 1.365489078 | 0.577599605 |
| L_warm_600 | 1.179837681 | 0.548693572 |
| F_cool_1200 | 1.102950945 | 1.275686953 |
| H_warm_1200 | 1.369634282 | 2.815821638 |
| L_warm_1200 | 1.503131793 | 2.922133627 |

Five checks pass: full coverage, overall improvement over comparator, overall
improvement over median, new-1200 improvement, and nonworse combined maximum.
Two fail: each original condition must be nonworse, and original maximum must
be nonworse. Gates remain unchanged. This one comparison is complete and closed;
no feature/alpha/condition/weight/recipe sweep, rescue fit or automatic retry.

Independent stdlib verification passes ten weighted-scaling and scalar normal
equation checks, sixty candidate and sixty comparator prediction checks, thirty
exact original comparator replays, all errors/metrics/support flags and frozen
checks at 1e-10 tolerance. Verification performs zero fits or model predictions;
it checks the recorded arithmetic. No additional tests of generated examples
were run for this data-only execution; the independent numerical replay is the
validation of this run.

Private evidence: `outputs/combined_reviewed_mst_validation_v1`. Both original
and expanded results are retained with scientific/application flags false. No
all-data fit, photographic score, correction-tree fit, image/model-image read,
demo/Android change, acquisition, upload, contact, commit or push occurred.
Final 24 and older locked images remain byte-unread. Decision tree, ITA and MST
remain required.

The reviewed data remain useful; this result does not reject the user's masks
or justify more marks. Seven photographic inputs also remain beyond the
reviewed brightness maximum. The next substantive task is a saved-residual and
model-assumption review to distinguish systematic illumination-dependent bias
from isolated cases before selecting any further calibration design. That review
would use saved scalar records only. No new intervention, fit or acquisition is
selected here, and the original 600-only model is not thereby qualified for the
brighter photographic domain.
