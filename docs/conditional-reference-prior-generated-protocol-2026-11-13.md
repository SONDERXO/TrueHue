# Fixed generated-only conditional reference-prior test

13November2026. User authorized specification after the [candidate review](conditional-reference-colour-prior-review-2026-11-13.md). **Design only: do not implement/run the prior or fit a correction tree at this stage.** This is our green-conditioned acceptable-reference adaptation, not the original luminance-conditioned illuminant estimator or an implementation of published author code.

## Fixed table and units

Use normalized encoded RGB triples in[0,1], not physically linearized RGB. A generated RGB8 adapter converts each code tocode/255. For each strictly positive pixel define u=log(R/G),v=log(B/G). Use8fixed green bins: b=min(7,floor(8*G)). Green1 belongs tobin7; every channel must be within[0,1] and all must be>0 for logarithms. Zero-channel pixels are excluded from statistics and counted explicitly, never assigned zero chromaticity. Negative, >1, nonfinite, malformed or wrong-channel values are errors. No bright-only, skin-tone or white-object selection.

For each FITTING reference source and each occupied bin compute its mean(u,v). The table expectation for that bin is the arithmetic mean of these source-bin means over contributing sources. Thus each source has equal weight WITHIN each conditional bin, regardless of pixel count. Missing-source bin contributions are omitted, never replaced by zero. This is conditional equal-source weighting, not a claim of equal total table mass or equal demographic representation. Record contributing source IDs/counts and eligible pixel counts per bin and source. A fitting source with no positive pixels is refused, not silently dropped.

No smoothing, interpolation, pseudocount, bin merging, fallback prior, learned threshold or alternative bin count. An empty bin is explicitly unavailable: expectations null, contributing sources0. Table outputs are acceptable empirical log-chromaticities, not desired gray values or canonical physical skin colour.

## Fixed descriptor/availability

For an input, evaluate only positive pixels whose green bin is populated. Compute mean[u-mu_R(bin)] and mean[v-mu_B(bin)] over supported pixels. Return named fields: available, positive_fraction, supported_fraction, mean_red_residual, mean_blue_residual, plus explicit zero-channel/unsupported counts. Fractions use ALLinput pixels as denominator. Empty input is unavailable with null residuals; malformed input is an error. No supported pixel means available=false and residuals=null, not numeric0 or neutral controls. Partial support is reported, not concealed; there is no fraction cutoff selected here. These descriptors do not directly choose gamma/gains or modify images.

Inference uses only the input and the prelearned table. No source identity, reference, edit role or prior-corrected variant is supplied to descriptor evaluation. Those labels exist only in generated records and table-training provenance. A zero residual is not a verified acceptable original, confidence certificate or fair-tone decision.

## Source split and leakage contract

The table builder receives explicit unique fitting source IDs and explicit disjoint excluded/held IDs. It selects fitting records by sourceID BEFORE inspecting pixel payloads. Each fitting source must have exactly one record marked generated_fixture=true, role=reference. Missing/duplicate fitting IDs, ID overlap with held/excluded, a distorted-role reference or an entirely ineligible reference are errors. A malformed record from a held source must be ignored without reading its pixel payload. Unknown extra records do not expand the fitting roster. Record exactly which source IDs contributed; held references never enter the table. This is a generated leakage test, not authorization to inspect real source manifests or locked holdouts.

The descriptor itself cannot select a source-specific expectation or look up the test source. Any later photographic evaluation would require fitting the prior separately inside every source-held fold and binding its own eligible sources/reference hashes. No global table learned from all11development references, held-target subtraction or same-source canonical lookup is permitted.

## Frozen generated reference trend

Let G_k=(k+0.5)/8 for k=0..7, and define non-neutral, brightness-dependent reference ratios:

u_k=0.12+0.08*G_k; v_k=-0.15+0.04*G_k;
RGB_k=[G_k*exp(u_k),G_k,G_k*exp(v_k)].

Only k0..5 are used for the basic trend references and ideal probes so that the high-green reference red channel remains within1. Bins6and7 are reserved for missing-bin and clipping stress where explicit alternative pixels are specified below. These are artificial material/brightness relations, not measured skin colours or demographic labels.

Fitting references A contains one pixel per k0..5; B contains1,2,3,4,5,6repeats respectively; C contains6,5,4,3,2,1repeats. All share the same within-bin RGB_k. Held reference H reverses k order and uses counts2,1,4,1,3,5. Its sourceID is excluded from the builder. Exact same-conditional-trend holdout tests pixel-composition changes, not source-offset generalization.

