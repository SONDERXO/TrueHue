param(
    [string]$JdkPath = 'C:\Program Files\Android\openjdk\jdk-21.0.8',
    [string[]]$Tasks = @('assembleDebug', 'testDebugUnitTest', 'lintDebug')
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$sdkPath = Join-Path $projectRoot 'outputs\android_toolchain\sdk'
if (-not (Test-Path -LiteralPath (Join-Path $JdkPath 'bin\java.exe'))) {
    throw 'A JDK is required; pass -JdkPath with its installation folder.'
}
if (-not (Test-Path -LiteralPath (Join-Path $sdkPath 'platforms\android-35\android.jar'))) {
    throw 'Install Android SDK platform 35 into outputs/android_toolchain/sdk first.'
}
$env:JAVA_HOME = $JdkPath
$env:ANDROID_HOME = $sdkPath
$env:ANDROID_USER_HOME = Join-Path $projectRoot 'outputs\android_toolchain\android-user'
$env:GRADLE_USER_HOME = Join-Path $projectRoot 'outputs\android_toolchain\gradle'
New-Item -ItemType Directory -Force -Path $env:ANDROID_USER_HOME | Out-Null
$previousErrorPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    & (Join-Path $projectRoot 'android-app\gradlew.bat') -p (Join-Path $projectRoot 'android-app') --no-daemon --console=plain @Tasks
    $gradleExitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $previousErrorPreference
}
if ($gradleExitCode -ne 0) { throw "Android build failed with exit code $gradleExitCode" }
