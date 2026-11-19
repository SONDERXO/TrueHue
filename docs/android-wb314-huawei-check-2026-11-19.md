# WB314 on Huawei nova 7i

The local TrueHue research build ran on a Huawei nova 7i with Android 10, API 29 and arm64-v8a. The debug APK installed and launched, and all eight local WB314 assets passed their checksum checks. The app completed original-size export. The phone failed the exact Python parity requirement.

| Saved fixture | PNG size | Output pixel differences from Python | Pixels changed outside Python support or in its protected area |
| --- | --- | ---: | ---: |
| Adjusted, camera-sized replica | 3072 × 4096 | 8,995 | 768 |
| Same adjusted image at emulator fixture size | 512 × 768 | 282 | 24 |
| Identity fixture | 512 × 768 | 0 | 0 |

The adjusted case selected the same tree leaf and controls at both sizes. Six support pixels differed at 256 × 256 in both runs. The smaller adjusted run changed zero pixels outside the phone's own selected support. That does not satisfy preservation against the Python reference. The camera-sized copy used integer replication of the saved development input, with no additional source photo or Python model inference.

The stage comparison on the same two normalized inputs matched both detector boxes and every parser category. The adjusted case differed in FaceOcc visibility on seven analysis pixels. This propagated to six measurement, protection and application-support differences. The identity case matched FaceOcc and application masks but differed by one baseline and one final measurement pixel.

## Landmark isolation

The follow-up reused the same two normalized inputs and their saved Python landmarks, aligned RGB, logits and reprojected masks. With saved landmarks, both Huawei visibility masks matched Python. With saved aligned RGB, every logit sign matched across 131,072 aligned pixels. Reprojecting saved logits with the saved matrix and with the Huawei matrix calculated from saved landmarks also gave exact masks in both cases.

Using live Huawei landmarks changed the adjusted case's aligned RGB by 12,434 channel values and its visibility mask by seven pixels. The largest landmark displacement was 0.01272 pixels on the analysis frame. Replacing only that run's reprojection matrix with the saved Python matrix still left seven differences. The identity case had 0.000411 pixels of maximum landmark displacement and no visibility differences. These comparisons establish the live landmark coordinates as the upstream source of the adjusted-case visibility discrepancy. The reason the landmark runtimes differ, and the identity case's separate one-pixel measurement difference, remain unverified.

The 3072 × 4096 run completed without an out-of-memory error, with post-processing PSS of 436,377 KiB. Its app elapsed time of about 120 seconds included a period when the operating system suspended the background test process. The process resumed after the app was brought to the foreground. In the smaller foreground runs, the reported processing times were 4.64 seconds for the first case and 1.15 seconds for the second. These timings describe the observed runs and do not qualify full-size latency or establish peak memory use.

The strict comparison remains failed. The emulator result is still valid on its two fixtures. The frozen WB314 model and expert-feedback materials were held fixed. Device and fixture logs remain local. [Emulator comparison](android-wb314-picker-2026-11-19.md)