Freeze four roles: identity, red245/255, blue245/255, blue255/245; gamma1. For ideal continuous arithmetic, no clipping is needed. Fit the one table from A/B/C only, then describe each role on A/B/C/H:16records. Require each available residual to equal(log redgain,log bluegain) within absolute/relative1e-12, with source conditional expectations unchanged by the unequal within-source counts. This tests the mechanism without fitting a correction tree or interpreting residuals as chosen controls.

## Fixed confound and engineering probes

1. **Unmodeled acceptable source offsets:** use H with red multiplier exp(s_R) and blue multiplier exp(s_B), for each pair in{-0.1,0,0.1}cross-product. Apply the four roles above to every offset:36records, including9identity inputs. No values clip in this set. Report descriptor departure from known edit log-gains for all offsets, with no threshold/favorable-offset subset. A source-offset residual is a prior error, not a proven need to correct skin. Do not label these generated offsets MST/tone classes or human unwanted changes.
2. **Equal-source weighting witness:** at green0.3125(bin2), fitting sources P,Q have u=0.1and0.3respectively, both v=-0.1. P has1pixel, Q has100duplicates. Expected bin mean u=0.2,v=-0.1. Repeating Q another100times must leave the table unchanged. Separately report the ordinary pooled-pixel mean as an analytical weighting comparator, not another selected prior. All references remain generated and valid.
3. **Held-reference poison/leakage:** add an Hrecord whose pixel payload raises if accessed; table construction with fitting A/B/C must remain identical. Deliberately request H as both fitting and excluded, duplicate a fitting source, omit a fitting source and pass a distorted-role fitting reference; each must refuse before using forbidden data. No prior alternative or roster repair after failure.
4. **Missing/zero cases:** one positive pixel at G=0.8125 with R=G*exp(0.1),B=G*exp(-0.1)falls in unpopulatedbin6 and is unsupported. A second set combines this pixel, one supported k2pixel and one[0,0.3,0.2]zero-channel pixel: expected positive_fraction2/3,supported_fraction1/3, available=true. All-zero pixels and empty input return unavailable with null residuals. All-zero fitting reference must refuse. Exact green boundaries0.125and1.0 test bin1and7respectively; green0 is excluded, not incorrectly assigned a log-ratio.
5. **Gamma and quantization stress:** on H apply identity, gamma1/.7, gamma.7, red245/255, blue245/255, blue255/245 and gamma1/.7withred245/255:7roles. Produce continuous values, and separately round-to-even clippedRGB8/255:14records. Report counts, residual shifts and differences between continuous and quantized versions. Pure-gain residual expectations are NOT imposed on gamma cases because green and the conditional reference change. No classifier/gamma estimator or conversion to correction controls.
6. **Clipping stress:** one supported-bin pixel[0.99,0.6875,0.98], apply the frozen blue255/245gain, clip to[0,1], and describe before and after RGB8quantization. Compare actual residual shift to log(255/245)and disclose saturation loss. This is not in the learned reference trend, so assess DIFFERENCE of residuals relative to the same unstretched pixel, not baseline absolute residual accuracy. No skipped clipped pixels other than the fixed zero/missing rules.

## Independent checks, artifact rules and stop

Implement one table version with deterministic source-ID ordering and scalar math.fsum reductions. An independent NumPy reconstruction must verify bin assignments, per-source/bin contributions, means and descriptor residuals to absolute/relative1e-12, with exact count/provenance equality. Store source dictionaries, table, all generated probe records, signed residuals and complete counts. Table JSON roundtrip, immutable-copy use, input nonmutation, invalid schema/data, missing/null handling, no overwrite and preserved expected failure must be tested. No real reference lookup or actual-image cache is involved.

Report engineering correctness, ideal conditional-trend mechanism and prior-mismatch bias separately. An engineering failure stops this fixed design; no automatic interpolation/bin/weight/feature/penalty/topology rescue. Even ideal mechanismPASS does not qualify a photo trial. Offset probes are intended to expose residual bias, not require universal identifiability or disprove statistical priors. Equal-source weighting is not fairness; a reference corpus can still encode complexion/background bias. No new photographic roster, table fit, tree fit, user review or tone labels are selected.

The resulting table would be an extra learned preprocessing component alongside one correction tree, a substantive paper method extension. This generated design does not choose the final tree family/leaf features or resolve earlier nominal-blue human preferences. Prior baselines/closed experiments/ratings/manualears59807support remain preserved. No arrays fromdatasets/raworiginals/lockedholdouts, runtimeAndroid/manuscript changes. Modelunfinished/paperpaused/darker-skinpriority/November14complete-deliverytargetatrisk/exacttimeunspecified.
