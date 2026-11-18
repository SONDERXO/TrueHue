# Continuous MST correction candidate results — 6 November 2026

The user-selected continuous-score experimental interface is implemented and
its generated checks pass. `src/correction/continuous_mst_candidate.py` joins
actual-input Lab/ITA features with contextual `input_mst_score` on 1–10. It
replaces the integer feature only in this separate candidate. The three
gamma/red/blue controls and existing tree procedure remain unchanged.

The helper preserves fractional scores, checks raw/clipped consistency and
measurement-contract declarations, and rejects missing/invalid predictions,
integer-schema extras and reference-label extras. It does not estimate MST,
prove prediction/image binding or establish scientific validity. The old
integer lookup and calibrator remain unchanged and available; no matched real
continuous-versus-integer comparison is claimed.

Script471 used 12 arithmetic inputs with a manually declared linear contextual
fixture, not a trained MST model. It exercised lower/upper clipping and interior
fractional scores. One generated correction tree used eight rows; four other
arithmetic rows were held from fitting. All12 portable JSON prediction replays
matched inverse-normalized fitting-model predictions to absolute tolerance
1e-12, zero relative tolerance. Those four rows are not held people or
independent photographic evaluation. No nested estimator/tree experiment ran.

Sixteen new interface tests plus existing contextual, target-scaled and portable
tree tests: **63 passed in 4.60 seconds**. These cover fraction preservation,
explicit clipping, invalid/missing predictions, incompatible feature schemas,
Lab ranges and contract mismatch. This is not a full-suite or device result.

Evidence: `outputs/continuous_mst_correction_generated_v1/` (ignored), with
fixtures, exported tree, fitting normalization, verification and source/artifact
hashes. Protocol: [continuous candidate](continuous-mst-correction-protocol-2026-11-06.md).
Source and artifact hashes were independently checked after execution.

The integer-category adapter is no longer required for this candidate. Real
skin/reference eligibility, compatible real contextual calibration, exact
prediction/input provenance and justified person grouping remain unresolved.
Nested subject-held predictions are required before a real correction fit.
Because the estimate derives from existing ITA/Lab inputs, extra predictive
benefit is a hypothesis, not additional independent information or an observed
improvement. No rounded labels or missing-MST fallback were introduced.

Zero real images, real MST fits, photographic tree fits, admissions, runtime or
Android changes, contacts or uploads. The source dataset's private research,
noncommercial, citation and no-redistribution conditions remain. This closes
one interface experiment; no automatic new batch, fit or review is activated.
