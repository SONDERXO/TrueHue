# SkinToneCorrection — Android app (thesis)

**WB314 FaceOcc alignment and reprojection, 19 November 2026.** Android detected matching landmarks from two saved detector boxes and returned the same visibility masks as Python on both images. The second alignment differed by one code level in two RGB channel values. Dense parsing and the full research mask rules still need integration before enabling WB314 in the picker. See [geometry verification](../docs/android-faceocc-geometry-2026-11-19.md).

**WB314 FaceOcc network, 19 November 2026.** OpenCV 5.0.0 on an API 35 emulator ran the pinned FaceOcc export on two saved aligned images. Every visibility decision agreed with Python across 131,072 pixels. See [FaceOcc verification](../docs/android-faceocc-research-port-2026-11-19.md).

**WB314 with saved masks, 19 November 2026.** The Android research path now verifies a local asset manifest and its tree, MST mapping and white-balance bank. It normalizes the input, checks that the supplied masks belong to that RGB image, computes all 314 features, predicts five controls and renders the original-size bitmap. One API 35 emulator test used two existing development cases, one adjusted and one preserved. Both matched Python exactly on features, leaf, controls and the exported 512 × 768 PNG pixels. Both fixtures were built from saved normalized photos by integer replication. Their reference masks and outputs remained local and outside the APK.

Build and JVM unit tests also passed. To reproduce the emulator check, prepare a private fixture with `scripts/prepare_android_wb314_parity_fixture.py`, stage the ten fixture files in the debug app's private `files/wb314_parity` directory using a binary-safe transfer, and compare their SHA-256 digests. Run `Wb314ResearchParityTest` with the `wb314ManifestSha` instrumentation argument set to the local manifest digest. An initial text-altering transfer was rejected by the asset check before inference. The run after byte-for-byte staging passed.

The app's regular photo picker still uses the older trial model. The WB314 renderer currently receives measurement, application and protection masks. Automatic masking still requires the matching parser and support rules. Device memory and latency remain to be measured.

**WB314 white-balance port, 19 November 2026.** A local JVM check with the pinned WB_sRGB research assets matched all 726 float32 coefficients from the 20 saved development images and two generated inputs. The check also rejected a flat image with unavailable histogram support. Run `scripts/verify_android_wb314_white_balance.py --jdk <JDK> --output-dir outputs/<new-local-folder>` to reproduce it. The Java calculation adapts Mahmoud Afifi et al.'s [WB_sRGB](https://github.com/mahmoudnafifi/WB_sRGB/tree/98340313cc7d1728e286ad9ba03e8f9a0e8b82c5) under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). The pinned assets and resulting parity bank stay in local research outputs.

The active Android pipeline still uses the older trial model. Full WB314 processing requires matching face and occlusion masks, local research asset integration, and end-to-end device verification of the feature vector, output pixels, memory use and timing.

**WB314 feature assembly, 19 November 2026.** Android has a component for the first 281 WB314 features from normalized RGB, OpenCV Lab and a supplied binary facial measurement mask. These include Lab/ITA, the mapped development MST score, scene summaries, facial green percentiles and colour histograms. The JVM arithmetic matched all 6,182 float32 values across 20 saved development cases and two generated inputs using Python OpenCV Lab bytes. One API 35 emulator test also matched the generated reference for Android OpenCV Lab conversion and assembled all 314 slots with 33 supplied test coefficients. The debug APK and all 18 JVM tests passed.

Run `scripts/verify_android_wb314_image_features.py --jdk <JDK> --output-dir <new-local-folder>` to reproduce the local arithmetic check.

**WB314 tree loader, 19 November 2026.** The Android code can load the frozen 314-feature tree using its expected SHA-256 digest and check the order and range of its five output controls. The compiled loader matched Python exactly on 86 saved development vectors and 27 float32 threshold probes. It rejected an incorrect digest, an invalid feature count and a NaN input. The debug build and 18 JVM unit tests passed. Run `scripts/verify_android_wb314_tree.py --jdk <JDK> --output-dir <new-local-folder>` after building the debug app and its JVM tests.

The verification uses supplied feature vectors on a JVM. The app's photo path uses the older model. WB314 photo integration requires the exact ordered feature pipeline, including the 33 white-balance coefficients, and matching measurement, application and protection masks. The loader checks vector width. Its caller owns feature ordering.

