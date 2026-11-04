# Fixed dense face-parsing feasibility experiment

26 October 2026. Defined before model download or candidate execution.

## Design checkpoint

Three requirements must remain separate: facial contour coverage, explicit
anatomical exclusion, and paint/non-skin protection. Current coarse semantic
classes fail the latter two on the fixed references; margin/framing tests did
not solve cheek coverage. A dense parser offers different anatomical classes,
but is not assumed to recognize paint. Do not fit another correction tree.

Selected single candidate: yakhyo/face-parsing BiSeNet ResNet18 ONNX, official
`weights` release. Use the smaller published backbone; no model/backbone search.
The author lists19 classes and provides separate eyes/brows/mouth/lips/hair.
Use skin1 and nose10 as the dense facial-skin diagnostic, excluding neck14,
ears7/8 and all other classes. Nose class may still contain nostrils; score the
existing nostril exclusions rather than silently relabeling them.

Sources checked26October2026:

- [Repository, training dataset and approximate size](https://github.com/yakhyo/face-parsing)
- [Author's ONNX preprocessing/postprocessing](https://github.com/yakhyo/face-parsing/blob/main/onnx_inference.py)
- [Class order](https://github.com/yakhyo/face-parsing/blob/main/utils/common.py)
- [Published weight URLs](https://github.com/yakhyo/face-parsing/blob/main/download.sh)
- [MIT software license](https://github.com/yakhyo/face-parsing/blob/main/LICENSE)
- [ONNX Runtime mobile deployment](https://onnxruntime.ai/docs/tutorials/mobile/)

The repository reports CelebAMask-HQ training and approximately43MB for this
backbone; record actual downloaded bytes/hash and source revision. This is not
a dataset download or proof of downstream model/dataset rights beyond the
documented source terms. Android deployment is possible in principle via ONNX
runtimes, but model/operator support, memory, speed and quantization remain
unverified. No Android directory or integration is created. Existing OpenCV DNN
is the first local inference backend; do not replace project dependencies.

## Frozen implementation and scope

Full saved native image BGR->RGB, bilinear resize512x512, float32/255,
ImageNet mean/std (0.485/0.456/0.406,0.229/0.224/0.225), NCHW. Argmax first
19-class output at512 then nearest-neighbor restore to original coordinates,
as in the author's ONNX inference code. Input/reference pixels remain unchanged.
Internal512 inference is not a change to the saved224/256 study preprocessing.
No test-time augmentation, color preprocessing, alignment or per-image selection.

Two fixed diagnostics:

1. D: parser skin1 OR nose10. Raw dense support, not approved segmentation.
2. V: existing stage mask AND D at source generation, actual-input measurement,
   and correction. Removal only. Existing thresholds/material/paint protections
   are not bypassed. This arm cannot recover an existing cheek hole.

No expansive replacement/union arm is implemented until these diagnostics are
assessed. A dense parser has no paint class; D must be scored on paint explicitly.

Fixed sample: same53 cases (nine generation sources,32 cohort inputs,12 native
clean/shift regressions), plus two83184 sentinels. No new source exposure or
reserved imagery. Three unchanged reference rasters, same nine matching
source/input frames and48 native point observations. Existing decisions, holds,
fold assignments and source provenance are frozen. Full-image parsing does not
guarantee selected-person identity; sentinel/pose errors remain diagnostic,
not rescued admissions. Every failure/unavailable case must be retained.

Record dense class maps; D/V full/interior reference scores; all-polygon feature/
paint subgroup histograms using the prior documented descriptive grouping;
cheek202/124; point outcomes;32cohort statistics/brightness/retention screens;
model bytes/hash, load and inference CPU timings. Timings are desktop-only.
Inspect all source/input comparison boards and reference/paint disagreements.
Independently replay V masks/class selection and scoring and verify original
input/model/ledger/review-label hashes before reporting. No original mask
replacement, synthetic regeneration, training table change, fit or runtime
adoption. No parameter sweep based on these references.

## Thesis record

This is another learned segmentation model beyond the proposal's rule-based
mask. If retained, record its role, dataset, binary size, runtime/device cost,
limitations and adviser guidance. Original photos/manual polygons are not
calibrated skin truth, final independent evaluation or a required application
annotation workflow. Final MST mapping, neck localization, datasets/splits,
expert evaluation and Android requirements remain pending.
