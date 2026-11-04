# Reduced-burden FaceOcc review: full comparison saved, four judgments pending

1November2026. User explicitly authorised replacing the excessive23-image
manual polygon task with assistant inspection of the full set and four simple
human judgments. See faceocc-light-review-amendment-2026-11-01.md, frozen before
new predictions. Old polygon files and browser storage keys remain unchanged;
no completed polygon export was present in its review directory. Browser-only
work is not assumed absent and is not cleared or imported as fabricated labels.

## Fixed scope and result

All24original selections retained. The four human-review IDs were fixed from
the declared challenge lane BEFORE new predictions:39083(facial hair),77101
(outer forehead/hairline),29321(mouth/shadow),74882(glasses). No substitutions
based on success or appearance. All four produced paired outputs.

Scripts375/376 ran the current preferred nostril baseline and unchanged FaceOcc
checkpoint/MPbridge/normalisation/logit>0/removal-only mapping. No rejected face-
outline clipping, threshold search, model swap or fitting. Script376 reuses the
previous one-pass inference source with only workspace output/plan paths changed;
verification confirms the underlying369source matches its original frozen hash.

| Fixed lane | Attempts | Paired outputs | Failures retained |
|---|---:|---:|---:|
| Additional FairFace train | 12 | 8 | 4 |
| Additional photographs of same four exposed MST-E subjects | 8 | 6 | 2 |
| Known challenge cases | 4 | 4 | 0 |
| Total | 24 | 18 | 6 |

Failures: three required-landmark failures, one near-zero meanb*/undefinedITA,
one face-detection cardinality failure, plus originalMP4still-image decode
failure. No retry/replacement. All18FaceOccoutputs succeeded and all18combined
masks retained1000pixels; no new candidate technical failure. Median parent-
selection retention96.14%, not actual-skin recall or a model-quality score.

## Assistant observations, separate from user evidence

All18paired boards inspected across five contact sheets. Every24attempt has a
saved entry in assistant_observations.json. These are assistant diagnostics,
not human ratings or dense ground truth. Findings include:

- Case5/7316: a new excluded mouth/cheek patch appears to remove useful skin;
  potential harm must accompany any claimed benefit.
- Cases4/34842 and21/39083: facial-hair/stubble vicinity is largely unchanged;
  no beard-exclusion claim.
- Cases12/52981 and24/74882: glasses/frame/bridge boundaries remain ambiguous;
  no blanket claim of glasses clearance.
- Case22/77101: prior outer-forehead coverage issue is not repaired by a
  removal-only veto; it cannot add missing skin.
- Case23/29321: mouth/shadow protrusion is reduced, with possible adjacent skin
  loss. Several other cases show small edge trims and similar facial support.
- Case16 profile/neck boundary shows a larger change; useful skin versus outside
  face loss cannot be quantified from inspection alone.

Mixed qualitative findings do not establish a general superiority decision.
Exposure, unverified person independence in FairFace, same-person MST images,
known-challenge selection, appearance/lighting and missing verified ten-tone
coverage remain limitations. No full-mask precision/recall/IoU or independent
validation can be reported after abandoning polygon scoring. No inaccurate
claim that the planned manual annotations were completed.

## Four-case user task

outputs/faceocc_four_review_v1/review.html shows original, previous measurement,
FaceOcc-assisted measurement for the fixed four cases. No drawing. Answer:

1. Does the previous method include unwanted pixels?
2. Does the FaceOcc-assisted method include unwanted pixels?
3. Does FaceOcc remove useful skin compared with the previous method?
4. Which measurement mask is better overall, or similar/uncertain?

Uncertainty is explicitly allowed. Notes optional. Download
truehue_faceocc_four_decisions.json into this review folder. Script379 verifies
exact four IDs, manifest and board hashes, required fields and allowed values;
it preserves the original export and does not adopt any model. Human judgments
remain pending; none have been inferred from assistant observations.

## Verification and next decision

Script378 replayed all18saved combined masks/features, original baseline
statistics and forbidden-class/anatomical/nasal-guard exclusions;0added pixels.
All source/preprocessing/model and saved correction hashes unchanged. All24
memberships/failures retained. No additional prediction pass for verification.
Two importer tests passed in0.06s; review JavaScript syntax passed. Exact four
board hashes/local links checked. No full-suite rerun for report/review tooling;
last broader result905passed/13.40s excluded desktopGUI(Tcl/Tk unavailable).

Evidence: outputs/faceocc_light_comparison_v1/plan.json,inference_plan.json,
baseline.json,inference.json,rawlogits/,per-case masks and boards,summary.json,
verification.json,assistant_observations.json and all_results.html. Actual logits
are in logits/; no duplicate scientific inference was performed. The four-case
manifest is separate and records selection-before-predictions.

After actual human export, combine the four judgments with full assistant
findings and known failures for ONE qualitative conclusion, then stop this
cycle. No automatic calibration, treefit, runtime adoption, Android claim or
participant collection. Correction masks/rendering unchanged. Panel register
updated with reduced manual workload and corresponding evidence limitations.
