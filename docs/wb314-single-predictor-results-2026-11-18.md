# One frozen WB314 predictor: fit complete, changed-output review pending

**Later18November update:** all22changed corrections were genuinely preferred and appearance-acceptable. Input-to-output implementation parity also passed. The current state is in [final review and inference results](wb314-final-review-and-inference-results-2026-11-18.md). The pending-review descriptions below record the earlier stopping point and are superseded.

The user authorized the preceding single-predictor proposal with: "Okay lets do that. Keep working until you nneed my input". This explicitly supersedes the earlier no-automatic-final-fit boundary for this one fit. The [prospective specification](wb314-single-predictor-protocol-2026-11-18.md) froze the existing WB314 method rather than opening another experiment.

## Delivered predictor

Exactly one real ordinary CART was fitted to all66 exposed development rows from11 sources. Features remain the same314float32 values; analytic targets, depth4, seed42, all remaining saved settings and the luminance/chroma renderer are unchanged. No feature extraction, external neural inference, target optimization, dataset acquisition, parameter search or failed-study rerun occurred. One separate generated adaptation fit passed before the real fit.

`outputs/wb314_final_training_v1/model.json` is the portable research predictor. Its SHA256 is `7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f`. Native predictions and leaf assignments matched independent scalar traversal on all66 fitting rows;50 scalar leaf-mean checks passed across10 leaves. Model sealing preceded all portrait pixel reads in this execution.

All66 outputs were then produced from the existing verified WB evaluation packs. Independent scalar rendering matched every RGB8 output exactly. Protected pixels and pixels outside application support remain exactly input. The subsequent audit independently checked66 routes,50 leaf means,75 artifact hashes,66 old/new pixel comparisons and all66 protection/outside comparisons, with zero fits. Receipts are `training_verification.json`, `verification.json` and `independent_audit.json` in the same local output directory.

## What changed from the reviewed source-held outputs

| Outcome | Cases |
| --- | ---: |
| Exactly identical to previously reviewed output | 42 |
| Changed identity output, now exactly unmodified input | 2 |
| Changed colour-only correction | 1 |
| Changed pure-underexposure correction | 11 |
| Changed combined-underexposure correction | 10 |
| Total | 66 |

All11 identity outputs now equal their unmodified inputs exactly. The two changed identities are39568and59807. This is a fitting/development preservation result, not evidence of preservation on new photographs. Pure-overexposure and combined-overexposure outputs are unchanged; their earlier brightness preferences and counts remain intact. The earlier neutral underexposure predictions for16061and48879, and combined-underexposure prediction for48879, now receive nonneutral controls. That is an observed change, not yet a new human usefulness judgment or independent generalization result.

Earlier ratings remain attached to their actual source-held outputs. They are not assigned to the22 changed corrections. The two identities restored exactly to input do not introduce a new corrected appearance; they are excluded from the new correction review. No arbitrary pixel-change threshold or favorable-case selection was used.

## Necessary user input

`outputs/wb314_final_changed_review_v1/standalone.html` displays all22 changed nonidentity corrections, alongside the distorted input and original photographic reference. It excludes all42 identical outputs and both unchanged-original restorations. The existing review interface, acceptable/unwanted/uncertain stop rule, separate usefulness and appearance questions, notes and event trail are retained. The new manifest, browser storage key, review IDs, round marker and download filename are separate. No answers are prefilled or generated.

All66 displayed PNGs round-trip to their exact cached pixel arrays; all66 embedded PNG hashes match. Preparation verification passes. The reused interface was not newly exercised in an interactive browser during this preparation; no such claim is made. Save filename: `truehue-wb314-final-changed-review-2026-11-18.json`; round: `wb314_final_changed_2026_11_18`. Wait for genuine answers before deciding whether this predictor's changed appearances are acceptable. Preserve the29617 face/background concern and all prior raw review bytes and notes.

## Interpretation and stopping point

The single final research predictor now exists. These are resubstitution and implementation checks on already exposed development sources, not a new held-out evaluation. Historical source-held numerical results still describe the earlier recipe comparison; they must not be relabeled as independent performance of this all-data tree. No new reference-error means or expert MOS were calculated.

Qualification is incomplete: changed-output appearance feedback is pending, input-to314 deployment compatibility is not established by exporting the tree alone, and tone/MST, genuine expert and current-model device qualification remain. No locked contents or manifests, raw project originals, runtime/Android defaults or expert contacts were accessed or changed. All failed studies remain closed. No model-strength adjustment, new fit, new source or tuning queue is selected. No jobs are running. This work is local after published commitf6f0e8a; no new push occurred in this continuation.
