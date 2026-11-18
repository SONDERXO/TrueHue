# DINO face-decoder compatibility audit

8 November 2026. Source inspection only. **The downloaded backbone is structurally the right variant, but not yet connected to a verified complete face parser.** No decoder was executed or downloaded, no dependency installed and no inference performed.

## Exact feature interface

The [encoder source](https://github.com/jseobyun/FaceParsing/blob/master/src/models/encoder.py) combines VGG19-BN features with DINOv3's normalized patch tokens. The expected DINO entry is `x_norm_patchtokens`, reshaped from batch × patches × 768 to batch × 768 × H/16 × W/16. At the predictor's 512 × 512 default, that is 1,024 patch tokens and a 768 × 32 × 32 map per image. Class/register tokens must not be included. The encoder freezes DINO and also constructs pretrained VGG19-BN, which can trigger an automatic weight download if uncached.

The [decoder source](https://github.com/jseobyun/FaceParsing/blob/master/src/models/decoder.py) expects this pyramid:

| Scale | Source | Channels | Spatial size at 512 input |
| --- | --- | ---: | ---: |
| 1 | VGG19-BN | 64 | 512 × 512 |
| 2 | VGG19-BN | 128 | 256 × 256 |
| 4 | VGG19-BN | 256 | 128 × 128 |
| 8 | VGG19-BN | 512 | 64 × 64 |
| 16 | Normalized DINO patch tokens | 768 | 32 × 32 |

It fuses these into 19-class segmentation logits and probabilities. A pooled embedding or raw patch projection cannot replace the normalized patch-token feature map. This records source expectations, not numerical compatibility established by execution.

## Loading and preprocessing

The [predictor](https://github.com/jseobyun/FaceParsing/blob/master/src/face_parsing/predictor.py) loads a separate checkpoint, constructs the original local torch-hub backbone, excludes backbone entries from decoder state loading and uses `strict=False`. It preprocesses RGB at 512 with ImageNet normalization and restores class maps using nearest-neighbour resizing. Our OpenCV arrays are BGR and must be explicitly converted; passing them directly would change colours. The downloaded Hugging Face processor's default 224 size must not silently replace this contract.

For a TrueHue loader, missing/unexpected keys must be enumerated against an explicit allowlist. All CNN/decoder parameters and buffers must be present and shape-compatible; only separately supplied backbone entries may be absent. Do not accept a successful `strict=False` call as proof of a fully loaded model. Do not initialise a random backbone if loading fails. Load a verified tensor-only checkpoint using a restrictive loading mode where supported; do not enable unrestricted pickle loading to bypass an error.

## Downloaded weights: possible paths, neither verified yet

1. **Original-format route:** obtain the author-specified original backbone through the approved official access route. Its state schema should match the parser's original DINO implementation; validate rather than assuming.
2. **Hugging Face adapter/conversion route:** explicitly map the downloaded weights or implement the same normalized patch-feature interface. Validate complete key/shape coverage, token ordering, final normalization, positional-encoding settings and numerical feature parity against a trusted implementation before using decoder outputs.

Do not rename `model.safetensors` to `.pth`. No conversion or adapter was implemented in this audit. The current venv lacks torch, torchvision, Lightning, torchmetrics, Transformers and safetensors distributions. The author's [requirements](https://github.com/jseobyun/FaceParsing/blob/master/requirements.txt) include training/visualization dependencies too; do not install that entire list blindly. A later approved setup should isolate and pin the inference dependencies and prevent automatic downloads.

## Decoder access and terms

The [README](https://github.com/jseobyun/FaceParsing) links `decoder.ckpt` on Google Drive and says it includes the trained CNN and decoder. This audit has not verified the actual checkpoint contents, size, digest, availability or training provenance. Backbone approval does not supply that file.

The README licence section addresses DINOv3 weights, but does not clearly state separate code/decoder reuse permission. A request for a conventional root `LICENSE` returned 404; this is not proof that no permission statement exists elsewhere. No legal clearance or compatibility claim is inferred from public visibility. No author contact or terms acceptance occurred.

## Concrete next prerequisite

Before inference, obtain a clear code/decoder research-use statement and a complete original decoder package from the author-linked source, then hash and inspect its tensor schema without executing its code. The model download alone is insufficient. If permission remains ambiguous, prepare a specific permission request for review; do not send it without explicit instruction.

After that, establish one verified backbone-loading route and freeze the existing-reference masking comparison. Keep the current masks, correction controls, app and final 24-photo holdout unchanged. DINO is a masking candidate, not an adopted correction model.

## Inspection limits

Public source pages were read on the date above; they were not vendored, pinned to a newly verified commit, imported or executed. Some raw file requests were unavailable. File contents and dependencies must be pinned before implementation. No tests of runtime or feature equivalence are claimed by this documentation audit.
