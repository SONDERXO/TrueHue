# Concrete MST method choice — 5 November 2026

**Subsequent status:** the user explicitly selected testing the ITA+Lab candidate.
The isolated [implementation and generated checks](contextual-mst-implementation-results-2026-11-05.md)
are complete. The choice-pending wording below records this document's original
decision stage; production/category adoption and real-cohort fitting remain unapproved.

## Recommendation, not adoption

Investigate **one context-aware MST estimator using measured ITA plus measured
L*,a*,b***, instead of trying to make one ITA-only threshold lookup account for
all lighting. Keep the three correction outputs and ITA/MST inputs in the overall
pipeline. This is a proposed mapping-method amendment, not a fitted estimator,
an implemented runtime replacement or permission to discard MST.

The user authorised defining how MST mapping should handle lighting. The earlier
explicit decision in [mst-method-retained.md](mst-method-retained.md) retains
an ITA-only lookup to official integer MST categories. Therefore this recommendation
requires the user's explicit method choice before implementing/adopting a different
MST estimator. No adviser approval is claimed. The submitted proposal is unchanged.

## Why this is a method decision

The saved [same-location comparison](stellenbosch-support-lighting-results-2026-11-05.md)
leaves median within-person ITA range106.29degrees across three conditions. The
blue–yellow b*mean changes sign across those conditions even on shared regions.
Mask improvements alone did not remove that feature instability. These findings
motivate testing colour context; they do not prove a particular contextual model
will work or prove every scalar lookup impossible.

The source paper investigates learned image-based regression across lighting,
not validation of TrueHue's scalar lookup:
Mbatha, Booysen and Theart (2024),
[Skin Tone Estimation under Diverse Lighting Conditions](https://pmc.ncbi.nlm.nih.gov/articles/PMC11122461/),
doi:10.3390/jimaging10050109. Its results must not be transferred to our cropped
features, preprocessing, subjects or validation. Dataset permission remains
research/noncommercial, citation required, no redistribution without consent;
the article's open-access licence does not override the supplied dataset terms.

## Two concrete directions

| Direction | What it means | Consequence |
|---|---|---|
| Recommended experimental amendment | Test whether ITA plus original-pixel L*,a*,b* can predict supplied decimal MST scores across the declared lighting conditions | Retains ITA and MST in the correction pipeline, but changes how MST is estimated; needs user choice and disclosure before implementation |
| Preserve the exact ITA-only method | Retain the current calibrated threshold interface and keep calibration on hold until a defensible measurement/domain policy is established | No alternative MST predictor; no silent well-lit-only selection or claim of all-light performance |

Selecting a lighting condition after seeing better outcomes, feeding enhanced
recognition-copy colours into measurement, using filename lighting codes at
inference, swapping atan for atan2, or inserting official source MST into a
correction feature are not shortcuts authorised by either direction.

## Exact first candidate if the amendment is chosen

Use one deliberately simple development candidate: standardized, regularized
linear regression (ridge, alpha1.0, intercept enabled) from the four measured
features `input_ita_degrees`, `input_mean_l_star`, `input_mean_a_star`,
`input_mean_b_star` to the supplied continuous decimal score. Standardization
must be computed on fitting subjects only, with each subject receiving equal
total weight in both scaling and regression. Use a zero-variance scale of1;
do not append filenames, lighting codes, subject IDs or source labels as features.
No hyperparameter sweep, image CNN, new pretrained model or predicted lighting
classifier is proposed for this first comparison.

This is a testable baseline candidate, not a claim that these four colour
features uniquely determine illumination or physical pigmentation. Complex
camera/lighting effects can remain unresolved. Predictions are clipped to1–10
as an explicitly declared bounded-score diagnostic; preserve unclipped values
for reporting. No decimal target is rounded or discarded.

The primary comparator is a fitting-subject median-score constant on exactly
the same held rows. An ITA-only ridge model with the same fixed alpha/scaling
and folds is the predeclared ablation: it tests added colour context, not the
existing integer-category threshold recipe. Neither diagnostic is the old
lookup or a production MST label generator. These three fixed methods are the
entire proposed comparison, not a menu for performance-driven searching.

No fit is authorised by this document. The present25technical measurements
remain skin-unverified and unadmitted. No fit of the seven complete keys is
proposed. A separately justified eligible development cohort and support/coverage
criteria are still required before real labels enter fitting.

## Evaluation rules before real fitting

- Bind the exact measurement/recognition contract and original-pixel features;
  protect individual labels, images and manifests as private local evidence.
- Keep every photo of each publisher subject in one role. Use subject-held
  development folds; the30already exposed photos are not an untouched test set.
  Fold counts and cohort size remain unassigned until eligible coverage exists.
- Keep all attempted rows in coverage/failure reports. Exclude unavailable
  measurements from conditional error arithmetic only, with original denominators
  and reasons visible; never treat missing prediction as zero error.
- Report equal-subject and image-weighted absolute score error, errors separately
  for each recorded condition, descriptive score-interval coverage and within-person
  prediction variation. Lighting metadata is for reporting, not model routing.
- Compare all three methods on identical held rows. Scaling, regression, median
  baseline and any uncertainty summaries may not use held-subject labels or
  statistics for fitting. Do not select settings using these outcomes.
- Baseline superiority is necessary evidence of useful prediction, not sufficient
  validation. Disclose unsupported score ranges, condition failures and subject
  counts; no universal numeric acceptance threshold or adequate power is invented.
- Evaluate the final correction tree separately. A mapping-score improvement is
  not correction-quality improvement, true-colour recovery or unseen-device parity.

## Interface and paper consequences

The existing `CalibratedMstLookup`, integer-only calibrator, configured MST indices,
tree feature schema and Android assets remain unchanged. A successful continuous
diagnostic would still need a justified integer-category interface/evaluation
policy before entering `input_mst_index`. Do not silently round predicted scores
into categories or replace the index with a continuous score.

If the contextual direction is selected, record it as an explicit C07/C08
amendment proposal: before, calibrated ITA-only thresholds; after, contextual
MST score estimation from ITA+Lab under subject-held evaluation, with category
deployment unresolved. Retain ITA as a separate correction input and gamma/red/
blue outputs. Discuss the mapping amendment and decimal/category policy with
the adviser before claiming the thesis methodology is approved or final.

## Completed in this decision turn

The exact recommendation, alternative, fixed candidate, comparator/ablation,
leakage controls, source citation and interface consequences are now concrete
and reviewable. No new photos, feature extraction, model passes, calibration/
tree fits, code/runtime changes, admissions, contact or dataset transfers occurred.
The remaining input is the user's method choice, not another readiness audit.
