# Repeated local Python inference benchmark

28 October2026. Completed the
[frozen benchmark protocol](development-mst-benchmark-protocol.md) on the unchanged
explicit MST development pipeline. Used all20approved held-source inputs and
their prescribed clean-leaf fold exports; no new fitting, feature/mask changes,
source selection or active model replacement.

Constructed ten fold pipelines and decoded input images before timing. Ran one
warm-up per input, excluded from primary summaries, followed by five deterministic
case-shuffled rounds:100measured calls, each of20inputs weighted equally. Every
one of120calls reproduced saved parameters,9features,masks and corrected-pixel
hashes. No failure,slow-call removal or timing-driven rerun occurred.

External elapsed time around`pipeline.run`, milliseconds:

| Input scope | Measured calls | Mean | Median | p95 | Minimum | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All | 100 | 63.42 | 61.63 | 75.52 | 55.06 | 84.59 |
| Unchanged | 50 | 63.26 | 61.53 | 75.62 | 55.06 | 79.37 |
| Distorted | 50 | 63.59 | 61.78 | 73.44 | 57.21 | 84.59 |

Includes square resize, detection, landmarks/skin masking, Lab/ITA, experimental
MST, chroma features, portable-tree prediction and correction. Excludes file
decoding, pipeline construction/artifact validation, PNG saving, parity checks
and report writing. Construction and20warm-up timings remain in the raw ledger.
Lazy detector/landmarker loading can occur during warm-up; construction time is
not a complete cold-start estimate.

These are warm sequential observations on this Windows/Python environment, not
Android/device timing or full end-user latency. The environment record preserves
processor/OS/architecture, logicalCPUcount, Python/dependency versions and OpenCV
thread count without changing system settings. The five repetitions of an input
are not five independent people; p95is descriptive, not a confidence bound.
Measurement-stage timing includes nested detection and mask timings and must
not be added to those child times. Do not infer frames-per-second application
performance from post-capture pipeline wall time.

Script187records all120attempts, per-input results and stage timings in JSON and
CSV. Script188independently checks20warm-ups/100measuredcalls, exact deterministic
order and repetition balance,23summarysets using separate sorted-quantile/sum
arithmetic, timing sanity, CSV/JSONL consistency and original hashes. Checks pass.
No shared algorithm module changed; latest full suite remains701passed from
pipeline integration, rather than a new full-suite claim.

This completes a reproducible **local development timing** result, not correction
quality validation. The strict clean gate still fails, all ten nested safety
checks reject correction, and light-distortion stress means remain problematic.
No active model or Android asset changed. Photographer source-suitability
responses are still uncollected; final expertMOS,finalreference/data validation,
neck support and Android correction integration remain unfinished. Android stays
paused; CPM deferred.

- [Frozen timing plan and environment](../outputs/development_mst_benchmark_v1/plan.json)
- [Full summaries and stage measurements](../outputs/development_mst_benchmark_v1/summary.json)
- [All timing records](../outputs/development_mst_benchmark_v1/timings.csv)
- [Independent timing verification](../outputs/development_mst_benchmark_v1/verification.json)
