# WB314 colour-cast training trial

The [fixed training protocol](wb314-colour-cast-training-protocol-2026-11-24.md) tested whether broader colour examples help the model correct casts while preserving photos that already look right. The original synthetic recipe used one cool cast at a fixed strength for all colour conditions. The trial added weaker cool, warm, green and magenta variants of the same 11 exposed development portraits. The four additions and the original colour-only case shared the original colour-only fitting weight. All exposure and identity rows kept their previous fitting weights.

The trial compared the two recipes on the same held inputs, excluding all variants of each held portrait from its model fit. It kept the five controls, features, masks and renderer. Each synthetic variant came from a processed photo with an available reference. The UT Austin portraits diagnosed the issue and did not enter fitting or scoring.

## Results

Each row covers 11 held portraits. Values are mean absolute RGB error in 8-bit code levels followed by mean CIEDE2000. Lower values are closer to the source photograph within application support.

| Condition | Uncorrected input | Earlier recipe | Cast-augmented recipe |
| --- | ---: | ---: | ---: |
| Clean original | 0.00 / 0.00 | 3.73 / 1.47 | 6.49 / 2.45 |
| Original cool cast | 6.56 / 4.88 | 2.48 / 0.90 | 4.18 / 2.23 |
| Underexposure | 20.41 / 6.83 | 11.25 / 4.55 | 4.50 / 2.28 |
| Overexposure | 23.05 / 7.27 | 1.60 / 0.81 | 1.60 / 0.81 |
| Underexposure and cool cast | 21.50 / 9.30 | 7.57 / 3.74 | 8.67 / 4.41 |
| Overexposure and cool cast | 21.95 / 7.60 | 1.25 / 0.54 | 1.25 / 0.54 |
| Added weaker cool cast | 3.26 / 2.35 | 5.05 / 2.71 | 6.86 / 3.41 |
| Added warm cast | 6.41 / 4.20 | 9.74 / 5.10 | 0.40 / 0.31 |
| Added green cast | 4.47 / 4.27 | 10.30 / 5.93 | 9.11 / 5.34 |
| Added magenta cast | 4.18 / 3.52 | 10.11 / 5.45 | 6.81 / 4.63 |

The candidate passed 8 of 21 checks and was rejected. It improved both errors against input on 11 warm, 8 weaker cool, 4 green and 1 magenta case out of 11 per condition. The weaker cool condition still had higher mean errors than either the previous model or the uncorrected inputs. The candidate modified all 11 clean originals, compared with 2 of 11 under the earlier source-held recipe. It also increased cases worse than input on the original cool, underexposure and combined-under conditions in at least one metric. Average underexposure errors improved, with one new case worse than input in CIEDE2000. The two overexposure conditions kept their prior mean errors and zero worse-than-input cases.

The colour variants had 13,825 clipped channel samples for weaker cool, 28,427 for warm, zero for green and 39,195 for magenta, summed over each condition's 11 generated views. Clipping discards some reference information. The four counts are channel samples, with repeated source portraits across conditions.

Four generated recipe checks matched independent scalar arithmetic. A generated preservation test confirmed that an added clean-photo edit rejects an otherwise eligible result. Eleven source-held fits passed portable route and weighted leaf checks. Predictions were saved before rendering, all 220 renders matched the scalar calculation and preserved protected and outside-support pixels, and all 12 comparator metrics on the original conditions matched their prior aggregates. The expert model hash matched before and after the trial. No final fit or app deployment was performed.

This is development evidence that examples of a missing cast can help the model learn that specific cast, with a substantial cost to deciding when to leave a photo alone. The candidate remains rejected. Natural-photo cast correction and the miss on the UT Austin portrait remain unresolved. A later training round would need paired phone photos with a cast and a matched reference, plus clean phone photos from separate subjects to check whether unnecessary edits increase.
