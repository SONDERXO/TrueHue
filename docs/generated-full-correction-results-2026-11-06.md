# Generated full-schema correction check — 6 November 2026

The feature-to-controls software check passed. Script
`scripts/470_check_generated_full_correction.py` uses 18 arithmetic rows from
six fictional groups, all five ordered `MST_FEATURES`, and the retained three
positive correction outputs. Integer MST indices are fictional inputs, not
estimates, photo labels or a continuous-to-category adapter.

The fixed depth-3, seed-42, minimum-leaf-1 target-standardized procedure was
used for six leave-group-out folds. Each fold fits 15 rows and predicts three
held rows. Six additional fits replace only held targets with extreme values:
exported trees and fitting normalization remain identical. Total: 12 generated
tree fits, zero real-data fits. Grouping is artificial and does not establish
person identities or photographic evaluation folds.

Checks completed:

- Six independent fitting-target mean/standard-deviation checks.
- 108 JSON-round-tripped portable predictions match inverse-normalized fitting
  model predictions to absolute tolerance 1e-12, zero relative tolerance.
- 108 named-feature order checks preserve predictions.
- Nine invalid feature vectors reject missing, null, empty, nonfinite, boolean,
  out-of-range or fractional MST and an extra reference feature.
- A source whose descendants cross group boundaries is rejected.
- Fixture rows and bound code/old lookup/calibrator bytes remain unchanged.

The harness validator is local to this generated check; it does not change
production validation, train a contextual MST estimator or exercise upstream
cross-fitting. It does not render images, validate segmentation, measure colour
recovery, compare photographic baselines or establish scientific accuracy.
Generated target arithmetic deliberately has no physical illumination claim.

Private regenerable evidence: `outputs/generated_full_correction_v1/`, including
fixtures, six exported fold trees/predictions, verification, input hashes and
artifact hashes. The script refuses an existing output directory. The saved
manifest was checked independently after execution.

Existing focused suites `test_target_scaled_tree.py` and `test_portable_tree.py`:
**32 passed in 5.99 seconds**. This is not a full-suite or device check. No new
photo processing, mask changes, real MST calibration, photographic tree fitting,
admissions, Android/runtime changes, contacts or sharing occurred.

The [controlled experiment plan](controlled-correction-experiment-plan-2026-11-06.md)
remains the execution boundary. Compatible MST category meaning/mapping,
actual skin/reference eligibility and justified person grouping still need
substantive resolution before photographic training. Passing these software
checks does not activate another batch, model sweep or fitting task.
