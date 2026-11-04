# Fixed12 measurement-region QA

28October2026. Prepared original-only face crops for the12previously exposed
diagnostic frames, then froze24provisional cheek-interior points before reading
their saved mask overlap or color measurements. No new mask or lookup candidate.

The saved baseline selects204of216marked patch pixels:22patches fully selected,
one entirely missed, one partially selected. This is sparse overlap accounting,
**not segmentation accuracy**. A subsequent marked-point visual check found
both frame7points at/near glasses rims; they are explicitly uncertain. Original
coordinates and scores remain unchanged with a separate provenance caveat.
These are Codex provisional observations, not user/expert labels. Unmarked
pixels remain unknown; this reference does not separate all non-skin regions.

Local patch ITA minus full-mask ITA spans-18.379to+34.492degrees, including large
differences even where both patches are selected. That does not establish a
better estimator: local highlights, anatomical variation, spatial lighting,
native resolution, sparse sampling and possible material contamination remain
confounded. Patch statistics use18pixels for an explicitly local diagnostic;
the mapping pipeline's1000pixel requirement is unchanged. No patch ITA enters
calibration or correction features. Subject-category support is unchanged.

## Decision

Do not adopt a cheek-only estimator or regenerate training data on this evidence.
The audit demonstrates both a concrete missed cheek and a limitation of the
provisional reference: even apparently simple interior selection can touch
glasses. Replacing the current full-mask estimator therefore needs independently
checked region references, with boundaries/material uncertainty retained, before
a fixed candidate is evaluated. Keep the existing scientific result: the
square256measurement arithmetic is reproducible but current masking/reference
conditions and independent-subject support do not validate a ten-category lookup.

The next prerequisite is actual adjudication of representative measurement
regions, rather than another automatic fit or retrospective point adjustment.
The prepared original crops and review page make that concrete. This is an
offline development/reference activity, not a proposed application-user step.
Independent-subject scarcity must still be addressed separately; region cleanup
alone cannot create held-subject support for singleton categories.

[Review page](../outputs/mst_region_quality_v1/review.html) ·
[Frozen provisional observations](../outputs/mst_region_quality_v1/provisional_points.json) ·
[Reference caveat](../outputs/mst_region_quality_v1/visual_qa.json) ·
[Accounting verification](../outputs/mst_region_quality_v1/verification.json).

Scripts141/142prepare and score fixed data; existing masks/source hashes and
24patch overlap counts independently checked. Initial scoring call used a wrong
keyword and failed before producing scores; corrected to the existing API, then
completed. No production code, original labels, source reviews, thresholds,
model or lookup changed. Existing607tests remain the latest full-suite result;
no claim of new runtime testing. Android paused, CPM deferred.