**Original-size export, 19 November 2026.** The Android prototype saves its corrected PNG at the photo's upright dimensions. Detection and measurement use a 256 × 256 analysis image. The app maps the mask back to the original frame and applies the current correction directly to those pixels. Files that exceed the available memory budget produce an error. The selected-skin preview displays the analysis mask.

The debug APK built with JDK 21. Eighteen JVM unit tests and three API 35 emulator tests passed. The export test used a 2304 × 512 fixture derived from the existing reference image. It verified the saved dimensions, an actual correction inside the mapped mask, and exact preservation outside that mask. The test also ran alongside the previous square reference-pixel and no-face tests. Physical-phone memory, latency and the selected WB314 pipeline still require device verification.

**WB314 preparation, 19 November 2026.** The Java WB314 renderer is available as a standalone component. A JVM check matched Python exactly on 32,000 generated RGB8 outputs across five control sets, including identity, positive and negative exposure, colour balance and feathered alpha. It also rejected an application mask that assigned nonzero alpha to a protected pixel. Run `scripts/verify_android_wb314_renderer.py --jdk <JDK> --output-dir <new-local-folder>` from the project root with the Python research environment.

The current Android app runs the older model and mask pipeline. Integration requires the selected model and matching feature and mask implementations, followed by a physical-device check of parity, memory use and latency. The standalone renderer check covers already decoded opaque pixels and supplied masks.

Latest: [5 November consultation demo polish and rebuild](../docs/android-consultation-update-2026-11-05.md).
Before/trial toggle and expandable mask;18JVM tests pass, lint0errors/45warnings.
Updated UI has not been checked on a connected device. Existing models/pipeline
remain; newer Python masks are not included. Debug APK: `app/build/outputs/apk/debug/app-debug.apk`.

Android front-end for *"Smartphone-Based Post-Capture Skin Tone Correction Using ITA
Estimation and Machine Learning"*. The local experimental pipeline is now wired
through photo decode, YuNet, the original rule-based mask, ITA, experimental MST,
the older Python-demo baseline5/fold1 and masked correction. Device behavior and
full Python pixel parity still require verification; correction quality is not
validated. No parser/beard or new correction-model training is included.

## Stack

Current evidence: [31 October emulator reliability check](../docs/android-reliability-check-2026-10-31.md)
records six native tests, eighteen JVM tests and fixed-example Python parity.
Physical-phone and broad parity remain pending. FaceOcc and the newer Python
whole-face/neck correction support are not part of this APK. See the
[1 November delivery checkpoint](../docs/delivery-checkpoint-2026-11-01.md).

| Concern      | Choice                                                                  |
|--------------|-------------------------------------------------------------------------|
| Language     | Kotlin                                                                  |
| UI           | Jetpack Compose (Material 3) — all UI is Compose, no XML layouts        |
| Architecture | Single-activity + one shared `ViewModel` (`MVVM`)                       |
| Navigation   | Navigation Compose (`ui/AppNavHost.kt`)                                 |
| Image loading| Coil (`AsyncImage`)                                                     |
| minSdk / targetSdk | 24 (Android 7.0) / 35 (Android 15)                              |
| JDK / AGP / Gradle | JDK 17+, AGP 8.7.3, Gradle 8.9                                    |

**Why minSdk 24?** ~97 % of active devices. It also lets us use the AndroidX Photo Picker,
which is **backported automatically** to API 24, so the app needs *no storage permissions*
at all (per-URI read grants).

## Project structure

```
android-app/
├── build.gradle.kts              # plugin versions (see gradle/libs.versions.toml)
├── settings.gradle.kts           # repositories + module list
├── gradle.properties             # Gradle daemon, AndroidX flags
├── gradlew / gradlew.bat         # Gradle wrapper (run via these)
├── gradle/
│   ├── wrapper/gradle-wrapper.properties
│   └── libs.versions.toml        # version catalog (all dependency versions here)
└── app/
    ├── build.gradle.kts          # :app module config + dependencies
    ├── proguard-rules.pro
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/example/skintonecorrection/
        │   ├── MainActivity.kt                 # single entry point
        │   ├── data/ImageRepository.kt         # local experimental decode/pipeline/results
        │   ├── util/Constants.kt               # routes + timing
        │   └── ui/
        │       ├── AppNavHost.kt               # navigation graph
        │       ├── SharedViewModel.kt          # shared state across screens
        │       ├── theme/{Color,Type,Theme}.kt # Material 3 theme
        │       ├── splash/SplashScreen.kt      # optional branding screen
        │       ├── home/HomeScreen.kt          # gallery selection
        │       ├── processing/ProcessingScreen.kt
        │       └── result/ResultScreen.kt
        └── res/
            ├── drawable/ic_launcher.xml        # simple vector icon
            └── values/{strings,colors,themes}.xml
```

