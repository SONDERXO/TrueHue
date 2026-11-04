# The supplied a.json export is partial

30 October 2026. The user supplied
`outputs/additional_six_source_mask_review_v1/a.json`. Its schema, scope,
fifteen mask IDs and original manifest hash are valid. Its recorded decisions are:

- 2434 gamma-lighten: reject, “Good face coverage, but holes in the face mask”.
- 2434 gamma-darken: reject, with the same exact note.
- The other thirteen entries: blank decisions and blank notes.

Imported that actual snapshot into
`outputs/additional_six_source_mask_import_v1/`, preserving the original bytes
and exact notes. The user said the review was finished, but the file contains
no accept decisions. Blank entries cannot be treated as acceptance. This is
incomplete annotation evidence, not a model-comparison result or rejection of
all fifteen masks. No source-level original approval was revoked by the two
variant-specific rejections.

## Continue without repeating completed judgments

[Continuation page: thirteen unresolved masks on five photos](../outputs/additional_six_source_mask_review_continuation_v1/review.html).

The two completed 2434 rejections are carried forward in the export and are not
displayed for review again. The page starts at 25517 and shows only 25517,
39083, 63509, 42965 and 77101. The counter includes the two saved decisions
(2/15 initially). Existing original-reference judgments remain separate.
The browser may recover other saved choices under the same original manifest
key; only an actual subsequent export establishes those judgments here.

The downloaded filename is `truehue_additional_six_source_mask_decisions.json`.
Its schema and original manifest hash remain unchanged, and it always exports
all fifteen IDs, including the two preserved rejections. Do not overwrite the
archived partial import; use a versioned successor import for the next file.
Do not rerun script301 against its existing output directory unchanged.

## Verification and next boundary

Verified exact preparation evidence, source roles, image/mask hashes and notes
during import. The continuation script passes syntax checking. An in-memory
interaction/export check verifies five displayed groups, thirteen blank defaults,
two exact inherited rejections, the original manifest hash, fifteen exported
IDs and source-local actions. No synthetic choice was written to the real review.
Live browser QA was not performed.

The117-case/32-source reviewed registry and conditional comparison design remain
unchanged. No accepted new primary row, fitting membership or model outcome is
inferred from this partial file. Training awaits actual completed mask judgments
and frozen accepted membership. Do not run the candidate with zero accepted
new-primary cases or repeat data generation/source screening while waiting.

- [Actual imported decisions](../outputs/additional_six_source_mask_import_v1/reconciled_reviews.json)
- [Import summary](../outputs/additional_six_source_mask_import_v1/summary.json)
- [Continuation snapshot](../outputs/additional_six_source_mask_review_continuation_v1/continuation.json)
- [Continuation verification](../outputs/additional_six_source_mask_review_continuation_v1/verification.json)
