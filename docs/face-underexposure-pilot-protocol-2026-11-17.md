# Approved fixed facial-underexposure pilot

17 November2026. Exact user approval: "Okay lets do that", responding to one frozen detector test on the existing66inputs. Paper63/65 rechecked. This is an approved external neural-score assessment, not a correction-tree fit, RGB replacement, runtime gate or unchanged original-proposal method. PPR319 and all earlier closed studies stay closed.

One asset only: already cached `deit_tiny_checkpoint8.pth`, SHA256 `8dcccb197787cbfc64ec2c01e22dc8bafe01db701485b4c3cc06bb88aa44d7e7`. No other checkpoint, model variant, crop, threshold, calibration or retraining queue. Existing noncommercial research notices/limits remain; no corpus/demo/new photos/contact. The later tiny model does not inherit the paper's base-model results.

## Runtime and generated barrier

Use existing Python3.13.17/torch2.15CPU/torchvision0.29.2/Pillow13/NumPy2.5.4, unchanged. Isolate missing packages under `outputs/fiqa_tiny_runtime_v1/site`; no install into the existing environment or dependency resolver replacing torch/torchvision. Pin timm1.0.9 and supporting wheels, select only compatible binary wheels from official PyPI JSON, verify publisher SHA256, total wheel ceiling16MiB. Preserve author/package licences and install receipt; stop if a large stack/build or core upgrade is required. No custom model port.

Native timm `deit_tiny_patch16_224`, pretrained=False,num_classes=2; strict safe weights-only state load, CPU/eval/frozen/two threads/deterministic. Never download initialization weights. This is the published tiny architecture with the same two-logit interface; no author-runtime bit-parity claim. Before actual portraits: exactly three generated RGB8arrays/base and fixed-/+halfstop, each twice, six forwards total. Check finite2logits, exact repeat, unchanged input/state, scalar stable2classsoftmax agreement within2e-7 and native preprocessing against independent float32 arithmetic. Wrong shape/dtype reject before forward. No large training/mock framework.

## Fixed actual input and inference

Exactly66existing camera-halfstop input arrays,11sources/sixroles each, same source roster/metadata/generated=False. These are previously exposed FFHQ-aligned256RGB8development inputs, not new photos or independent qualification. Hash all declared case containers before decoding; read ONLY each container's `input`. Do not read reference/support arrays or raw originals/locked contents or manifests. No source selection, omissions or substituted failures.

Fixed crop follows the paper's256-to224description: RGB array `[32:256,16:240,:]` (top32,left/right16); no resize/alignment/crop sweep. Apply published torchvision224Resize (no size change),ToTensor and ImageNet normalization mean(.485,.456,.406)/std(.229,.224,.225). Current framing inherits the FFHQ alignment; exact original dlib author-environment parity is not asserted. No directory-label inference. Alphabetical published classes normal_exposure=0,under_exposure=1; native argmax, ties class0. Underexposure probability is softmax logit1, threshold equivalent to logit1>logit0. Save BOTH raw logits, both probabilities, decision and input/crop hashes. Independently verify stable softmax; no score is a calibrated probability/EV claim.

After loading, one saved generated contract replay precedes exactly66actual input forwards; no actual repeats/head/tree/encoder training or correction renders. Verify input immutability and unchanged model weights/buffers and all bindings after completion. Seal all66scores BEFORE deriving role metrics; labels/source IDs are used only for reporting and pairing, never model inputs. Stop/preserve any failure, do not rerun a partly completed attempt silently.

## Frozen evidence criterion and stopping rule

This tests a conservative, directly interpretable underexposure cue on the present task. To advance this narrow pilot, require ALL:

- Zero of11unmodified originals classified underexposed at the published argmax rule.
- Zero of11colour-only cases classified underexposed.
- At least6of11pure-under and6of11combined-under cases classified underexposed.
- Strict score increase for at least6of11original-to-under pairs AND6of11colour-to-combined-under pairs. Equal scores are ties, never wins.

Report every score, confusion counts for all six roles, paired margins/ties, and all three prior neutral misses. Over/combined-over underexposure flags are reported descriptively, not treated as signed overexposure detection. No confidence interval, population significance, expert rating, per-tone/fairness or correction-usefulness claim from11repeated sources. No new feedback/review required.

Failure closes this fixed cue pilot with no threshold/crop/model/head/source rescue. These direct-score rules are an explicit time-bounded hypothesis, not a theorem that every possible use of a failed feature is impossible. A pass would justify considering a separately fixed combined exposure-and-colour correction comparison; it does not authorize one automatically, current-model adoption, final all-data training, Android or manuscript changes. Keep full objective/Friday expert-paper sequence, adviser-format-only role, all failures/ratings/manual ears and locks unchanged.
