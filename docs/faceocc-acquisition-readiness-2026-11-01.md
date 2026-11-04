# FaceOcc artifact acquired; input mapping remains unresolved

1 November 2026. User authorised continued progress after the shortlist and
requested explicit tracking of method changes for the panel letter.

## Completed acquisition

Scripts363/364 acquired public metadata, pinned source/config/licence evidence
and one pretrained artifact. No model source was executed and no photos were
processed. Project dependencies and current measurement/correction code remain
unchanged. No dataset download, remote inference, training or reserved access.

- Model: mertakin/FaceOcc, revision03f229dc75fa14ae480cca9810f983912c2730ad.
- Source: mertakinstd/FaceOcc, revision8d86c9a2c1a0094dbc1a1e5467413b49f8936b32.
- Saved checkpoint: models/faceocc_candidate_v1/model.safetensors.
- Size:57,377,516bytes.
- SHA256:5d6d27a9cb221692425840a80eb4efc07e6245670b233e2eb618e83fd9b7caf6.
- Digest matches publisher LFS metadata; SafeTensors header contains182tensors
  with valid sizes, in-bounds contiguous offsets and expected input/output
  shapes: encoder convolution[64,3,7,7], output convolution[1,16,3,3].
- Hub metadata reports public, not gated. Saved model/source licences and
  attribution notices are retained beside evidence; no dataset terms accepted.

These checks establish file integrity and structural plausibility, **not strict
model loading, numerical parity, output quality or Android readiness**. The
checkpoint is in an ignored models directory, not a runtime/default asset.

## Verified source behaviour and remaining gap

The saved runtime source defines U-Net/ResNet18 with fixed decoder channels,
ImageNet RGB normalisation, no output activation and a one-channel head. The
reference evaluation applies logit>0, equivalent to probability>0.5. It reads
already-prepared COFW images directly. These details now have pinned evidence
instead of relying only on a model-card description.

Training preparation includes landmark-driven alignment with a3D template and
an affine transform. The inspected alignment helper uses a scale derived from
116/s, fixed256output and reflected-border handling. Neither the compact model
config nor the evaluation entry point supplies a complete arbitrary-gallery
face detection/cropping/inverse-mapping contract. The raw prepared dataset was
not downloaded to guess that contract. Direct full-frame square256 resizing or
invented detector margins therefore are not established reference preprocessing.

The project Python3.14environment does not contain torch,
segmentation_models_pytorch, safetensors or onnxruntime. No package installation
or automatic upgrade was performed. Architecture reproduction would need a
separate inference environment and strict state-dictionary load; that remains
unverified. Training-stack requirements are not blindly installed for inference.

**Readiness decision:** artifact acquisition passed; end-to-end diagnostic
readiness is not established. This is not a failed segmentation result. Do not
report mask quality from this stage or silently substitute a second checkpoint.

## Next technical work

Resolve and freeze the source-supported input coordinate contract: actual
face-localisation/alignment requirements, template provenance, pixel centres,
forward/inverse transform, interpolation, border validity and unavailable-case
handling. Distinguish source-faithful reproduction from any TrueHue-specific
adaptation. An alternative input adaptation would be an explicit method choice,
not an unrecorded implementation detail or a crop-margin search.

Then create an isolated compatible inference environment, verify strict loading
and synthetic geometry round trips before processing a study photo. Once ready,
freeze the previously described single25attempt diagnostic (17saved successful
inputs/eight retained failures), old preferred measurement baseline, fixed
threshold and annotations. No new mask/threshold/model sweep. Correction stays
whole-face+neck with continuity/blending; FaceOcc would only veto measurement.
It supplies no explicit beard guarantee and does not resume beard-specific work.

No new matching MST lookup or correction tree follows automatically. New
candidate masks/features would require a new contract and separate evidence;
the current preferred measurement and old failed outline candidate stay intact.

## Evidence and verification

outputs/faceocc_readiness_v1/ retains the initial network-sandbox failure;
v2contains successful acquisition metadata with URLs/hashes. The approved
network run fetched public artifacts only. A Windows UTF-8 decoding error
stopped an initial checkpoint-acquisition attempt before any download and was
corrected explicitly. models/faceocc_candidate_v1/acquisition.json contains
artifact/source hashes, tensor metadata and status. Script syntax checks passed;
no project pipeline code changed, so pytest was not rerun. The last broader
result remains896passed/44.79s excluding desktop GUI tests, not a full-suite pass.

Panel register status: **pretrained occlusion-veto component under feasibility
assessment, artifact acquired, not adopted**. No validated method change or panel
approval is implied. Preserve FaceOcc research and derivative attribution if
used; exact submitted-paper sections still require verification before a letter.
