# Fixed brightness-feature comparison: not promoted

30 October 2026. Tested the existing six facial brightness statistics with
the newer direct-gamma regression targets and fitting-control leaf protection.
Retained the required inputITA,experimentalMST and meanLab features, yielding
eleven inputs. No reference statistics, source IDs, group labels or correction
outputs entered model features. Feature values match the historical script72
helper exactly on all30inputs; no feature subset was selected after scoring.

Same approved historical15-source/30-pair cohort, source/duplicate-group folds,
fixed depth3/seed42/minleaf1, masks, targets and scoring support as the matched
five-feature comparison. One new tree per fold; raw and protected outputs are
both retained. The dataset is repeatedly exposed development evidence, not a
new independent final evaluation. Older failed brightness experiments remain
preserved; the changed targets/policy justified this specific comparison but
do not make the feature design novel.

| Method | All30CIEDE2000 | Unchanged15 | Distorted15 | Harmed unchanged photos |
| --- | ---: | ---: | ---: | ---: |
| No correction | 10.076 | 0.000 | 20.153 | 0 |
| Five-feature protected direct gamma | 7.132 | 1.870 | 12.393 | 1 |
| Eleven-feature raw direct gamma | 9.351 | 5.283 | 13.418 | 13 |
| Eleven-feature protected direct gamma | 8.525 | 3.544 | 13.506 | 3 |

The new protected candidate worsens both clean and distorted reconstruction
relative to the five-feature protected baseline. Its harmed clean cases are
68453,84364and75027; the original remaining75027problem is not solved.
No feature trimming, depth search, confidence cutoff or source-specific skip
was introduced to rescue the result. Both new variants fail the clean gate
and are not eligible to replace the demo or the stronger research candidate.

All30feature vectors,15new regression fits, protected leaf membership,
210fitting controls and60held outputs/metrics independently replay. Tests check
that outside-mask pixels cannot alter these features, brightness directions,
unavailable undersupported halves and invalid mask types. The full suite
passed **780 tests in28.28seconds**. Algorithmic verification does not turn
this negative quality result into an improvement.

No newer rejected/unreviewed mask row was admitted, no measurement/calibration
contract changed, no held-out final source accessed and no demo preset changed.
The newer mask-validation failures and historical experimental-MST, clipping,
source-quality and missing-dark-coverage limitations remain unresolved.

This result argues against continuing to expand these summary features on the
small exposed cohort without new justification. Retain the stronger five-feature
protected direct-gamma candidate as a research baseline, while acknowledging
that it still harms one clean photo and is not release-ready. Better supported
training evidence and clean-versus-distorted separation remain the problem;
more tree inputs did not solve it. No additional human photo review is
requested for this completed comparison.

- [All predictions and failures](../outputs/direct_gamma_brightness_comparison_v1/predictions.json)
- [Features and availability](../outputs/direct_gamma_brightness_comparison_v1/features.json)
- [Summary and failed gates](../outputs/direct_gamma_brightness_comparison_v1/summary.json)
- [Independent verification](../outputs/direct_gamma_brightness_comparison_v1/verification.json)
- [Predeclared comparison](direct-gamma-brightness-protocol.md)
