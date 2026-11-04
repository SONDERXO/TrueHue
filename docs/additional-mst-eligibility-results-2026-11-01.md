# Additional MST-E eligibility screen: stop without fitting

1 November 2026. User authorised the next bounded eligibility check. The frozen
protocol selected25 photographs from the337 unique keys of subject_1/9/11/10,
before reading pixels. Two per occupied subject/lighting/mask-status stratum,
ranked by fixed hash; no replacements.312 photographs remain unassessed.

Pre-pixel duplicate reconciliation found a mask-status conflict. Its original
rows were preserved and the combined0|1 status formed its own stratum, rather
than choosing an annotation. Labels/lighting were consistent. A first metadata
assertion stopped before output or pixel reads; the documented conflict policy
was added before freezing the actual plan. No outcome-driven selection change.

| Subject / official MST | Attempts | Technical success | Failure | Not assessed |
|---|---:|---:|---:|---:|
| subject_1 /2 | 8 | 6 | 2 | 65 |
| subject_10 /9 | 6 | 3 | 3 | 60 |
| subject_11 /5 | 7 | 5 | 2 | 100 |
| subject_9 /4 | 4 | 3 | 1 | 87 |
| Total | 25 | 17 | 8 | 312 |

Failures: six face-detection cardinality failures, one unavailable-landmark
failure and one degenerate semantic geometry failure. No stale-feature fallback,
retry, deletion or replacement. Saved source IDs/hashes, exact plan, attempts and
access ledger are in outputs/additional_mst_eligibility_v1/.

## Visual findings

All17 successful measurement boards were inspected across five contact sheets.
Three clear contamination examples appear despite successful programmed checks:

- Case4, subject_1: selected neck and garment pixels below the face.
- Case10, subject_10: selected beard/chin hair under dark illumination.
- Case14, subject_10: selected pixels from a worn face covering.

Other cases have hairline/brow/ear ambiguity or limited support. Warm indoor
casts and dark illumination are not independently qualified colour references.
The remaining14 successful cases are not declared clean or approved by absence
of a clear finding at diagnostic scale. visual_diagnostics.json records every
successful case separately as assistant diagnostics, not user judgments.

## Verification and decision

Script361 reconstructed all17 saved masks from categories and landmarks with the
unchanged nasal guard, reproduced Lab/ITA and endpoint feature vectors, and
verified source/artifact/input hashes and exact attempt memberships. All pass.
Measurement contract remains1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7.
Reproducibility does not prove actual-skin selection. Correction support was
not modified or evaluated here. No calibration, tree fit or lookup export.

**Stop: additional subject eligibility is not established.** Zero rows admitted.
Do not drop the three contaminated cases and fit the rest. Do not expand to
the312 unsampled files, replace failures or tune masks on this sample. Existing
training readiness remains unmet; categories7/10 still lack independent support.
These four subjects are historically exposed and cannot become an untouched test.

The concrete measurement issue is broader than nostrils: actual non-skin pixels
can be assigned to the skin class and associated with the face. Another small
radius or calibration tweak is not a justified response. Any next measurement
change needs a separate error-based proposal and independent evaluation scope,
with beard-specific model work still held. Improved correction rendering does
not resolve this issue. Recruitment is not being imposed as the only option.

Gallery: outputs/additional_mst_eligibility_v1/review.html. No new review export
or large user review batch is requested. Scripts360/361 compile; saved-evidence
replays pass. Existing nostril/semantic unit tests were run separately; no new
full-suite result is claimed. Reserved correction pixels and SCIN images were
not accessed; demos and source/label/review records remain unchanged.
