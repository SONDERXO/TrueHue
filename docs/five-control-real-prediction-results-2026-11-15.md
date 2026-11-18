# Five-control real source-held prediction: not advanced

15 November2026. Completed the fixed11-fold prediction test authorized by the
user, using the verified66feature rows without recomputation. Independent
verification passed660fitting routes,66held routes and132tree/constant renders
with metrics and the frozen role checks. The scientific result is
**NOT_ADVANCED: closed, not adopted**. No new review or rescue run is selected.

## Outcome under the predeclared checks

The learned tree improves all four exposure/combined families on average,
but the colour-only family worsens against both input and the fitting-only
constant comparator. This fails the frozen requirement that each nonidentity
family improve RGB MAE and DE against both comparators. Positive exposure means
cannot override the colour failure. No criterion or tolerance changed.

Source-equal primary alpha>0 means over11cases per role follow. RGB MAE is
8-bit channel codes; DE is CIEDE2000 under assumed decoded sRGB. These are
photographic restoration errors, not physical skin-colour accuracy.

| Role | Input RGB | Tree RGB | Constant RGB | Input DE | Tree DE | Constant DE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Identity | 0 | 9.162 | 16.816 | 0 | 3.994 | 5.912 |
| Colour-only | 6.666 | 20.790 | 17.467 | 5.179 | 8.346 | 7.075 |
| Exposure-under | 71.552 | 14.355 | 80.559 | 24.482 | 6.309 | 28.151 |
| Exposure-over | 70.494 | 16.416 | 54.429 | 22.100 | 7.565 | 17.824 |
| Combined-under | 71.944 | 20.146 | 81.345 | 25.346 | 8.378 | 28.991 |
| Combined-over | 71.395 | 15.517 | 55.112 | 22.296 | 7.140 | 17.297 |

Colour-only has8RGB/DE improvements and3regressions versus input; the three
large regressions dominate its mean. Exposure-under has no individual RGB/DE
regressions. Exposure-over has one DE regression (49131), and combined-under
has one RGB regression (29617). Combined-over has none in these metrics.
All cases remain; no source or metric is pooled away.

## Saved-route explanation of the three colour failures

The following is arithmetic inspection of existing fitting rows, reached leaves
and saved held predictions. No new fits or predictions were made for it.

| Held colour-only source | Input RGB | Tree RGB | Roles in its reached fitting leaf |
| --- | ---: | ---: | --- |
| 29617 | 6.667 | 62.868 |1exposure-over +1combined-over |
| 48879 | 6.667 | 75.107 |1exposure-over +2combined-over |
| 49131 | 6.666 | 62.033 |2exposure-under +4combined-under |

These three colour inputs receive controls averaged from exposure-type fitting
examples, not the reference-aware colour controls. Each reached leaf excludes
the held source as required. This establishes incorrect correction-family
selection for these cases. It does not by itself identify a new reliable
inference cue, prove source confounding the only cause or authorize a guard/
normalization/depth/feature rescue. Earlier closed colour failures stay closed.

## Identity behavior and operator-versus-prediction distinction

All11held identity inputs change numerically. Mean primary RGB error is9.162;
range.547–72.426. Mean whole-crop RGB change is3.076codes. Source48879 is the
large identity outlier and receives a fitted exposure-over control vector.
The changes are not automatically reclassified as human-unwanted judgments:
no visual acceptability review ran, and the user allows slight acceptable
differences. The numerical colour failure already determines NOT_ADVANCED.

The preceding five-control capacity comparison remains valid: reference-aware
local controls restored exposure/combined cases much better than the three-
control local fits. It did not show that a tree could select those controls.
This prediction test demonstrates that the chosen281-input/depth4/raw-five-
target recipe does not reliably preserve that benefit across all required
families. It does not disprove all five-control operators or decision trees.

Raw target variation remains gamma-dominated, source-specific controls and
conditioning remain unresolved, and nine mapper endpoint cases plus six
offset-bound targets are retained. No new claim that normalization, extra
capacity, alternate starts or a different mapper will repair these failures.

## Exact execution and verification

`scripts/run_five_control_real_prediction.py --execute-fixed-prediction-test`
verified the frozen design, generated workflow QA, dependency versions and
completed real feature-preparation hashes before fitting. It reused all66saved
input-only281float32vectors and exact saved five-control targets. There were
exactly11native tree fits,0target/mapper/baseline refits and0feature recomputations.
All settings and source roles remained fixed; no retries or sweep occurred.

Each fold fits60rows from ten other complete source lineages. The independent
scalar route/leaf-mean/export checks finish for all11fits before the first held
prediction. Inference projections contain features and case metadata only,
without target or reference fields. Role/source metadata is not a feature.
All66held control predictions are sealed before reference pixels are decoded
for scoring. Fitting-only constant means use the same60rows, never held targets.

Only the declared cached directional input/support packs were read for scoring.
The support `reference`, `alpha` and `protected` keys were decoded after the
all-fits/held-controls barriers; input packs supplied only `input`. No original
identity pack, raw photograph, baseline-output key, measurement re-extraction,
parser or new mask was used. The approved ear and59807manual support remains
exact, with all protected/zero-alpha pixels unchanged relative to actual input.
Whole cached files were hash-read and rechecked unchanged.

`scripts/verify_five_control_real_prediction.py` binds the scored arrays back
to those original cached inputs/support and exact prepared feature rows. It
imports no trainer/optimizer, performs0fits and uses the already-tested separate
route, leaf-mean and scalar-render/metric verifier. It checks660fitting routes,
66held routes,132tree/constant renders, source-equal means, case regressions
and the frozen NOT_ADVANCED label. Standard DE uses scikit-image with separate
conversion/aggregation, not an independently derived colour-difference formula.

The workflow's existing54focused tests and full generated11-fold rehearsal
were already bound and passed; source implementation hashes remained identical.
The real entry point is a thin adapter on that workflow and received complete
real-record numerical replay, not a new full-suite or device-validation claim.
Generic log text says generated/research; actual row/model provenance remains
generated_fixture=false throughout, verified against the prepared real rows.

Evidence: `outputs/five_control_source_held_prediction_v1/` contains the bound
plan, reused rows, native-fit accounting,11models and fitting proofs, sealed
inference inputs/controls,66evaluation records, independent verification and
assessment. All bound artifacts were rehashed after verification. New research
use is explicit; original source admission flags remain unchanged.

## Stopping decision

Close this fixed prediction recipe without adoption, additional fits, changed
gates or a user-rating batch. Do not request66ratings for a numerically failed
candidate. Preserve its operator-capacity evidence and complete prediction
failure separately. No all-data/final model, fallback-to-exposure-only thesis,
scope abandonment, Android migration or paper completion is inferred.

Future model research needs a substantive rationale for selecting correction
families and preserving accepted inputs, checked against the closed history;
simply extending the renderer or feeding stronger distortions is insufficient
for this recipe. No next training intervention is selected by this result.

These repeatedly exposed unlabelled FFHQ sources provide no independent
darker-skin bias-reduction qualification. That goal remains central and
unfinished. All prior artifacts/closures/ratings and approved manual/ear
support preserved; locked final24/older contents/manifests remain unread.
No runtime/Android/manuscript edits, new acquisition/contact or ratings.
Model unfinished; paper paused; November25 deadline retained.
