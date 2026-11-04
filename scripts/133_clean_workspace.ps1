param([string]$PlanPath = 'outputs\workspace_cleanup_20261028_v1\plan.json')
$ErrorActionPreference = 'Stop'
$workspace = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path.TrimEnd('\')
$planFile = Join-Path $workspace $PlanPath
$plan = Get-Content -LiteralPath $planFile -Raw | ConvertFrom-Json
if ($plan.root.TrimEnd('\') -ne $workspace) { throw 'Cleanup plan belongs to another workspace.' }
$checked = @()
foreach ($target in $plan.candidates) {
    $relative = $target.path.Replace('\', '/')
    $allowed = $relative -eq '.pytest_cache' -or
        $relative -match '(^|/)__pycache__$' -or
        $relative -match '^outputs/(pytest_[^/]+|[^/]+_pytest_[^/]+|[^/]+_full_tests_v1)$' -or
        $relative -match '^outputs/[^/]+/pytest_tmp$' -or
        $relative -match '^android-app/app/build/(intermediates|tmp|kotlin|generated)$' -or
        $relative -eq 'outputs/android_toolchain/commandlinetools-win-13114758_latest.zip' -or
        $relative -eq 'outputs/android_toolchain/gradle-threads.txt'
    if (-not $allowed) { throw "Unrecognized cleanup target: $relative" }
    $absolute = [IO.Path]::GetFullPath((Join-Path $workspace $relative))
    if (-not $absolute.StartsWith($workspace + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Target escapes workspace: $absolute"
    }
    if ($absolute -ne $target.absolute_path) { throw "Target resolution changed: $relative" }
    if (Test-Path -LiteralPath $absolute) {
        $item = Get-Item -LiteralPath $absolute -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Linked target: $relative" }
        if ($item.PSIsContainer) {
            $links = @(Get-ChildItem -LiteralPath $absolute -Recurse -Force -Attributes ReparsePoint)
            if ($links.Count -gt 0) { throw "Linked descendant in $relative" }
        }
    }
    $checked += [pscustomobject]@{ path=$relative; absolute=$absolute; bytes=$target.bytes; files=$target.files; reason=$target.reason }
}
$results = @()
foreach ($target in $checked) {
    $status = 'already_absent'
    $failure = $null
    try {
        if (Test-Path -LiteralPath $target.absolute) {
            Remove-Item -LiteralPath $target.absolute -Recurse -Force
            $status = 'deleted'
        }
    } catch {
        $status = 'failed'
        $failure = $_.Exception.Message
    }
    $results += [pscustomobject]@{ path=$target.path; status=$status; bytes=$target.bytes; files=$target.files; error=$failure }
}
$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path (Split-Path $planFile) 'deletion_results.json') -Encoding UTF8
$deleted = @($results | Where-Object status -eq 'deleted')
$failed = @($results | Where-Object status -eq 'failed')
[pscustomobject]@{
    deleted_targets=$deleted.Count
    failed_targets=$failed.Count
    deleted_files=($deleted | Measure-Object files -Sum).Sum
    removed_mib=[math]::Round(($deleted | Measure-Object bytes -Sum).Sum / 1MB, 2)
} | ConvertTo-Json
if ($failed.Count -gt 0) { throw 'Some cleanup targets could not be removed; see deletion_results.json.' }
