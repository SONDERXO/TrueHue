# Face-masking shortlist and one recommended candidate

1 November 2026. User authorised researching pretrained candidates, classes,
licences and Android feasibility. Current measurement/correction pipelines remain
unchanged. The user prefers the old measurement overlay; the face-contained
candidate remains unadopted. This research does not resume beard-specific model
work, authorise training or select a model by TrueHue test outcomes.

## Recommendation

**FaceOcc is the best task-matched lead for one local occlusion-veto diagnostic.**
This is a research selection, not proof it works or a ready Android component.
Use it, if acquisition/preprocessing checks pass, as a removal-only veto on the
current measurement mask. Keep current anatomical/nasal exclusions, correction
coverage and inward blending separate. Do not reinstate the rejected hard face
outline. Do not change models until exact artifact/preprocessing provenance is
available. More recent release packaging is not evidence of better segmentation.

## Shortlist

| Candidate | Task/classes and pretrained evidence | Licence/access finding | Android finding | Decision |
|---|---|---|---|---|
| FaceOcc original authors | Binary face extraction; documented occluders include spectacles, sunglasses, worn masks, hands and scarves; pretrained link supplied | Authors explicitly state MIT for dataset and pretrained extraction model; linked binary not downloaded/verified here | Original reference uses PyTorch; no verified Android deployment in this review | Recommended model family; acquisition lead, not installed |
| FaceOcc modernised distribution, mertakin/FaceOcc | Binary visible-face output; U-Net/ResNet18, complete SafeTensors checkpoint advertised | Model card declares MIT; separate derivative/third-party attribution remains; binary/config fetch not verified here | No verified LiteRT/ONNX Android artifact or TrueHue device benchmark | Preferred packaging lead for the same candidate, conditional on provenance/runtime checks; not a second inference competitor |
| FACER/FaRL | Public pretrained parsing paths; LaPa11 classes, CelebM19 classes, including glasses only in latter | Toolkit MIT checked; checkpoint-specific provenance/terms not fully audited | PyTorch inference and coordinate warping; Android export/parity unverified | Defer: lacks explicit beard/worn-mask class; no direct evidence it fixes our failures |
| MediaPipe SelfieMulticlass | Six classes: background, hair, body skin, face skin, clothing, accessories | Official model/API exists; already acquired/tested in TrueHue | Official Android ImageSegmenter path; actual current-project device performance not established here | Preserve historical evidence, not a new candidate or repeated parser trial |
| OFIQ | Face-quality toolkit with an occlusion-segmentation interface in its reference manual | Core MIT; downloaded models have separate licences | Project supplies mobile build documentation | Defer: isolate/check model-specific artifact and terms before claiming a ready mask component |

Primary sources:

- [Original FaceOcc repository and weight/licence statement](https://github.com/face3d0725/FaceExtraction).
  Its [training code](https://github.com/face3d0725/FaceExtraction/blob/main/train.py)
  defines a one-output U-Net with ResNet18 encoder. Original research is
  [Yin and Chen, FaceOcc](https://arxiv.org/abs/2201.08425), not a new2026 algorithm.
- [Modernised FaceOcc model card](https://huggingface.co/mertakin/FaceOcc) states
  RGB256, ImageNet normalisation, one-channel logits and fixed0.5 probability
  threshold. It says the full encoder/decoder weights are included and notes
  COFW was used for checkpoint selection, not untouched testing. These are
  publisher claims, not reproduced TrueHue results. The
  [derivative implementation](https://github.com/mertakinstd/FaceOcc) describes
  an updated runtime/training workflow; do not run its dataset setup or training
  scripts for inference acquisition. [Attribution notice](https://github.com/mertakinstd/FaceOcc/blob/main/NOTICE.md).
- [FACER parser source](https://github.com/FacePerceiver/facer/blob/main/facer/face_parsing/farl.py)
  supplies the exact label arrays and pretrained URLs; [toolkit licence](https://github.com/FacePerceiver/facer/blob/main/LICENSE).
  A modern representation backbone does not supply absent output categories.
- [Official MediaPipe segmentation guide](https://developers.google.com/edge/mediapipe/solutions/vision/image_segmenter)
  and [Android guide](https://developers.google.com/edge/mediapipe/solutions/vision/image_segmenter/android).
  TrueHue's earlier result is docs/semantic-support-results.md: face-skin alone
  retained reviewed paint points, so this is not an untested substitute.
- [OFIQ project](https://github.com/BSI-OFIQ/OFIQ-Project) and
  [licence inventory](https://github.com/BSI-OFIQ/OFIQ-Project/blob/main/LICENSE.md):
  core licensing does not establish the licence of separately downloaded models.

## Important limits

Visible face is not automatically actual skin: eyes/lips and potentially facial
hair can belong to that target definition. No explicit beard class or reliable
beard exclusion is established for the selected lead. Keep beard cases as
unresolved diagnostics, not evidence this is a beard model. Explicit facial-hair
leads were already audited in docs/explicit-facial-hair-model-inventory.md;
do not repeat blocked unauthenticated Roboflow calls or bypass that hold.

SAM-style general promptable segmentation is not selected: prompts and large
general models do not by themselves establish an automatic actual-skin mask or
Android feasibility. No advantage on TrueHue is demonstrated by popularity.

Web access read model/source documentation. FaceOcc config/API and original
Drive binary were not accessible through the browsing tool on this pass.
This does not prove gated or unavailable weights. Do not claim verified artifact
access, revision, checksum, binary size or runtime compatibility from a README.
No repo revision or model hash is pinned until actual acquisition succeeds.

## Concrete next step: acquisition/readiness, then one diagnostic

Acquire only the chosen FaceOcc artifact and source/config/licence evidence,
pin exact revisions and SHA256, verify tensor architecture and inference
preprocessing against publisher code. Establish whether a face crop/alignment
is required: direct full-frame resizing must not be assumed from input size.
Reject an unclear coordinate mapping rather than improvise crop margins.
Python3.14 compatibility is unverified; if needed use an isolated environment
within the workspace, without replacing the project environment. No automatic
dependency upgrade, model training, dataset download or image upload.

Only after readiness passes, freeze one diagnostic protocol before inference:

- Use the current preferred measurement baseline, not the rejected outline mask.
  Candidate rule: baseline AND model-visible-face at the publisher's fixed
  threshold. No threshold/crop/morphology search and no addition of pixels.
- Reuse the fixed25attempt additional-subject diagnostic with all eight failures
  retained. Save alignment, logits/probabilities, mapped mask, removal fractions,
  source/artifact hashes and exact unavailable outcomes. No replacement rows.
- Bind actual-skin/occluder annotations before viewing predictions; existing
  sparse marks are diagnostics only. Check clothing, worn mask and skin loss
  together; include beard as an unresolved limitation. An apparent improvement
  on familiar cases is exposed development evidence, not independent validation.
- Correction masks/rendering and the active measurement contract stay unchanged.
  Any candidate gets its own contract and no old MST lookup. One run then stop;
  failure or destructive skin loss does not trigger another model/threshold trial.
- Android feasibility requires actual export, output parity and target-device
  memory/latency measurements. A ResNet18/U-Net architecture makes conversion
  worth investigating, but does not establish supported operators or speed.

This shortlist is complete. No model weights/dependencies installed, inference
performed, labels changed, datasets uploaded, reserved pixels accessed or fits
run. No pytest rerun for documentation research. Last broader test result is
896passed/44.79s excluding desktop GUI(Tcl/Tk unavailable), not a full-suite pass.
