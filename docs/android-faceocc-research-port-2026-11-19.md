# Android FaceOcc research port

The Android research runner accepts an already aligned 256 × 256 RGB image, applies the same float32 ImageNet normalization as the Python runner, and returns FaceOcc logits. The existing visibility decision is `logit > 0`. The runner verifies the ONNX file against a trusted SHA-256 digest before loading it into OpenCV DNN on the CPU.

## Verification on 19 November 2026

OpenCV 5.0.0 on an API 35 x86-64 emulator matched all 131,072 visibility decisions from two saved Python inference runs. The maximum absolute logit errors were 0.000009827316 and 0.000012397766. The inputs were previously saved aligned RGB images from the approved two-photo check. The export used a generated zero tensor and the frozen checkpoint. The reference logits came from the saved receipts.

The debug and test APKs built, all 18 JVM tests passed, and the targeted emulator instrumentation passed. All five staged files matched the local export receipt byte for byte. The private fixture was removed from the emulator after the check. The exported graph SHA-256 is `706b236065be76c0d68a67d5497a53e153debc43894aae0ce16f0fb22eebc936`.

This covers the occlusion network stage. Producing the full WB314 masks from a new Android photo still requires landmark-based alignment, reprojection, dense parsing and the research support and protection rules. The regular photo picker still uses the trial pipeline. Physical-device performance remains pending.

## Reproduce the local check

1. Use the existing FaceOcc Python environment with ONNX 1.20.1 on its import path. Run `scripts/prepare_android_faceocc_fixture.py --output-dir outputs/<new-private-directory>` with that interpreter. The converter verifies the pinned weights and validates the fixed-shape opset 13 graph. It joins the two saved aligned images and logits to their earlier inference receipts.
2. Build the debug and instrumentation APKs. Copy the five files listed in the export receipt into the debug app's private `files/faceocc_parity` directory with a binary-safe transfer. Check each digest against the receipt.
3. Run `com.example.skintonecorrection.FaceOccResearchParityTest` with the `faceOccGraphSha` instrumentation argument set to the exported graph digest. The check requires finite float32 logits, a maximum absolute error of 0.001 or less and zero visibility mismatches on each image. Read the observed errors from the private `files/faceocc_parity/result.txt` and remove the staged fixtures when finished.

The graph, images and reference arrays are local research files. The APK and repository contain the runner and test code. Reuse or distribution of the model assets depends on their separate terms.
