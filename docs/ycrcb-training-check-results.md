# Frozen YCrCb policy and separate twenty-photo training check

Review export imported: six accept, eleven reject and three blank decisions.
Five targeted clarifications are pending (three blanks plus two accepted entries
with failure notes). Preserve raw selections; no policy promotion or fitting.
[Review findings](ycrcb-training-check-review-results.md).

29 October 2026. Packaged the reviewed YCrCb-only mask as a separate version,
`face_ycrcb_complete_mouth_square256_v1`, without changing the original pipeline.
Its contract binds the exact dependencies, same square256 detection frame,
YCrCb thresholds/morphology, largest component, frame-local margin landmarks,
feature/complete-mouth exclusions and 1000-pixel minimum. Missing landmarks
produce no fallback support or features. The candidate contract differs from
the original; the historical MST lookup is explicitly inapplicable.

Before opening this check, froze all 20 IDs and the contract. Retained all 12
originally reserved training-check sources and added eight by fixed ID hashes,
excluding all 60 human development-reviewed sources and their duplicate groups.
No technical-outcome, severity, appearance or quality filtering determined the
additional selection. All sources are original-training, post-quarantine and
source-group disjoint from the 60; verified person separation is not claimed.
They already had historical pipeline processing, so this is a separate training
check, not pixel-untouched or final test evidence.

The packaged implementation first replayed **all 40 development candidate
masks exactly**, then opened the declared check-access phase. No policy was
tuned on check outcomes. The original reservation and exposure artifacts remain
preserved; a new check-phase ledger records all 20 computational accesses.

Each source supplies its original reference and a fixed global medium color
probe (R−10/B+10), with original baseline and frozen candidate masks shown for
both. This uniform global edit is a diagnostic camera-cast check, not a
source-MST-assigned training variant. It avoids needing a fabricated tone label
or reference mask when generating this check. Every frame uses its own geometry.

| Technical availability | Original baseline | Frozen YCrCb candidate |
| --- | ---: | ---: |
| Reference frames | 17/20 | 18/20 |
| Fixed global color-probe frames | 16/20 | 18/20 |

Seventeen candidate sources pass technical requirements on both frames.
Failures remain visible: 7571 has no reference landmarks; 65974 has only 782
selected probe pixels; 71358 lacks landmarks on both frames. No replacement
IDs or forced masks were introduced. None of these references is exactly
monochrome. Availability is not mask quality, acceptance or correction success.

## Review task

These are the agreed **20 mask-check photos**, after the completed 60 unique
development sources. The later 16 corrected-output reviews remain separate.
Review candidate masks in **panels 3 and 6**, together with source suitability.
Accept only if both masks and the reference are usable; otherwise reject or
choose uncertain and identify the issue. Keep foreign-object, hair, coverage,
blur and lighting concerns explicit. Export the decisions as a portable backup.
Do not skip failed cases merely because their numerical mask is absent.

After the review, assess this frozen policy without silently tuning to the
check and retaining an independence claim. A supported candidate must next
undergo matching measurement/MST calibration checks. No old lookup is applied
to new pixels. No correction-training approval, target fits, tree fits, active
mask/model replacement or final validation/test access occurred here.

Independent verification reconstructs the prospective extra-eight selection,
preserved reserved12, all40 candidate frame reports/masks and fixed color edits.
The full suite passed **765 tests in 9.40 seconds**. Mock-DOM checks verify 20
records, six-panel labels, paired review scope, saved notes/navigation and
export. A local board was visually inspected; interactive-browser visual QA
remains unavailable.

- [Review the 20 check photos](../outputs/ycrcb_training_check20_v1/review.html)
- [Frozen measurement contract](../outputs/ycrcb_training_check20_v1/candidate_measurement_contract.json)
- [Prospective source plan](../outputs/ycrcb_training_check20_v1/plan.json)
- [All check attempts](../outputs/ycrcb_training_check20_v1/attempts.jsonl)
- [Summary](../outputs/ycrcb_training_check20_v1/summary.json)
- [Verification](../outputs/ycrcb_training_check20_v1/verification.json)
- [Predeclared protocol](ycrcb-training-check-protocol.md)
