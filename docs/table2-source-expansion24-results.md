# Fixed 24-source training expansion: suitability checkpoint

28 October 2026. Executed the user-authorized screened source expansion under
the [frozen protocol](table2-source-expansion24-protocol.md). Source selection
used no correction predictions and no replacements. No tree was fitted.

The actual metadata pool contains 170 remaining unreviewed TRAIN candidates.
Selected exactly four from each of six historical L*/b* rank cells using the
fixed hash rule, before raw-image inspection. Photo-appearance ranks are not
MST labels or intrinsic complexion. Known duplicate groups and non-TRAIN
allocations were excluded. All 24 sources now have recorded development-review
exposure; this is not a new final holdout. The prior exposure ledger's complete
byte prefix is preserved, with exactly 24 new records appended before processing.

## Processing and suitability results

All 24 reference measurements succeed using the established square256 contract.
Each reference provides an identity/control candidate and a Table2 input at its
experimental reference-MST-conditioned severity. Actual distorted-input ITA
supplies its own MST feature; no reference feature fallback occurs.

| Outcome | Sources |
| --- | ---: |
| Reference measurements available | 24 |
| Distorted measurements available | 20 |
| Approximate recovery targets available | 19 |
| Codex provisional candidates for user review | 3 |
| Held after numerical or qualitative suitability screen | 21 |
| New training admissions / fitted models | 0 / 0 |

Assigned severities are 21 medium and three light; none is dark. The weak
experimental lookup, lack of MST10 output and limited independent MST evaluation
remain unchanged. Processing every remaining source would not guarantee balanced
MST coverage, and this batch does not establish it.

Failures are retained explicitly:

- 74448: distorted face detection fails.
- 86027: distorted support has 796 pixels, below the unchanged 1,000 minimum.
- 85960 and 14470: distorted landmarks unavailable.
- 52483: distorted measurement succeeds, but reference/input support intersection
  is insufficient for the recovery target. No target or feature fallback.

Codex inspected all 24 boards and recorded source-reference and selection
concerns separately from numerical status. Glasses/hair/surroundings included in
support, strong illumination/casts, limited detail and severe support loss are
common. Nineteen successful fits therefore do not mean nineteen suitable sources.
The 21 holds remain in the screen ledger; none was replaced or deleted. These
are qualitative development recommendations, not new user rejections or expert
MOS. Preview concerns about possible cosmetics are not asserted as proven makeup.

## Three provisional candidates

| Source | Assigned severity | Concerns for user verification |
| --- | --- | --- |
| 51803 | Medium | Broad support; soft detail and lower-face/neck or surrounding edge selection. |
| 53109 | Medium | Broad support; side-face/ear and clothing boundaries need checking. |
| 713 | Light | Broad face support; hand/neck selection and possible cosmetic/styled-lighting reference concerns. |

These sources remain unapproved. Acceptance would concern the exact displayed
reference/control and MST-conditioned distorted input, preserving any concerns;
it would not validate reference colors, MST labels, independent people or final
model quality. Source photographs remain reconstruction references, not calibrated
skin truth. User review is the next admission gate, not another mask experiment.

The limited provisional yield does not yet establish the intended larger eligible
cohort. Do not automatically fit a new model or launch replacement batches to
hide that limitation. After actual user decisions, reconcile the accepted exact
processing with the existing eight-source cohort and freeze any justified
source-group comparison before fitting. Retain the existing overall and
zero-identity-harm gates. No active model or Android asset changed.

## Evidence and checks

- [Three-source review page](../outputs/table2_source_expansion24_v1/shortlist_review.html)
- [All 24 attempts, including held cases](../outputs/table2_source_expansion24_v1/review.html)
- [Frozen selection](../outputs/table2_source_expansion24_v1/plan.json)
- [Processing results](../outputs/table2_source_expansion24_v1/summary.json)
- [Qualitative screen and retained reasons](../outputs/table2_source_expansion24_v1/codex_source_screen.json)
- [Independent selection/pixel/measurement/target verification](../outputs/table2_source_expansion24_v1/verification.json)
- [Screen/review hash binding](../outputs/table2_source_expansion24_v1/screen_verification.json)

Scripts 167/168/169 reproduce the processing and separate screen record. Checks
independently reconstruct selection, validate TRAIN/group restrictions, preserve
previous exposure bytes, recompute reference pixels and detect exact selected
reference duplicates, reproduce all 24 distortions and clipping, recompute 44
valid measurements/MST assignments and independently check 19 target residuals.
Original tracked hashes remain unchanged. No algorithm module changed; latest
full suite remains 692 passed from the earlier application-mask stage, rather
than a claimed new full-suite run. Android remains paused; CPM remains deferred.
