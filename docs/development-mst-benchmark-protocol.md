# Repeated local Python inference benchmark

28 October2026. Fixed before timing: use all20approved ten-source held inputs,
their assigned clean-leaf fold exports and the unchanged integrated development
pipeline. No new fits, model selection or feature/mask/threshold edits. Reference
photographs are not inference inputs; saved outputs are used only for parity.

Construct each of ten fold pipelines once, recording construction/hash-validation
time separately. Detector/landmark loading can be lazy and appear in warm-up.
Decode20inputs before timing. Run one warm-up per input, excluded from primary
summaries. Then run five rounds over all20inputs, with deterministic SHA256
ordering of `mst_benchmark42/round/pair_id`.100measured calls receive equal
case weight. Preserve all attempts/failures, never omit slow observations or
retry to obtain better timings. A failure invalidates a clean100success summary.

Measure external wall time around `pipeline.run` and retain internal total and
stage timings. File decoding, artifact validation/construction, image saving,
pixel-hash comparisons and reporting are outside the primary timed region.
Square resize, detection,landmarks/mask,Lab/ITA,experimentalMST,chroma features,
portable inference and correction are inside. Measurement contains detection/
mask stages; their times overlap and must not be summed as disjoint components.

Verify each warm-up and measured output,parameters,features and mask against its
saved held-source evidence. Record environment versions, OS/architecture, logical
CPU count, processor description when available and OpenCV thread setting,
without changing thread/power/system settings. Report count,mean,p50,p95,min,max
overall and clean/distorted/per-case scope. Small-sample percentiles are
descriptive,not confidence bounds. Repetitions are not independent subjects.

This is warm repeated local Windows/Python timing, not cold startup, photo decode,
end-user latency, Android performance, model quality or a passed deployment gate.
No target time or speedup is invented; retain the existing failed quality results.
Actual photographer source-review responses and final expertMOS remain pending.
