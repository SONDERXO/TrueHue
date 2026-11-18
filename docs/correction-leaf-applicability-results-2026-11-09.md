# Correction-leaf applicability audit

9 November 2026. **Do not add a blanket fitting-range veto.** It flags the one harmful edit, but also many useful corrections. No model or predictions were changed.

For all 756 saved attempts, compared available feature vectors against float32 per-feature minimum/maximum values of the fitting rows in their own routed leaf. Used strict outside comparisons, with no margin or threshold search. Facial Lab/ITA, derived MST and scene features are reported separately. The reserved-clean facial exception remains unchanged; its clean ranges are different from these leaf-fitting ranges.

## What a range warning flags among actual edits

| Warning based on | Useful core edits flagged, development / later | Useful stress edits flagged, development / later | Harmful edits flagged |
| --- | ---: | ---: | ---: |
| Raw facial Lab/ITA | 20 / 7 | 7 / 4 | 1 |
| Derived MST alone | 0 / 2 | 4 / 1 | 0 |
| Scene features | 20 / 23 | 6 / 11 | 1 |
| Any of the 12 features | 34 / 28 | 12 / 12 | 1 |

The rows overlap and must not be added. The any-feature rule flags **86 useful conditions and one harmful condition**; the raw-facial rule flags 38 useful conditions and one harmful condition. These categories agree under RGB and CIEDE2000 in this flagged subset. Conditions reuse original photos and are not independent people.

These are saved-outcome counts, not a newly evaluated veto model. Under a hypothetical identity substitution, those flagged useful edits would lose their demonstrated benefit. No outputs were rendered or altered, and no aggregate post-guard error is claimed.

All 40 usable clean evaluation photos already remain unchanged. Four development and two later clean photos fall outside at least one fitting-leaf feature range despite being preserved. This further shows that range coverage is not a cleanliness or safety classifier. The other 14 clean measurement failures have no available feature vector and are not treated as in-range.

Across all conditions, 451 feature vectors are available; unavailable attempts retain their failure handling. Of the latest candidate's 259 edited conditions, 87 have any-feature warnings. The other edited conditions include unscored outputs; an available measurement does not guarantee a reference scoring region. No missing reference is counted as a benefit or successful exclusion.

## Decision

Reject the blanket range-veto idea before fitting or rendering it. It cannot recover any of the identity misses, would discard useful recovery, and uses an exposed harmful case as its motivating example. Do not tune a margin or choose a feature subset from this table to make that case disappear.

The next substantive correction design needs evidence distinguishing **exposure distortion from colour distortion**, while preserving clean photos. The harmful colour-only case enters an underexposure-dominated branch; a simple feature-range check does not resolve that confusion. Before proposing a fit, examine the existing saved fitting features for exposure-versus-colour overlap with all source variants kept together. This is a bounded descriptive audit, not permission for another classifier, feature or capacity sweep.

In parallel, decoder/code permission clarification remains awaited. No DINO execution is required for this audit. The latest correction candidate remains unadopted and the final 24-photo holdout remains byte-unread.

## Verification

Scripts 654â€“655. Independent scalar float32 bounds, routes and summary reconciliation passed on all available vectors; all source hashes checked. Private records: `outputs/correction_leaf_applicability_v1`. Zero fits, new predictions, inference, renders or source-image reads. No runtime changes or new accuracy claim.
