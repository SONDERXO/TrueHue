# SegFace loader and fixed mask screen — 9 November 2026

The user authorised continuing until input was needed. The isolated loader
passes, and the single six-photo screen is complete. **SegFace improves visible
skin coverage substantially but includes four newly unwanted hair/beard points.
It fails the fixed protection requirement and is not adopted.** No correction
fit, runtime integration or final-holdout read occurred.

## Loader readiness completed

Reused the existing `outputs/faceocc_inference_env_v1` CPU runtime in a separate
process; no environment installation or modification was needed. Observed torch
2.15.0+cpu, torchvision 0.29.2+cpu, NumPy 2.5.4 and Pillow 13.0.0. The main
project venv and active demo were unchanged.

Pinned source dependencies were staged separately. The only model-constructor
change is `mobilenet_v3_large(pretrained=True)` to `weights=None`; minimal package
initializers avoid imports of unrelated models. The Meta copyright notice in
the transformer source is retained, with the official SAM Apache-2.0 licence
alongside the SegFace MIT notice. No external source module was fetched at
runtime, and the loader blocked network calls.

All 431 checkpoint state entries exactly match the constructed model's keys,
shapes and dtypes. Strict loading with `weights_only=True` on CPU reports zero
missing/unexpected keys. The model has 7,035,824 parameter elements. This is a
successful restrictive load, not an unrestricted-pickle safety certification.

Two synthetic forwards give finite, bit-identical output of shape
1x19x512x512. Independent PIL/RGB/ImageNet preprocessing equals the author-style
torchvision transform exactly on an artificial image. All nineteen synthetic
output channel IDs and softmax/argmax parity pass. No private photo was read
by these loader checks. Script 695 and its source/weight/environment receipt
are saved in `outputs/segface_loader_check_v1`.

## Fixed private screen

The [protocol](segface-fixed-mask-comparison-protocol-2026-11-09.md) was written
before photo inference. Exactly five new SegFace forwards use the current saved
normalized inputs for the six previously reviewed photos. Review_06 retains
its landmark failure with no forward. No detector, landmark or FaceOcc forward,
new annotation, preprocessing variant, backbone sweep or mask tuning ran.

Class IDs were mapped to the current parser schema. All existing landmarks,
anatomical/nostril exclusions, 1,000-pixel guard, cached raw visibility and native
projection were retained. Original pixels supply Lab/ITA. This is a facial
measurement-mask screen, not a validation of the broader correction support.

Procedural detail: before private inference, the remap assertion checked its
length/bijectivity and three critical skin/nose/glasses entries; all nineteen
entries were independently matched by class name afterward. Thus full pre-run
mapping assertion coverage fell short of the protocol's stated timing, even
though the saved mapping was confirmed correct. No extra private forward was
run to conceal or repair that verification-order deviation.

| Fixed measure | Current raw baseline | SegFace |
| --- | ---: | ---: |
| Usable measurements, all six attempts | 3 | 5 |
| Skin points selected, same five diagnostic cases / 113 points | 39 | 74 |
| Unwanted points selected, same five cases / 94 points | 3 | 7 |
| Diagnostic marked-patch pixels | 687 | 1,417 |
| Marked pixels in usable measurements, all 3,156 marked pixels | 653 | 1,417 |

| Photo | Diagnostic patch pixels, baseline → candidate | Skin points, baseline → candidate | Technical outcome |
| --- | ---: | ---: | --- |
| review_01 | 21 → 208 | 1 → 9 | failed → usable |
| review_02 | 129 → 296 | 7 → 16 | usable → usable |
| review_03 | 13 → 181 | 0 → 9 | failed → usable |
| review_04 | 48 → 266 | 3 → 12 | usable → usable |
| review_05 | 476 → 466 | 28 → 28 | usable → usable |
| review_06 | unavailable | unavailable | landmark failure retained |

On the three jointly usable cases, the same 79 skin/55 unwanted points change
38→56 skin and 3→4 unwanted. This differs from total usable coverage (38→74 skin,
3→7 unwanted) because two formerly failed measurements become usable. Failed
photos are not successful exclusions. The positive patches include some neck;
they are not dense facial ground truth and unmarked pixels are not negatives.

## Protection failure

Four previously excluded reviewed hair/beard points become selected: one in
review_02 and three in review_03. None falls in the previously documented
point/polygon conflicts. Zero-new-unwanted and conflict-aware definite-unwanted
requirements both fail. All previously usable measurements are retained and
coverage requirements pass, but those gains do not override protection failure.

The review labels combine hair and beard; they do not establish a dense beard
mask or a beard-only accuracy score. The selected SegFace checkpoint has no
separate beard class. Existing generic object points cannot certify glasses
frames/rims or transparent-lens behaviour. No workaround or newly tuned veto
was added after seeing these outputs.

## Independent replay and review

Script 698 independently decoded saved raw logits, checked all nineteen class
mappings, reconstructed the parent and cached-visibility masks, verified native
projection, original-pixel statistics, point coordinates and patch counts, and
checked all seventy input bindings. It adds zero model forwards. All software
replay checks pass; the quality acceptance checks fail.

Viewed every one of the five comparison boards using view_image. Reviews01–04
show appreciably more facial coverage; review05 loses a small marked patch.
Masks remain partial and hair/beard protection remains inadequate. Review06's
failure is retained in the ledger; no comparison board is fabricated for it.
The exhaustive review receipt binds all five boards and worker outputs.

Private artifacts: `segface_loader_sources_v1`, `segface_loader_check_v1`,
`segface_fixed_masks_v1` and `segface_fixed_mask_comparison_v1` under `outputs`.
Scripts 695–699 implement loader, five forwards, assessment, replay and review.
All prior checkpoints, failed acquisitions and experiment artifacts are intact.

## User steering and next boundary

The user confirmed no new DINO code/decoder permission and explicitly required
**fully automatic masking**, rejecting an optional manual mask-correction route.
Both constraints persist. DINO remains unused and SegFace remains experimental.

A focused primary-source follow-up did not establish another ready permitted
facial-hair checkpoint. Sapiens' FaceSynthetics documentation includes a beard
class, but describes finetuning; its inspected released segmentation zoo is
body-part segmentation, not a verified released beard/face checkpoint. A beard
presence classifier is not a pixel mask. No additional parser inference ran.

There is a concrete possible *training* route: Microsoft's
[FaceSynthetics](https://github.com/microsoft/FaceSynthetics), with 100,000
512x512 synthetic faces, dense beard/skin/hair/glasses/facewear labels and an
explicit distinction between opaque lenses and visible content behind clear
lenses. The full archive is advertised as approximately 32 GB. Its
[R-UDA licence](https://github.com/microsoft/FaceSynthetics/blob/50797c97ea0784581a0ffe4007e9e1aa75629323/LICENSE.txt)
restricts the data and trained results to noncommercial research; it is not a
commercial deployment clearance. Real-photo transfer would still need testing.

Pinned documentation is saved under `outputs/automatic_material_route_review_v1`.
No dataset was downloaded and no parser training began. Proceeding requires
the user's choice about this larger training route and information about
available GPU/training hardware. If selected, prepare a fixed data/resource/
training protocol before acquisition or fitting; do not fine-tune on these six
exposed review photos. No automatic rescue experiment follows the failed screen.

All 24 final holdout photos remain byte-unread. No correction model fitting,
runtime adoption, private-data upload, external message, commit or push occurred.
