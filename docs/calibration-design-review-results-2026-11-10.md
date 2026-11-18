# Calibration-design review — 10 November 2026

The review identifies two separate issues: information/order loss in the scalar
ITA-only mapping, and limited calibration coverage of the photographic inputs'
brightness. A fixed contextual candidate can be tested, but better performance
on the30labelled photos would not by itself validate transfer to the photographic
correction data. No new mapping, tree or prediction was fitted/run in this review.

## Why the scalar mapping pooled the inputs

Script749 checks all30reviewed labelled records, preserving exact source hashes,
scores and features. Of435unordered observation pairs,30same-subject pairs and
nine equal-score cross-subject pairs are excluded from the ordering diagnostic.
Among the396distinct-subject/different-score pairs,136contradict a nonincreasing
ITA→MST ordering. These are dependent descriptive pairs, not396independent people
or a predictive-accuracy statistic.

| Recorded condition | Different-score subject pairs | Ordering conflicts |
| --- | ---: | ---: |
| F_cool_600 | 44 | 32 |
| H_warm_600 | 44 | 3 |
| L_warm_600 | 44 | 2 |

For example, cool cases04and25have reference scores2.4and9.2but ITA68.8049and
82.3052. The darker reference has the higher measured ITA, contrary to the
mapping's intended direction. Allten cool records have L*<50and b*<0, so the
retained ratio( L*−50)/b*is positive; all20warm b*means are positive. This is a
mechanical property of these recorded values, not proof of a causal camera
mechanism or permission to change the ITA formula.

The19observations in the fitted plateau have subject-weighted reference mean
4.494736842105263, reproducing the pooled value exactly. The constant is not a
software default. A nonincreasing scalar fit must compromise when its measured
orders conflict with the reference scores.

## Existing contextual candidate

The separate L*,a*,b*statistics preserve magnitudes and colour context compressed
by the scalar ITA ratio. Descriptively, within-condition L*correlates negatively
with the source scores in allthree conditions (about−0.94to−0.98), whereas cool
ITA has the opposite sign from warm ITA. This motivates a candidate, not unseen-
subject accuracy or an intrinsic-tone measurement claim. No exact conflicting
four-feature collisions were found; absence of collisions is not a separability
or single-photo identifiability proof.

The project already implements subject-balanced standardized **ITA+L*,a*,b*
ridge alpha1**, with an unpenalized intercept and decimal-score output. A prior
exploratory test obtained equal-subject MAE0.7448on29/30available observations.
All30originals match today's source hashes, subjects, conditions and reference
scores. However, its masks/measurements were different and unadmitted. That old
error is historical rationale only, not the current candidate's result, a fresh
independent cohort, reusable coefficients or validated calibration transfer.

The proposed bounded test is specified in
[the contextual validation protocol](contextual-reviewed-mst-validation-protocol-2026-11-10.md):
exactly ten current-subject-held fits of that existing recipe, no alpha/features/
condition search, no all-data fit or PPR predictions. Use the saved30case
reviewed-mask isotonic/median predictions as exact matched comparators after
source/annotation/numerical joins. Fix advancement checks before fitting: better
overall error, no worse condition error or maximum error, and full30case coverage.

This changes **MST calibration**, not the final correction predictor. ITA and
MST remain; final gamma/red/blue decisions remain a decision tree. Contextual
MST is an experimental method extension from the scalar lookup, consistent with
the earlier continuous-contextual branch; no adviser/panel approval is inferred.
Its output is derived from existing inputs, not new independent information.

## Separate brightness/domain coverage limitation

Script752 audits the14photographic inputs without predicting their labels:

| Feature | Calibration range,30records | Photographic range,14roles | Outside calibration marginal range |
| --- | --- | --- | ---: |
| ITA | −82.5892to85.8743 | −32.1202to83.6423 | 0 |
| L* | 8.6235to43.8131 | 37.6508to71.8763 | 12 |
| a* | 1.1462to21.2804 | 9.7922to25.4444 | 1 |
| b* | −8.1186to30.7629 | 1.8365to35.3533 | 1 |

Twelve photographic roles are outside at least one calibration marginal range.
Being inside every marginal range would still not prove joint support or
statistical compatibility. The fact that all14ITAvalues were inside the scalar
fitting range masked this separate context-domain gap. These are image-derived
brightness values, not an assertion that the labelled people all have dark skin.

Therefore, even a passing contextual30case developmental test must **not** trigger
automatic transfer/admission on the brighter photographic inputs. A later
application design must address and report reference coverage across the actual
brightness/cast domain. It must not regard varied PPR scores or clipping as
evidence of correct tone. PPR labels are still missing. Do not fabricate labels,
lighten the calibration images to match references, select warm-only records or
use final/locked subjects to fill the gap.

The fixed contextual validation remains one useful proposed diagnostic. It is
not a complete fix selected for the working model. Brighter labelled reference
coverage is a separate data-readiness issue to assess from eligible existing
evidence before planning any acquisition or annotation; no new source expansion
or collection is executed/selected here. No more current mask reviews are needed.

## Artifacts, verification and next boundary

Private evidence, fold definitions, prospective validation plan and coverage
audit are under `outputs/calibration_design_review_v1`. Scripts749–752 perform
no estimator fitting, mapping predictions, image reads or action/tree experiments.
Independent verification counts score-ordered pairs using a separate scalar
enumeration and reproduces condition correlations, exact30case comparator joins,
the fixed candidate/gates and subject allocations. All checks pass.

The next **candidate validation**, if selected for execution, is the prepared
tenfold contextual test only. Do not blindly rerun script479 (which fits two
models per fold under older measurement roles) or reuse a qualified evaluator by
setting admission flags true. A separate development evaluator must preserve
the false scientific flags. No automatic second candidate follows a failure.
Passing would still require addressing the application-coverage limitation
before a defensible PPR application or bounded tree-comparison decision.

No tree-family question is reopened, no MST feature is removed, and no working-
model success is promised. The current correction predictor is unchanged. All
prior reviews, snapshots and closed results are preserved. Final24photos and
older locked allocations stay byte-unread. No downloads, uploads, contact,
commit, push, original-image reads, active-runtime or Android changes.
