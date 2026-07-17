[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('APPLY', 'RESTORE')]
    [string]$ApplyToken,

    [string]$SteamRoot = 'F:\SteamLibrary\steamapps\common\NOBU16',

    [string]$CandidateRoot,

    [string]$VerificationPath,

    [Parameter(Mandatory = $true)]
    [string]$BackupRoot,

    [switch]$DryRun,

    [switch]$Restore
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$resource = 'MSG_PK/JP/msgev.bin'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$repoTmp = Join-Path $repoRoot 'tmp'
if (-not $CandidateRoot) { $CandidateRoot = Join-Path $repoTmp 'steam_jp_msgev_full_layout_v2\candidate' }
if (-not $VerificationPath) { $VerificationPath = Join-Path $PSScriptRoot 'verification.v2.json' }

function Fail([string]$Message) { throw $Message }
function FullPath([string]$Path) { return [System.IO.Path]::GetFullPath($Path) }

function Assert-Under([string]$Path, [string]$Root, [string]$Label) {
    $fullPath = FullPath $Path
    $fullRoot = (FullPath $Root).TrimEnd('\')
    if (($fullPath -ne $fullRoot) -and (-not $fullPath.StartsWith($fullRoot + '\', [System.StringComparison]::OrdinalIgnoreCase))) {
        Fail "$Label must remain below ${fullRoot}: $fullPath"
    }
    return $fullPath
}

function Get-Spec([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer) { Fail "expected a file: $Path" }
    return [PSCustomObject]@{
        size = [Int64]$item.Length
        sha256 = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
    }
}

function Same-Spec($Actual, $Expected) {
    return (($Actual.size -eq [Int64]$Expected.size) -and ($Actual.sha256 -eq ([string]$Expected.sha256).ToUpperInvariant()))
}

function Assert-Spec($Actual, $Expected, [string]$Label) {
    if (-not (Same-Spec $Actual $Expected)) {
        Fail "$Label differs: actual $($Actual.sha256)/$($Actual.size), expected $($Expected.sha256)/$($Expected.size)"
    }
}

function Assert-GameStopped {
    $names = @('nobu16', 'nobu16pk', 'nobu16pk_en', 'nobu16_launcher', 'nobu16_sd', 'nobu16pk_sd', 'nobu16pk_en_sd')
    $running = @(Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $names -contains $_.ProcessName.ToLowerInvariant() } |
        Select-Object -ExpandProperty ProcessName -Unique)
    if ($running.Count -gt 0) { Fail ('Close the game and official launcher before applying: ' + ($running -join ', ')) }
}

function Replace-From([string]$Source, [string]$Destination, $Expected, [string]$Label) {
    $directory = Split-Path -Parent $Destination
    $temporary = Join-Path $directory ('.' + [System.IO.Path]::GetFileName($Destination) + '.n16kr.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $replaceBackup = Join-Path $directory ('.' + [System.IO.Path]::GetFileName($Destination) + '.n16kr.' + [Guid]::NewGuid().ToString('N') + '.bak')
    try {
        Copy-Item -LiteralPath $Source -Destination $temporary -Force
        Assert-Spec (Get-Spec $temporary) $Expected "$Label staged"
        Assert-GameStopped
        [System.IO.File]::Replace($temporary, $Destination, $replaceBackup, $true)
        Assert-Spec (Get-Spec $Destination) $Expected "$Label live"
    }
    finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue }
        if (Test-Path -LiteralPath $replaceBackup) { Remove-Item -LiteralPath $replaceBackup -Force -ErrorAction SilentlyContinue }
    }
}

if ($Restore -and $ApplyToken -ne 'RESTORE') { Fail 'restore requires -ApplyToken RESTORE' }
if ((-not $Restore) -and $ApplyToken -ne 'APPLY') { Fail 'apply requires -ApplyToken APPLY' }

$SteamRoot = FullPath $SteamRoot
$CandidateRoot = Assert-Under $CandidateRoot $repoTmp 'candidate root'
$BackupRoot = Assert-Under $BackupRoot $repoTmp 'backup root'
if (-not (Test-Path -LiteralPath $SteamRoot -PathType Container)) { Fail "Steam root does not exist: $SteamRoot" }
if (-not (Test-Path -LiteralPath $VerificationPath -PathType Leaf)) { Fail "v2 verification is absent: $VerificationPath" }

$verification = Get-Content -LiteralPath $VerificationPath -Raw | ConvertFrom-Json
if ($verification.schema -ne 'nobu16.kr.steam-jp-msgev-full-layout-verification.v2') { Fail "unexpected verification schema: $($verification.schema)" }
if ($verification.resource -ne $resource) { Fail "unexpected verification resource: $($verification.resource)" }
$sourceSpec = $verification.source.packed
$targetSpec = $verification.expected_candidate.packed
if (($null -eq $sourceSpec) -or ($null -eq $targetSpec)) { Fail 'verification lacks packed source/candidate specs' }

$relative = $resource -replace '/', '\'
$live = Join-Path $SteamRoot $relative
$candidate = Join-Path $CandidateRoot $relative
if (-not (Test-Path -LiteralPath $live -PathType Leaf)) { Fail "Steam event file is absent: $live" }

if ($Restore) {
    if (-not (Test-Path -LiteralPath $BackupRoot -PathType Container)) { Fail "restore backup is absent: $BackupRoot" }
    $statePath = Join-Path $BackupRoot 'state.json'
    $original = Join-Path (Join-Path $BackupRoot 'originals') $relative
    if ((-not (Test-Path -LiteralPath $statePath -PathType Leaf)) -or (-not (Test-Path -LiteralPath $original -PathType Leaf))) {
        Fail 'restore requires an applied v2 backup state and original file'
    }
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    if (($state.schema -ne 'nobu16.kr.steam-jp-msgev-full-layout-apply.v2') -or ($state.status -ne 'applied')) {
        Fail 'restore state is not an applied v2 transaction'
    }
    Assert-Spec (Get-Spec $original) $sourceSpec 'restore original'
    $before = Get-Spec $live
    if ((-not (Same-Spec $before $sourceSpec)) -and (-not (Same-Spec $before $targetSpec))) {
        Fail 'Steam event file is neither the frozen source nor v2 target'
    }
    if ($DryRun) {
        [PSCustomObject]@{ status = 'PASS'; result = 'restore_dry_run'; writes_performed = $false; resource = $resource } | ConvertTo-Json -Compress
        return
    }
    Assert-GameStopped
    if (Same-Spec $before $targetSpec) { Replace-From $original $live $sourceSpec 'restore event' }
    Assert-Spec (Get-Spec $live) $sourceSpec 'post-restore event'
    $state.status = 'restored'
    $state.restored_at_utc = [DateTime]::UtcNow.ToString('o')
    $state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $statePath -Encoding UTF8
    [PSCustomObject]@{ status = 'PASS'; result = 'restored'; resource = $resource; font_files_written = $false } | ConvertTo-Json -Compress
    return
}

if (-not (Test-Path -LiteralPath $CandidateRoot -PathType Container)) { Fail "candidate root is absent: $CandidateRoot" }
if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { Fail "candidate event file is absent: $candidate" }
if (Test-Path -LiteralPath $BackupRoot) { Fail "backup root already exists: $BackupRoot" }
Assert-Spec (Get-Spec $candidate) $targetSpec 'candidate event'
$before = Get-Spec $live
if ((-not (Same-Spec $before $sourceSpec)) -and (-not (Same-Spec $before $targetSpec))) {
    Fail 'Steam event file is neither the frozen source nor v2 target'
}
$action = if (Same-Spec $before $targetSpec) { 'already_target' } else { 'replace' }
Assert-GameStopped
if ($DryRun) {
    [PSCustomObject]@{ status = 'PASS'; result = 'apply_dry_run'; action = $action; writes_performed = $false; resource = $resource; font_files_written = $false } | ConvertTo-Json -Compress
    return
}
if ($action -eq 'already_target') {
    [PSCustomObject]@{ status = 'PASS'; result = 'already_target'; resource = $resource; writes_performed = $false; font_files_written = $false } | ConvertTo-Json -Compress
    return
}

New-Item -ItemType Directory -Path (Join-Path $BackupRoot 'originals\MSG_PK\JP') -Force | Out-Null
$original = Join-Path (Join-Path $BackupRoot 'originals') $relative
Copy-Item -LiteralPath $live -Destination $original -Force
Assert-Spec (Get-Spec $original) $sourceSpec 'saved event original'
Replace-From $candidate $live $targetSpec 'apply event'
Assert-Spec (Get-Spec $live) $targetSpec 'post-apply event'
$state = [ordered]@{
    schema = 'nobu16.kr.steam-jp-msgev-full-layout-apply.v2'
    status = 'applied'
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    steam_root = $SteamRoot
    candidate_root = $CandidateRoot
    resource = $resource
    action = $action
    source = $sourceSpec
    target = $targetSpec
    font_files_written = $false
}
$state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $BackupRoot 'state.json') -Encoding UTF8
[PSCustomObject]@{ status = 'PASS'; result = $action; resource = $resource; backup_root = $BackupRoot; font_files_written = $false } | ConvertTo-Json -Compress
