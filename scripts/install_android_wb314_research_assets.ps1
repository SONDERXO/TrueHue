param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9_.:-]+$')]
    [string]$Serial,
    [string]$Adb,
    [switch]$PickerTest
)

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
if (-not $Adb) {
    $Adb = Join-Path $root 'outputs/android_toolchain/sdk/platform-tools/adb.exe'
}
$Adb = (Resolve-Path -LiteralPath $Adb).Path
$package = 'com.example.skintonecorrection'
if ($PickerTest) { $package += '.pickertest' }
$destination = 'files/wb314_models'
$assets = [ordered]@{
    'manifest.json' = @('outputs/wb314_android_research_parity_v1/manifest.json', 'b1146aff3c5a190b9e495c62caef44e573d28674cb5050c479051314593b8de6')
    'model.json' = @('outputs/wb314_android_research_parity_v1/model.json', '7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f')
    'mapping.json' = @('outputs/wb314_android_research_parity_v1/mapping.json', '6863575e284a6495e71e7445c88445d4215300db95f2b9111a43cd2191fe6be3')
    'wb_srgb.bin' = @('outputs/wb314_android_research_parity_v1/wb_srgb.bin', '055558a79e77cc3c9c15069690c3ee07e4e2b9de10ea1053f281c9e561647120')
    'yunet.onnx' = @('models/face_detector/face_detection_yunet_2023mar.onnx', '8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4')
    'parser.onnx' = @('models/face_parser_experimental_v1/resnet18.onnx', '0d9bd318e46987c3bdbfacae9e2c0f461cae1c6ac6ea6d43bbe541a91727e33f')
    'faceocc.onnx' = @('outputs/wb314_android_faceocc_v1/fixture/faceocc.onnx', '706b236065be76c0d68a67d5497a53e153debc43894aae0ce16f0fb22eebc936')
    'template.bin' = @('outputs/wb314_android_faceocc_geometry_v1/fixture/template.bin', '3f4f5ef1f0f9ae1acbf4d4756aaa2c1b4a4de1287a3ed570c427e467db3cdd90')
}

foreach ($asset in $assets.GetEnumerator()) {
    $path = Join-Path $root $asset.Value[0]
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash -ne $asset.Value[1]) {
        throw "Local checksum mismatch for $($asset.Key)."
    }
}

& $Adb -s $Serial shell "run-as $package mkdir -p $destination"
if ($LASTEXITCODE -ne 0) { throw 'Install the debug APK on the selected device first.' }

foreach ($asset in $assets.GetEnumerator()) {
    $name = $asset.Key
    $expected = $asset.Value[1]
    $path = Join-Path $root $asset.Value[0]
    $nonce = [Guid]::NewGuid().ToString('N')
    $temporary = "/data/local/tmp/truehue_$nonce"
    $pending = "$destination/$name.$nonce"
    try {
        & $Adb -s $Serial push $path $temporary
        if ($LASTEXITCODE -ne 0) { throw "Could not upload $name." }
        & $Adb -s $Serial shell "run-as $package sh -c 'cat $temporary > $pending'"
        if ($LASTEXITCODE -ne 0) { throw "Could not stage $name." }
        $deviceHash = & $Adb -s $Serial shell "run-as $package sha256sum $pending"
        if ($LASTEXITCODE -ne 0 -or ($deviceHash -split '\s+')[0] -ne $expected) {
            throw "Device checksum mismatch for $name."
        }
        & $Adb -s $Serial shell "run-as $package mv $pending $destination/$name"
        if ($LASTEXITCODE -ne 0) { throw "Could not install $name." }
    } finally {
        & $Adb -s $Serial shell "rm -f $temporary; run-as $package rm -f $pending"
    }
}

Write-Output "Verified $($assets.Count) local WB314 research assets on $Serial."
