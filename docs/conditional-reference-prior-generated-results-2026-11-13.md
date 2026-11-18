# Conditional reference prior: generated mechanism works, source bias remains

13November2026. User authorized implementing and running the [frozen generated design](conditional-reference-prior-generated-protocol-2026-11-13.md). **27tests PASS in0.80s;442independent numerical checks, maximum difference2.22e-16. Engineering PASS and ideal conditional-trend mechanism PASS. Real photographic prior/tree fitting remains UNQUALIFIED.** Evidence: outputs/conditional_reference_prior_generated_v1.

New code: src/model_training/conditional_reference_prior.py, conditional_prior_fixtures.py, conditional_prior_numpy_check.py; scripts/check_conditional_reference_prior_generated.py; tests/test_conditional_reference_prior.py. No image libraries, sklearn or NumPy are required by the standalone scalar prior/evaluator. Independent reconstruction uses NumPy. No new dependency installed, photographic data read or correction tree fitted.

## Implemented contract and checks

The fixed eight green bins, strictly positive RGB selection, equal source-bin mean weighting and no smoothing/interpolation/pseudocount remain unchanged. A/B/C alone contribute to the generated table; H is excluded before pixel access. Held/unknown poison payloads remain unread. Duplicate/missing/overlapping source IDs, distorted/scientific fitting records and all-zero references refuse explicitly. The expected all-zero failure is preserved and cannot be overwritten.

Missing bins return null expectations and unavailable residuals when no supported pixels remain. Partial support is explicit. Empty-input count fractions use zero by a stated empty-count convention, while residuals remain null; this is not a zero residual/neutral decision. RGB8conversion, green boundaries, zero channels, counts, schema corruption, source contribution arithmetic, table JSON roundtrip, input nonmutation and immutable artifact copies are tested. Source-bin weighting remains unchanged after repeating the already numerous source's pixels100times; it differs from pooled-pixel weighting as specified.

Independent source/bin contributions and descriptors agree within1e-12 for the declared probes, with exact provenance/count checks. Stored73probe records comprise16ideal,36source-offset,5availability,14gamma/quantization and2clipping records. All final design/code hashes, held exclusion and missing-count accounting verify unchanged. These are generated records, not photographs, people or tone-group evidence.

## Ideal edit mechanism

On all16ideal cases, including H's changed pixel composition, residuals recover the separate applied red and blue log-gains within arithmetic tolerance. The reference trend is explicitly non-neutral and brightness-dependent; the cue does not force colors toward gray. This demonstrates the conditional relationship under the assumed trend. It does not show that processed portrait colors follow this relationship, that these residuals should set controls directly or that a correction tree would transfer them successfully.

## Prior mismatch, gamma and clipping

All eight nonzero acceptable-source offsets produce corresponding nonzero identity residuals. Their values reproduce the unmodelled offsets approximately exactly: an acceptable source shifted by0.1log units produces a residual near0.1despite no added edit. The9th zero-offset identity has zero residual. Thus source weighting and conditioning remove the constructed brightness trend, but do not distinguish an unmodelled source colour from an applied cast. These are bias probes, not human judgments or proof that every statistical prior fails.

Gamma further invalidates a simple pure-colour interpretation. On the generated underexposure-only example the residual is approximately[0.07545,-0.05228]despite no added red/blue gain. On the overexposure example only68.75%ofpixels remain supported, versus100%for the pure-gain examples; residuals are approximately[-0.05405,0.03598]. A downstream method would need to handle this coupling without an inference recipe oracle. No additional bin range or interpolation is introduced to rescue support.

In the fixed clipping probe, the continuous residual shift is0.02020rather than ideal logbluegain0.04001. The quantized stretched value differs from the same continuous unstretched baseline by0.02199; that number includes quantization as well as saturation and is not a pure clipping estimate. The table does not undo lost signal. Full continuous/quantized probe values and support counts are saved; there is no JPEG/resize or real-photo robustness claim.

## Disposition

Preserve this as engineering-correct with a demonstrated ideal conditional mechanism and explicitly observed prior-mismatch/gamma/availability limitations. Do not treat any nonzero residual as evidence that a person's complexion needs correction. Equal source weighting does not establish darker-skin fairness; a learned prior can encode acceptable-reference corpus bias.

No real-photo prior fitting, new descriptor append, correction-tree choice/fit, parameter/bin/interpolation/feature rescue or user review is selected. The current small exposed/unlabelled corpus does not establish the broader reference prior required for a photographic claim. A future proposal needs concrete credible source context or independent evidence that the conditional relation is useful, with per-fold prior construction and tone-group harms/benefits accounted for. Generated bias is not a universal-identifiability rejection gate, but ideal synthetic success alone supplies no real-fit qualification.

Earlier accepted baseline, all closed experiments, ratings and approved59807manual/ears remain intact. No raworiginals/lockedholdouts/manifests/runtimeAndroid/manuscript changes, actual dataset arrays or real prior/tree fits/predictions. Modelunfinished/paperpaused/darker-skinpriority/November14complete-deliverytargetatrisk/exacttimeunspecified.
