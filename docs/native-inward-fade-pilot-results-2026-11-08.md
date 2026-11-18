# Native inward-fade pilot results

8 November 2026. The fixed fade softens edges, but substantially weakens reconstruction. It is a useful diagnostic result, not an adopted pipeline change.

Applied the [fixed protocol](native-inward-fade-pilot-protocol-2026-11-08.md) to four conditions from two originals, keeping controls, masks, scoring regions and protection unchanged. Zero fits or image-model inference. A native distance-based smoothstep reduces alpha in the first two pixel layers; alpha never increases or expands support.

| Condition | RGB error before → after | CIEDE2000 before → after | Alpha jumps ≥ 0.5 before → after |
| --- | ---: | ---: | ---: |
| Development warm + overexposure | 4.23 → 12.65 | 2.99 → 5.19 | 298 → 0 |
| Later overexposure | 2.46 → 12.69 | 2.34 → 4.92 | 122 → 0 |
| Later cool + overexposure | 5.15 → 14.85 | 1.79 → 5.17 | 86 → 0 |
| Later warm + overexposure | 3.54 → 13.84 | 2.83 → 5.60 | 128 → 0 |

All four still improve RGB reconstruction over their distorted inputs, but substantially less than the previous render. The three later conditions reuse one original. Counts are not independent photos or people.

The mean change in correction residual across the existing support boundary falls from 28.45–29.76 to 7.70–7.85 RGB units. This measures local correction discontinuity, not naturalness. Viewed every board at native size and nearest-neighbour crop enlargement: edges look softer, but incomplete facial coverage and internal exclusions remain. The development face is still uneven; the later face still receives mostly forehead correction.

The earlier diagnosis counted adjacent alpha jumps within the native crop; this pilot counts the whole image, including its crop perimeter. That explains 298 versus the earlier 285 development-case count; other cases match. No baseline metric was silently replaced.

The pilot meets its narrow edge-softening criteria, including no protected-pixel changes. It does not establish a finished correction or justify integration. Reducing correction strength near many boundaries weakens recovery across much of these small, fragmented masks. The saved model's fitting costs also used the previous alpha, so this is not a validated end-to-end candidate.

**Next recommendation:** investigate the missing/fragmented correction support before extending this fade to a full replay. Do not start a width sweep or fill/dilate uncertain masks. Any mask intervention needs its own fixed protocol and protection checks. Keep this rendering candidate frozen; no full replay, model fit or app integration was started.

Independent verification used SciPy Euclidean distance transforms against the OpenCV implementation, checked all four alpha maps, exact RGB rendering, RGB/CIEDE2000 metrics, unchanged positive support, protection and bound hashes. All passed. Four boards inspected. Script 643; private output `outputs/native_inward_fade_pilot_v1`. The separate 24-photo final holdout remains byte-unread. No new annotation, dataset search or external sharing.
