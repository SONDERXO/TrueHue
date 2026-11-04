# Delivery plan: before 7 November 2026

1November2026 current checkpoint: see delivery-checkpoint-2026-11-01.md and
thesis-results-addendum-2026-11-01.md. Android integration/resumption and emulator
execution supersede the historical pause/pass-through statements below: saved
6native/18JVMtests pass,onefixedexampleparity,physicalphone/broaderparity pending.
It retains the older experimental baseline, not FaceOcc/newwhole-face+neck.
MST remains unreliable; FaceOcc preferredexperimental, no newfit authorised.
The dated original plan and earlier progress below are retained as history.

User confirmed on28October: Python prototype, Android application and thesis
results are all required before7November. Working cutoff:6November, Asia/Manila.
These are targets, not evidence that an unfinished component is complete.

| Target dates | Deliverable | Completion evidence |
| --- | --- | --- |
| 28–29October | Establish Android build and port frozen inference | APK builds; Java tree parity; actual gallery/decode path; no placeholder success |
| 29–31October | Connect on-device detection, mask, Lab/ITA and correction | Stage reports and saved outputs on phone; component comparisons with Python; all processing offline |
| 30October–2November | Validate the retained ITA→MST path and lock Python/data method | Measured calibration/held-subject evidence, MST included in correction features; no fabricated labels; fixed data/processing/exclusions |
| 1–3November | Freeze demonstrable application and evaluate | Gallery input/output/save, single-face failures, original preservation, actual phone timing and stable cases |
| 2–5November | Quantitative results and expert MOS | Reproducible tables with denominators/splits, actual expert responses and limitations; no invented MOS |
| 5–6November | Thesis integration and delivery check | Method/results agree with implementation; APK, Python instructions and evidence bundle; final regression/device check |

Android and thesis preparation can proceed while model-quality issues remain
open. Do not delay every deliverable behind another small model experiment.
Conversely, APK availability does not repair correction performance or validate
MST. A proposed method amendment needs actual agreement; none is assumed here.

## Current concrete progress

The user explicitly retained the paper's MST method on28October. Direct
ITA/Lab prototype results do not authorize dropping MST. [Current implementation
and data checkpoint](mst-method-retained.md). Android remains on hold while
the Python model is prioritized.

The existing Android Compose scaffold was discovered on disk; the old AGENTS.md
description was stale. Its repository currently returns the original URI after a
simulated delay. That is not real inference and must not count as an integrated app.

Gradle8.9 now runs using the locally installed JDK21.0.8. The project retains its
existing AGP8.7.3 configuration. Its required Gradle/JDK compatibility is recorded
in the [official AGP8.7 notes](https://developer.android.com/build/releases/agp-8-7-0-release-notes).
Build-tool cache is isolated under `outputs/android_toolchain/gradle`.
The user confirmed an Android phone but no SDK/Studio. Command-line SDK setup
and the first APK build are now complete: [build results](android-build-results.md).
Fourteen Android-module unit tests pass; lint has no errors and27retained warnings.
The packaged asset and APK signature verify. Actual phone validation remains pending.

Added a platform-independent Java regression-tree evaluator and an Android asset
loader, with a byte-identical copy of the frozen development JSON. This is a
development port, not a model replacement. Script128 compiled the Java source
with `javac --release11` and executed it on the JVM:23saved vectors,12split-boundary
vectors and9additional float32-rounding witnesses exactly match Python leaves
and all parameters;15invalid numeric/graph cases are rejected. Prediction/node
immutability is checked. Android-specific Kotlin JSON loading now compiles and
passes14unit tests; actual device testing remains pending. The original JVM-only
[verification](../outputs/android_tree_parity_v1/verification.json) is retained;
[APK verification](../outputs/android_build_check_v1/verification.json) records the newer result.

## Critical unresolved items

- The four-feature correction model still harms unchanged images; current
  source-held-out controls comparison is worse than no correction. Preserve
  that result. A successful demo cannot be reported as final effective correction.
- Operational ITA→MST is unvalidated. Historical MST-E feasibility work is
  development evidence and cannot be turned into approved training calibration;
  the proposal reserves MST-E for evaluation. Do not manufacture thresholds.
- The32regenerated candidates are not a newly approved core cohort. Changed-mask
  concerns, resolution/policy differences and final FairFace/SCIN roles remain.
- Face/visible-neck correction, actual phone parity/timing, final split/reference
  evidence and two photographers' MOS remain unfinished. Expert participation
  and scheduling require real people; no outreach has been sent.

CPM stays deferred. Paint/makeup remains a limitation. Original reviews, holds,
folds and evaluation allocations remain intact. The explicit Android deliverable
request authorizes extending the existing Android project.

Reproduce JVM parity with a fresh output directory:

```powershell
.\venv\Scripts\python.exe scripts/128_verify_android_tree.py --jdk 'C:\Program Files\Android\openjdk\jdk-21.0.8' --output-dir outputs/android_tree_parity_v2
```
