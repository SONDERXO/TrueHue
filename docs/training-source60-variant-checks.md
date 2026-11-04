# Fixed75 variant checks and user review

24 October 2026. All15 follow-up sources received five fixed variations. All75 had available geometry, experimental correction support and ten measurements. No model was fitted.

| Disposition | Pairs |
|---|---:|
| Pending user visual review |48|
| Held for mask coverage loss |5|
| Clipped, stress only |7|
| Held for visible contamination |15|

Codex inspected all75 previews. The63 unclipped numerical screen passes were reduced by15 source-wide visual holds:51446 has scarf/clothing selection,55007 has hair selection along the left edge, and56444 includes background foliage. This supplies new evidence beyond the original source screen; historical observations and pending human labels are preserved.

Coverage holds:31154 color;63870 dark/color;67583 color;84364 color. Clipped stress:40048 bright/color,47217 bright,60162 bright,63870 bright,67454 bright,67583 bright. Even one clipped pixel follows the same stress-only rule. No thresholds were relaxed or alternative features substituted.

## Review instructions

Open [the local review page](../outputs/training_source60_variants_v1/review.html) in a browser. It groups48 proposed pairs into12 source boards. Choose Accept, Reject or Uncertain for each eligible variation; add notes for concerns. Excluded variations remain visible but cannot be accepted there.

Board columns: input, baseline measurement mask, alternative YCrCb mask, correction mask. Check the baseline and correction masks for missing cheeks/forehead or inclusion of hair, paint, clothing and background. Green means selection, not correctness. Eye/mouth exclusions are expected. Actual neck skin is not automatically unwanted, but neck-specific support remains unfinished. These are mask previews, not corrected outputs.

Click **Download review results** before closing, then return the saved `truehue_source60_variant_review.json` file path. Browser storage may retain progress locally; the downloaded file is the review record. All48 decisions start pending, and downloading does not update the training set automatically. Image references and JavaScript syntax were checked; browser interactions were not exercised in this run.

## Verification and next step

Independently regenerated75 inputs, inverse targets and clipping counts; recomputed150 estimator statistics/retention checks and75 brightness sets; verified original hashes. Exact decoded-image/dHash<=4 checks across15 new plus10 existing sources found no duplicate candidates; subject independence remains unverified. **464 tests passed**.

Original fold assignments are preserved: pending pair counts9,15,9,12,3 for folds1 through5. User decisions may reduce these further. Reconcile decisions against immutable numerical/clipping exclusions and check source/fold coverage before staging. Keep all75 cases and previous45 source holds, and do not silently replace failures or reassign folds.

No runtime model, frozen schema, master eligibility, original human label or114-row exposure ledger changed. Operational MST, face-and-neck correction, final data eligibility and expert/thesis evaluation remain pending. This is a documented development extension, not a proposal amendment.

[All15 boards](../outputs/training_source60_variants_v1/review-index.md) | [All75 dispositions](../data/manifests/training_source60_variants_v1/pair_dispositions.json) | [Verification](../outputs/training_source60_variants_v1/verification.json)

Completed user review: [35 accepted,11 rejected,2 uncertain](source60-user-review-results.md). Original decisions and notes preserved; no fitting yet.
