# Material-model feasibility: CPM pattern branch

27 October 2026. Investigated a material-supervised lead after the
[reference-quality checkpoint](material-protection-design-checkpoint.md).
**No image inference, candidate masks, training-pair regeneration or model fitting.**
The checkpoint is available locally for further static/portability work; it is
not adopted or ready for an image-level protection experiment.

## Focused source comparison

| Source inspected | Relevant supervision/task | Decision for this investigation |
| --- | --- | --- |
| [CelebAMask-HQ](https://mmlab.ie.cuhk.edu.hk/projects/CelebA/CelebAMask_HQ.html) | Facial components/accessories, including skin;19classes | No explicit paint/material class in its listed taxonomy; another parser alone would not establish protection |
| [MicroGlam](https://github.com/tobyclh/MicroGlam) | Microscopic skin patches under cosmetic products/lighting | Material-specific acquisition, but a different image domain from ordinary portraits; no direct portrait-veto candidate selected |
| [CPM pattern branch](https://github.com/VinAIResearch/CPM/tree/main/Pattern) | Synthetic makeup-pattern segmentation | Most directly relevant of these inspected leads; investigate input/output and portability before evaluation |

This is a bounded source screen, not an exhaustive claim that no suitable model
exists. MicroGlam documents45small patches from9participants and research-use
terms; it does not establish portrait paint localization for TrueHue. The
CelebAMask-HQ site documents anatomical annotations and noncommercial research
restrictions. No external dataset/sample portrait was downloaded or viewed.

## Exact provenance and observed checkpoint

CPM repository revision:`101b1ff6a4275b6da434ca5658533eb232d57fa8`.
Fourteen source/document/license files were fetched at that revision through
the GitHub connector and saved as ignored text snapshots in
`outputs/cpm_pattern_preflight_v1/source/`. Source URLs and local paths are in
`source_manifest.json`; hashes are in the preflight summary.

The author links a separate [pattern checkpoint](https://drive.google.com/file/d/1ciy8INrxMQufDodT4a89KxrpZn4le4ud/view)
from the [repository README](https://github.com/VinAIResearch/CPM/blob/101b1ff6a4275b6da434ca5658533eb232d57fa8/README.md).
Downloaded only that file, under the declared256MiB bound:

- Local:`models/cpm_pattern_experimental_v1/pattern.pth`(gitignored).
- Bytes:`130433505`(130.43MB decimal;124.39MiB).
- SHA256:`27421250269552f61a6c52581a73baf50cb3f4dee88c8403d87943b53a9ebfec`.
- Hash computed locally; no independent publisher checksum was available in
  the inspected source. Do not call it publisher-verified.

The [predeclared protocol](cpm-material-preflight-protocol.md) preceded download.
The first sandbox attempt could not open a network socket; the network-enabled
retry succeeded. No raw dataset was uploaded/downloaded and no dependencies
were installed. The current environment is Python3.14; torch, torchvision,
TensorFlow, ONNX and segmentation-models-pytorch are absent.

Script110initially checked bounded ZIP metadata and correctly retained the
non-ZIP limitation. Following that format discovery, script111performs a static
legacy-format follow-up: reads at most16MiB, scans five metadata pickle streams
with pickletools and stops at byte125125. The remaining130308380bytes are opaque
storage data and are not interpreted as tensors. The initial report remains
unchanged beside `legacy_metadata.json`.

The header magic/version agree with [PyTorch1.6legacy serialization source](https://github.com/pytorch/pytorch/blob/v1.6.0/torch/serialization.py).
Serialized GLOBAL names include Unet, ResNetEncoder, UnetDecoder and Sigmoid,
consistent with the author's wrapper/defaults. These strings are evidence of
serialization structure, not executed architecture, label calibration or model
accuracy. No pickle.load, torch.load, class import, tensor materialization,
archive extraction or external source execution occurred.

## Input/output contract discoveries

1. **UV domain matters.** The [main entry point](https://github.com/VinAIResearch/CPM/blob/101b1ff6a4275b6da434ca5658533eb232d57fa8/main.py)
   obtains source/reference texture maps with PRNet, then passes a reference
   texture to get_mask. The [makeup wrapper](https://github.com/VinAIResearch/CPM/blob/101b1ff6a4275b6da434ca5658533eb232d57fa8/makeup.py)
   maps256face images into that domain. Resizing a native portrait and treating
   its output as a native mask would silently change the domain. A UV map must
   be mapped back through valid visible geometry; missing/self-occluded support
   must remain unavailable rather than being filled as skin.
2. **Training and transfer preprocessing differ.** The
   [training data loader](https://github.com/VinAIResearch/CPM/blob/101b1ff6a4275b6da434ca5658533eb232d57fa8/Pattern/dataloader.py)
   reads the mask's green channel divided by255, rather than a19class anatomy
   map. [Pattern preprocessing](https://github.com/VinAIResearch/CPM/blob/101b1ff6a4275b6da434ca5658533eb232d57fa8/Pattern/utils.py)
   applies an encoder preprocessing function. Transfer get_mask instead scales
   by255 and transposes. We have not established which contract reproduces the
   published checkpoint's intended behavior; no convenient one is selected.
3. **Cutoffs are task-specific.** main.py uses0.0001for pattern-only transfer and
   0.001for combined transfer; training metrics use0.5. These are source-code
   observations, not three candidate settings to sweep or calibrated TrueHue
   protection thresholds. No material veto cutoff is selected here.
4. **Portability is unresolved.** The wrapper uses U-Net/ResNet50, one output
   and sigmoid, while loading a serialized Python model. Its documented stack
   includes Python3.7, torch1.6 and TensorFlow-GPU1.14; serialized source paths
   mention Python3.8. These are distinct pieces of evidence. No claim is made
   that source defaults exactly reconstruct every checkpoint setting. The
   current environment and Android cannot directly use this artifact as an
   ONNX model. No conversion, CPU parity, memory or latency test has run.

The source describes CPM-Synt-1 as synthetic pattern examples with masks; that
does not establish supervision for arbitrary real paint, foundation, skin-like
cosmetics, visible marks or all lighting. The [dataset documentation](https://github.com/VinAIResearch/CPM/blob/101b1ff6a4275b6da434ca5658533eb232d57fa8/about-data.md)
limits use/distribution separately from the repository's BSD3-Clause software
license. No checkpoint/data redistribution or Android rights clearance is
inferred solely from the code license.

## Concrete next experiment and gates

Proceed with **isolated portability and input-contract reproduction**, before
image-quality evaluation:

1. Reconstruct/export only the pattern network in a separate compatible local
   environment using a validated conversion method. Preserve the main venv and
   raw checkpoint; record every package, artifact hash and conversion step.
   Existing unsafe full-object loading examples are not copied into TrueHue.
   A converted artifact needs its own provenance and source/config checks.
2. Establish the intended UV preprocessing/geometry from source and a
   reproducible reference implementation. Compare reference/export outputs
   first on deterministic non-study numeric tensors. Failures stay explicit;
   do not pick a normalization by whichever looks better on16798.
3. Declare native-coordinate restoration, visibility/invalid-pixel handling,
   selected-person identity and the prospective cutoff before study inference.
   This isolated feasibility work must not choose a cutoff using label overlap.
4. Complete the material-reference adjudication/coverage prerequisites in the
   [checkpoint](material-protection-design-checkpoint.md) before treating image
   results as material accuracy. The existing17frames remain exposed diagnostics.
   No new source exposure or external dataset download follows automatically.
5. Only after those gates, freeze an image-level removal-only veto alongside
   the current anatomical candidate at source generation, actual-input
   measurement and correction. Score all protected/ordinary-skin references,
   uncertainty, missing cases and historical regressions. Do not use a generated
   bare-face image as a true color target or replace the correction tree with
   makeup transfer.

This specifies the next experiment; it does not report those steps as completed.
Technical/reference holds and every original user review/fold remain. A relevant
model lead and a downloaded checkpoint do not satisfy protection readiness.

## Verification and thesis distinction

Ten offline tests cover static inspection without executing REDUCE, invalid
headers/truncation, duplicate/missing ZIP metadata, bounded downloads and
preserving existing partial files. The full suite result is recorded with the
preflight verification: **491tests passed in16.98s**, including10new offline
tests, with a fresh workspace basetemp. Input snapshots, checkpoint and previous reference/
review/ledger artifacts are hashed; no production pipeline code changed.

This would be another learned material model, UV geometry and conversion runtime
beyond the proposed rule-based masking stage. Model-task relevance is not final
accuracy, calibrated skin truth, formal proposal approval or phone feasibility.
No application-user annotation step is added. Neck, operational MST, final data/
splits/reference/evaluation, expert MOS and Android remain unfinished.
