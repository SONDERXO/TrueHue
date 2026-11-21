# Huawei FaceOcc boundary protection

The existing Huawei test found pixels changed outside the Python application support on a 3072 × 4096 replica of one development photo. The app respected its own support. The earlier trace connected the disagreement to subpixel landmark drift changing the aligned FaceOcc input.

A live trace on the same adjusted fixture reproduced seven binary visibility differences. Four points vetoed by the research visibility mask crossed above zero on the Huawei. Their positive logits ranged from 0.00218 to 0.02089. The new application preview uses a fixed visibility margin of 1/32, the next binary fraction above the largest observed positive value. It keeps the original zero cutoff for facial measurement and uses the existing protection, glasses and feathering rules. Both visibility decisions come from one FaceOcc inference.

The focused check uses the saved original-size adjusted fixture, a saved identity fixture and the previously approved 3000 × 4000 brightness portrait. It checks original dimensions, exact raw controls, identity preservation, and zero changes outside both the device support and the original research support. The brightness preview is tested on the approved portrait. The exact-mask comparison remains a separate requirement from preservation against the original research mask.

The debug APKs built and all 18 JVM tests passed. The Huawei instrumentation passed all three checks with live masks.

| Fixture | Changes outside the original research support | Application-support differences at analysis size |
| --- | ---: | ---: |
| Adjusted, 3072 × 4096 | 0, down from 768 in the earlier run | 4 |
| Identity, 512 × 768 | 0, with the full output identical to its input | 1 |
| Brightness portrait, 3000 × 4000 | 0 | 3 |

All three cases retained their original dimensions and raw controls. The brightness portrait kept the exact effective controls and 213 newly clipped pixels observed in the approved preview. The new boundary changed 3,483 of 12 million pixels relative to that preview, by at most six RGB code levels. The earlier exact-match report still applies to the old preview version.

This check resolves the observed preservation leak on the adjusted fixture. Exact mask parity remains open and the boundary rule stays opt-in in the Android research pipeline. The temporary phone fixtures were removed and the previous APKs were restored and verified by checksum. The photo picker and expert round use their existing versions.
