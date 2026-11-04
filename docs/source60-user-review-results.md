# Imported user review: fixed60-source variants

24 October 2026. Imported `C:/Users/NYTHAN/OneDrive/Documents/truehue_source60_variant_review.json`, exported24 October2026 at16:22:44 Manila time. The file matches all48 expected pending pairs, without duplicate/missing IDs or altered provenance.

| User decision | Pairs |
|---|---:|
| Accept |35|
| Reject |11|
| Uncertain |2|
| Pending |0|

All decisions and notes are preserved exactly. The source file is unchanged and an exact byte copy is retained in the project. The previous27 exclusions (7clipped,5coverage and15visual-contamination cases) remain excluded; they were not part of this user review. All75 attempts remain in the reconciled record, and none is admitted to training yet.

The35 accepted pairs span10 sources and all five original development folds. Pair counts by fold1-5 are6,15,8,3,3. Only42532 and83205 have all five variants accepted. Counts by variant: dark8, bright6, color3, unchanged9, mild9. User-rejected controls from60162 remain rejected even though two other variants were accepted. The cohort remains small and uneven; allfolds nonempty is not sufficient evidence of final evaluation quality.

Uncertain cases stay held:31154 dark and47217 color shift. Your rejection of67454 concerns another person's neck skin; that is distinct from the requested correction of the selected person's own visible neck.

## Accepted notes needing technical follow-up

Seven accepted pairs retain explicit concerns:

- 31154 bright/unchanged/mild: hair included near the neck. Distinguish hair from valid neck skin.
- 60162 dark/color: incomplete background exclusion; both controls were rejected. Review residual non-skin selection without reinstating those controls.
- 63870 unchanged/mild: baseline measurement includes hijab while correction support excludes it. A cleaner correction mask does not remove bias from baseline features or generation masks.

These flags do not change your acceptance decisions. They separate human review from technical readiness; the other28 accepted pairs are also pending provenance/staging checks, not automatically approved final training data. No masks or features have been repaired yet.

Next recommended work is a focused inspection of those seven accepted cases using their saved input/estimation/generation/correction masks. Document whether contamination affects measurement, synthetic generation or correction, and keep the frozen estimator/feature policy intact during diagnosis. Do not silently replace baseline measurements with the alternative YCrCb mask, lower thresholds or retrain around known failures. Resolve these notes before final staging/fitting, and preserve your original decisions separately from any technical holds.

Verified all48 user decisions/notes against the exact export,27immutable exclusions,75unique records, unchanged original/master/model/schema/ledger hashes and no training admissions. The runtime model, master source labels, source allocations and original exposure ledger are unchanged. Operational MST, face-and-neck support, final data eligibility and thesis evaluation remain pending.

[Reconciled75 records](../data/manifests/source60_user_review_v1/reconciled_pairs.json) | [Original export copy](../data/manifests/source60_user_review_v1/original_user_export.json) | [Summary](../outputs/source60_user_review_v1/summary.json) | [Verification](../outputs/source60_user_review_v1/verification.json)

Follow-up: [completed seven-case layer inspection](source60-note-inspection.md). User acceptance preserved; technical holds leave an empty planned fold.
