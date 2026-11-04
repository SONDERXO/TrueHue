# Full-path JPEG check: benefit retained, mask sensitivity remains

30 October 2026. All **141 full-path attempts complete successfully** through
face detection, original rule mask/landmarks, Lab/ITA, experimental MST, endpoint
features and frozen source-held correction. The candidate retains reconstruction
benefit at both JPEG settings with no additional clean overcorrection. However,
some masks lose substantial facial coverage. Successful stage completion is
not a passing skin-mask quality assessment or a release-ready correction model.

The [protocol](endpoint-full-path-jpeg-protocol.md) reuses the exact 47 lossless,
47 JPEG95 and 47 JPEG85 saved inputs from the earlier fixed-support check.
Every input mask is now recomputed. Every scoring mask remains the original
reference mask; reduced input support therefore cannot hide uncorrected facial
pixels by shrinking the score region. Trees, features and thresholds are not
tuned or fitted. The original mask/ITA contract and lookup remain unchanged.

| Encoding | Completed /attempts | Corrected CIEDE2000 /47 | Unchanged /47 | Clean photos corrected /26 |
|---|---:|---:|---:|---:|
| Lossless | 47/47 | 5.300 | 9.165 | 1 |
| JPEG quality 95 | 47/47 | 5.469 | 9.520 | 1 |
| JPEG quality 85 | 47/47 | 5.704 | 9.653 | 1 |

Lower error is better. Both compressed full-path errors are slightly worse than
the fixed-support results (5.357 and 5.491), while remaining below the unchanged
comparators. There are no failures excluded from these means. Source 68453 is
still the one clean-photo overcorrection at every encoding; it prevents adoption.
The JPEG inputs' unchanged clean error is nonzero because compression itself
changes pixels, but that is not counted as an operator-induced clean change.

The lossless rerun reproduces all 47 original masks exactly and matches the
original candidate's aggregate errors. Every JPEG mask differs by at least one
pixel; this alone does not establish material damage. Compared with the earlier
fixed-support JPEG run, the medium-distortion 68453 parameters additionally
change at each JPEG setting. Other prediction changes caused by compression
alone were already recorded in that earlier check.

## Mask changes and visual inspection

| Encoding | Mean mask IoU with original /47 | Lowest mask IoU | Lowest-agreement case |
|---|---:|---:|---|
| Lossless | 1.0000 | 1.0000 | all exact |
| JPEG95 | 0.9584 | 0.7978 | 75027 medium distortion |
| JPEG85 | 0.9385 | 0.5199 | 1398 medium distortion |

IoU is agreement with the original candidate mask, not human skin-label accuracy.
Human acceptance of original masks does not automatically approve compressed
or newly measured masks. No new training eligibility or review decisions are
inferred from these stage-success results.

Inspected the two minimum-IoU boards. At JPEG95, source 75027's darkened face
has noticeable changes around the eye/forehead boundary. At JPEG85, source
1398's recomputed mask loses much of the forehead and other facial support.
Thus the lower-agreement tail represents a real coverage problem, despite
overall averages retaining benefit. Original anatomical holes and masked-only
application also continue to cause visual boundaries; they are not fixed here.

- [JPEG95 largest mask change](../outputs/endpoint_full_path_jpeg_v1/worst_mask_jpeg95.png)
- [JPEG85 largest mask change](../outputs/endpoint_full_path_jpeg_v1/worst_mask_jpeg85.png)

## Verification

`scripts/270_check_full_path_jpeg.py --verify` replays **141 face detections**,
checks face boxes, reconstructs **141 masks and anatomical exclusions** from
captured frame-local landmarks using the original rule/component/mouth code,
recomputes features/MST/routes, reconstructs outputs and metrics, checks
outside-mask preservation and held-source separation, and accounts for every
attempt. There are zero failed attempts in this run and zero model refits.
The verifier still explicitly handles failures and prohibits a saved corrected
output or parameters after a failed measurement.

`scripts/271_report_jpeg_mask_changes.py` independently recomputes all mask IoUs
from saved pixels and prepares the largest-change boards with hashes. Its red
overlay means newly added pixels and blue means removed pixels. Neither color
denotes a human skin classification.

Evidence is in `outputs/endpoint_full_path_jpeg_v1/plan.json`, `attempts.json`,
`summary.json`, `verification.json`, `mask_agreement_report.json` and saved
geometry/masks/results. No core library changed. The last full test suite remains
794 passing tests; this script-only full-path check uses the recorded stage,
geometry and pixel replays rather than claiming another full-suite run.

No reserved data, calibration, photographer forms, source exceptions or demo
replacement occurred. This remains a small, repeatedly exposed synthetic
development cohort. JPEG95/85 are chosen engineering settings, not verified
phone-camera presets, and one extra encode/decode cycle does not cover all
camera pipelines. Remaining work must address clean-photo safety and robust
facial coverage, retaining the paper's rule-mask/ITA/MST/tree requirements and
documenting any proposed method change. No further user review is needed for
this completed check.
