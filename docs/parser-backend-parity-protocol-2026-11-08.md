# Fixed parser backend comparison

User approved 8 November 2026. Compare OpenCV CPU and ONNXRuntime CPU on exactly the four saved fragmented-input conditions listed in `outputs/fragmented_correction_support_trace_v1/trace_PRIVATE.json`. Use the pinned ResNet18 ONNX, the same existing preprocessing tensor and named primary `output`. Exactly four forwards per backend, eight total; no transforms, retries with different settings, fitting or holdout access.

Save both logits and category maps privately. Report maximum/mean absolute logit differences, argmax agreement at 512 and restored 256 resolution, and parity with cached categories. Finite correct shapes are required. Report actual disagreement without treating a tolerance as mask accuracy. No new correction masks or app changes; do not adopt either backend automatically. No data leaves the machine. Installing the missing ONNXRuntime dependency in the project venv supports this explicitly approved comparison.
