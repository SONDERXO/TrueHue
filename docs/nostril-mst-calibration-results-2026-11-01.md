# Skin-only ITA/MST recalibration: completed results

1November2026. The adopted whole-face+neck correction and inward blending design
is frozen for continued development. Measurement remains separate. The user
authorized one matching recalibration/evaluation cycle; it is now complete.

**Result: the mapping is not yet reliable.** The exclusions are reproducible,
but the held-subject results remain weak. No new runtime lookup was exported,
no correction tree was fitted and no alternative calibration settings were tried.

## Measurement and exclusion checks

Exactly418previously exposed MST-E mapping-development photographs from15subjects
were attempted with the actual nostril-measurement pipeline.393succeeded and25
failed:21face detection,1landmark and3semantic geometry/mask failures. Failures
were retained; no old-ITA fallback or selective retry occurred. The successful
image memberships and all15fold fitting memberships match the prior semantic
cycle exactly, verified from saved IDs.

For all393successful measurements, the saved masks contain zero pixels from
forbidden predicted classes, hard eye/brow/mouth exclusions and the conservative
nasal guard. Neck, whole-face correction pixels and blending alpha never enter
Lab/ITA/endpoint features. The guard removes0–270previously selected pixels per
MST-E photograph; zero can mean those pixels were already absent. It excludes
some surrounding nasal skin, not precisely annotated nostril holes.

These are programmed exclusion checks, not ground-truth accuracy. All15fixed
diagnostic boards were inspected. Some beard pixels and the known subject_7
face-covering example remain misclassified as skin. The parser has no distinct
beard class. We therefore cannot claim that every actual hair/occluder is
excluded, or that accepted photographed skin equals correctly lit reference
color. No new beard model or post-result mask modification was introduced.

## Matching subject-held calibration

The same decreasing isotonic/interpolation method was fitted once per held
subject, with equal total weight per fitting subject. All photos of the held
subject stayed outside fitting. The baseline uses the median label of fitting
subjects only. Counts, weights, knots and predictions were saved.

| Measure, same393photos | Prior semantic mapping | New nostril-excluded mapping |
|---|---:|---:|
| Mean absolute MST category error | 2.097 | 2.125 |
| Equal-subject mean error | 2.132 | 2.165 |
| Exact category accuracy | 12.47% | 12.98% |
| Within one category | 36.64% | 35.88% |

The new mapping has lower mean error than its fitting-subject median baseline
(2.125versus2.855), but lower exact accuracy (12.98%versus13.99%). Removing the
nasal region did not produce an overall mapping improvement on this cohort.
This is one fixed development result, not proof that the exclusion is wrong or
that another small setting change would solve the problem.

The new mapping's available well-lit observations have mean error1.962;
poorly-lit observations2.370. Recorded lighting groups are descriptive and
confounded with other image differences; no causal lighting conclusion or
well-lit-only refit follows.

177of393measured photos lack a different fitting subject with the same official
category. Categories4/5/7/9/10have only one subject each. Repeated photographs
do not supply additional independent subjects. This exposed development cohort
cannot establish untouched final performance or supported ten-category fairness.

## Decision and next direction

Retain the user's masking/exclusion design, but do not adopt this mapping as a
reliable runtime lookup or unblock correction training using old incompatible
features. The measurement contract remains
`1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7`.
No all-row mapping fit/export was performed in this cycle. Both deployed
experimental correction demos remain unchanged.

Stop this calibration cycle. Do not start another radius/threshold/recipe trial
on these same subjects. Further reliability work needs qualified measurement
references and genuinely independent labeled support under a declared capture/
evaluation scope. Existing beard/face-covering concerns must be handled through
explicit eligibility or a separately justified measurement change, not hidden
outcome-dependent removal. Better reference evidence is a direction, not a
guaranteed fix or proof the retained thesis method is impossible. No further
large review batch is requested at this checkpoint. Adviser-request timing is
not a technical prerequisite under the user's direction.

## Reproducibility

- Frozen protocol: `docs/nostril-mst-single-cycle-protocol-2026-11-01.md`.
- Source/code/model hashes, access ledger, all418records, saved category maps,
  landmarks, masks and guards: `outputs/nostril_mst_measurement_v4/`.
- Subject memberships/weights, predictions, subgroup denominators and metrics:
  `outputs/nostril_mst_calibration_v4/summary.json`.
- Independent393vector/mask/exclusion replays,15refits,393prediction replays
  and complete metric-denominator replay: `outputs/nostril_mst_verification_v4/`.
- Fixed15-case measurement gallery:
  `outputs/nostril_mst_verification_v4/diagnostics.html`. It is not a review
  export or a set of approved masks.
- Scripts352–354. Full Python suite: **890passed in20.10seconds**, cache disabled.
  Two added tests guard recomputation/no parent-mask mutation and failure without
  stale features when nasal geometry is unavailable.

No reserved correction-evaluation pixels, correction-tree fitting, new mask
approvals, new-source selection, professional contact or invented ratings.