## Opening the project in Android Studio

1. Install **Android Studio** (Ladybug 2024.2.1 or newer). It bundles JDK 17+ and the
   Android SDK. *Beware Android Studio versions before 2024.2.1 can also work; anything
   recent is fine.*
2. **Open this folder** (`android-app/`), not the repo root:
   `File > Open…` → select the `android-app` directory → OK.
3. **Let Gradle sync.** On first open Android Studio may ask to trust the project / Gradle.
   Accept. It will download Gradle 8.9 (a Gradle distribution, ~130 MB once) and all
   dependencies. `local.properties` (SDK path) is auto-generated — don't commit it.
4. If sync complains about the wrapper, choose *File > Sync Project with Gradle Files*
   again, or *Build > Rebuild Project*.

> If you prefer to build from the command line:
> `.\gradlew assembleDebug` (Windows) or `./gradlew assembleDebug` (macOS/Linux).

## Running the app

### On an emulator
1. *Tools > Device Manager* → *Create virtual device* → pick any phone profile.
2. Choose a system image (API 35 recommended; API 24+ is fine).
3. Start the emulator, then press **Run ▶** in the toolbar (target = the running emulator).

### On a physical device
1. Enable **Developer options**: Settings → About phone → tap *Build number* 7×.
2. In *Developer options* enable **USB debugging**.
3. Plug in the phone; accept the debug authorization prompt.
4. Press **Run ▶** and pick your device.

## Expected behaviour

| Screen        | What happens                                                                 |
|---------------|------------------------------------------------------------------------------|
| Splash        | Shows the app title for 1.5 s, then Home. *(Optional — delete if unwanted.)* |
| Home          | Tap *Select Photo* → Android Photo Picker. A preview + a Snackbar showing the picked `content://` URI appear. *Process Image* is enabled only after a photo is chosen. |
| Processing    | Runs the experimental image pipeline off the UI thread; failure gives an explanation and an exportable report. |
| Result        | Shows photo used, selected skin and actual trial output; exports PNG/report through the system file picker. |

## Implemented vs. stub

**Implemented in code:** selection, bounded decode/EXIF orientation, square256
OpenCV processing, YuNet, required MediaPipe landmarks, HSV/YCrCb and complete-mouth
exclusions, Lab/ITA, experimental MST, five-feature tree, reciprocal-gamma masked
output, result views, PNG/report export, explicit failure and stale-result handling.
There is no fake processing delay or original-as-corrected fallback.

**Still pending:** native pipeline/device execution and pixel parity, usability
on a physical phone, device timing, robust correction quality, final MST
validation and neck coverage. Android subsampling and mean accumulation are
declared port differences; the old Python measurement hash is provenance, not
a claim that Android measurements are already validated as equivalent.

Before building from the existing local Python evidence:

```powershell
venv\Scripts\python.exe scripts/321_prepare_android_pipeline_assets.py
```

If assets already exist, use `--verify` instead. Model assets stay ignored and
are unavailable in a new clone without the existing local artifacts. The original
four-feature asset is retained for historical component tests; the app's image
pipeline explicitly loads the separate five-feature demo baseline. No raw dataset
photo is included in the main APK. The one local instrumentation photo is ignored
and belongs only to the device-test APK.

## Troubleshooting

- **Gradle sync fails / "Gradle wrapper not found"**: make sure you open `android-app/`
  (not the repo root), that `gradle/wrapper/gradle-wrapper.jar` exists, and that you have
  a working internet connection. Try *File > Invalidate Caches / Restart*.
- **"SDK location not found"**: Android Studio writes `local.properties` with your SDK
  path. Ensure you're opening the project in Studio (not CLI first) so it can set it.
- **Photo Picker says no image found**: that's the cancel path. On an emulator, push a
  test image first (`adb push pic.jpg /sdcard/Pictures/`).
- **Model checksum mismatch**: rerun the asset verifier; do not silently substitute
  another tree or calibration. The experimental status must remain visible.
- **JDK errors**: AGP 8.7 needs JDK 17+. Studio bundles one; make sure Gradle JVM in
  *Settings > Build Tools > Gradle* points to the Studio JBR.
