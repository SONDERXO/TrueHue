# Frozen candidate retains benefit under two JPEG encodings

30 October 2026. The frozen endpoint-feature candidate retains its reconstruction
benefit at JPEG quality 95 and 85 in this fixed-support development check. There
are no additional clean-photo correction changes: source 68453 remains the one
clean failure in every encoding. This improves our evidence about the candidate's
encoding sensitivity, but does not satisfy the clean-photo safety requirement
or justify replacing the demo model.

The [protocol](endpoint-jpeg-sensitivity-protocol.md) declares the original
lossless input plus two JPEG re-encodings. All 47 admitted pairs use their
already frozen source-held tree. No model, tolerance, feature or rule is tuned.
All eleven input features are recomputed from decoded stress pixels, including
Lab means, ITA, experimental MST and exact channel endpoint fractions. None are
copied from the uncompressed row. All earlier human labels remain unchanged.

Lower CIEDE2000 is better. Each unchanged comparator uses its actual decoded
input; JPEG clean references are still the original clean photos, so their
unchanged error is nonzero. Correction changes count only pixels altered by the
operator relative to that decoded input, not JPEG's own pixel differences.

| Encoding | Corrected error /47 | Unchanged error /47 | Clean photos corrected /26 | Parameter changes vs lossless /47 |
|---|---:|---:|---:|---:|
| Original lossless | 5.300 | 9.165 | 1 | 0 |
| JPEG quality 95 | 5.357 | 9.520 | 1 | 1 |
| JPEG quality 85 | 5.491 | 9.653 | 1 | 1 |

All 21 distorted inputs average 11.279 corrected error in the original encoding,
10.638 at quality 95 and 10.641 at quality 85; corresponding unchanged errors
are 20.511, 20.508 and 20.495. Lower corrected error after compression does not
establish better fidelity in general: JPEG can smooth artifacts and changes
the feature routing for one case.

The only changed parameter triple is source 6236's light-distortion input, at
both JPEG settings. All 26 clean parameter predictions remain identical to
their lossless predictions. Source 68453 still has an unwanted correction;
all three encodings fail the zero-clean-change gate. No source-specific skip
rule or exception was added.

## Verification and limits

`scripts/269_check_endpoint_jpeg_sensitivity.py` saves encoded stress inputs,
feature vectors, source-held routes, parameters and output PNGs. Its `--verify`
mode checks frozen hashes, re-decodes saved bytes, independently reconstructs
endpoint counts using channel histograms, recomputes Lab/ITA/MST, verifies
source separation and prediction routes, reconstructs every corrected image,
checks outside-mask preservation and metrics, and reproduces all 47 original
lossless predictions. There are **141 verified feature/output replays** and
**zero new model fits**. Evidence lives in
`outputs/endpoint_jpeg_sensitivity_v1/verification.json` and `summary.json`.
The latest full core suite remains 794 passing tests; this script-only stress
check does not claim a new full-suite run.

This check intentionally freezes original application and scoring masks to
isolate encoding-related feature/curve sensitivity. It does not rerun face
detection, landmarks or skin-mask generation, and it does not approve masks on
newly encoded images. Quality 95/85 are engineering settings, not measured
phone-camera defaults. Only one additional encode/decode cycle is tested.

The original cohort is small, repeatedly exposed and largely synthetic.
Endpoint features could still depend on synthetic artifacts. No unreviewed
sources, reserved evaluation roles, new calibration, photographer forms or
runtime assets were introduced. The original ITA/mask contract and experimental
lookup stay unchanged.

Next work should test the entire frozen detection/mask/feature path under
encoding changes, preserving explicit stage failures and lineage. Retain the
same clean failure for honest evaluation rather than fitting an exception to
it. Independent mask quality, clean-photo safety and real-photo generalization
remain required before adoption; this result alone is not thesis completion.
