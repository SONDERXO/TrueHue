# Android consultation demo update — 5 November 2026

User selected polishing and rebuilding the existing Android demo for the adviser
consultation. The updated debug APK is at
`android-app/app/build/outputs/apk/debug/app-debug.apk` (246,286,006bytes).
SHA256: `d169dbb5dd875f72f6bc9d5c2474f47b170fd93d38b94aa182a5f8bf0fa0b99b`.

## What changed

- TrueHue heading, clearer photo-selection instructions and local-processing copy.
- Result screen switches between Before and Trial correction in the same image
  area, using the same256px working input for a fair visual comparison.
- Expandable selected-skin mask with an explanation of white pixels.
- Short prototype notices retain the older model's failed quality checks and
  unvalidated status. Newer masking remains Python development work.
- Processing/failure screen scrolls and shows the complete photo preview.
- Removed stale result text claiming correction was a placeholder.

The detection, skin measurement, MST lookup, correction tree, model files and
correction mathematics were not updated. No research model was trained or adopted.
No Stellenbosch photos, scores or other dataset images were packaged in the APK.

## Checks and limits

`scripts/130_build_android.ps1 -Tasks assembleDebug,testDebugUnitTest,lintDebug`
completed successfully:51tasks,22executed;18JVM tests passed, zero lint errors,
45lint warnings. Kotlin could not write its external daemon cache and successfully
used its fallback compiler. This was not an automatic-review rejection.

Script437 verified APK signature, packaged model checksums against the existing
manifest, absence of packaged dataset image assets and absence of INTERNET
permission. Evidence: `outputs/android_consultation_20261105_v1/verification.json`.
No connected phone/emulator was available; no new native tests or visual device
verification are claimed. Earlier native-test results are historical evidence.

## Consultation walkthrough

1. Install the rebuilt debug APK on your Android phone and open the app.
2. Choose a personal or otherwise permitted photo with one clearly visible face.
3. Generate a trial correction, then switch Before/Trial correction.
4. Expand Inspect selected skin and discuss missing skin or unwanted selections.
5. Explain that this demonstrates the app flow and older local pipeline; the
   improved Python masking and final correction model remain development work.

Check this flow on the actual presentation phone before the meeting. Dataset
access does not permit sharing restricted photos with others; use a permitted
demo photo. The APK is a development build, not a validated release.
