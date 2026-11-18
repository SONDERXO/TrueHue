# Approved facial-underexposure pilot: completed, not advanced

17 November2026. User approved "Okay lets do that". The [prospectively fixed pilot](face-underexposure-pilot-protocol-2026-11-17.md) is **complete and failed its narrow screen**. No correction-training run, runtime gate, threshold revision, crop/model variant or further review follows. This is not proof that every possible use of these features is impossible. The full correction model remains unfinished.

## Actual detector result

One frozen tiny checkpoint,66previously exposed inputs/11sources/sixroles. Published argmax rule, normal=0/under=1, ties normal. All scores sealed before role metrics. Counts are cases, not independent people or expert judgments.

| Input condition | Flagged underexposed | Expected underexposure for this synthetic task |
|---|---:|---:|
| Unmodified original | 1/11 | 0/11 |
| Colour only | 2/11 | 0/11 |
| Pure underexposure | 3/11 | 11/11 |
| Overexposure | 2/11 | 0/11 |
| Combined underexposure/colour | 5/11 | 11/11 |
| Combined overexposure/colour | 2/11 | 0/11 |

The false-underexposure original is29617 (score0.837499). Colour false alarms:29617(0.879038),49131(0.567479). These are task-label disagreements, not fabricated human appearance ratings, expertMOS or official tone labels. The underexposure score is an uncalibrated classifier softmax output, not a validated real-world probability.

The narrow ordering hypothesis was positive: underexposure raises the score in **11/11original-to-pure-under pairs**, and **9/11colour-to-combined-under pairs**, with zero ties. The combined pair losses are46795 and52445. Nevertheless, both majority-detection requirements and both zero-false-alarm requirements failed; only the two ordering gates passed. Do not lower the threshold or hide these failures because the pair ordering is encouraging. The directly interpreted detector is not a reliable apply/skip decision on the present development task. A direct-score failure does not establish universal feature uselessness; the fixed pilot is closed rather than converted into another regressor automatically.

Prior neutral misses:16061pure-under score0.442000/classnormal (still missed),48879pure-under0.543175/classunder,48879combined-under0.537798/classunder. No actual correction was made, so these are detector decisions, not repaired portraits. For16061the original score0.344766 is lower than the darkened score but both are classnormal. Large between-source score offsets remain visible; do not infer skin-tone bias or a calibrated adjustment from these11sources. The earlier PPR brightness concern and all its results stay preserved/closed.

## Readiness and verification

Native timm1.0.9 `deit_tiny_patch16_224`, strict weights-only checkpoint loading,152tensors/5,524,802parameters, CPU/eval/frozen/two threads. Six generated repeat forwards passed exact preprocessing, finite logits/scalar softmax, invalid-input rejection, input/state immutability. Then one generated contract replay plus exactly66actual input-only forwards, zero fits or correction renders. Crop `[32:256,16:240]`, published ImageNet normalization, class ordering and threshold unchanged. Inference runtime after loading was3.24seconds; setup/verification are separate costs. Actual safe checkpoint/source readiness was reused rather than redownloaded.

Runtime dependencies are isolated in `outputs/fiqa_tiny_runtime_v2/site`; existing torch/torchvision/environment unchanged. Initial v1 preparation stopped before installation because safetensors0.4.5 had no compatible Windows Python3.13wheel; original source/two wheels/failure saved. One [compatibility-only revision](face-underexposure-runtime-compatibility-2026-11-17.md) used safetensors0.5.3, preserving all scientific settings. Twelve publisher-hash-verified binary wheels total3,855,770bytes; both attempts combined6,610,973bytes, within16MiB. No core upgrade, source build, custom model port, additional checkpoint or external photographs.

Independent audit:66scalar softmax/class checks, maximum probability difference7.1436e-8, six role counts/means/ranges,22paired margins and six gates, five original run-artifact hashes and80source bindings. All66access records contain ONLY `input`. Input bytes and frozen model state unchanged; all data/code/checkpoint bindings retained. No broad or repeated training test suite needed.

## Continuation boundary

Artifacts `outputs/face_underexposure_native_v1`, `face_underexposure_pilot_design_v1`, `face_underexposure_pilot_v1`; dependency receipts in `fiqa_tiny_runtime_v1`(preserved failure) and`fiqa_tiny_runtime_v2`. Scripts `face_underexposure_pilot.py`, `verify_face_underexposure_pilot.py`, `prepare_fiqa_tiny_runtime.py`/`_v2.py`. Exact approval and bound roster saved before actual input calls. Checkpoint SHA256 `8dcccb197787cbfc64ec2c01e22dc8bafe01db701485b4c3cc06bb88aa44d7e7`; no author-published-checksum claim.

**Fixed pilot CLOSED/NOTADVANCED; no qualified next correction fit selected.** No further detector inference, threshold/crop/normalization/checkpoint/head/feature/source rescue queue, current-model adoption, final all-data fit or human review. Positive within-source ordering remains evidence with the stated failures, not a retrospectively successful pilot. A later scientifically distinct proposal still needs a credible inference basis, history/paper check, fixed assessment and the relevant authorization; urgency alone is not that basis.

This neural-score assessment is a disclosed method extension to proposal63/65. It is repeatedly exposed development, not independent person/MST-stratified qualification. No TrueHue darker-skin benefit, expertMOS or tiny-model performance inherited from the paper's base model. PIQ23 remains separate/access-use-pending. Preserve all prior failures, raw ratings/user corrections/manual ears, locked contents AND manifests/raw-original prohibition, runtime/Android and manuscript pause. Full exposure/colour/preservation objective and actual expert feedback before Friday paper submission remain. Adviser remains formatting/conferences only; no completion promise.
