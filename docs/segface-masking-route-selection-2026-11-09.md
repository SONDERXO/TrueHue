# Selected permitted masking route: SegFace MobileNet

9 November 2026. The user requested another permitted masking route after the
bounded correction cycle produced no evaluation gain. **Select SegFace MobileNet,
CelebAMask-HQ, 512 input, as the next candidate for package/readiness work.** It
is not adopted, locally loaded, or shown to improve TrueHue masks yet.

## Permission and exact artifact

The [authors' code](https://github.com/Kartik-3004/SegFace) has an explicit
[MIT licence](https://github.com/Kartik-3004/SegFace/blob/9416628e7b5a3e4b9a1068b8467bdc0cf0be7a7d/LICENSE).
The [author-owned model repository](https://huggingface.co/kartiknarayan/SegFace)
also declares `license: mit` in its model card, independently of the code
licence. This is materially clearer release evidence than the unresolved separate
DINO decoder/code terms. Retain MIT attribution/notices with any copied source
or package. No training dataset download or redistribution is implied.

Selected code revision: `9416628e7b5a3e4b9a1068b8467bdc0cf0be7a7d`.
Selected author weight:
`mobilenet_celeba_512/model_299.pt` in `kartiknarayan/SegFace`.
The [author's upload commit](https://huggingface.co/kartiknarayan/SegFace/commit/7c6077ee6b09c0ea63ac15c5b4184db52637da78)
identifies the immutable file as:

- Revision: `7c6077ee6b09c0ea63ac15c5b4184db52637da78`.
- Size: 84,928,824 bytes.
- Published SHA256:
  `4d67ea7d8c33849272b293b421fa3d20d54d9987f1bca8c1ef0eebe4534993e8`.

These are remote author metadata, **not a hash of a locally downloaded file**.
The current model card's MIT declaration was observed separately; it has not
been asserted to exist at the older weight-upload revision. Attempts to read
that revision's raw README via the web tool failed. Model/code licensing
evidence is recorded, but no legal advice or third-party-rights guarantee is
claimed.

## Why this candidate, and its limits

SegFace is an automatic semantic face parser, unlike a general prompt-based
segmenter. Its release covers skin, neck, hair and infrequent accessories such
as glasses, earrings and necklaces. The MobileNetV3-Large variant is selected
for the project's eventual mobile direction, rather than choosing a large
model and assuming it can later run on Android. Published benchmark speed or
F1 is not TrueHue accuracy, latency or an Android performance measurement.

This is a different parser/decoder architecture from the previously tested
BiSeNet ResNet18/34 models, not a rerun of that backbone-size experiment. It
provides a permitted route to test coverage/protection without waiting for
DINO's unresolved decoder terms.

**It does not provide a separate beard label, facial stubble model or separate
glasses-frame/lens labels.** It is not a verified substitute for every material
distinction originally sought. Selecting it does not waive beard/object/rim
protection, accept beard as measurement skin, or silently narrow full-face/neck
scope. If the fixed checks expose those failures, report them and reject the
candidate rather than calling licensing clearance a quality pass.

Alternatives inspected briefly: official
[SAM 2.1](https://huggingface.co/facebook/sam2.1-hiera-tiny) has documented
Apache-2.0 release terms but produces prompt-based masks, not the required
facial material labels; it would introduce a separate prompting/selection
design. The [Jonathan Dinu SegFormer parser](https://huggingface.co/jonathandinu/face-parsing)
states noncommercial research/educational use, but likewise lacks a beard label.
Neither is selected for an automatic combined-model trial or a model sweep.

## Verified source interface; not a runtime claim

The pinned CelebAMask-HQ loader converts BGR to RGB, uses PIL bicubic resizing
to 512x512, then ToTensor and ImageNet mean/std. Label resizing is nearest-neighbour.
The author evaluation upsamples output logits bilinearly with align_corners=False
before class argmax. Keep preprocessing/output ordering exact in a later adapter;
do not reuse the current parser's input or class mapping on assumption.

Its class IDs are:

| ID | Class | ID | Class |
| --- | --- | --- | --- |
| 0 | background | 10 | nose |
| 1 | neck | 11 | mouth interior |
| 2 | skin | 12 | lower lip |
| 3 | clothing | 13 | upper lip |
| 4 | left ear | 14 | hair |
| 5 | right ear | 15 | glasses |
| 6 | left brow | 16 | hat |
| 7 | right brow | 17 | earring |
| 8 | left eye | 18 | necklace |
| 9 | right eye | | |

The pinned model constructs `mobilenet_v3_large(pretrained=True).features`, which
could initiate a separate download. A later isolated loader must disable that
automatic fetch and establish that the selected checkpoint supplies every
required parameter. The author's test script expects `state_dict_backbone` and
uses strict load_state_dict by default; the actual selected package's keys,
shapes and completeness have not yet been inspected. Do not copy its unrestricted
torch.load call or use strict=False to conceal mismatch. Forward accepts image,
labels and dataset arguments, but inspected image inference does not use the
labels/dataset arguments to generate the mask.

The current project venv reports torch, torchvision and timm absent; ONNX Runtime
1.31.1 is installed. The upstream environment file targets an old Linux/CUDA
stack and is not a suitable Windows environment to install wholesale. No
dependency was installed. CPU and on-device support remain unverified.

## Next concrete step and fixed stopping rules

1. Acquire only the selected author checkpoint at the pinned revision into a
   new ignored candidate folder. Verify exact size and SHA256; preserve the
   source snapshots and both code/model permission evidence. No mirrors or
   alternate backbone downloads. This selection turn did not download weights.
2. Inspect archive/state schema with restrictive handling, then build an isolated
   compatible loader. Require complete key/shape matching, no automatic network
   fallback and exact class/preprocess checks before photo inference. No changes
   to the active parser or demo model are part of package readiness.
3. Freeze one comparison using the existing completed skin-point and six-photo
   patch references; retain failures and the original source framing/pixel
   coordinates. No repeat user annotation task or final-holdout reads.
4. Require additional reviewed skin coverage and zero newly included definite
   unwanted points, plus protected-pixel and boundary review. Report per-photo
   outcomes, neck, hair/beard and glasses limitations, not just aggregate F1.
   Do not remove protection vetoes, retune thresholds or add another model to
   rescue an unfavourable result.
5. Only after actual mask qualification consider matching new ITA/MST
   calibration, features/costs and correction training. Old mask-dependent
   calibration/adoption approvals never transfer automatically.

The selected alternative is a permitted **candidate**, not a ready or validated
replacement. The earlier readiness record's no-complete-qualified-package
finding remains accurate historically. A newly verified public release route
does not retroactively change it.

## Evidence and work performed

Pinned author source snapshots (README, licence, loader, model factory, model
definition and evaluation code) and the selection receipt are saved privately
under `outputs/segface_route_selection_v1`. Some guessed source paths returned
404 before the official directory listing resolved them; no missing-file claim
was inferred from those guesses. GitHub API/web read failures are access limits,
not evidence of absent permissions or files.

This turn performed public documentation/source inspection and local installed-
package metadata inspection only. No checkpoint or dataset download, imports
of the remote code, model execution, dependency install, private-photo read,
upload, new fit, runtime change, external contact, commit or push occurred.
The eight-group, 24-photo final holdout remains byte-unread. Existing parser,
DINO assets, failed candidates and unrelated uncommitted work are preserved.
