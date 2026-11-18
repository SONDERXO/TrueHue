# Parser contract check on the fragmented distorted inputs

8 November 2026. **No mismatch was found in the checked input, asset or label conventions.** No network forward, model fit or mask change occurred.

This extends the earlier [54-clean-input audit](parser-input-contract-audit-2026-11-08.md) to the four distorted conditions implicated in the latest coverage trace, rather than repeating the earlier experiment.

## Checks completed

- The exact ResNet18 ONNX asset matches its recorded SHA-256 and archived release provenance. The archived author inference code, class names, README and licence also match their saved hashes.
- The local 19-class order agrees with background plus the archived 18 foreground attributes. Skin is class 1, glasses 6, nose 10 and hair 17. No class-order shift was identified.
- All four native crops exactly match the saved distorted scene slices. Their 256-pixel processing images exactly match the recorded bilinear resize.
- Their parser tensors exactly match an independent transcription of the archived author contract: BGR to RGB, bilinear 512 × 512 resize, float32 division by 255, ImageNet mean/std, channel-first batch layout.
- All saved category maps have the expected dimensions and valid class IDs. Synthetic logits verify all 19 class indices through argmax decoding. Nearest-neighbour restoration was also checked in the earlier audit.
- OpenCV loads the pinned model and exposes the expected primary `output`; the other exposed outputs remain unused. No forward was run.

The archive identifies the asset as ResNet18. This check verifies provenance and loadability, not an independent architectural reconstruction of the ONNX graph. The Python ONNX inspection package is not installed; no dependency was installed to broaden this audit.

## What remains uncertain

These checks cannot regenerate saved class predictions, establish OpenCV-versus-ONNXRuntime numerical parity, prove that this framing suits the pretrained model, or validate skin/object segmentation. The background-labelled facial regions could reflect recognition limits or an untested numerical issue; this audit does not establish which.

The prior current-framing contrast experiment already produced mixed coverage and protection outcomes and was not adopted. The larger-parser comparison also traded more selected skin for more unwanted inclusions. Neither should be repeated or adopted automatically as a solution.

## Recommended next bounded step

Before another masking-policy change or correction fit, define a **backend-parity diagnostic** on these same four saved inputs: compare the pinned primary-output logits and decoded categories from OpenCV CPU and ONNXRuntime CPU, with identical tensors and no preprocessing variants. This would require exactly eight forwards if neither backend's logits are cached. First check local backend availability and freeze a protocol; do not install dependencies or start inference merely from this recommendation.

The purpose is to rule out a numerical execution issue, not to optimise masks. If both backends agree, preserve the result and make a separate decision about parser suitability/recognition. If they differ, diagnose that discrepancy before changing protections. No threshold, appearance, model-capacity or dataset sweep is implied.

Keep background/object protection intact. No hole filling, dilation, clear-lens inference or automatic runtime change. The separate 24-photo final holdout remains byte-unread. Existing manual reviews remain complete and do not need repeating.

## Artifacts

Script 645; private `outputs/fragmented_parser_contract_audit_v1/audit_PRIVATE.json` records four exact input/tensor checks, archived hashes, labels, outputs and limits. Input/source hashes were checked before completion. No new inference, fitting, annotation, dataset search or external sharing.
