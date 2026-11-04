# Completed original-mask development review

29 October 2026. Validated the exported training36 JSON against its schema,
scope, frozen 36 IDs, source evidence and unchanged displayed-board hashes.
Preserved the original export byte for byte. **16 accepted, 20 rejected; all36
decisions complete.** Eleven accepted entries have no note; five have notes.

| New accepted source | Exact concern, if supplied |
| --- | --- |
| 85815 | No note |
| 11521 | Good coverage and exlclusion, but mask has holes |
| 55060 | Mask has holes |
| 30546 | Usable face mask but holes are present in mask |
| 56839 | No note |
| 71379 | Holes in mask |
| 75166 | No note |
| 68073 | No note |
| 75898 | No note |
| 62105 | No note |
| 20648 | No note |
| 72400 | No note |
| 34227 | No note |
| 16033 | Too much hair coverage |
| 34458 | No note |
| 29880 | No note |

16033 remains human-accepted with its exact concern. Its hair inclusion needs
assessment before fitting; acceptance must not be rewritten as rejection or
described as a clean mask. The four accepted hole-related concerns are also
preserved. A note-free acceptance is not proof of pixel accuracy.

Rejections identify significant holes or missing face/chin/jaw coverage,
background/clothing/hair inclusion and generally messy masks. 5362 has no
rejection note; no reason was invented. Exact notes, including spelling and
whitespace, are retained in the reconciled artifact.

Combined with the previous24, the original rule-based development review now
covers **60 unique sources: 21 accepted and 39 rejected**. Semantic-parser
candidate decisions remain separate and are not used to overwrite original
mask judgments. The combined60 is a deliberately selected development cohort,
not representative final accuracy, a verified person-separated dataset or
new test evidence. The 20-photo mask check and 16 later output reviews have
not yet been completed; the existing12 reserved sources remain closed.

All36 associated synthetic distortions are clipped. These reference/mask
approvals do not approve distorted masks, make fitted recovery targets exact,
or silently admit clipping into an unclipped primary experiment. Preserve
the existing MST method, input-only features, source groups and identity
controls. No new training admissions, tree fits, mask/calibration changes or
validation/test exposure occurred during import.

Next, reconcile technically usable accepted references with source concerns,
then verify input-mask/target/clipping dispositions separately before a new
correction-model experiment. Do not request another whole batch merely to
repeat the completed source reviews, or transfer semantic-mask approvals
onto different pixels. No additional review is requested at this import step.

- [Exact new reviews](../outputs/training_review36_import_v1/reconciled_reviews.json)
- [Combined60 original-mask reviews](../outputs/training_review36_import_v1/combined_original_mask_reviews60.json)
- [Preserved export](../outputs/training_review36_import_v1/original_user_export.json)
- [Summary](../outputs/training_review36_import_v1/summary.json)
