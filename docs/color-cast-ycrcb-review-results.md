# YCrCb-only paired mask review imported

29 October 2026. Found and validated the eight-source export against its
manifest, exact IDs, paired-reference/color-input scope and unchanged displayed
board hashes. Preserved the original export byte for byte and all exact notes.

**Six accepted, two rejected.** Four accepted entries have notes; two have none.
This was a purposive gain/risk packet, so six of eight is not representative
mask accuracy or evidence of final correction quality.

| Source | Decision | Exact note |
| --- | --- | --- |
| 14418 | Reject | Included the background too much |
| 75166 | Accept | This is acceptable, but the face mask caught some foreign object not that much |
| 20648 | Accept | No note supplied |
| 72595 | Accept | Acceptable, but minor holes in face mask |
| 34227 | Accept | No note supplied |
| 68073 | Accept | Acceptable, but foreign object (earrings) got caught in face mask |
| 75898 | Reject | No note supplied |
| 66413 | Accept | Okay facial coverage, but this photo is too blurry |

Keep 14418 rejected despite its numerical retention gain. No reason is invented
for 75898. Preserve accepted foreign-object and hole concerns without changing
the user's decision or calling those masks clean. 66413 is accepted for the
candidate mask pair, but its explicit blurry-photo concern requires separate
source-suitability assessment before fitting.

Approval applies only to the displayed YCrCb candidate reference and color
input masks. It does not transfer to exposure/combined masks or new targets,
validate the unchanged historical MST lookup for different measurement pixels,
or admit sources automatically. Prior baseline/parser decisions remain separate.
The unreviewed sources among the full twenty remain held.

The result supports taking this fixed, unchanged rule into a separate training
mask check rather than repeatedly tuning on these eight. Freeze its precise
measurement definition first, retain all source exclusions and concerns, and
keep that check separate from final validation/test. Only a supported policy
should proceed to matching MST calibration and correction-row construction.
Do not promote globally based solely on the improved retention count or this
small selected review. No new full-source review batch is requested here.

Import checks pass for exact scope, decisions, notes and board evidence. No
algorithm, calibration, active asset, training eligibility or review label was
rewritten; no reserved check was opened or correction tree fitted. The last
full suite remains 762 passing tests; this import uses exact artifact checks.

- [Exact reconciled reviews](../outputs/color_cast_ycrcb_review_import_v1/reconciled_reviews.json)
- [Original export](../outputs/color_cast_ycrcb_review_import_v1/original_user_export.json)
- [Summary](../outputs/color_cast_ycrcb_review_import_v1/summary.json)
- [Verification](../outputs/color_cast_ycrcb_review_import_v1/verification.json)
