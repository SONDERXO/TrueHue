# Table 2 known-source feasibility results

28 October 2026. Executed the [frozen protocol](table2-known-source-feasibility-protocol.md)
with scripts 151 and 152. Six previously exposed FairFace TRAIN sources, three
counterfactual severity probes per source. These settings were not assigned
as verified source complexion groups. The same square256 measurement contract
and explicitly experimental input-derived MST lookup were used throughout.

All six reference measurements succeeded. Of 18 distorted inputs, 17 produced
measurements and identifiable approximate targets. Source 75027 at dark severity
failed face detection (zero detected faces); its failure and distorted image
are retained. All 18 probes clipped generation-support pixels. **Zero pairs
are admitted under the current unclipped-training contract.** Converged target
fits do not override clipping or mask-quality requirements.

Oracle correction applies reference-informed fitted parameters on the freshly
estimated distorted-input mask. The following CIEDE2000 means score the entire
fixed reference skin mask, including reference skin missed by that input mask.
They assume decoded sRGB and measure reconstruction, not calibrated complexion.
Each source contributes equally within a severity; dark uses five paired sources,
excluding the explicitly reported failure from both paired metric columns.

| Probe severity | Measured / planned | Reference mask retained, mean | Uncorrected error | Fitted oracle error |
| --- | ---: | ---: | ---: | ---: |
| Light | 6/6 | 90.1% | 12.619 | 3.280 |
| Medium | 6/6 | 69.7% | 23.368 | 11.297 |
| Dark | 5/6 | 58.7% | 30.265 | 16.677 |

These are oracle capacity results, not learned model improvements. Scoring only
the surviving intersection would report smaller oracle errors (2.259, 7.838,
10.919), hiding missed reference-mask regions. No improvement claim is based
on that smaller region. Strong settings leave substantial residual error even
with reference-informed parameters.

All six boards were visually inspected. Stronger probes fragment selected skin,
especially 22211, 62331 and 75027. Some reference masks already include questionable
boundary/hair selections; reference masks are pipeline estimates, not expert truth.
Source 51739 includes another partial person at the left edge despite exactly one
detected box. No single-face scene-validity claim follows from detector count.
Original source decisions and holds remain unchanged; this inspection does not
approve new mask coverage or admit these regenerated pairs.

Saved PNGs pass exact decode roundtrips and hash checks. Seventeen floating RGB
fit residuals were independently reconstructed from saved target parameters.
Script 152 separately checks all evidence/input hashes, fitting-support counts,
and unchanged pixels outside each correction mask, and computes fixed-support
metrics. The existing full suite passes: **671 tests**.

[Attempt ledger](../outputs/table2_known_source_feasibility_v1/summary.json) |
[Fixed-support verification and metrics](../outputs/table2_known_source_feasibility_v1/fixed_support_verification.json) |
[Review boards](../outputs/table2_known_source_feasibility_v1/review-index.md)

## Implication for the next model build

Retain Table 2 and approximate targets as authorized. Do not quietly reduce its
severity, relabel clipped inputs as clean training pairs, or claim that fitting
recovers information lost to clipping. A new correction tree cannot be justified
from this diagnostic under the current admission rule. Next, prepare a separate
clipping-stress training/evaluation design with source-held splits, clean identity
controls, explicit irrecoverable residuals and unchanged mask-quality holds.
Changing clipped-pair training eligibility needs an explicit methodological
decision; the current contract remains intact until then. The weak experimental
MST mapping and absent MST10 outputs remain separate limitations.

No tree fitting or active runtime changes. Android paused; CPM deferred.
