# Versioned paper-gamma implementation and matched comparison

29 October 2026. Implemented the proposal's direct-power gamma convention in
`src/distortion_generation/paper_gamma.py`, separately from legacy code.
Normalized pixels use `x ** gamma`: below1 brightens, above1 darkens. Added an
explicit legacy-to-paper parameter converter that reciprocates gamma while
preserving red/blue gains and the exact predicted correction curve. Existing
models, operators, target reports and Android artifacts were not relabeled.

The new Table2 composite is explicitly a **gamma-convention sensitivity**:
same numeric settings, contrast/brightness/channel-shift order and units as
the legacy interpretation; only the exponent changes. Those other choices
remain documented engineering assumptions. This does not reconstruct Table3
exactly or complete the paper's three-distorted-version design.

## Matched-source results

Generated new inputs for exactly the20technically usable accepted original-mask
training references, retaining reference pixels, generation support and
reference-estimated severity. The original measurement mask algorithm and
experimental MST artifact remain frozen; actual new input pixels supply new
features and masks without reference-feature substitution.

| Diagnostic on identical20sources | Legacy reciprocal gamma | Direct gamma |
| --- | ---: | ---: |
| Clipped reference-support pixels, summed | 306,080 | 13,650 |
| Inputs with any clipping | 19 | 17 |
| Available input measurements | 20 | 20 |
| Existing support-screen passes | 3 | 6 |
| Both unclipped and support-screen passing | 1 | 0 |

Clipped pixel count falls by approximately95.5%. That is a useful numerical
change, not proof of better skin accuracy, a validated augmentation recipe or
learned correction performance. All masks remain unreviewed in their new
distorted form; six screen-passing cases are72595,60229,85815,11521,30546,56839.
Their inputs still clip. Coverage/contamination and source-level concerns
remain separate from brightness or pixel-count success.

Available approximate recovery targets number19. The target-construction
function was called for20inputs;14418returns immediately unavailable because
its input/reference mask intersection is empty. The inspected mask selects
non-skin at the side rather than the original facial support despite meeting
the measurement pixel minimum. No reference mask or parameter fallback is
introduced. This is a recorded regression and a concrete reason not to promote
the full new path automatically.

For each available target, preserve the existing optimizer's report explicitly
in legacy parameter coordinates, and store a separately named direct-gamma
target after reciprocal conversion. Verify identical corrected pixels for the
two parameterizations. The composite includes offsets/contrast/clipping, so
these are reference-informed approximate fits, not analytic exact inverses.
Target fitting is not decision-tree training: no regression trees were fitted.

## Verification and remaining work

Script232reconstructs all20new composites/clipping reports, recomputes input
features and support screens, and verifies19curve-equivalent target conversions.
Source/dependency hashes and the original measurement contract match. Thirteen
new unit cases cover the stated gamma direction, legacy-curve preservation,
invalid parameters, explicit versioning and source immutability. The full suite
passed **755 tests in12.40seconds**. Comparison boards were inspected as local
images; no interactive-browser QA is claimed.

No reserved training-check, development-validation or final-test source was
accessed. No active tree, default mask, calibration threshold, source review or
fitting eligibility changed. The prototype lookup remains experimental; a
new input measurement is not new evidence of intrinsic tone or calibrated MST.

The next implementation decision is to complete a documented, versioned
augmentation specification for the paper's three variants and resolve the
remaining brightness/contrast/channel choices. Keep the paper's gamma
definition explicit without claiming that Table2's ambiguous “Gamma/Midtone”
label or darkening description uniquely determines every operation. Recheck
matched input masks and source concerns before any learned-model comparison.
Do not solve the remaining gaps by redefining the support screen or admitting
14418's failed target. No new full-batch user review is requested at this stage.

- [Matched comparison boards](../outputs/paper_gamma_input_comparison_v1/review.html)
- [Summary](../outputs/paper_gamma_input_comparison_v1/summary.json)
- [New input features and explicit target coordinates](../outputs/paper_gamma_input_comparison_v1/attempts.jsonl)
- [Verification](../outputs/paper_gamma_input_comparison_v1/verification.json)
- [Frozen comparison protocol](paper-gamma-comparison-protocol.md)
