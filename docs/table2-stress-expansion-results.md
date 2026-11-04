# Fixed six-source Table 2 expansion

28 October 2026. Executed the user-authorized expansion and its next verification
step under the [frozen protocol](table2-stress-expansion-protocol.md). No new
source search or evaluation-set exposure. Selected six historically reviewed
FairFace TRAIN sources with accepted identity controls and no rejected or
uncertain original variant decisions. Pending variants and previous changed-mask
holds remain unchanged. Rejected51739 remains excluded.

All six reference and six distorted-input measurements succeeded. All six target
fits were available. The same square256 contract and frozen weak experimental
lookup were retained; reference estimates select one severity and actual
distorted-input measurements supply model features. No official source MST or
calibrated reference truth is asserted. Five selected severities are medium,
one light; there is still no dark-group coverage.

| Source | Estimated reference MST | Severity | Original mask retained | Generation pixels with any clipped channel |
| --- | ---: | --- | ---: | ---: |
| 40048 | 4 | Medium | 74.1% | 15.7% |
| 42532 | 5 | Medium | 58.8% | 97.4% |
| 63870 | 2 | Light | 96.7% | 3.3% |
| 67583 | 4 | Medium | 88.8% | 21.7% |
| 83205 | 4 | Medium | 72.5% | 81.7% |
| 84364 | 4 | Medium | 83.3% | 20.5% |

Retention is reference-mask/input-mask intersection divided by reference-mask
pixels. These are pipeline estimates, not expert skin truth. Clipped pixel
fractions count any out-of-range channel before final encoding; they do not
mean that all channels in those pixels were destroyed. Severe clipping and
nonzero target residuals are preserved rather than tuned away.

All six boards were inspected. Reference selections can include boundary/hair
regions; distorted masks have visible holes, especially40048/42532/83205/84364.
42532 includes a hard face-crop boundary; 67583 has tight facial feature
exclusions. 84364 includes another partial person near the right edge, so scene
validity and whether the mask selects that person's material need review.
These observations are provisional Codex concerns, not user decisions.

The historical master exposure boolean predates the fixed60 review. An initial
pre-processing assertion rejected that stale boolean before output creation;
the implementation now checks actual recorded later review decisions instead.
Original metadata remains unmodified. This change does not expose new sources.

Scripts157/158 verify original source/review/artifact hashes, exact PNG roundtrips,
all twelve saved-mask Lab/ITA measurements, all input MST indices, all six
generated input images and clipping counts, and all six target support/residual
records. No algorithm modules changed; the latest full suite remains692passed
from the preceding model stage. This stage's independent evidence replay passes.

The next step is prepared: a provisional combined source-group plan contains
the prior ten accepted pairs plus twelve pending pairs, for up to22pairs and
11held-source/known-duplicate-group folds. This is conditional planning, not
new admission; all new masks/scenes need actual review and rejected/uncertain
sources must be removed before rebuilding the final fitting plan. Source groups
do not establish cross-source person identity. No new trees were fitted.

[Review these exact masks](../outputs/table2_stress_expansion_v1/review.html) |
[Attempt ledger](../outputs/table2_stress_expansion_v1/summary.json) |
[Independent verification](../outputs/table2_stress_expansion_v1/independent_verification.json) |
[Provisional combined plan](../outputs/table2_stress_expansion_v1/provisional_combined_plan.json)

After review, keep the fixed five-feature depth3/seed42/leaf1 recipe, both variants
of each source together, full-reference-mask metrics, oracle capacity separate,
and the zero-identity-harm gate. Preserve the earlier failed candidate. Any
improvement remains exposed-data development evidence. Runtime unchanged;
Android paused, CPM deferred.
