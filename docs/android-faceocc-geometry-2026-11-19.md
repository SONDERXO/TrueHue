# Android FaceOcc alignment and reprojection

Android now has a research path from whole-frame MediaPipe landmarks to a FaceOcc visibility mask in the original analysis coordinates. It uses the same five anchors, FaceOcc template, reflected border and border blur as the Python research path. The reprojection excludes model predictions on alignment padding and samples the binary visibility mask with nearest-neighbour interpolation.

The app and research check share the existing MediaPipe detection code. The regular picker still selects its trial mask and correction model. The dense face parser and the research application, measurement and protection rules are still needed before enabling WB314 through the picker. Physical-device testing is still pending.

## Verification on 19 November 2026

On the API 35 x86-64 emulator, both transforms matched the saved Python reference within `1e-8`. Android MediaPipe returned the same landmark coordinates when given the two saved detector boxes. Both routes, saved landmarks and Android landmarks, produced exact visibility masks on both images. Each route compared 131,072 mask pixels with Python.

The first aligned image matched byte for byte. In the second image, two of 196,608 RGB channel values differed by one code level. The initial exact-RGB check therefore failed. The follow-up measured RGB drift separately and required exact visibility masks. This demonstrates mask parity for these two inputs. End-to-end equality on new photos still requires Android detector and mask pipeline verification.

The debug and test APKs built, 18 JVM tests and four existing emulator regression tests passed, and the focused visibility-mask test passed. The four staged fixture files were verified by SHA-256. The FaceOcc graph, template and saved photo references remain local.

## Reproduce the emulator check

Run `scripts/prepare_android_faceocc_geometry_fixture.py --output-dir outputs/<new-private-directory>` with the main Python environment. It checks the pinned template and saved artifact digests, then uses the two saved normalized analysis images, landmarks, Python-aligned images and reprojected visibility masks. It does not rerun Python inference or read the original photos.

Stage the three binaries in the fixture receipt and the previously verified FaceOcc graph under the debug app's private `files/faceocc_geometry` directory. Check all four device digests, then run `FaceOccGeometryParityTest` with the `faceOccGraphSha` instrumentation argument. The test requires the saved-landmark transform to agree within `1e-8` and the reprojected visibility masks to agree exactly, both with saved landmarks and with Android landmarks detected using the saved face boxes. The report records aligned RGB differences and landmark drift. Keep the fixtures and the graph local. [FaceOcc graph verification](android-faceocc-research-port-2026-11-19.md)
