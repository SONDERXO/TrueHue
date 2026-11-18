# Proposed fixed contextual calibration validation — 10 November 2026

Status: **design prepared, not executed**. This is one bounded candidate proposal
after the authorized calibration-design review. It does not reopen the closed
isotonic assessments, old contextual experiments or correction sweeps. No
additional annotations, image reads, model assets or acquisition are needed.

## One candidate and its role

Test the existing subject-balanced standardized ridge recipe from
`src/ita_estimation/contextual_mst_experiment.py`, fixed alpha1 and unpenalized
intercept, with exactly **inputITA, inputL*, inputa*, inputb*** in that order.
Predict the original decimal publisher MST score, retaining raw predictions and
explicit clipping to[1,10]. No category rounding or label substitution.

This is contextual MST estimation instead of an ITA-only monotone lookup. It is
a documented experimental method extension, consistent with the earlier
continuous-contextual MST branch; it is not identical to the proposal's scalar
lookup and does not imply adviser/panel approval or a proposal amendment. The
final correction predictor remains the decision tree. The calibrator predicts
only MST, never gamma/gains or correction decisions; there is no hidden
replacement for the final tree. ITA and its formula remain unchanged.

Retain the15other correction-feature definitions, three-output operator,
14actions and depth4tree contract. This candidate introduces no new image feature,
condition tag, subject identifier, target reference, PPR label, external model or
inference metadata. Separate L/a/b preserve existing input context rather than
claim new independent information. A varying derived MST feature alone does not
prove accuracy, transfer or meaningful tree use.

## Frozen data and fits

Use exactly the30reviewed labelled rows under measurement core76262df2…, allten
publisher subjects and allthree conditions, preserving raw decimal references,
review/producer provenance and false scientific admission flags. The existing
qualified-evaluator admission flag must not be changed to trick it into accepting
the data. Use a separate explicit developmental evaluator with appropriate
validation, reusing only the fixed arithmetic recipe.

Run **ten ridge fits only**, one per existing publisher-subject-held fold. Each
fold fits27rows from nine subjects and predicts the three held observations.
Each fitting subject has total weight1; row weight1/3. Compute feature means and
population standard deviations from fitting rows only with those weights. Use
scale1only for an exactly constant fitting column. Fit an unpenalized intercept
equal to the weighted fitting-label mean, then ridge alpha1 on standardized
features with the same weighting convention as the existing implementation.

Do not perform an alpha/feature/sign/condition/architecture sweep, extra ablation,
all-data fit or PPR prediction in this validation run. No held subject influences
scaling, intercept, coefficients, baseline or model selection. No outlier,
condition or successful-only subset may be selected. If frozen data bindings no
longer match, stop rather than drop or impute. The data are exposed development
subjects, not a new blind test.

## Matched comparators and prospective development gate

Reuse the saved30case predictions from the completed reviewed-mask isotonic
assessment and its fitting-subject median baseline **only after exact** source
hash, case/subject/condition, decimal-score, annotation-manifest and numerical
feature joins. They are valid paired developmental score comparators here;
their coefficients are not copied or relabelled. Do not rerun those fits or use
the older29-case contextual performance as the current comparator.

Before execution, freeze these checks for advancing this calibration candidate:

-30/30attempts/predictions, allten held subjects and allthree conditions retained.
-Equal-subject MAE strictly below both saved isotonic1.611868168093567and saved
  median2.99, with1e-12comparison tolerance.
-No condition MAE exceeds its saved isotonic comparator by more than1e-12:
  F_cool2.566875, H_warm1.1595446272405165, L_warm1.1091848770401846.
-Maximum absolute error does not exceed the saved isotonic maximum
  4.966666666666667by more than1e-12.

Also report every raw/clipped prediction, clipping counts, per-subject errors,
per-condition errors and within-subject score ranges. Lower variation without
better predictive errors is insufficient. These are prospective **development
advancement checks**, not production-calibration thresholds or replacements for
the unchanged correction-model joint gates. No significance or fairness claim is
established with ten subjects.

## Conditional next phase

If any advancement check fails, close this one comparison and preserve the
failure; no automatic tuning or repair. If all pass, a **separate** explicit
one-fit application design may fit the same fixed recipe on all30external rows
and produce14input-only photographic scores, with raw/clipped/support and
transfer diagnostics. Do not inspect PPR score variation to choose/tune this
calibration candidate. PPR lacks labels, so nonconstant outputs would remain a
sanity finding, not PPR mapping accuracy or automatic qualification.

That application would require a new versioned mapping/application contract
declaring the contextual estimator, preserving core76262df2… and all old mapping
and feature artifacts. Never attach old isotonic coefficients or an old contextual
model to a new hash. A subsequent bounded correction-tree protocol must still
specify constraints, comparators, complete inputs, targets, group allocation and
the unchanged quality gates. No tree fit, release fit, runtime/Android change or
final-holdout access is authorized by this design.
