# Table 2 severity coverage and recovery capacity

28 October 2026. User directs continuation of the recommended thesis work and
sets historical-mask identification aside. Executed the fixed
[coverage protocol](table2-next-coverage-protocol.md), keeping the existing
measurement/application policy and eight accepted source groups unchanged.
No new mask method was tested, no tree was fitted and no source was admitted.

Scripts 164/165 generate and independently verify 24 probes: light, medium and
dark Table 2 settings on each of 22211, 22454, 62331, 6236, 67583, 75027, 83205
and 84364. These are **counterfactual distortion severities**, not new complexion
assignments, dark-MST coverage or permission to train every source at every
severity. Actual inference features still use distorted-input Lab/ITA and the
same experimental MST mapping. All four rejected sources remain excluded.

Twenty-three measurements and recovery targets succeed. The 75027 dark probe
fails face detection (zero detections); no reference feature or prediction
fallback is supplied. Its generated input and failure remain recorded. The
original eight source-conditioned distorted predictions reproduce exactly.

The same held-source fold predictor is reused across a source's three probes;
no training or hyperparameter search occurs. Each fitted oracle uses references
and describes approximate recovery capacity, not learned performance.

| Severity probe | Successful / attempted | Mean clipped pixels, all attempts | Mean reference support retained, successful | No correction | Saved-fold prediction | Fitted oracle on input support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Light | 8 / 8 | 7.52% | 90.99% | 12.694 | 12.319 | 3.222 |
| Medium | 8 / 8 | 40.51% | 72.37% | 23.488 | 15.790 | 10.973 |
| Dark | 7 / 8 | 61.86% | 52.68% | 30.117 | 21.785 | 18.123 |

Last three columns are mean CIEDE2000 on the same saved reference support;
lower is better. Dark reconstruction means include the same seven successful
sources in all three columns; the failure is not scored as zero. Clipping means
include all eight attempts. Different successful-source denominators preclude
an unqualified paired light-to-dark comparison. All are exposed-development
reconstruction scores under assumed sRGB, not calibrated skin truth or final
independent thesis accuracy. No identity controls are added to these probe
averages; the previous failed identity gate remains fully applicable.

Codex inspected all eight source boards. The light inputs often remain
uncorrected or nearly unchanged, and 75027 light is visibly over-lightened.
Medium/dark results show extensive residual patches, with similarly conspicuous
artifacts in several fitted-oracle images. 67583 medium/dark stays visibly dark
under the saved predictor. These are qualitative observations, not expert MOS.
On 75027 dark, both output panels show the input because inference and the
input-support target are unavailable; the generic oracle column heading does
not signify a fitted result for that failed row.

## Fixed-reference recovery capacity

Script 166 separately fits and applies the same bounded gamma/red/blue operator
on the complete saved reference support, including the detection-failed input.
This uses privileged reference support for diagnosis only. It neither changes
the runtime support nor supplies a detection fallback or new training targets.

| Severity | Full-reference fitted oracle, all eight | Same successful cases: input-support oracle | Same successful cases: full-reference oracle |
| --- | ---: | ---: | ---: |
| Light | 2.613 | 3.222 | 2.613 |
| Medium | 9.391 | 10.973 | 9.391 |
| Dark | 15.942 | 18.123 | 15.021 |

The last two dark entries use seven cases. Full-reference recovery reduces
residual error but does not eliminate it. Clipping destroys information, and
the specified brightness/contrast distortion is not exactly inverted by the
three correction outputs. The bounded optimizer uses a fixed identity start
and minimizes RGB squared error, so these numbers are **not a mathematical
lower bound**, proof of global optimality or an exact decomposition of error
into clipping, support and operator mismatch. They provide direct evidence of
substantial residuals under the documented recovery procedure.

## Consequence for the thesis implementation

Keep Table 2 and gamma/red/blue outputs as requested, report approximate recovery
and clipping explicitly, and retain the weak MST mapping and limited evaluation
scope. Increasing a tree's depth or training all counterfactual variants would
not by itself address these findings and would change the current training
design if done silently. Do not call dark-severity probes dark-complexion data.

The current eight-source model still fails its unchanged-image and overall gates.
No runtime replacement is supported. The next model-development priority is a
larger, consistently processed, reference-screened training-source pool with
source-group controls, keeping MST-conditioned severity assignment. That requires
source/reference suitability and exact processing review before admission; the
24 probes here are not automatically added to fitting. Final independent data,
expert MOS and Android correction integration remain unfinished. Android remains
paused under the user's existing direction; CPM remains deferred.

## Evidence and validation

- [Eight-source output boards](../outputs/table2_counterfactual_coverage_v1/review.html)
- [All attempts, failures and paired metrics](../outputs/table2_counterfactual_coverage_v1/summary.json)
- [Independent 24-probe verification](../outputs/table2_counterfactual_coverage_v1/verification.json)
- [Fixed-reference capacity results](../outputs/table2_fixed_support_capacity_v2/summary.json)
- [Capacity residual and PNG checks](../outputs/table2_fixed_support_capacity_v2/verification.json)

Verification independently reconstructs Table 2 pixels and clipping, recomputes
23 valid measurements/MST indices, replays portable predictions, checks corrected
PNGs and fixed-denominator metrics, and recomputes target residuals. All original
tracked hashes remain unchanged. Capacity checks independently reconstruct all
24 oracle PNGs and RGB residuals. No algorithm module changed; the latest full
suite remains 692 passed from the preceding application-mask stage, with these
new scripts verified through their artifact checks rather than another full run.
