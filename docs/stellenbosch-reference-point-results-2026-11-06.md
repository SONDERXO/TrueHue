# Actual reference-point review results — 6 November 2026

The user's real six-image export was found in the private review folder,
validated and imported without modifying its bytes. **238actual marked points
provide concrete evidence of selected-skin omission and some unwanted inclusion.**
This completes the six-case review; there are no pending answers for this task.

Export SHA256: `99d477c3e080e6e7bb6845b1e594f4bf2aed7df97d1743b1670f2d31cce76c55`.
It matches the fixed manifest
`9d7637101adf11b4a8f5595536ce89f4cd1ee042ae29451d6737c69784004293`.
All six images have marked status, with no uncertain points or Cannot judge
responses. Reviewer identity is preserved privately and not reproduced here.

## Actual sparse-point comparison

| Quantity | Result |
|---|---:|
| All actual points, six images | 238 |
| User-labelled skin / hair-beard / object-other points | 129 / 101 / 8 |
| Points with unavailable prediction, landmark-failed image | 31 |
| Skin points with an available prediction | 113 |
| Those skin points selected by final mask | 54/113 (47.8%) |
| Hair/object points with an available prediction | 94 |
| Those unwanted points selected by final mask | 9/94 (9.6%) |

The31unavailable points comprise16skin and15hair/beard marks; their lack of a
prediction is not an all-negative mask or successful rejection. Of the nine
unwanted inclusions, eight are hair/beard and one is object/other. Seven of the
hair/beard inclusions occur in the beard example; the other is in the broad-
support control. The object inclusion occurs in the glasses example.

These proportions are agreements at deliberately selected native pixel centres,
not whole-mask recall/precision/accuracy, native sample independence, colour
validity, population performance or evidence of adequate calibration. The user
had prior exposure to outputs; this is not independent/blinded validation.
No dense ground truth, reviewer uncertainty or expert judgement was fabricated.

## Where skin points were missed

For the59user-labelled skin points not included by an available final mask:

- 52were already absent from the parent mask outside its mapped anatomical
  exclusions. This does not attribute every point to a parser error; face/neck
  scope, component selection and geometry can also contribute.
- 5were present in the parent and removed by FaceOcc.
- 2fall in the mapped anatomical-exclusion probe.

This changes the repair priority for the present frozen candidate: parent
selection omissions and residual facial-hair/material protection need attention;
another unstructured FaceOcc enhancement is not supported merely by these misses.
It does not overturn earlier saved findings from earlier candidates or imply
FaceOcc is universally correct now.

## Face-only measurement versus neck marks

All six actual-point comparison boards were visually inspected after import.
The user marked visible neck skin as well as facial skin. Those neck labels
are preserved as skin, but the current colour-measurement region is face-only;
neck exclusion is not automatically a defect. Correction face/neck support is
a different component and was not evaluated as this measurement mask.

A separate geometric-oval diagnostic finds83available skin points inside the
existing face outline,45selected, and30outside,9selected. The38omissions even
inside that diagnostic outline show the result is not explained only by neck
marks. The oval is a prediction, not anatomical truth: outside points also
include contour/mapping uncertainty, so30must not be reported as30neck points.
This secondary breakdown does not replace the original all-point denominator
or relabel any user mark to improve the result.

The glasses example retains only1/17available user skin points; the dim forehead
example retains3/17. The beard example retains16/24skin points while also
including7/16hair/beard points. The broad-support control retains26/33skin points,
with one unwanted inclusion; some control misses are outside face-only scope.
These are selected-case diagnostics, not per-skin-tone performance estimates.

## Decision and next repair scope

Keep the masks and actual user export frozen. No calibration/training admission
is established by this review: reference points expose both omission and material
inclusion, while native detail and cross-lighting/cohort coverage remain unresolved.
No real mapping/ablation/baseline fit, correction-tree training or app update ran.

The specific next repair question is how to retain clearly visible facial skin
in the parent while excluding facial hair and objects. Any candidate must be
separately fixed, retain failures and test both sides of that tradeoff, with
glasses/beard concerns visible. Do not fill a mask using the user marks, tune
thresholds until those points pass, or present a later fit to these exposed
points as independent validation. They are development reference evidence.
No repair, model sweep, new sample batch or additional review task is activated
by this import. Do not repeat the completed six-case review or another readiness
inventory before proposing substantive measurement work.

## Verification and privacy

Script460performed exact schema/manifest/membership/native coordinate validation,
checked source/mask/artifact bindings, preserved actual JSON bytes, and compared
points against the frozen native-grid predictions. Script463independently
recomputed238point outcomes,59miss-stage partitions and per-case counts; all
aggregate numbers match the import. Script464preserved all user labels and
added the separate face-outline scope diagnostic. Original sources, model
outputs, masks and parent manifests remained hash-identical. No additional
inference or fits occurred. The prior19strict-import tests remain software
evidence; no redundant new pytest/full-suite run is claimed for actual import.

Private actual export/comparison: `outputs/stellenbosch_reference_points_import_v1/`.
Actual-point boards/assessment: `outputs/stellenbosch_actual_reference_assessment_v1/review_PRIVATE.html`.
Scope diagnostic: `outputs/stellenbosch_reference_scope_v1/scope_PRIVATE.json`.
All user decisions, source images, scores/identifiers and manifests remain
ignored local evidence. Research/noncommercial use, citation and no redistribution
without author consent remain. No dataset transfer, source publication, contact,
recruitment, submitted-paper change or adviser approval occurred.
