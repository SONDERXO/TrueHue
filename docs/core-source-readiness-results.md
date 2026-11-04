# Existing source pool: readiness and implementation consequences

28 October 2026. Reconciled existing records rather than screening another
batch. [Source table](../outputs/core_source_readiness_v1/sources.csv),
[full evidence](../outputs/core_source_readiness_v1/summary.json),
[independent verification](../outputs/core_source_readiness_v1/verification.json).
Scripts125/126 reproduce the audit and verification; the audit refuses overwrites.

## What is available

All114 inventoried sources are previously exposed TRAIN sources. Among the
75 recorded variant attempts from the fixed60-source follow-up, original user
decisions are35accept,11reject,2uncertain and27pending. Those35acceptances span
10sources. Only42532 and83205 have original acceptances for all five variants.
This does not make them calibrated or independent final references.

The proposed regenerated cohort contains32candidate pairs across nine sources:

| Source | Dark | Bright/warm | Color shift | Unchanged | Mild |
| --- | --- | --- | --- | --- | --- |
| 40048 | yes | — | — | yes | yes |
| 42532 | yes | yes | yes | yes | yes |
| 60162 | yes | — | yes | — | — |
| 63870 | — | — | — | yes | yes |
| 67583 | yes | — | — | yes | yes |
| 69531 | yes | yes | — | yes | yes |
| 7994 | yes | yes | — | yes | yes |
| 83205 | yes | yes | yes | yes | yes |
| 84364 | yes | yes | — | yes | yes |

These are candidate IDs, not newly approved pairs. The counts are8dark,
5bright/warm,3color,8unchanged and8mild. Nine saved source-held folds have exact
ID accounting, disjoint fitting/held sources and no recorded duplicate-group
crossing. Subject identities remain unverified. The older five-fold plan is
not silently replaced or called a final evaluation split.

## Why this is not a ready core training expansion

The candidate recipe resizes to256, uses hair/material-veto generation and
measurement, expanded correction support and ten features. The current core
comparison uses native224 inputs, four Lab/ITA features and legacy facial
correction support. Their saved features and acceptance histories cannot be
merged as though processing were identical. Operational neck coverage is also
not implemented by the core runner.

The user's coverage response says the regenerated masks are generally suitable
but retain missing facial areas. That response is preserved alongside the
earlier per-pair decisions; it does not resolve the reported defect. The two
other regenerated sources preserve rejected controls and technical concerns.
Later contour/parser work did not establish an adopted replacement policy.
Therefore this audit establishes **zero newly ready core training pairs**;
it does not revoke the historical acceptances or invalidate the original
prototype's already recorded fitting set.

The source-screen reference statuses are photographic reconstruction judgments,
not verified neutral illumination or skin-color truth. No recorded pool supplies
the missing calibrated reference evidence or an independent operational MST
mapping. Availability of extra images alone does not resolve the conflicting
synthetic targets observed in the preceding diagnostic.

## Implementation decision under the deadline

Stop serial small-cohort correction experiments for now. Preserve the working
Python pipeline, portable tree and negative control results as the reproducible
development baseline. Do not spend the next work block on a deeper tree,
material model or another broad source search.

The next bounded implementation task is a reproducible core demo/evaluation
entry point with one report of software success, correction quality, failures
and unfinished thesis stages. It should run the existing fixed cases and
produce shareable results without altering their eligibility. The existing
runner/check scripts already provide the calculation; package their outputs
and instructions into a clearly labeled development demonstration.

In parallel with scheduling, resolve the thesis method decision for MST: the
implemented continuous-feature tree differs from the proposed MST-conditioned
pipeline, and the attempted mapping is unvalidated. Do not invent a mapping
or train on evaluation-only MST-E. Final FairFace/SCIN roles, subject/split
claims, expert MOS and Android remain explicit deliverables. Android creation
still requires an explicit user request under AGENTS.md. The user's visible-neck
request remains pending. Record a scope amendment only if actually agreed.

A future data stage must declare one processing recipe before regenerating
anything, retain all failed/rejected attempts and source groups, and resolve
the relevant measurement/reference and changed-mask concerns. No new stage is
executed or admitted by this report. Paint/makeup remains a documented
limitation and CPM remains deferred.

## Verification

Independent replay checks all75original decisions/notes/statuses,114source rows,
32candidate IDs and nine folds, with all input hashes unchanged. The audit
process opens no raw images and performs no model inference or fit. No original
label, review, mask, training manifest, exposure ledger or runtime model changed.
