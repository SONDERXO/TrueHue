# Parser backend comparison results

8 November 2026. **Both backends produce identical class maps on all four inputs, including the fragmented facial regions.** Switching inference backends does not recover missing coverage in these cases.

Completed the [fixed protocol](parser-backend-parity-protocol-2026-11-08.md): exactly four OpenCV forwards and four ONNXRuntime forwards on the pinned ResNet18 model, identical existing tensors and primary `output`. No preprocessing variants, new fits or mask-policy changes.

| Saved condition | Maximum absolute logit difference | Class disagreements at 512 × 512 | Class disagreements at 256 × 256 |
| --- | ---: | ---: | ---: |
| Development warm + overexposure | 0.00002050 | 0 | 0 |
| Later overexposure | 0.00001621 | 0 | 0 |
| Later cool + overexposure | 0.00001526 | 0 | 0 |
| Later warm + overexposure | 0.00001907 | 0 | 0 |

Mean absolute logit differences range from approximately 0.00000124 to 0.00000135. Both backends' restored category maps also exactly match the previously cached categories. Logits are not bit-identical, but their class decisions agree everywhere checked. These four conditions reuse two originals, not four independent photos.

ONNXRuntime 1.31.1 and its protobuf 7.36.2 dependency were installed into the project venv; no application dependency manifest or runtime selection changed. ONNXRuntime explicitly used `CPUExecutionProvider`. OpenCV was requested to use its OpenCV backend and CPU target; its new graph engine logged that target selection is not supported. The report therefore records the request and warning rather than claiming independently instrumented device placement. No remote inference or image upload occurred.

Independent saved-artifact verification recomputed all four logit differences, argmax maps, decoded map files and bound hashes. All passed without additional forwards. Existing masks and correction outputs remain unchanged, so no new visual-quality claim follows.

## Interpretation and next decision

Together with the preprocessing/coordinate/label audit, this removes a demonstrated execution discrepancy as the explanation for these particular masks. It does not prove general backend equivalence or locate the precise recognition failure. Crop suitability, limited native detail and the pretrained parser's recognition on these faces remain possible issues.

The next work should be a bounded parser-suitability decision using existing experiment evidence, not another correction gate or backend switch. Review what the earlier contrast and larger-parser trials recovered and incorrectly included, then define one justified intervention addressing coverage and object protection together. Do not automatically remove the background veto, fill holes, repeat preprocessing sweeps or start new annotation/data collection.

The correction model remains unadopted, its visible masking problems remain unresolved, and the separate eight-group, 24-photo holdout remains byte-unread. No app integration or follow-up fit started.

Script 646. Private logits, maps and receipts: `outputs/parser_backend_parity_v1`. Preserve research-use/privacy restrictions; do not redistribute private outputs.
