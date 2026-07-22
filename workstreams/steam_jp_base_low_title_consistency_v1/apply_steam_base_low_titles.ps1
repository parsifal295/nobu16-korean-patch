[CmdletBinding()]
param(
    [string]$GameRoot = 'F:\SteamLibrary\steamapps\common\NOBU16'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path.TrimEnd('\')
$resolvedGameRoot = [IO.Path]::GetFullPath($GameRoot).TrimEnd('\')
$candidate = [IO.Path]::GetFullPath((Join-Path $repoRoot 'tmp\base_low_title_consistency_dimibang_full_v1\candidate\RES_JP\res_lang.bin'))
$outputRoot = [IO.Path]::GetFullPath((Join-Path $repoRoot 'tmp\base_low_title_consistency_dimibang_full_v1'))
$live = [IO.Path]::GetFullPath((Join-Path $resolvedGameRoot 'RES_JP\res_lang.bin'))
$stage = $live + '.codex-base-low-title-new'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backupRoot = [IO.Path]::GetFullPath((Join-Path $outputRoot ("steam_apply_backup_" + $stamp)))
$backup = Join-Path $backupRoot 'res_lang.before.bin'
$reportPath = Join-Path $backupRoot 'apply_report.json'

$expectedBefore = @{
    size = [int64]160992303
    sha256 = 'D89EAEF8F1EBE15439BC250853C8AB3E219F02422D3393A618D5C80A289BE6FC'
}
$expectedAfter = @{
    size = [int64]154714712
    sha256 = 'FD86E3AEB9F2D2E4E56B1F04E4715B6D999A1414751106C05941B443999F93E3'
}

function Get-Spec([string]$Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{
        size = [int64]$item.Length
        sha256 = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    }
}

function Assert-Spec([string]$Label, [string]$Path, $Expected) {
    $actual = Get-Spec $Path
    if ($actual.size -ne [int64]$Expected.size -or $actual.sha256 -ne [string]$Expected.sha256) {
        throw "$Label differs: size=$($actual.size) sha256=$($actual.sha256)"
    }
    return $actual
}

if (-not $live.StartsWith($resolvedGameRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw "live target escapes game root: $live"
}
if (-not $candidate.StartsWith($repoRoot + '\tmp\', [StringComparison]::OrdinalIgnoreCase)) {
    throw "candidate escapes repository tmp: $candidate"
}
if (-not $backupRoot.StartsWith($outputRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw "backup target escapes output root: $backupRoot"
}
if (-not (Test-Path -LiteralPath (Join-Path $resolvedGameRoot 'NOBU16PK.exe'))) {
    throw "game executable is missing: $resolvedGameRoot"
}
if ((Get-Item -LiteralPath $live).Attributes -band [IO.FileAttributes]::ReparsePoint) {
    throw "live BASE LOW target is a reparse point: $live"
}

$gameProcesses = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -match '^(NOBU16|NOBUNAGA)'
})
if ($gameProcesses.Count -gt 0) {
    throw "game process is running: $($gameProcesses.ProcessName -join ', ')"
}

$beforeSpec = Assert-Spec 'live BASE LOW precondition' $live $expectedBefore
$candidateSpec = Assert-Spec 'BASE LOW title candidate' $candidate $expectedAfter
if (Test-Path -LiteralPath $backupRoot) {
    throw "backup root already exists: $backupRoot"
}
if (Test-Path -LiteralPath $stage) {
    throw "staging file already exists: $stage"
}

New-Item -ItemType Directory -Path $backupRoot | Out-Null
Copy-Item -LiteralPath $live -Destination $backup
$backupSpec = Assert-Spec 'BASE LOW backup' $backup $expectedBefore

$applied = $false
try {
    Copy-Item -LiteralPath $candidate -Destination $stage
    Assert-Spec 'staged BASE LOW candidate' $stage $expectedAfter | Out-Null
    Move-Item -LiteralPath $stage -Destination $live -Force
    $afterSpec = Assert-Spec 'live BASE LOW postcondition' $live $expectedAfter
    $applied = $true
}
catch {
    $failure = $_
    Copy-Item -LiteralPath $backup -Destination $live -Force
    Assert-Spec 'rolled-back live BASE LOW' $live $expectedBefore | Out-Null
    throw $failure
}
finally {
    if (Test-Path -LiteralPath $stage) {
        Remove-Item -LiteralPath $stage -Force
    }
}

$report = [ordered]@{
    schema = 'nobu16.kr.base-low-title-consistency-steam-apply.v1'
    applied = $applied
    applied_at = (Get-Date).ToString('o')
    commit = (& git -C $repoRoot rev-parse HEAD).Trim()
    branch = (& git -C $repoRoot branch --show-current).Trim()
    game_root = $resolvedGameRoot
    game_process_running_at_apply = $false
    changed_outer_entries = @(3)
    changed_title_slots = @(0..109)
    live = [ordered]@{ path = $live; before = $beforeSpec; after = $afterSpec }
    candidate = [ordered]@{ path = $candidate; spec = $candidateSpec }
    backup = [ordered]@{ path = $backup; spec = $backupSpec }
    runtime_qa = [ordered]@{
        performed = $false
        selected_resolution = $null
        full_process_restart_completed = $false
    }
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding utf8
Write-Output ($report | ConvertTo-Json -Depth 8)
Write-Output "report=$reportPath"
