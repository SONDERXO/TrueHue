# MST calibration and evaluation design

28 October2026. Implements the user's requested design work while retaining
ITA→MST→decision-tree correction. This fixes data roles and reporting; it does
not declare existing measurements valid or authorize a model release.

## Data roles

| Data | Permitted role now | Prohibited claim/use |
| --- | --- | --- |
| Existing418reviewed MST-E attempts | Disclosed, previously exposed mapping development;396successful square256measurements | Untouched final test; correction-tree fitting |
| Existing FairFace correction probes | Development training/evaluation under original eligibility and groups | Independent final performance; race-derived MST truth |
| SCIN metadata/images | Preserve both annotator labels and original holds; source/reference selection under a separately declared policy | Automatic agreement-only admission; case IDs treated as verified independent people |
| Future independent eligible labeled subjects | Potential final mapping evaluation after protocol and grouping are fixed | Repeated tuning after examining outcomes |

The proposal's MST-E-calibration wording is implemented as **mapping development**,
separate from fitting the correction tree. Its evaluation-only wording needs
this explicit qualification in thesis writing. Existing exposure is irreversible:
renaming or randomly splitting the current images cannot create a fresh test.
No new source allocations are changed by this document.

## Measurement and reference contract

Retain the hashed square256contract and all failures. Record raw-image/model/code
hashes, decoded dimensions, face box, selected-pixel count, anatomical exclusion,
mask review status and exact rounding/color assumptions. Use the same input
preprocessing for calibration and future correction features. No historicalITA
substitution. Reviewed sparse patches remain diagnostic references, not a new
estimator and not neutral-color targets. Glasses clearance is required for
reference placement but no automatic glasses detector is claimed.

## Subject-separated development evaluation

Before another fit, freeze one record per image with official MST, subject,
recorded lighting, processing outcome and exposure. Hold all photos of one
subject out together. For each fold, save exact fit/evaluation IDs and hashes.
Calibrator training must never receive held-subject images or labels; summaries
and thresholds use fitting subjects only. Give each fitting subject equal total
weight; photos are repeated observations, not independent subjects.

For each held fold, report:

1. Category/subject support in fitting data, including absence of the held
   subject's category. An interpolated label is not independently supported
   merely because its numerical value can be predicted.
2. Processing failures over all attempted photos, rather than silently dropping
   them from the availability denominator.
3. Exact-category accuracy, within-one accuracy and ordinal MAE on available
   predictions, both image-weighted and equal-subject-weighted. Always include
   training-subject median-label baseline on the exact same evaluated rows.
4. Unsupported-fold and unavailable-prediction counts separately from errors.
   Report the current strict recipe as0available predictions, not0%accuracy.
5. Per-category and recorded-lighting breakdowns with sample/subject counts;
   do not average unsupported categories away.

Leave-subject-out is development evaluation here, not a substitute for an
untouched final test. No hyperparameter or lookup-rule selection on these
folds is permitted without another explicit development protocol and disclosure.

## Lighting sensitivity

Use all qualifying held-subject photos for the primary claim about the existing
capture range. Report well-lit and poorly-lit observations separately using
existing metadata. Do not feed recorded lighting labels to the operational
ITA-only mapping: these metadata are unavailable for an arbitrary gallery image.
Within-subject differences are descriptive and confounded by pose and region
selection; do not call them causal effects of illumination.

A well-lit-only calibration is a distinct, limited method question. It cannot
be substituted after inspecting bad all-light results and then presented as
general gallery-image validation. It would require a declared operational
capture/quality policy and its own evaluation. The current well-lit subset has
seven singleton categories, so it does not resolve independent-category support.
No new filtering, lighting normalization or restricted fit is executed here.

## Algorithm and release gates

The completed midpoint/isotonic-center recipe is retained as failed development
evidence. Do not force pooled centers apart. A different calibration algorithm
must have a scientific rationale and be fixed before a new fit; this design
does not select an algorithm by favorable performance.

For a ten-category validation claim, each evaluated category needs independent
calibration and evaluation subject support. Two subjects/category is only the
minimum condition for such separation, not a statistical sample-size argument
or adequate power. The current reviewed cohort lacks it atMST4/5/7/9/10; the
official full dataset itself has singletonMST7/10. Therefore an entirely
ten-category independently supported MST-E-only claim is infeasible as currently
documented. Obtain suitable additional independent labeled support, or report
an actually agreed limited evaluation scope with unsupported categories explicit.
Retaining ten output labels does not require pretending ten labels are validated.

Release also requires verified measurement-region validity, no subject leakage,
superiority to the same-row median baseline, lighting-specific results and a
documented claim appropriate to the evidence. Baseline superiority alone is
insufficient. No artificial universal accuracy threshold is invented here.
No deployed lookup is permitted merely because a schema says validation passed.

## Downstream correction training

Only after a frozen, justified mapping exists: derive mapped MST from **distorted
input** measurements using that lookup, together with inputITA and facial
statistics. Never substitute the reference's official MST as an inference
feature. Record lookup and measurement-contract hashes in each training row.
Split original sources/known duplicates before variants; hold eligible final
test sources apart. A source-level70/15/15MST-stratified allocation must account
for verified labels/support and prior exposure before it can be called final.

Resolve the paper's light/medium/dark group boundaries and brightness/contrast
operators before tone-dependent generation; no guessed groups or inverse targets.
Keep unchanged/mild controls, source-separated evaluation and no-correction
baseline. Preserve all32unadmitted regenerated candidates and original reviews.

## Concrete current implementation

Script144freezes all15current subject folds and lighting/support inventories
without fitting. This is a reusable evaluation plan bound to the exact saved
measurements. It records why a final ten-category claim remains unavailable.
Next substantive work is securing representative measurement/reference and
independent-subject support or an actual documented limited-evaluation decision.
Another fit on the same unsupported cohort cannot supply that evidence.
Android remains paused; CPM remains deferred. No data acquisition, outreach,
method approval or completed final evaluation is implied.
