# Explicit facial-hair model inventory — 30 October 2026

Follow-up: both unauthenticated Roboflow artifact/metadata requests returned
HTTP401 (API key required). See [checkpoint acquisition](facial-hair-checkpoint-acquisition.md)
for evidence and the specific account/download step needed. Stop repeating
unauthenticated checks; access remains the dependency.

The bounded search is complete. It found projects that explicitly label facial
hair, but no complete checkpoint with verified access and reuse terms suitable
for a local TrueHue test. **No new inference or automatic mask change occurred.**
This is an access/readiness result, not evidence that these models perform badly
or that automated beard exclusion is impossible.

## Candidates checked

| Candidate | Actual label/task evidence | Weight/access finding | Decision |
|---|---|---|---|
| [jseobyun/FaceParsing](https://github.com/jseobyun/FaceParsing) | Explicit beard class 14; no separate moustache class documented | Decoder checkpoint linked on Google Drive; separate DINOv3 ViT-B/16 backbone required. Repository has no declared code/decoder license beyond reference to DINO terms. | Do not install or claim ready for adoption; obtain backbone access and decoder/code reuse terms first. |
| [PhD facial_hair-8quxg/1](https://universe.roboflow.com/phd-witpb/facial_hair-8quxg) | Instance segmentation with beard, mustache, eyebrow, hair | Public project shows API-key deployment; local weight access and model reuse terms not verified. No Roboflow credential configured under the two conventional environment names checked. | Most directly matched labels; next acquisition lead if authorized account access/weights become available. No hosted inference used. |
| [IFrajtag/Facial_hair_segmentation_analysis](https://github.com/IFrajtag/Facial_hair_segmentation_analysis) | Explicit separate beard/mustache training annotations | Complete repository tree contains annotations and masks, no checkpoint or Python inference code; no release assets or repository license declared. | Dataset/annotation resource, not a runnable pretrained model. Do not download its images or start training as part of this search. |
| [Charlie2802/Beard-Segmentation-Final](https://github.com/Charlie2802/Beard-Segmentation-Final) | README describes beard segmentation | No actual checkpoint in repository or release assets; no repository license declared. | Not runnable from the published artifacts checked. |
| [jonathandinu/face-parsing](https://huggingface.co/jonathandinu/face-parsing) | Published configuration has 19 facial classes, no beard or moustache label | Readable pretrained configuration, but wrong label schema for this task | Exclude before inference; do not repeat another generic parser test. |

The DINO backbone's [official model page](https://huggingface.co/facebook/dinov3-vitb16-pretrain-lvd1689m)
requires account access, information sharing and approval (API reports
`gated: manual`). No access form was submitted and no terms were accepted on
the user's behalf. The linked decoder alone does not make the network runnable.

Roboflow supports [local weight deployment](https://docs.roboflow.com/models/model-weights/download-roboflow-model-weights.md),
so its project should not be described as cloud-only. However, platform support
does not establish this public project's download access or weight license.
The project's displayed CC BY 4.0 dataset license must not be treated as proof
of pretrained-weight licensing. Its published benchmark numbers are not TrueHue
validation evidence.

## Reproducible evidence and stopping point

`scripts/313_inventory_explicit_facial_hair_models.py` records repository trees,
release metadata, source READMEs, backbone access metadata and the SegFormer
label configuration in `outputs/explicit_facial_hair_inventory_v1/`.
`inventory.json` includes source URLs and SHA256 hashes of saved evidence.
Repository revisions:

- FaceParsing: `bb649e99424ea988ca2bec8b5a3c8e8ca33f3f2e`.
- IFrajtag: `144f9449b4fca54fee5bb44e96879610deadff26`.
- Charlie2802: `6bda7d891e2bf6be21afe6cdb00ab2db77e0827b`.

No local photographs were opened or uploaded, no external dataset images or
annotations were downloaded, and reserved evaluation roles were not accessed.
Only source documentation, repository metadata and label/access configurations
were fetched. No dependencies or model weights were installed this phase.
The metadata script completed; no new pytest run is claimed for this audit.
Last full suite remains 833 passed in 11.62 seconds from the brush implementation.

**Next concrete dependency:** obtain a locally downloadable explicit beard/
mustache segmentation checkpoint with its label mapping, preprocessing and
usable terms. The Roboflow project is the most direct label match among these
leads; the DINO parser is a second route needing both access and licensing
clarification. Do not contact authors, purchase access, upload photos or train
a new network without a separate user instruction.

When a complete checkpoint is available, freeze its hash and preprocessing,
use the existing twelve exposed training examples for one diagnostic, and
subtract only its explicit facial-hair pixels from the preferred skin mask.
Inspect both clean-skin preservation and beard/moustache coverage, including
darker skin and stubble. No dense facial-hair ground truth exists for those
photos, so visual findings cannot establish validated accuracy. Do not retune
the two failed EasyPortrait candidates or substitute a presence classifier for
a pixel mask. Broader confirmation is needed before adoption.

The fuller mask, optional manual brush and correction demo remain unchanged.
ITA + calibrated MST + facial-statistics decision-tree correction remains the
method; matching mask-dependent MST calibration is still required for adoption.
