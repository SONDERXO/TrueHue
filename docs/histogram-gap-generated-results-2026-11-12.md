# Histogram-gap descriptor: generated robustness results

12 November 2026. **Engineering verification passed; limited signal, not a qualified real-data fit.** One own six-feature full-frame descriptor was specified before implementation. No author-code reproduction, alternate bands, learned thresholds or post-result feature changes.

Features are internal empty-code fractions for low0?127/high128?255bands in each RGBchannel, restricted to observed min/max. Empty bands and constant channels are defined explicitly. No minimum pixel count or brightness correction gate. Diagnostics are separate from the six features. Measurement, ITA/MST, approved ear support and renderer remain unchanged; the experimental module is not connected to inference.

Seven generated unit tests passed in.69seconds.224frozen generated probes cover7palettes x8roles x4processing conditions. All1344feature values independently match Python set/Fraction computations. Tests cover hand counts/RGBorder, constant/empty/type handling, unchanged inputs and duplicate-pixel support invariance. No scientific source or image is used.

| Generated processing change | Cases with changed descriptors /56 | Largest sum of absolute six-feature changes |
|---|---:|---:|
| JPEGquality90 |38/56|2.051925|
|256->128AREA->256LINEAR|31/56|3.029364|
|Every16throw/column sample|48/56|5.600111|

These are feature sensitivity counts, not correction harm rates or a new acceptance threshold. Changes do not automatically imply failure; exact invariance is not required. Native full-ramp gamma under has low/high gaps .03125/.2265625perchannel, versus over .2578125/0. Full-ramp identity/cool/warm all have zero internal gaps: uniform attenuation removes range endpoints rather than internal codes, so this descriptor alone supplies no colour-gain correction signal there. Existing facial/chromatic inputs could still provide complementary information; this result does not test that combination.

Sparse original palettes have large gaps without requiring correction. More decisively, the already-gamma-edited ACCEPTABLE source's identity descriptor exactly equals the full-ramp overexposure descriptor. Underexposure of that already-edited source, after the fixed resizing probe, has all-zero gaps and matches the full native identity descriptor. Nine multi-role collision groups were recorded across the fixed conditions, including constant-palette degeneracies. These generated ambiguities do not prove actual feature conflicts on photos, impossibility of tree correction or a need for physical calibration. They demonstrate why quantization signatures cannot be treated as a runtime exposure label.

## Decision and paper alignment

The engineering code is correct for its frozen definition and contains some added-edit information on synthetic ramps. It has not shown source transfer or practical exposure/colour restoration. No real-data fit is justified from these checks alone. No automatic quality/band/channel/count/smoothing/descriptor-grid rescue follows. Do not require perfect identifiability, but do not turn detection of our generation pipeline into a real-world correction claim.

If pursued, the next bounded step would be to SPECIFY one input-only audit on the already exposed caches using exactly these frozen six features. It would check whether the actual inputs contain the same basic signal, source-related confounds and identity/cool overlap, with no tree fit, learned cutoff, old-candidate rescoring, changed feature settings or new review. This report does not select or execute that extraction. The paper's target remains synthetic-original photographic restoration; camera-response linearization is not substituted. Full declared distortion/tone/independent/MOS/Android evidence remains separate and unfinished.

Artifacts: histogram-gap-generated-protocol-2026-11-12.md, src/model_training/histogram_gap_features.py, tests/test_histogram_gap_features.py, script859 and outputs/histogram_gap_generated_robustness_v1. Source hashes verified unchanged. All generated rows excluded from science. Zero dataset/cache/photo/mask/final24/olderlocked bytes, real fits/predictions/runtimeAndroidchanges. Old failures stay closed, approved ear integration retained, model-first/paperpaused/traditionaltree/ITA/MST/singlephoto/manual/neckscope unchanged.
