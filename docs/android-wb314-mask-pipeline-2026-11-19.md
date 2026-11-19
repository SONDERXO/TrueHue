# Android WB314 research masks

The Android research mask generator takes the area-normalized 256 × 256 BGR analysis image and runs the pinned YuNet detector, MediaPipe landmarker, dense face parser and FaceOcc. It applies the Python rules for facial measurement, face and neck correction support, object and occlusion vetoes, explicit glasses handling, associated ear coverage and inward feathering.

The generator requires one face and sufficient facial measurement support. If the parser detects glasses and the choice is uncertain, it requires an explicit clear or opaque designation. It produces a binary measurement mask, application alpha and a separate protection mask. Protected pixels must have zero application alpha.

## Verification on 19 November 2026

The API 35 x86-64 emulator started from both saved normalized images and detected the face boxes itself. Both boxes matched Python. Across 131,072 pixels, every parser category, FaceOcc visibility value, baseline and final measurement value, protection value, correction-support decision and alpha value matched its saved Python counterpart. All protected pixels had zero application alpha.

Both APKs built after adapting the distance-transform constant for the Android OpenCV bindings. All 18 JVM tests and five emulator tests passed, including four existing picker regressions. All six fixture files were checked by SHA-256 after staging. This establishes parity on the two saved inputs. It does not measure mask accuracy on new photos.

## Reproduce the local comparison

1. Run `scripts/prepare_android_wb314_mask_fixture.py --output-dir outputs/<new-private-directory>` with the main Python environment. The script verifies the saved reference hashes and packs both analysis images and their expected intermediates. It uses neither new source photos nor new Python model predictions.
2. Install the app and instrumentation APKs. Using a binary-safe transfer, stage the two fixture files, `yunet.onnx`, `parser.onnx`, `faceocc.onnx` and `template.bin` in the debug app's private `files/wb314_masks` directory. The parser is the project's pinned `resnet18.onnx` and the template is the 120-byte reduced template from the geometry fixture. Check the staged digests before running the test. [FaceOcc export](android-faceocc-research-port-2026-11-19.md) · [Template fixture](android-faceocc-geometry-2026-11-19.md)
3. Run `Wb314ResearchMaskParityTest` with the `faceOccGraphSha` argument set to the trusted graph digest. Capture the per-stage differences in the private `files/wb314_masks/result.txt`. Remove the staged private files after verification.

The research generator is separate from the regular picker. Picker integration, full-resolution WB314 rendering with generated masks and physical-phone checks remain separate milestones. Keep the graphs, templates, photos and fixtures local.
