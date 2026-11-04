# First Android build and SDK setup

28 October2026. User confirmed an available Android phone and no installed
Android Studio/SDK. Installed command-line tools and SDK packages locally;
Android Studio is not required for this workflow.

The debug APK builds successfully and the Android-specific Kotlin asset loader
now compiles. **14 local Android-module unit tests pass** with no skips, failures
or errors. Android lint completes with0errors and27warnings (mostly dependency
update suggestions, plus backup configuration/version-catalog advice). Warnings
are retained in the report; no dependency upgrade sweep was performed.

[Debug APK](../android-app/app/build/outputs/apk/debug/app-debug.apk) ·
[Verification](../outputs/android_build_check_v1/verification.json) ·
[Phone/build instructions](android-device-testing.md).

APK size10,770,836bytes; SHA256
`5e7df735dae338a252eebd6aa9011e27c2fa1c7fc94d28cc6ac732b7ca050d4d`.
The development APK signature verifies. Its packaged tree and checksum exactly
match the frozen Python export, SHA256
`23bdef6cb6fa201d6a1b9c4aca56fe0c71a5b52a8ab3390ba5fe5f7b74115148`.

## Reproduction and checks

Scripts129–131 prepare official tools, build/test/lint and verify output
artifacts. The SDK uses command-line tools19.0, platform35, build-tools34.0.0
and platform-tools37.0.1; local SDK package revisions/properties and download
provenance are recorded. The143,040,480-byte command-line tools archive matches
Google's published SHA1 and locally recorded SHA256. SDK packages were installed
using SDK Manager with standard installation licenses; all dependencies/cache
files remain under ignored workspace paths. Existing JDK21.0.8 and Gradle8.9
are used; the project's existing app plugin/library versions are retained.

Initial restricted networking prevented downloading tools; authorized network
execution succeeded. Initial build stopped at an AAR dependency task and its
full error was obscured by PowerShell native-stderr handling. The script now
preserves diagnostic output and checks the actual exit code. The subsequent
build passes all51tasks without changing dependency versions. Original logs
are retained; the first failure's exact cause is not established.

The14tests verify real bundled JSON loading/prediction, checksum rejection,
schema/name ordering, numeric contracts, strict integer indices, string-number
rejection, cyclic graphs and invalid leaves. Separate prior JVM checks retain
44exact Python-parity vectors and15invalid cases. The new verifier also checks
actual APK structure/signature, packaged assets and real unit/lint XML reports.

```powershell
.\scripts\130_build_android.ps1
.\venv\Scripts\python.exe scripts/131_verify_android_build.py --output-dir outputs/android_build_check_v2
```

Use a fresh verification directory. A built APK may change hash after future
source/build changes; verify the actual delivered artifact again then.

## Implementation boundary

This completes build-tool setup and a buildable scaffold with the tree
component. It does **not** complete on-device image processing: the existing
image repository still passes its input URI through after a simulated delay.
No original-as-corrected result counts as real inference. Detection, masking,
Lab/ITA, actual correction and image saving still need Android integration.
The APK has not been installed, launched or tested on the user's phone.

Operational MST and correction-quality limitations remain. No model fit,
training admission, mask adoption or original review/fold change occurred.
CPM remains deferred. The next implementation work is real on-device pipeline
integration plus phone testing, with Python parity and stage/failure reporting.
