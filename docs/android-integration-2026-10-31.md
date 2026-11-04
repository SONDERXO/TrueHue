# Android integration checkpoint — 31 October 2026

Later31October: [emulator execution](android-emulator-check-2026-10-31.md) now
records two passing native tests, exact parity for one fixed example and a real
gallery/result/PNG+report export flow on API35 x86_64. This supersedes the
compiled-but-unrun status below for those two tests only. Physical-phone and
broader parity/performance/scientific validation remain pending.

The user resumed Android work while awaiting the adviser. The app's pass-through
and simulated delay are replaced by a local experimental processing flow.
**Native execution and whole-path Python pixel parity remain pending:** the user
has no phone available and ADB lists no phone/emulator. Compilation is not proof
of working device inference or reliable correction quality.

## Implemented code

Gallery URI → bounded decode/EXIF orientation → OpenCV square256 → YuNet0.85,
exactly one face → required MediaPipe landmarks → original HSV AND YCrCb mask,
5x5 open/close/close, largest component and feature/complete-mouth exclusions →
minimum1000 skin pixels → Lab/ITA → experimental MST → five-feature tree →
masked correction. Crop-margin order is retained. No parser or beard model is
added. Neck correction remains unfinished.

The selected tree is the same older ten-source `baseline5`,fold1 as the Python
demo, not the retained eleven-feature endpoint reference or either rejected
successor. It uses reciprocal gamma with red/blue gains; direct-gamma research
targets are never substituted. Tree SHA256:
`81dcc65c9c30c61a70a8c3f123486a09575f06741ee23f98c46a1f069ed018ad`.
Lookup SHA256:
`3e3f3635ed860f68ab664c86f9ac985c7c3e8e461a16475156ebcd0eafe0cd7e`.

Successful results show the256-frame input, selected skin and actual trial PNG.
There is no original-as-corrected fallback; identity predictions may legitimately
leave an input unchanged. Changed pixels are counted. Failure stages explain
the problem and export a report when available. The ViewModel clears prior
outputs and guards against stale completion after a new selection.

Images and reports save through the system document picker on API24+, without
broad storage permission. Original files are never written. Reports include
source/model/output hashes, run identity, features, parameters, stage/timings and
experimental/parity-pending flags. App-private runs stay local without backup.
The main APK contains no dataset photographs. One ignored, previously exposed
demo fixture belongs only to the device-test APK.

OpenCV5.0.0, MediaPipe Tasks Vision0.10.35 and ExifInterface1.3.7 are pinned.
Native API sources: [OpenCV](https://docs.opencv.org/4.x/javadoc/org/opencv/objdetect/FaceDetectorYN.html)
and [MediaPipe](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/android).
Existing models are bundled locally with checksum checks and no runtime download.
`scripts/321_prepare_android_pipeline_assets.py --verify` checks the bundled
assets against the originals. Models remain ignored; a fresh clone needs the
existing local assets. No Python measurement dependency, model or calibration
changed, and no reserved data or new fitting was used.

## Explicit port limitations

Android BitmapFactory subsamples large images and handles EXIF before OpenCV
resizing. Decode/color behavior can differ from Python. Per-sample Lab uses
float32 conversion, but double mean accumulation does not reproduce every NumPy
reduction detail. Native detection/landmarks may also differ. These can alter
rounded features, tree routing and output.

The port has a separate `android_square256_port_v1_parity_pending` measurement
identity. The Python contract hash is provenance, not a claim of validated
Android equivalence or scientifically matching calibration. Do not turn off
pending flags after component tests alone. The visible notice identifies the
failed-quality-gate model and unvalidated MST. No app-quality, fairness or final
thesis completion claim follows from integration.

## Verification

The app and device-test APKs compile. All18 Android JVM tests pass without skips:
14 existing loader/schema tests and4 numerical tests covering20 saved five-feature
tree vectors,47 MST knot/midpoint/endpoint queries and111 Python reciprocal-gamma
pixel outputs. These JVM tests do not run native detection/masking.

Two instrumented tests are compiled but **not run**: a synthetic no-face failure
must export a report without a correction; one fixed exposed development example
must match Python input/mask/output pixels exactly. That parity test can expose
real port differences; no tolerance was relaxed to claim success.

The initial compiler error was an OpenCV5 API move of contourArea to Geometry.
After correcting it, package inspection found a transitive Internet permission.
The app manifest now explicitly strips Internet/network-state permission, and
the final package check verifies this. Separate initial/fixed/offline build logs
are preserved. These are software fixes, not additional model trials.

`scripts/322_verify_android_integration.py` checks APK signature, exact packaged
models, native libraries, absence of dataset photos/network permission, actual
JUnit/lint XML and pending device flags. Final evidence is under
`outputs/android_integration_20261031_v1/`. No new Python full-suite claim is made;
the previous result remains836passed in28.36seconds.

Final debug APK: `android-app/app/build/outputs/apk/debug/app-debug.apk`,
245859122bytes (about234.5MiB). It includes native libraries for multiple CPU
architectures; no size-optimized release is claimed. SHA256:
`626cf6925031cf040438d7a106105ee748b8d6a88c9b0f63cd59256447d2101d`.
Signature, model bytes and absence of Internet permission are verified. These
checks do not replace the unrun device/native tests.

## Next when a phone is available

Android lint reports0errors and44warnings; the complete list remains in the
verification JSON. No unrelated dependency-update or warning cleanup was run.

Follow [device setup](android-device-testing.md), then run
`scripts/130_build_android.ps1 -Tasks @('connectedDebugAndroidTest')` with the
authorized phone connected. Verify native output and gallery/cancel/failure,
PNG/report saving, rotation/background handling and timing on that device. Use
only designated exposed examples, never reserved evaluation photos for debugging.
Investigate port differences before claiming parity; no new training, changed
masking method or model tuning is implied. Parser/beard work stays held, and
thesis comments remain unresolved until final implementation/evaluation.
