# Dense face-parser feasibility results

26 October 2026. The [design checkpoint and fixed protocol](face-parsing-protocol.md)
separate facial contour coverage, anatomical exclusion and paint protection.
Scripts95-97 downloaded one published model, ran the fixed sample and verified
the results. No correction model was fitted and no runtime mask policy changed.

[Local comparison gallery](../outputs/dense_face_parser_v1/review.html) |
[Full metrics](../outputs/dense_face_parser_v1/summary.json) |
[Independent verification](../outputs/dense_face_parser_v1/verification.json).

## Selected model and method distinction

One candidate was selected before execution: the author's BiSeNet ResNet18 ONNX
[release](https://github.com/yakhyo/face-parsing/releases/tag/weights), with
[documented anatomical classes](https://github.com/yakhyo/face-parsing/blob/main/utils/common.py).
It has separate eyes, brows, lips, mouth and hair classes, but no paint class.
The author identifies CelebAMask-HQ as its training source. No training dataset
was downloaded or uploaded. The ONNX asset and pinned author source/license
metadata live only in the ignored local models directory.

Actual binary size: **53,205,364 bytes (50.74 MiB)**, differing from the author's
approximate43MB repository table. SHA-256:
`0d9bd318e46987c3bdbfacae9e2c0f461cae1c6ac6ea6d43bbe541a91727e33f`.
This matches the digest in the GitHub release metadata. Archived author source
revision: `8a4729d95118d0e97c44185f9bdef3d6bfeaaf99`. Software MIT license and
release/source metadata are preserved alongside the model.

OpenCV DNN successfully loads the published graph and its primary19-class output.
Preprocessing follows the author's RGB/512 bilinear/ImageNet normalization,
then argmax and nearest-neighbor restoration to native saved coordinates.
Internal512 inference is not a claim that saved224/256 study preprocessing has
changed. No project dependency was installed or replaced.

Two frozen diagnostics were compared:

- **D:** predicted skin1 or nose10, raw dense support; no paint guarantee.
- **V:** original stage mask AND D, removal only at generation, measurement
  and correction. Existing protections and existing holes are retained.

This is a new learned segmentation model beyond the proposed rule-based mask,
not an implementation of the original thresholds. Nose10 can include nostrils;
these remain scored against the original excluded regions. Neck14 and ears7/8
are not selected; this does not implement or reject the requested neck scope.

## Fixed sample and reference results

All53 cases succeeded: nine clean generation sources,32 cohort inputs and12
native regression inputs. Two83184 sentinel predictions are diagnostic only,
not geometry approval or reversal of their previous rejection. No new source,
reserved image, replacement case or data exposure was introduced.

Nine source/input frames share the exact three reference coordinate systems.
The following rows show labeled-skin coverage / selected reference-exclusion
pixels, not final segmentation accuracy.

| Reference/input | D dense | Original correction | V correction |
| --- | --- | --- | --- |
| 40048 dark | 97.79% /701 | 97.34% /806 | 96.75% /606 |
| 40048 unchanged | 99.08% /796 | 97.19% /805 | 97.06% /645 |
| 40048 mild | 98.48% /786 | 96.84% /847 | 96.68% /672 |
| 60162 dark | 98.94% /833 | 95.97% /873 | 95.44% /717 |
| 60162 color | 98.78% /838 | 98.75% /1025 | 98.08% /725 |
| 16798 clean regression | 95.71% /6629 | 91.76% /2110 | 89.35% /1831 |
| 16798 shifted regression | 94.69% /6552 | 91.71% /1743 | 88.37% /1496 |

D includes the annotated40048 cheek point202/124 in the source and all three
saved variants. This differs from the previous oval-based proposals. It is
promising evidence for a different contour representation, not permission to
adopt every dense pixel. V cannot recover that point because the original
stage masks omit it. No expansive replacement/union arm was run.

On the clean sources, D selects796/3458 and820/3739 feature-exclusion pixels
for40048/60162, versus all3458/3739 under the earlier coarse face-skin class.
This is substantial anatomical separation, but remaining eyelid/margin/nostril
and lip-boundary disagreements are visible. It is not a complete match to the
reviewer's broader feature outlines.

## Paint and hair findings

D selects **5969/6003 painted pixels (99.43%) clean** and **5893/6003 (98.17%)
shifted**. It also selects all three prior paint points per variant. The model
does not supply paint protection; its paint selection is even higher than the
coarse semantic model in this example. Anatomical classes do not imply a
skin-versus-paint material distinction.

V still excludes all three paint points per variant, but its clean/shift
correction masks select **1327/1001 painted reference pixels**, plus504/495
feature-exclusion pixels. Passing sparse paint points is therefore insufficient
to establish paint-area safety. These measurements preserve the original
annotations and Codex's separately documented descriptive polygon grouping.

D and V correction retain all12/12 prior skin points per variant and select
0/4 hair points per variant. V removes the pre-existing one clean correction
hair inclusion. Other/non-skin point selection remains0/5. These sparse checks
do not certify the unannotated hairline, background or clothing boundaries.

## Numerical and visual checks

All32 cohort V measurements produce valid CIELAB/ITA and the frozen six
brightness features. The ten-feature definitions were unchanged. The original-
generation retention screen passes31/32 cases.60162dark is flagged for
lower-left correction retention0.796965 against the existing0.8 threshold.
This denominator contains old selected features as well as skin; the flag is
not independent proof of facial-skin loss, but remains an explicit technical
failure. The original user acceptance is preserved; no new veto-mask approval
or rejection is inferred from it.

All35 stage-comparison boards, two sentinel boards and nine reference
disagreement boards were inspected. D often gives a more coherent face outline,
but dark42532 brow failure, closed-eye7994 ambiguity, nostril inclusion and
paint selection persist. V preserves old gaps/edges by construction, including
the shifted19/62331 measurement limitations and fragmented10480 generation.
Side-pose, hairline and lower-jaw boundaries remain unvalidated outside labels.

Script97 independently reconstructs all158 D/V masks from saved class maps and
original masks; pixels match exactly. Independent conventional Lab/ITA and
brightness calculations verify44 measurement sets (32 cohort plus12 native
regressions).52 full/interior reference count checks pass. All recorded
original input/mask/model/label/ledger/review-decision hashes remain unchanged.
Four new tests cover RGB normalization/input preservation, argmax/nearest
coordinate restoration, exact class selection and malformed-output rejection.
**475 tests pass** in11.58s with a fresh workspace-local temporary directory.

## Deployment evidence and limitations

Desktop inference over55 images has median0.2268s, range0.1783-0.3232s, plus
model-load cost recorded in the summary. A separate initial smoke inference
also succeeded before the fixed batch. OpenCV5.0 reports that its new graph
engine does not support explicit target selection; CPU was requested, and no
GPU/device performance claim is made. These are desktop timings, not Android
speed or memory measurements. No Android application/directory was created.

[ONNX Runtime documents mobile deployment](https://onnxruntime.ai/docs/tutorials/mobile/),
but this graph's Android operator support, memory, latency, quantization and
accuracy remain unverified. Backend parity with the author's ONNX Runtime or
PyTorch inference was not checked. A larger learned model and512 inference
have real deployment implications and cannot be hidden as threshold tuning.

## Decision and next experiment

Keep the parser as a **development candidate for contour/anatomical evidence**,
not a final mask or runtime replacement. V supplies useful hair/anatomy removals
while preserving current guards, but fails one retention screen and leaves
paint-area contamination. D can recover the cheek but fails paint protection.
Neither satisfies all three design requirements, and neither is adopted.

Before any expansion, predeclare a separate combined-mask experiment that
keeps explicit anatomical exclusions and tests a separate material/paint veto
on every proposed addition, including the existing painted area references.
Do not tune a paint rule to16798 alone or claim skin-colored paint can be
automatically recognized without evidence. Retain source-generation versus
actual-input consistency and all prior regression/hold decisions. If adequate
automatic paint protection cannot be demonstrated, record that limitation and
reconcile it with the intended thesis workflow before final-method claims.

No synthetic input regeneration, training admission, fold reassignment,
correction-tree fitting or runtime change followed. Previously approved masks,
human notes,31154 hold and empty original fold4 remain unchanged. Human polygon
diagnostics, exposed mixed-resolution sources and the additional learned model
are documented proposal distinctions. MST mapping, neck localization, final
data/split/evaluation, expert MOS and Android remain unfinished.
