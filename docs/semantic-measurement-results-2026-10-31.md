# Fuller-face measurement and MST results — 31 October 2026

The fuller-face mask now has its own working measurement path and a matching
development calibration comparison. The improvement is modest. The skin-tone
mapping and correction model are still unfinished; neither demo was changed.

## What changed and why

The user authorized continuing this work and recording changes/results without
waiting for an adviser reply. This supersedes the earlier parser hold, not the
separate hold on beard/mustache models. It is the user's process clarification,
not evidence of a panel decision. The appeal drafts and the user's ongoing
edits were not modified during this work.

We reused the existing fuller-face parser and exclusions without changing its
weights, mask rules or thresholds. Its binary mask now supplies the pixels for
Lab/ITA and six RGB endpoint measurements. Forehead/chin pixels are not clipped
back to the old detector rectangle. The feathered display edge is not used for
measurement. The existing 1000-pixel minimum remains. Required detection and
landmark failures do not fall back to old measurements.

This changes the measurement support and therefore requires a separate contract:
`f128f543377efab22930e5c60b4c20efd4c5f386d951a645818ca5c2a6265828`.
The old contract and lookup remain unchanged. No old mask approvals transfer.
The existing ITA/MST/facial-statistics decision-tree method is retained.

## One fixed development cycle

Protocol: [single-cycle plan](semantic-measurement-single-cycle-protocol.md).
Exactly 418 previously exposed MST-E development attempts from 15 subjects were
remeasured. No reserved correction-evaluation photos were opened. MST-E supplied
mapping/evaluation data, not correction-tree training. All failures were kept.

The same decreasing, equally subject-weighted isotonic recipe was fitted once
for each held subject. All photos of that subject stayed out of fitting. New
technical-success memberships were saved rather than copying old memberships.
No masks, thresholds or calibration recipes were adjusted after seeing scores.

| Measurement result | Old rule mask | Fuller-face candidate |
|---|---:|---:|
| Attempts | 418 | 418 |
| Available measurements | 396 | 393 |
| Failures | 22 | 25 |

The new path has 21 face-detection failures, one landmark failure and three
degenerate-geometry failures. The three additional failures are retained:
subject_6/PXL_20220922_141635391.jpg,
subject_6/PXL_20220922_142133535.jpg and
subject_7/PXL_20220922_200522557.jpg. They were not silently retried with another
mask, altered exclusion rule or old ITA.

The following comparison scores exactly the same 393 available photos. Each
calibrator uses its own mask contract's successful fitting membership, so this
controls the scoring denominator but does not isolate mask area as a cause.

| MST measure on shared photos | Old mapping | Fuller-face mapping |
|---|---:|---:|
| Average absolute category error | 2.234 | 2.097 |
| Average error giving each subject equal weight | 2.310 | 2.132 |
| Exact category accuracy | 10.94% | 12.47% |
| Within one category | 33.33% | 36.64% |

The candidate's fitting-subject median baseline has category error 2.855 and
exact accuracy 13.99% on these photos. Thus the candidate improves average error
against that baseline while its exact accuracy remains worse. Neither result
establishes reliable skin-tone estimates. The old full 396-row result must not
be substituted into the shared-row table.

177 of the 393 measured photos lack a different fitting subject with the same
official category. Categories 4, 5, 7, 9 and 10 each have only one subject in
this cohort. Repeated photos do not increase independent-subject support.
Previously exposed subject-held development is not untouched final validation.

The new mapping's category error is 1.924 on available well-lit photos and
2.357 on available poorly-lit photos; one video observation has error 3. These
are descriptive groups, not evidence that lighting alone caused the difference.
No lighting-based runtime policy or post-result filtering was introduced.

## What the result means

Better face coverage did not solve MST accuracy. There is no evidence here that
the correction tree now performs better: no correction tree was fitted, no new
distortions were generated, and no corrected images were claimed. The parser
still has no beard-specific class, can mistake objects for skin, and does not
establish suitable reference lighting or intrinsic skin color.

We have matching development calibration evidence, not a production lookup.
No all-row lookup was exported, no failed correction candidate was promoted,
and Android/desktop retain their existing experimental presets. We should not
force category 10 into the output or select another small calibration recipe
in response to these results.

Next, use the saved mask diagnostics and subject-support records to identify
the minimum missing mask/reference judgments and genuinely independent labeled
support. Then declare a consistent correction-data preparation plan before any
new correction fit; the old distortions were generated with different masks.
No new review batch is requested in this record. Beard/mustache-specific work
remains on hold. Professional feedback follows a good initial correction model.

## Evidence and checks

All 15 deterministic diagnostic boards were visually inspected in three contact
sheets. The selected subject_7/PXL_20220922_201156891.jpg includes part of a worn
face covering in the skin mask. Beard pixels remain in several other examples.
These are assistant-observed concerns, not user mask decisions or quantified
ground-truth scores. No outcome-dependent exclusion or refitting followed.
This establishes a concrete reason not to adopt the candidate automatically;
better coverage and modestly improved mean mapping error do not override it.

Verification passed: 393 saved full-frame statistics/endpoint-feature replays,
15 subject-held calibration refits, saved mask hashes and exact fit membership/
weights. These are reproductions of the fixed candidate, not extra scientific
trials. The original measurement contract and demo inputs stayed unchanged.

- Measurement plan, source hashes, access ledger and every attempted record:
  `outputs/semantic_mst_measurement_v1/`.
- Saved subject memberships, weights, knots, predictions and subgroup metrics:
  `outputs/semantic_mst_calibration_v1/summary.json`.
- Independent saved-feature and calibration replay:
  `outputs/semantic_mst_verification_v1/verification.json`.
- A bounded diagnostic page selects one attempt per subject using a fixed hash,
  without filtering by result: `outputs/semantic_mst_verification_v1/diagnostics.html`.
  It requests no annotations and grants no mask approvals.
- Scripts 327–329 reproduce the fixed measurement, evaluation and verification.
- Full Python suite: **841 passed in 32.72 seconds**. Five new tests cover
  full-frame support outside the detector box, failure isolation and insufficient
  mask support. No Android rebuild was needed.

Execution record: a whitespace check was corrected before processing began.
The next start encountered a Windows slash-normalization error after its first
inference but before saving any measurement record. That incomplete folder and
its access ledger are preserved as `semantic_mst_measurement_preflight_failure_v1`.
The corrected complete pass did not change the cohort or scientific recipe.
