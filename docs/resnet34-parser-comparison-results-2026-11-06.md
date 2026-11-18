# Alternative parser comparison: more skin, more unwanted material — 6 November 2026

The single authorised ResNet34 comparison improves actual skin-point inclusion
54→77/113, but worsens unwanted inclusion9→15/94. It recovers24skin points and
loses one; all nine old unwanted inclusions remain and six new ones appear.
**Do not replace the baseline on the strength of improved skin coverage alone.**

This completes the one-alternative comparison, with no subsequent model search,
calibration, cohort admission or runtime adoption.

## Selected alternative and provenance

The alternative is the published ResNet34 ONNX variant of
[yakhyo/face-parsing](https://github.com/yakhyo/face-parsing), compared with the
existing ResNet18 variant. Both are BiSeNet-family models using the same19labels
and input/output convention. This is a larger backbone comparison, not an
architecture-independent model or a dedicated facial-hair label system.

Script467verified the official asset ID328506789,93,632,554bytes and release
SHA256`5b805bba7b5660ab7070b5a381dcf75e5b3e04199f1e9387232a77a00095102e`.
Pinned author sources at revision8a4729d95118d0e97c44185f9bdef3d6bfeaaf99
match the previously recorded LICENSE/README/inference/utils source hashes.
The [MIT software notice](https://github.com/yakhyo/face-parsing/blob/8a4729d95118d0e97c44185f9bdef3d6bfeaaf99/LICENSE)
and published model/data lineage are retained locally; this is not blanket
commercial rights clearance. Model files stay ignored, research-only and local.
Initial sandbox socket access failed; the authorised network download succeeded
on escalation. No image/dataset upload or remote inference occurred.

## What stayed fixed

The [predeclared protocol](resnet34-parser-comparison-protocol-2026-11-06.md) uses
the same six reference-review cases, original crops, source scores/actual points,
fixed parser-only CLAHE copy and reviewed512RGB/ImageNet preprocessing adapter.
Only the model asset changes. This does not use the unadopted upper-face cutoff,
background-recovery rule or a different crop/preprocessing setting.

Script468ran six new CPU parser forwards. The missing-landmark case received a
category map but remains unavailable for full measurement, without fabricated
geometry/visibility. For the other five cases, unchanged full-face semantic
skin/nose association, anatomical/nostril exclusions and1000pixel parent guard
were applied. The original five FaceOcc logits/aligned inputs were reused;
there were zero new FaceOcc/detector/landmark passes. Original pixels alone
supply masked Lab/ITA; old sources, masks and measurements remain untouched.

## Actual user-point results, same denominator

Both alternatives yield five technical successes out of six attempts. All238
user points remain;31in the landmark-failed image have unavailable predictions,
not successful exclusions. The paired-five-image result uses exactly the same
207points and gives the same comparisons below.

| Definite actual points with prediction available | ResNet18 baseline | ResNet34 alternative |
|---|---:|---:|
| Skin selected | 54/113 (47.8%) | 77/113 (68.1%) |
| Hair/object selected | 9/94 (9.6%) | 15/94 (16.0%) |
| Hair/beard selected | 8/86 | 13/86 |
| Object/other selected | 1/8 | 2/8 |

Point transitions:53skin retained,24gained,1lost,35still excluded. Nine unwanted
inclusions persist, six are newly admitted and79remain excluded. None of the
old unwanted inclusions is repaired. The larger parser therefore improves
coverage at the cost of protection, rather than resolving both sides.

Parser-only category predictions on the same five cases select61→85/113skin
points, but16→31/94unwanted points. This is before anatomical/component/FaceOcc
guards and is not the final-mask score; it localises the changed classification.
The sixth case's category output does not turn its failed full pipeline into
an available final result. No denominator changes or hidden failure filtering.

These are exposed sparse-development point agreements, not dense segmentation
accuracy, independent validation or native sample independence. The actual
skin marks also include neck/contour points outside the face-only measurement
scope; no user marks or original denominators were relabelled for this comparison.

## Six-board inspection and decision

The assistant inspected all six original/old/new/change boards. The glasses
example gains broad cheek/chin and some forehead support, although fine frames
and reflections remain uncertain. The beard example gains central skin-looking
coverage while also including beard material. One dim warm case gains broad
facial coverage; the dim cool forehead case remains patchy with new isolated
regions. The broad-support control changes mostly at chin/boundaries. The
landmark-failed case remains unavailable. These are qualitative observations,
not a second invented user annotation set.

Keep ResNet34 as an isolated coverage-gain candidate and retain the worse
material-inclusion result. It is not adopted for measurement, calibration or
Android, and no additional backbone is automatically tested. The same19class
label set lacks an explicit beard class; simply increasing backbone size did
not solve this observed failure mode. Further work needs a separately justified
material-discrimination strategy and honest evaluation scope, not a sweep until
the existing238development marks score well. No new review task is activated.

## Verification and tests

Script469verified six exact transformed inputs/category maps, five independently
reconstructed semantic/nostril/final masks, five original-statistic/native-grid
replays, actual point counts and parser-stage denominators. Five exact saved
service replays passed without new forwards. All model/source/actual-export/
parent artifact hashes remain unchanged; the verified alternative model is
added separately, with no overwrite of ResNet18 or dependency installation.

35focused parser/semantic/nostril/reference-import tests passed in1.91seconds,
not a full-suite, device or scientific acceptance test. Effective alternative
contract:`93deb70a400d40d020403b091d9c8767029127746646b16dad134bbef92854ed`.

Private gallery: `outputs/resnet34_parser_comparison_v1/review_PRIVATE.html`.
Verification/observations: `outputs/resnet34_parser_assessment_v1/assessment_PRIVATE.json`.
Acquisition/provenance: `models/face_parser_resnet34_candidate_v1/`.
Dataset photos, scores/IDs, actual marks and manifests remain private ignored
under research/noncommercial+citation/no-redistribution terms. No fit, admission,
app/runtime change, contact, recruitment, publication or adviser approval occurred.
