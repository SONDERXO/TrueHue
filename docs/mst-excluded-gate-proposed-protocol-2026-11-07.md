# Proposed single gate restriction: exclude estimated MST from the gate only

7 November 2026. **Proposed, not authorized or fitted.** This follows the
completed saved-trace clean-preservation audit. It does not activate a sweep.

## Reason for this specific comparison

The constrained gate's estimated-MST term is the largest positive difference
from the nearest protected fitting-clean vector in all3later clean failures and
4of7development clean failures. One later failure occurs close to a fitting-clean
vector (standardized distance0.351). Two severe clean errors dominate the summed
per-photo error, with different wrong controls: darkening in one, colour in another.

This supports testing the gate's dependence on estimated MST, not claiming that
the estimate is wrong or that deletion must solve the problem. The same feature
can carry useful information for distorted inputs. Nearest-reference terms are
descriptive, not a causal retraining experiment or a confidence calibration.

## One change

Use the same clean-constrained signed-benefit gate. Add the exact constraint
`coefficient[input_mst_score] = 0` for that gate. Keep the12-feature interface,
frozen training means/scales/weights, alpha1 objective, saved benefits, same clean
constraints (score<=-1e-6), strict score>0 inference rule and original optimizer
settings. No threshold, margin, loss, seed, weights or capacity search.

**ITA, estimated MST and Lab measurements remain in the correction predictors.**
The upstream MST estimator and three correction controls are unchanged. This is
a restriction on the extra apply/no-apply decision, not removal of MST from the
retained skin-tone-aware correction method.

## Execution if separately agreed

-10nested held-group gate fits and1full gate fit,11total; same excluded keys,
  fitting rows and labels as the completed constrained comparison.
-0new MST/photographic-control/target fits,0image-model forwards,0new sources,
  masks, distortions, labels or annotations. Original artifacts are preserved.
-Apply the new gate only to the already-saved unchanged or original-control
  outputs. Keep all1428condition records, failures and original availability;
  duplicated clean conditions are not independent photos.
-Compare with the retained gate, unconstrained signed gate and current
  constrained gate in separate working256, borrowed224, actual-input224 and
  fallback224 tables. Do not pool cohorts or renderer conditions.

## Acceptance and verification

Use the previous necessary development screen: zero changed pixels on all29
available held-group clean photos and23later clean photos, plus lower core RGB
MAE than the retained gate on both held-group256 and fallback-native224. Preserve
the failed originals and undefined-ITA fallbacks separately. Always report
individual harms, stress errors, action/missed-benefit costs and selected visual
results, even if the screen passes. Passing is not deployment or final validation.

Verify zero MST gate coefficient, all290repeated fitting constraints, fitting-key
exclusions, frozen normalization/weights/benefits, gate arithmetic, untouched
controls, unchanged pixels outside masks and source hashes. Inspect all held and
later clean boards plus fixed distortion/focal contexts. Preserve a rejected
candidate without automatic retry or selection of another feature.

The current cohorts are development-exposed. This comparison cannot provide an
untouched generalization result, fairness validation, object-mask truth or app
adoption. No Android/desktop runtime change follows automatically.
