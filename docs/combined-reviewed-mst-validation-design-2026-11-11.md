# Combined reviewed MST validation design — 11 November 2026

Status: prepared and verified, **not executed**. No fit or prediction occurred.
Scripts 766–767 package `outputs/combined_reviewed_mst_design_v1`.

The sixty reviewed captures comprise the same ten publisher subjects under
F_cool, H_warm and L_warm at both 600 and 1200 illumination. They are exposed
development data, not sixty independent people or a blind test. Exact decimal
labels, source identities, annotation manifests and all available outcomes remain
bound. Original 600 and 1200 method identities are preserved. Shared measurement
and brush code hashes match, and sixty independent cached-image Lab/ITA replays
are exact under core 76262df2…. Upstream contracts differ; computation parity
does not prove empirical photographic transfer. No original JPEGs were read.

## Fixed candidate and grouping

Propose exactly ten fits of the existing ITA/L*/a*/b* standardized ridge alpha1
recipe, with unpenalized training-label-mean intercept. This estimator supplies
only MST; the final correction predictor remains a decision tree. Keep ITA's
formula unchanged. No features, alpha, condition subsets or model-family sweep.

Each fold holds one person’s six captures together. The other nine people supply
54 fitting captures. Each fitting person has weight1, each row weight1/6. Learn
all scaling, intercept and coefficients using fitting rows only. Predict the six
held captures; retain raw outputs and clip to [1,10] without category rounding.
Total proposed candidate predictions: sixty. No all-data fit or PPR prediction.

## Frozen comparator and prospective checks

Use the ten saved 600-only contextual models from the completed assessment as a
fixed data-expansion comparator. Match by held subject, verify the original
thirty exact rows and nine fitting subjects, and retain models unchanged. Those
models excluded the same held person; applying them to that person's six
captures remains subject-disjoint. This would produce sixty comparator outputs,
without comparator refits. It is a new evaluation on the expanded evidence, not
a rerun or tuning of the closed original assessment. A separate fitting-subject
median uses the nine distinct fitting-person scores, never held labels.

Before execution, freeze these development advancement checks (tolerance1e-12):

- Full sixty-capture, ten-subject, six-condition prediction coverage.
- Combined equal-subject MAE strictly better than both the frozen-model
  comparator on the same sixty rows and the fitting-subject median.
- New 1200-capture MAE strictly better than that comparator on those same thirty.
- Each original 600-condition MAE no worse than its saved contextual result.
- Combined maximum absolute error no worse than the comparator on the same sixty.
- Original 600 maximum error no worse than its saved value, 2.1126542316677384.

Report every prediction/error, clipping, per-condition and per-illumination
metrics, per-subject metrics, within-person prediction ranges and fitting-only
marginal support. Preserve any failure; no automatic tuning or selective gate
removal. These are development checks, not production qualification or changes
to the correction model's joint gates.

## Verification and limits

Independent stdlib checks confirm sixty unique source hashes/case IDs, ten
subjects each with all six conditions, ten exact 54/6 disjoint folds, equal
subject weights, sixty unique held evaluations, unchanged saved comparator models
and bound metadata/cached artifacts. All scientific admission flags remain false.
The subjects are disjoint from the final eight locked groups.

Seven photographic inputs remain above the reviewed maximum L*=61.5026. Even a
passing comparison would not qualify those extrapolations, provide photographic
MST labels, prove mask accuracy or authorize automatic runtime promotion.
Application/support and bounded correction-tree design remain separate.

No further user annotation is needed. Next substantive action, if selected, is
this one fixed ten-fold comparison; no old assessment rerun, all-data refit,
PPR scores, tree fit, image-model calls, acquisition or demo changes. All prior
artifacts remain preserved; final 24 and older locked images remain byte-unread.
