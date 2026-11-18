# Six-photo reference review ready — 6 November 2026

The user authorised a small reference-skin review instead of another sampling
or enhancement round. A local six-photo point-marking page and strict importer
are ready. **Actual user responses are pending.** No annotations, agreement
results, skin validation or admissions have been invented.

Open the private local page:
`outputs/stellenbosch_reference_points_v1/review.html`.

## Simple review instructions

1. Enter your name or reviewer code. Select a label, then click a few clear
   points on the enlarged original face: skin, hair/beard, object/other, or unsure.
   Aim for clearly visible cheek/forehead/chin skin; avoid ambiguous mixed edges.
2. Choose Points marked, or Cannot judge with a reason when the image is too
   dark/blurred. You do not need full masks, every label or50points. A single
   definite point can complete a marked photo; uncertain photos are valid outcomes.
3. Complete all six and click Export my six responses. Save
   `truehue_stellenbosch_reference_points.json` locally and tell the assistant
   where it was saved. Browser drafts alone are not an imported response file.

The magnification shows original native pixel blocks, not added detail. Clicking
an existing pixel replaces its label; Undo removes the last point. A Cannot judge
photo must have no definite points, so undo any definite marks before choosing it.
Review originals only: model predictions, score labels, enhanced images and prior
assistant grades are not displayed. Prior exposure means this is not a blinded
or independent validation study. Keep dataset images and exports private.

## Fixed evidence scope

The [protocol](stellenbosch-reference-point-review-protocol-2026-11-06.md) fixes
six exposed diagnostic examples, including glasses, facial hair, dim selections,
a broad-support control and an existing landmark failure. They represent five
publisher subject keys; two are different conditions of the same key. No new
subjects or images were processed and none was replaced based on readability.
Membership/source/crop/mask hashes were frozen before page preparation.

Marks refer to original native-crop pixel centres, not interpolated measurement
pixels. After an actual export, the importer will compare them with the frozen
native-grid final mask. The landmark-failure case has unavailable predictions,
not an all-negative mask. Sparse point inclusion on selected diagnostic examples
is not whole-mask accuracy, skin coverage, colour validity or calibration admission.
Uncertain points are excluded from definite agreement denominators, with their
counts retained. No model fitting or threshold selection is activated by marking.

## Tools and verification

- Script459prepares the prediction-hidden page and image/manifest bindings.
- `src/evaluation/reference_point_review.py` validates exact membership, schema,
  image/plan hashes, reviewer/status, native integer coordinates and duplicate/
  conflicting labels. It computes separate skin/unwanted point inclusion only
  when a frozen prediction exists.
- Script460imports an actual export without overwriting a previous import. It
  checks all bound parent artifacts, preserves actual JSON bytes and records
  sparse comparisons. It was not run with synthetic answers on the real package.
- Scripts461–462check synthetic UI interactions and the exact page/image payload.
  Six-case export, native coordinate conversion, repeated-pixel replacement,
  undo, outside clicks, navigation, local draft restoration and incomplete-export
  blocking passed. Synthetic exports stayed in memory; none is a user response.

Nineteen strict-import/comparison tests passed in0.39seconds, including unavailable
predictions, uncertain points, wrong bindings, extra/missing/duplicate cases,
invalid coordinates and fake completion. JavaScript syntax passed. Package/source
hash checks and six original-context/native-crop parities passed; UI payload has
no predictions or source scores. No actual browser-render or full-suite test is
claimed. Verification: `outputs/stellenbosch_reference_points_verification_v1/`.

For the actual response, from the project root:

```powershell
venv\Scripts\python.exe -B scripts/460_import_stellenbosch_reference_points.py "C:\path\truehue_stellenbosch_reference_points.json"
```

Do not execute against a fabricated/test export in the actual review package.
No actual import folder exists yet. Stop awaiting the user's real file before
point comparisons or any conclusion. No new inference, mask change, fit, runtime
adoption, source expansion, recruitment, author contact or dataset publication.
All copied originals, manifests, scores/IDs and actual decisions remain ignored
local evidence under research/noncommercial, citation and no-redistribution terms.
