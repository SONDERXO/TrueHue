# Existing PPR10K eight-pair readiness assessment — 9 November 2026

## Decision

All eight pairs are retained. **Zero are established as automatic-training-ready
from the saved evidence; all eight remain unresolved, not rejected as photos.**
Their historical acquisition, dimensions, colour handling and oracle-fit records
provide a useful starting point. No new source download or repeated operator fit
is necessary to establish those facts.

The next concrete technical check is automatic support and correspondence
feasibility on these exact eight pairs. Its fixed scope is documented separately;
it has not run. It cannot by itself qualify a correction model or supply missing
MST truth. The final holdout stays byte-unread.

## Checks completed

Script 702 creates `outputs/ppr10k_saved_readiness_v1/readiness_PRIVATE.json`,
including a full per-pair ledger. It verifies six historical metadata files
against the original `sha256.json`, checks the saved protocol's plan/region
bindings, and reconciles all sixteen image-audit entries, eight region records,
eight solver/metric records and eight independent-replay records. All match.

All sixteen TIFF paths exist and are nonempty; saved source hashes agree with
the historical manifest. No current TIFF bytes were read or decoded. This is
metadata reconciliation, not fresh verification that the image bytes/profile
remain unchanged. Before future processing, recheck the original TIFF hashes.

Each saved pair has matching dimensions, RGB16 source/RGB8 target, matching
embedded ICC hashes and prior sRGB verification. All eight groups are below
the publisher's training boundary 1356. These photos are already TrueHue
development-exposed; eight publisher groups do not prove eight independent
people, unseen status or representative skin-tone coverage.

## Per-pair evidence

The DE numbers are historical target-aware fits on held checkerboard blocks
within approximate source-only polygons. They are not automatic predictions,
independent-photo evaluation or measured skin-colour accuracy.

| Pair | Saved source observation / practical concern | Three-control DE | Four-control DE | Three-control clipped samples / polygon samples |
| --- | --- | ---: | ---: | ---: |
| 787_0 | Sun/hat shade, fringe, smile and lipstick | 6.218 | 2.684 | 88/15342 |
| 330_0 | Small downward/profile face, headpiece/net, bright boat | 2.708 | 2.154 | 0/3576 |
| 767_0 | Indoor bridal portrait, fringe/makeup, darker face | 8.486 | 2.191 | 0/17052 |
| 1117_0 | Small spotlit face against dark studio, highlights/makeup | 6.735 | 2.527 | 0/3816 |
| 1188_0 | Couple; selected small downward male profile with facial hair | 5.978 | 2.443 | 55/2259 |
| 990_0 | Indoor seated portrait, hat/hair, uneven illumination | 2.603 | 2.255 | 4/2832 |
| 904_0 | Family; selected image-right face, glasses/facial hair, hard light/profile | 5.576 | 4.871 | 5/5148 |
| 455_0 | Studio portrait, rollers and pronounced makeup | 1.409 | 1.294 | 0/5772 |

Equal-image mean DE is 4.964 for three controls and 2.552 for four. Adding contrast
increased clipping in six of eight. Four controls remain unadopted, and no
acceptable residual-error threshold was predeclared. These data cannot justify
silently changing the retained gamma/red/blue model. Earlier reciprocal gamma
parameters must not be copied as direct exponents.

The eight-pair result JSON does not include unchanged-input DE for these blocks.
Consequently this ledger does not claim all three-control fits improve over the
input. Recomputing that baseline later requires the saved source/target arrays
or original TIFFs, with the original support and metric contract; it does not
require a new parameter fit. Earlier six-pair baseline improvements are separate
evidence and must not be transferred to these eight.

## Readiness matrix applying to all eight

| Requirement | Saved evidence | Disposition |
| --- | --- | --- |
| Traceable source/editor-A linkage | Frozen exact sample and paired filenames/historical hashes | Established historically; recheck image hashes before processing |
| Matching dimensions and documented colour contract | Sixteen image-audit records, matching ICCs, source/65535 and target/255 | Established historically; no previews as numeric originals |
| Pixel correspondence | Layout inspected, no measured registration or warp | Unverified; equal dimensions alone do not prove alignment |
| Automatic selection of intended face | Historical largest-source-outline rule, ties image-left; polygons saved before targets | Historical source-only manual selection is available, automatic matching not established |
| Automatic facial skin measurement | No current-pipeline skin masks from these diagnostics | Missing; polygons include features/hair/makeup and cannot be promoted to skin masks |
| Face/visible-neck support and protection | Historical diagnostic excludes neck, uses hard polygon boundaries | Missing; no product scope reduction inferred |
| ITA/MST compatibility | No supplied MST labels or matched current measurement/calibration evidence | Unresolved; do not invent labels, calibrate on these targets or substitute old features |
| Three-control representability | Target-aware residuals above, no declared acceptance threshold, no saved unchanged baseline for these eight | Limited approximation demonstrated, acceptability unresolved |
| Identity and independent evaluation | Eight publisher-training groups; all exposed; cross-source person/duplicate links unknown | Preserve groups conservatively; no final-evaluation admission |
| Dataset rights | Existing noncommercial research record and editor choice | Retain local/ignored photos and attribution; no public gallery or commercial clearance inferred |

Predicted MST is not independent tone truth. The absence of supplied labels
does not prohibit photographic/support inspection, but does prevent verified
per-MST coverage or fairness claims. Even a successful mask screen would not
resolve that requirement automatically.

## Verification and boundary

Metadata scalar replay reconciles all eight metrics with the original records,
recomputes the two equal-image means and six clipping increases, and checks every
named input hash remains unchanged. No model refit or photographic metric replay
is claimed. Zero source/target image-byte reads, detector/parser/FaceOcc forwards,
MST/correction fits, correction renders, acquisitions, final-holdout reads or
runtime changes occurred. Existing artifacts remain intact.

- [Original eight-group comparison](ppr10k-new-group-comparison-results-2026-11-02.md)
- [Dataset review](dataset-correction-reference-review-2026-11-09.md)
- [Fixed next screen protocol](ppr10k-automatic-support-screen-protocol-2026-11-09.md)
