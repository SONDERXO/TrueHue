# Traced JPEG mask losses and tested one cleanup-order change

30 October 2026. Stage tracing identifies where compressed-input masks lose
original support. A fixed close/open/close application-support candidate
recovers some missed facial areas and modestly improves reconstruction error.
It also adds pixels outside reference support and leaves visible color patches.
The candidate remains experimental; no demo, estimator, lookup or training
mask is replaced.

## Stage attribution

`scripts/272_trace_jpeg_mask_stages.py` reconstructs all 141 full-path masks and
partitions lost original selected pixels into disjoint stage categories. This
attributes disagreements in the actual sequential pipeline; it is not an
independent causal intervention or a human skin-label accuracy measurement.

| Loss category | JPEG95 pixels | JPEG85 pixels |
|---|---:|---:|
| Outside changed face box | 2,681 | 3,408 |
| Anatomical exclusions | 4,987 | 6,518 |
| Largest component discard | 971 | 11,588 |
| Morphological cleanup discard | 12,122 | 11,150 |
| HSV-only rejection | 13,398 | 19,445 |
| YCrCb-only rejection | 2,583 | 3,244 |
| Both color rules reject | 699 | 1,185 |
| Total original pixels lost | 37,441 | 56,538 |

All lossless stage differences are zero. At JPEG85, component selection discards
substantial regions still surviving color/morphology filtering. Morphology
loss is substantial at both settings, motivating the single comparison below.
Color-rule rejection remains another major source of loss and is not solved
by reordering cleanup.

## Fixed application-support comparison

The [protocol](jpeg-cleanup-order-protocol.md) was written before comparison.
Original cleanup is open/close/close; the candidate is close/open/close. Both
retain the same HSV AND YCrCb ranges, 5x5 ellipse, one opening/two closings,
largest component and required anatomical/complete-mouth exclusions. No color
threshold, kernel size, iteration count or source-specific rule is tuned.

Only correction support changes. Original measurement masks and Lab/ITA/MST/
endpoint inputs, held-source trees and all parameter triples remain frozen at
their full-path results. Using this candidate to estimate ITA would require
separate contract/calibration work and is not performed. Reference scoring
masks stay fixed, and no compressed/new mask inherits human acceptance.

All 47 candidates per encoding meet the existing 1000-pixel support minimum;
no attempted case is dropped or silently replaced by a fallback.

| Encoding | Original support CIEDE2000 | Candidate support CIEDE2000 | Unchanged input |
|---|---:|---:|---:|
| Lossless | 5.300 | 5.246 | 9.165 |
| JPEG95 | 5.469 | 5.289 | 9.520 |
| JPEG85 | 5.704 | 5.447 | 9.653 |

Lower error is better. The same clean photo, 68453, is still overcorrected in
each encoding. The clean-safety requirement remains unmet.

| Encoding | Missed reference-support pixels before → after | Outside-reference candidate pixels before → after |
|---|---:|---:|
| Lossless | 165,059 → 155,377 | 12,320 → 16,511 |
| JPEG95 | 193,805 → 164,302 | 22,501 → 25,255 |
| JPEG85 | 208,965 → 170,906 | 22,836 → 26,700 |

Counts pool pixels over the 47 cases, not independent subjects. The JPEG85
candidate misses about 18% fewer original reference-support pixels, but also
selects more pixels outside that reference. Outside-reference additions may
be genuine missed skin or non-skin; these masks are not exhaustive ground truth.
No original selected pixels are removed in the 141 observed candidates, but
this finite result is not asserted as a guarantee for arbitrary inputs.

## Visual result and adoption limit

Inspected [1398 JPEG85 before/after](../outputs/jpeg_cleanup_order_v1/known_forehead_loss.png).
The missing forehead region is restored, with 7,329 additional selected pixels;
771 additions lie outside the original reference mask. This case is both the
previously identified forehead-loss example and the maximum outside-reference
addition, so the two selection labels in the visual report refer to the same
board rather than two independent examples.

The corrected output still has severe patchy red/color artifacts. Wider support
can expose more of that correction artifact rather than produce a polished
photo. Recovering geometric coverage and improving a masked mean error are
not sufficient evidence of natural-looking correction or safe non-skin handling.
Do not promote this candidate or erase prior mask concerns from the results.

## Verification

Stage tracing checks 141 exact original mask reconstructions and 141 disjoint
loss partitions. `scripts/273_compare_jpeg_cleanup_order.py --verify` independently
rebuilds all 141 alternative masks from explicit color comparisons and morphology,
checks unchanged parameters and baseline metrics, reconstructs all outputs using
the direct gamma equation, verifies saved mask/output hashes and recomputes
support counts, output metrics and aggregate denominators. There are zero
new model fits. Script 274 generates and hashes the diagnostic comparison boards.

Artifacts: `outputs/jpeg_mask_stage_trace_v1/` and
`outputs/jpeg_cleanup_order_v1/`, including plans, attempts, summaries and
verification. No core-library change occurred. The last full suite remains
794 passing tests; this work uses the recorded image/stage replays and does
not claim another full-suite run.

The scope remains exposed synthetic development. Existing clipping, approximate
recovery targets, weak experimental MST, incomplete neck support and clean-photo
safety remain unresolved. No reserved data, new labels, photographer forms or
runtime behavior changed. Next work should separate recoverable exposure/color
errors from information-loss artifacts in the retained correction operator;
another unvalidated global mask expansion is not justified by this result.
