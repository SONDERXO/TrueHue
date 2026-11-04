# Build and test TrueHue on a phone

The command-line SDK lives in `outputs/android_toolchain/sdk`; Android Studio
is optional. All commands below run from the project root in PowerShell.
The SDK and Gradle caches are local, ignored build dependencies.

## Build

```powershell
.\scripts\130_build_android.ps1
```

This runs debug assembly, JVM unit tests and Android lint with the local JDK
and SDK. A successful build produces
`android-app/app/build/outputs/apk/debug/app-debug.apk`. It does not establish
pipeline accuracy or phone behavior. The31October integration replaces the
pass-through with experimental native processing and PNG/report saving. Full
native execution, pixel parity and device timing still need a phone/emulator.
No phone was available during integration; do not call compiled device tests passed.

The SDK setup uses official Google command-line tools19.0 and project-required
platform35/build-tools34.0.0. `scripts/129_prepare_android_sdk.py` prepares the
tools; download provenance and the SDK install log are under
`outputs/android_toolchain/`. Package licenses are handled by SDK Manager,
not copied from another installation. Official instructions:
[Android SDK Manager](https://developer.android.com/tools/sdkmanager).

To reproduce SDK installation on this workspace (review any SDK license prompts):

```powershell
.\venv\Scripts\python.exe scripts/129_prepare_android_sdk.py
$env:JAVA_HOME = 'C:\Program Files\Android\openjdk\jdk-21.0.8'
$env:ANDROID_USER_HOME = Join-Path (Get-Location) 'outputs\android_toolchain\android-user'
$sdkPath = Join-Path (Get-Location) 'outputs\android_toolchain\sdk'
& "$sdkPath\cmdline-tools\19.0\bin\sdkmanager.bat" "--sdk_root=$sdkPath" 'platform-tools' 'platforms;android-35' 'build-tools;34.0.0'
```

## Connect the phone

1. Enable Developer options on the phone (usually tap Build number seven times
   in Settings → About phone; manufacturer menus vary).
2. Enable USB debugging, connect a data-capable USB cable and unlock the phone.
3. Approve the USB debugging authorization prompt on the phone.
4. Check the connection:

```powershell
.\outputs\android_toolchain\sdk\platform-tools\adb.exe devices -l
```

The state must be `device`. `unauthorized` means the phone still needs approval.
If no phone appears, check the cable/USB mode and the manufacturer's Windows
USB driver. Device identifiers should stay local; no need to publish them.

After a successful build, install and launch the development APK:

```powershell
.\outputs\android_toolchain\sdk\platform-tools\adb.exe install -r .\android-app\app\build\outputs\apk\debug\app-debug.apk
.\outputs\android_toolchain\sdk\platform-tools\adb.exe shell am start -n com.example.skintonecorrection/.MainActivity
```

If several devices are connected, add `-s <device-id>` immediately after
`adb.exe`. Installation and real phone testing have not happened merely because
these instructions exist.

## Evidence to retain once the pipeline is integrated

Record phone model/Android version, app build and asset checksums, input size,
per-stage timings, successful and rejected cases, MST availability and saving
behavior. Keep Python/image-component parity separate from phone timing and
correction quality. Use designated development examples; do not expose reserved
evaluation images as ad-hoc debugging cases. Preserve original photos and all
existing review decisions. No production accuracy or expert-MOS claim follows
from installing the application.
