# Bounded Android reliability check — 31 October 2026

Status: complete for the declared emulator checks. No correction training,
mask-rule changes or new scientific model comparison occurred. The same
experimental baseline5/fold1, lookup and detection/landmark model files remain.

## Results

| Check | Evidence and outcome |
|---|---|
| No face | Native test: explicit face-detection failure, zero faces, no correction, report available |
| Multiple faces | Native test: duplicated existing development face rejected with more-than-one-face message and no correction |
| Cancel selection | Actual system picker: neutral cancellation message; no-photo state and existing selected preview retained in separate checks |
| Cancel PNG/report export | Actual document picker: explicit cancellation message, current result retained, earlier exported bytes unchanged |
| Rotation during processing | Rotation requested while actual ViewModel state was PROCESSING; successful completion followed by explicit Activity recreation retained the same ViewModel/report |
| Select a new photo | Native lifecycle test: old correction/mask/report cleared immediately; invalid new image ended in ERROR without an old correction |
| Supersede a running selection | Native test: replacement invalid input remained selected and ended in ERROR; prior output was not published |
| Failed save and retry | Repository test on emulator: invalid destination failed; a valid destination then received the exact failure-report bytes; source unchanged |
| Numerical regression | The fixed exposed development example still matched Python input/mask/output pixels exactly |

The native lifecycle checks exercise real processing with ActivityScenario;
they are not exhaustive tests of every navigation/configuration interleaving.
The failed-save check exercises local storage/error handling, not every system
document provider. No claims are made about process death, other API/ABI
combinations or physical-phone performance.

## Issues found and addressed

The initial run passed four cases, then native MediaPipe code crashed during
the rotation case; the suite stopped before all six could finish. The initial
XML/log evidence is preserved under `initial_failure/`. It is not hidden or
described as a passing run.

The implementation now owns a checksum-verified direct model buffer until the
native graph closes. Repository processing is serialized; queued work checks
cancellation before starting, while ViewModel generation checks continue to
prevent stale publication. These are lifetime/scheduling safeguards, not changes
to model weights, preprocessing rules or correction parameters. Both were
changed together, so this check does not isolate a single definitive crash cause.
After the changes, all six native tests passed without relaxing assertions or
test tolerances, including the rotation case and exact parity regression.

Cancellation wording was corrected: a cancelled photo picker no longer says
the image is invalid. Photo selection now gives a short confirmation instead
of an internal URI. Cancelling an image/report save explicitly says that the
existing result/report remains unchanged.

## Final verification and artifact

- Six emulator instrumentation tests passed, with no failures/errors/skips.
- Eighteen local Android JVM tests passed.
- Build and lint passed: zero lint errors,45 retained warnings.
- Final APK signature, bundled-model hashes and no-Internet permission checked.
- Actual picker cancellation states were inspected in UI screenshots/XML;
  existing exported PNG/JSON checksums stayed unchanged.

Main evidence: `outputs/android_reliability_20261031_v1/verification.json`,
passing native XML, cancellation records, screenshots/XML and preserved initial
failure evidence. Source, output and report hashes are recorded. These local
QA images include an already exposed development photo and must not be uploaded
as raw dataset material. No new Python full-suite result is claimed; last Python
suite remains836passed in28.36seconds.

Updated APK: `android-app/app/build/outputs/apk/debug/app-debug.apk`.
SHA256: `3720f08a0b1c343ae421163837a09a79655265fa172512a0ed290173abff9780`.
The updated app is installed on the emulator. Old build verifications remain
historical snapshots; this APK supersedes their recorded APK hashes.

This ends the agreed reliability cycle. Do not automatically expand it into
more image/model experiments. Reliable correction, final MST validation, neck
coverage and real-phone evidence remain unfinished. New training and parser/
beard changes stay held; thesis review comments are not marked accepted or final.
