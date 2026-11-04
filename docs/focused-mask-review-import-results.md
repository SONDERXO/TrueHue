# Completed 24-photo reference/mask review

29 October 2026. Found `truehue_batch_focused24_reviews.json` in the focused
review folder and validated the schema, exact 24 IDs, manifest identity,
reference-only scope and unchanged displayed-board hashes. Preserved the
original export byte for byte and reconciled annotations separately.

**Five accepted, nineteen rejected, no uncertain or missing decisions.** Four
accepted cases have explicit concerns; they must not be reported as clean masks.
The diagnostic selection oversamples risks and failures, so 5/24 is not an
estimated acceptance rate for the full dataset.

| Accepted ID | Exact review note |
| --- | --- |
| 43909 | Acceptable with minor background coverage in mask |
| 72595 | Jagged edges in face mask, acceptable but needs improvement |
| 14418 | Not enough facial coverage |
| 60229 | Acceptable, but included a bit of background |
| 66413 | No note supplied |

43909 remains technically excluded because required landmarks were unavailable.
Visual acceptance does not override that failure. The other accepted references
are not approvals of their distorted masks, correction targets or model outputs.
No new source was admitted for fitting.

Rejected cases explicitly identify background/clothing inclusion (72663,
75050, 52056, 32903), holes plus background (14120), missing or inadequate
coverage (77889, 77580, 12559, 59484, 30236, 55166, 31367, 20653, 25129) and
glasses inclusion (34898, 9149). Rejections 13718, 14385 and 18034 have no note;
no reason is inferred for them. All exact original wording is preserved in the
reconciled JSON, including qualified acceptances and spelling.

The next useful work is an isolated mask comparison on these reviewed sources:
test anatomical containment against background/clothing spill, investigate
coverage loss and landmark failures, and inspect glasses/feature exclusions.
Do not assume hole filling or larger masks are automatically improvements:
they may include excluded anatomy or foreign objects. Preserve the existing
baseline and record every candidate failure and support change.

Any changed measurement mask needs its own version and measurement contract;
the existing MST lookup cannot silently be treated as calibrated for new mask
pixels. No new threshold, mask change, calibration or correction-tree fit was
performed during this import. Keep the 12 reserved training sources out of
mask design and use them only after a candidate is frozen. The agreed overall
96-photo review budget remains staged; this completed review counts as its
first 24, with no immediate request to review the old seven batches.

- [Preserved original export](../outputs/focused_mask_review24_import_v1/original_user_export.json)
- [Reconciled decisions and exact notes](../outputs/focused_mask_review24_import_v1/reconciled_reviews.json)
- [Import summary](../outputs/focused_mask_review24_import_v1/summary.json)
- [Verification](../outputs/focused_mask_review24_import_v1/verification.json)
