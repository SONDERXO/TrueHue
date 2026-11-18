# One dependency compatibility adjustment

The first isolated wheel preparation stopped before installation/model construction/portrait inference: author's safetensors0.4.5 has no compatible CPython3.13Windows binary. Original helper, two downloaded wheels and `outputs/fiqa_tiny_runtime_v1/download_failure.json` remain unchanged. No scientific outcome, core-package change or unsafe checkpoint load occurred.

One compatibility-only revision uses safetensors0.5.3, preserving timm1.0.9/all other pins, detector checkpoint, architecture, preprocessing, class/threshold/acceptance rules and existing torch environment. PyPI-compatible binary selection and publisher SHA verification remain; no source build. Use a fresh `outputs/fiqa_tiny_runtime_v2` overlay. Both attempts combined remain under16MiBwheel transfer. This checkpoint uses .pth/torch weights-only, not a new safetensors model format. Stop rather than create a dependency/version search queue if this bounded adjustment fails.
