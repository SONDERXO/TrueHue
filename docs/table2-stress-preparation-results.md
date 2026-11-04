# Table 2 clipping-stress preparation

28 October 2026. User approved the recommended separately labelled experimental
training path. The [design](table2-clipping-stress-design.md) now records that
authorization; clipping permission does not require another confirmation.

Added `src/data_preparation/table2_stress_contract.py` with a separate policy.
Clipped Table 2 rows may pass only with explicit mask and scene review,
generation-support clipping accounting, input/mask hashes, matching square256
and lookup contracts, input-derived MST and converged approximate targets.
The existing unclipped validator still rejects clipped rows. Tests check that
this exception cannot bypass failed processing, unsupported datasets, review
holds, incorrect severity provenance or invalid clipping counts. Neither
validator independently verifies external files; the calling stage must do so.

Script 153 verified prior input/evidence hashes and staged the following choices:

| Source | Experimental reference MST | Selected Table 2 severity |
| --- | ---: | --- |
| 22211 | 4 | Medium |
| 22454 | 3 | Light |
| 51739 | 4 | Medium |
| 62331 | 4 | Medium |
| 6236 | 2 | Light |
| 75027 | 6 | Medium |

Each source also has an unchanged identity control. There are 12 candidate rows,
six provisional source/duplicate-group folds, and **zero admitted training rows**
while review is pending. No dark-group coverage, official FairFace MST labels,
independently verified person-disjoint split or final model accuracy is claimed.
The weak lookup and its missing MST10 output remain limitations.

All prior decisions and artifacts remain. The new review applies to these exact
square256 masks and selected distortions, not an implicit replacement of earlier
reviews. Visible concerns include partial second person 51739, mask holes under
stronger distortion, and uncertain boundary/hair selections. Source acceptance
cannot establish MST accuracy. Rejected/uncertain sources stay held; folds must
be rebuilt on the actual approved cohort before any fitting.

[Offline review](../outputs/table2_stress_review_v1/review.html) |
[Candidate ledger and provisional folds](../outputs/table2_stress_review_v1/readiness.json) |
[Evidence verification](../outputs/table2_stress_review_v1/verification.json)

The full suite before the final scene-approval check passed 691 tests; the final
contract-focused check passed 45 tests including the added scene-review rejection.
No tree fit or runtime replacement. Android remains paused and CPM deferred.
