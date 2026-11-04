# Android emulator execution — 31 October 2026

The app now has actual emulator execution evidence, not just a successful build.
The user started TrueHue_API35; ADB initially reported it offline, then Android
completed boot. Environment: Android15/API35, x86_64, emulator hardware ranchu.
No physical phone was used. No correction model was trained or changed.

## Native tests: two passed

`scripts/130_build_android.ps1 -Tasks @('connectedDebugAndroidTest')` completed
successfully. JUnit XML confirms2 tests,0failures,0errors,0skips:

- Synthetic no-face input failed at face detection, reported zero faces and
  produced no corrected image; its failure report existed.
- The fixed, previously exposed development demo example matched Python
  pixel-for-pixel for input, selected mask and corrected output. No tolerance
  was relaxed and no threshold, model or recipe was tuned.

The test was enhanced only to write diagnostic report/images before assertions.
Gradle removes the test installation/data after connected execution, so those
private native-test files were not recovered afterward. The actual passing XML
is preserved. The subsequent real UI run generated separately retrieved files.

## Visible app flow: passed for the designated example

Installed the same experimental main APK manually, imported the existing
development photo into the emulator's Pictures directory and scanned it for
the system picker. Observed/captured the home screen, gallery picker, processing
screen, result input/mask/correction views and save dialog.

The gallery-selected photo processed successfully through native code. Both
PNG and JSON report exported through Android's system document picker to the
emulator Downloads folder. Exported bytes matched the app-private originals;
all output hashes recorded in the report passed. The selected source's bytes
remained unchanged. The UI-run input/mask/output pixels also matched the saved
Python fixture after comparing equivalent image channels.

The trial output visibly retains the known mask-shaped artifacts/overcorrection
of this failed-quality-gate baseline. Successful execution and parity reproduce
that behavior; they do not establish a correction improvement. No new mask review,
clean-source approval or scientific evaluation was inferred from the UI run.

Evidence: `outputs/android_emulator_check_20261031_v1/` contains emulator
metadata, passing native XML, captured UI images/XML, exported PNG/report,
retrieved app-run files and `ui_flow_verification.json`. These local QA artifacts
include the existing development photograph; do not upload/commit them as raw
dataset material. Main APK still contains no dataset photograph. No source or
image was sent to an external inference service.

## What this establishes, and what is still pending

This establishes native execution, no-face failure behavior, exact parity on
one fixed development example and one gallery-to-export user flow on API35
x86_64. The18 JVM component tests from the preceding integration remain separate
evidence; they were not rerun unnecessarily. No new Python full-suite result is
claimed (last836passed in28.36seconds).

It does not validate arbitrary-photo parity, every EXIF/color/decode path,
multiple-face or mask-stage failures, cancelled/failed exports, rotation/process
death, other API/ABI variants, real-phone latency/memory, final MST or reliable
correction quality. Those unchecked cases must not be described as passed.
The global platform-parity flag stays pending despite this successful example.

The app remains installed in the running emulator for the user. Saved files are
in emulator Downloads as `truehue_experimental.png` and `truehue_report.json`.
Future phone testing is still useful; no phone connection is required to use
the emulator now. New model training and parser/beard work remain held.
