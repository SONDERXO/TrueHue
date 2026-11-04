# Completed broader-source comparison — 30 October 2026

**The source-expanded candidate is not adopted.** The one predeclared comparison
finished on121 cases /32 development-exposed source groups. It changes four
clean originals, worsens total error against the endpoint reference, and does
not improve the four newly accepted primary cases over leaving them unchanged.
No follow-up settings, masks, weights, recipes or source exceptions will run.

## Matched results

Mean source-mask CIEDE2000; lower is better. Every column uses the same rows.

| Evaluation set | No correction | A: endpoint reference | B: prior primary | C: expanded primary |
|---|---:|---:|---:|---:|
| All121 cases | 8.765 | 6.613 | 7.751 | 7.956 |
| Pooled primary62 | 8.066 | 8.020 | 6.552 | 6.787 |
| Newly accepted primary4 | 3.782 | 3.782 | 5.439 | 5.439 |
| Primary color11 | 3.828 | 3.828 | 5.187 | 5.076 |
| Stress27 | 20.756 | 10.357 | 18.524 | 18.524 |
| Clean originals changed /32 | 0 | 2 | 3 | 4 |

The candidate improves pooled primary and total error over no correction,
but this does not compensate for the clean-photo failures or the failed
comparative gates. The primary gain is not a general color-correction success.
Source-equal total means also favor A:6.552, B:7.943, C:8.116 versus no
correction8.888. All case-weighted and source-equal strata, including separate
old/new primary, lightening, darkening, exposure, old/new stress, original47 and
original105, are saved in `summary.json`. No empty mean is treated as passing.

Candidate clean failures are62331,83205,29880 and68073. Their respective errors
are10.320,11.277,10.136 and10.047, with38586,37163,38533 and41952 changed pixels.
All four saved comparison boards were visually inspected: the changes are
visible unwanted corrections, not merely numerical differences. B has the last
three failures; C adds62331. A changes68453 and the new control2434; A is a
research reference that also fails safety, not a validated automatic model.

Only two added sources supplied the four accepted primary masks. The six added
controls did not establish broad distortion coverage. The15 reviewed inputs
yielded4accept/11reject with exact notes preserved. Preparation also retained
13new clipped variants and2technical mask-screen holds outside this fit and
matched evaluation. These are explicit holds, not hidden model-processing
failures. Every one of the121 admitted cases produced all three method outputs.

## Fixed method and reuse

The [predeclared protocol](broader-source-comparison-predeclaration.md) and
[resolved readiness plan](broader-source-comparison-readiness.md) were retained:
eleven input features including ITA and experimental calibrated MST, original
square256 rule-based masks, direct gamma/red/blue outputs, depth3, seed42,
leaf1, no sample weighting and fitting-control-only identity-leaf protection.
C's pool was94 cases (32controls +62primary) before each held-source exclusion.
All variants of the held source/group were excluded together in32 folds.

Exactly34 new trees were fitted:two shared A/B historical-data trees for the
six added held sources and32 C trees. The52 old A/B fold trees and210 historical
predictions/metrics were reused. Only153 new prediction images were added;
363 method/case records are saved in total. No tuning followed the results.

A reporting KeyError on missing variant metadata in the added-source registry
interrupted the first execution. The29 already fitted trees were preserved
and their hashes checked after recovery. The resume used those saved trees and
performed only the remaining five fits. Some image renders were reconstructed
to recover records not yet written; existing PNGs were checked and preserved.
This was bookkeeping recovery, not a second correction-model trial.

## Verification and artifacts

Scripts315–317 run, verify and report the comparison. Verification passed:

- 121 input feature vectors independently reconstructed, including channel
  endpoint fractions, with the matching measurement contract and lookup.
- 34 new tree memberships and protected/unprotected leaf values checked against
  fitting controls/target means; exported raw tree predictions also checked
  against sklearn at fitting time. Verification performed **zero refits**.
- 153 new saved image/metric outputs replayed; outside-mask pixels unchanged.
- 210 historical records retained verbatim,52 saved tree hashes bound,32 folds
  source-separated, and all29 interrupted-fit hashes preserved.

The leaf-value check does not independently prove split optimality; it verifies
saved training membership and prediction values without repeating the fits.
Full suite: **833 passed in14.11seconds**, cache disabled, with JUnit evidence
saved separately in `tests.xml`.
No correction-core code changed in this phase.

Main evidence is under `outputs/broader_source_comparison_v1/`:
`plan.json`, `predictions.json`, `summary.json`, `verification.json`, per-fold
trees/memberships/outputs, `holds.json`, `stopping_decision.json`,
`interruption_recovery.json` and `review.html`. The gallery preserves all121
cases and requests no further annotations. Static image hashes were checked;
no live-browser gallery test is claimed.

## Stopping decision and remaining work

The stronger endpoint research reference and the separate current demo preset
remain unchanged. Parser and beard/moustache work remain on hold pending the
user's adviser discussion. Reserved development-validation and final-test
roles were not opened. Source groups are not verified distinct people, mask
acceptance is not proof of reference-lighting truth, and the MST lookup is still
experimental. This is development evidence, not final validation.

This completes the approved bounded source-expansion comparison. Do not begin
another small correction trial on these sources. The next decision should
address the documented reference/illumination and matching MST calibration
requirements, with an adviser-facing method decision before any method change.
No adviser message has been sent. These findings do not establish mathematical
impossibility or that simply adding more sources will finish the method.
