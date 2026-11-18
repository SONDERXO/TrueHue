# Contextual MST experiment implemented — 5 November 2026

The user explicitly selected testing the ITA+Lab candidate. An isolated
decimal-score experiment and subject-held evaluator are now implemented in
`src/ita_estimation/contextual_mst_experiment.py`. The authorised experimental
direction supersedes the earlier ITA-only retention decision for this comparison;
the production/category interface is unchanged. No adviser approval or completed
scientific method validation is implied.

The [implementation protocol](contextual-mst-implementation-protocol-2026-11-05.md)
fixes the exact arithmetic and generated-only execution. The earlier
[method-choice design](lighting-aware-mst-method-choice-2026-11-05.md) supplies
the rationale, comparison and remaining real-cohort requirements.

## What is implemented

Three fixed methods share exactly the same held-subject rows:

- ITA+L*,a*,b* standardized ridge regression, alpha1, with unpenalized intercept.
- ITA-only standardized ridge, alpha1, as the fixed colour-context ablation.
- Median source score of fitting subjects as the constant baseline.

Each fitting subject contributes total weight1 across available photos, both
in population-variance scaling and regression. All observations of the held
subject are excluded from fitting, scaling and baseline construction. Exact
constant columns use scale1; an initial unit test exposed roundoff in weighted
constant-column means, and the implementation was corrected before the saved
fixture run. No settings were selected by real-data performance.

Exact decimal target strings survive in reports. Predictions store both raw
and clipped1–10continuous diagnostic scores, without category rounding. Inputs
require one measurement contract and exactly the four finite original-colour
features. Extra reference/lighting features, unadmitted sources, mixed contracts,
conflicting subject labels, duplicate IDs and invalid scores are rejected.

Admission flags are declarations, not independent verification of skin truth.
Actual admission evidence must be checked before passing real rows to the API.
Unavailable attempts remain in denominators, including folds with no available
fitting measurements; missing predictions have unavailable metrics, not zero
error. Fold reports expose the actual number of fitting subjects/photos even
when mathematically possible support is scientifically inadequate.

The output includes image/equal-subject MAE, condition and descriptive-score-
interval reports, per-subject prediction ranges, fitting case IDs, means/scales,
coefficients and intercepts. Condition names are reporting metadata only. No
filename, source label or recorded light code is used as an inference feature.

## Executed checks, generated data only

Script451 exercised18generated arithmetic rows for six fictional subject IDs
and three fictional reporting conditions. These fixtures are not simulated
skin, physical illumination, real admissions or calibration evidence.

The first leave-subject-out run performs12generated ridge fits (two per held
subject); a second run repeats those12fits exactly. Thirty-six saved linear
prediction replays and18median-baseline predictions match. Fixture results and
inputs round-trip through JSON. This fit count describes script451, not all
additional generated fits made by unit tests. No real measurement rows were
loaded and no real calibration or correction tree was fitted.

Fifteen new tests cover training-only features/labels/scaling, weighted-ridge
objective residuals, subject-photo duplication invariance, decimal preservation,
report-only lighting labels, unavailable outcomes, explicit clipping, constant
features and invalid/leaking input rejection. Together with existing lookup,
integer-calibrator and decimal-reader tests, **55tests pass in12.50seconds**.
This is a focused software check, not a new full-suite run or scientific result.

Saved package: `outputs/contextual_mst_generated_v1/`. Its verification includes
code/protocol hashes and unchanged bytes for the old lookup/calibrator and the
two retained parent manifests. The check does not claim an exhaustive rehash of
every historical package. No image inference, new photo, preprocessing variant,
dataset upload, author contact, admissions or Android changes occurred.

## Remaining boundary before real testing

The current25Stellenbosch technical measurements remain skin-unverified and
unadmitted. The seven complete subjects are not silently promoted to fitting
data. The new method is ready for generated software checks; real predictive
evaluation still requires a justified eligible cohort and subject-held scope.
Do not repeat a readiness inventory or fit the favourable sample automatically.

The experimental output is a continuous source-score estimate. A justified
integer-category adapter and validation are still required before it could
enter `input_mst_index`. The old `CalibratedMstLookup`, integer-only calibrator,
correction-tree schema/three outputs and Android assets remain byte-for-byte
unchanged. No old integer threshold is exported under the new contract, no
continuous score is silently substituted for an index, and MST is not omitted.

This explicitly recorded mapping-method experiment should be discussed with
the adviser before claiming an approved final thesis method. Neither runtime
adoption nor approval follows from the user's experimental-method selection.
