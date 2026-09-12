# SkinToneCorrection — Android app (thesis)

Android front-end for *"Smartphone-Based Post-Capture Skin Tone Correction Using ITA
Estimation and Machine Learning"*. This is **Thesis 2** UI scaffolding: it compiles and
runs, but the ML pipeline is **stubbed** (see [Implemented vs. stub](#implemented-vs-stub)).

## Stack

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
        │   ├── data/ImageRepository.kt         # STUB: future ML pipeline
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
| Processing    | *Process Image* starts a simulated **2 s** delay; then auto-navigates to Result. |
| Result        | Shows the same image twice (Original / Corrected placeholder), *Re-select Photo* back to Home, *Save Corrected Image* → Snackbar "Save not implemented yet". |

## Implemented vs. stub

**Implemented:** app skeleton, navigation, Photo Picker, image previews, simulated
processing, error state wiring, theming.

**Stubbed (marked `TODO(ml-pipeline)`):**
- `ImageRepository.runCorrection(...)` returns the input unchanged.
- `SharedViewModel.startProcessing()` uses a fake delay, no real correction.
- Saving the corrected image (`TODO(media-store)`).

The real pipeline (face detection → skin mask → ITA → MST → decision tree → correction)
mirrors the Python repo (`src/` top level) and will replace those stubs.

## Troubleshooting

- **Gradle sync fails / "Gradle wrapper not found"**: make sure you open `android-app/`
  (not the repo root), that `gradle/wrapper/gradle-wrapper.jar` exists, and that you have
  a working internet connection. Try *File > Invalidate Caches / Restart*.
- **"SDK location not found"**: Android Studio writes `local.properties` with your SDK
  path. Ensure you're opening the project in Studio (not CLI first) so it can set it.
- **Photo Picker says no image found**: that's the cancel path. On an emulator, push a
  test image first (`adb push pic.jpg /sdcard/Pictures/`).
- **No ML model yet**: expected — the app deliberately does **not** bundle ONNX
  Runtime/TensorFlow Lite in this milestone.
- **JDK errors**: AGP 8.7 needs JDK 17+. Studio bundles one; make sure Gradle JVM in
  *Settings > Build Tools > Gradle* points to the Studio JBR.