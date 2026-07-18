[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('APPLY', 'RESTORE')]
    [string]$Operation,

    [string]$SteamRoot = 'F:\SteamLibrary\steamapps\common\NOBU16',

    [string]$CandidateRoot,

    [string]$ManifestPath,

    [Parameter(Mandatory = $true)]
    [string]$BackupRoot,

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# This is a one-file transaction, but it still verifies the full release
# profile before and after the replacement.  Do not weaken the profile gate:
# the Wave 6 source is explicitly the installed Wave 5 target profile.
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$tmpRoot = Join-Path $repoRoot 'tmp\pc_dialogue_quality_wave6_v1'
# The normal workspace sandbox and the Steam-write context do not share ACLs
# for F:\Games.  This tightly scoped per-user temp root is the only alternate
# staging location accepted by this transaction; all candidate/output hashes
# are still verified before any Steam write.
$stagingRoot = Join-Path $env:TEMP 'nobu16_wave6_apply_stage'
$profilePaths = @(
    'MSG/JP/ev_strdata.bin',
    'MSG/JP/msggame.bin',
    'MSG/JP/strdata.bin',
    'MSG_PK/JP/msgbre.bin',
    'MSG_PK/JP/msgdata.bin',
    'MSG_PK/JP/msgev.bin',
    'MSG_PK/JP/msggame.bin',
    'MSG_PK/JP/msgire.bin',
    'MSG_PK/JP/msgstf.bin',
    'MSG_PK/JP/msgstf_ce.bin',
    'MSG_PK/JP/msgui.bin'
)
$changedPaths = @('MSG_PK/JP/msggame.bin')
$inputHashes = [ordered]@{
    'MSG/JP/ev_strdata.bin' = '25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834'
    'MSG/JP/msggame.bin' = '32247AB97112243E58F8EB5B2930EE8A8AB9DF6A2FE0907A49AE28A255720610'
    'MSG/JP/strdata.bin' = '10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE'
    'MSG_PK/JP/msgbre.bin' = 'E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939'
    'MSG_PK/JP/msgdata.bin' = '8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752'
    'MSG_PK/JP/msgev.bin' = '134F6356B194AE319125D369A23EBDA11CA8C75FB79EFA7C987D956EDD4CF154'
    'MSG_PK/JP/msggame.bin' = '51320EE41C17608BC6DD558B35F5243793BBD74168E51BE8C7F7B65E136B330D'
    'MSG_PK/JP/msgire.bin' = '46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB'
    'MSG_PK/JP/msgstf.bin' = '13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B'
    'MSG_PK/JP/msgstf_ce.bin' = '06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63'
    'MSG_PK/JP/msgui.bin' = '5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7'
}
$targetHashes = [ordered]@{}
foreach ($relative in $profilePaths) { $targetHashes[$relative] = $inputHashes[$relative] }
$targetHashes['MSG_PK/JP/msggame.bin'] = 'CE56A3C6577929513FFEEDFB71637316AA41822DC6F7B26749A6276D572CDF0A'
$manifestSchema = 'nobu16.kr.pc-dialogue-quality-wave6.v1'
$transactionId = 'pc-dialogue-quality-wave6-v1'
$applySchema = 'nobu16.kr.pc-dialogue-quality-wave6-apply.v1'

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

function Assert-Under-OneOf([string]$Path, [string[]]$Roots, [string]$Label) {
    $fullPath = FullPath $Path
    foreach ($root in $Roots) {
        $fullRoot = (FullPath $root).TrimEnd('\')
        if (($fullPath -eq $fullRoot) -or $fullPath.StartsWith($fullRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
            return $fullPath
        }
    }
    Fail "$Label must remain below an approved Wave 6 staging root: $fullPath"
}

function Get-Sha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { Fail "missing file: $Path" }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Get-Profile([string]$Root, [string]$Label) {
    $hashes = [ordered]@{}
    foreach ($relative in $profilePaths) {
        $path = Join-Path $Root ($relative -replace '/', '\')
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { Fail "$Label is missing $relative" }
        $hashes[$relative] = Get-Sha256 $path
    }
    return $hashes
}

function Get-MapValue($Map, [string]$Key, [string]$Label) {
    if ($Map -is [System.Collections.IDictionary]) {
        if (-not $Map.Contains($Key)) { Fail "$Label is missing $Key" }
        return [string]$Map[$Key]
    }
    $property = $Map.PSObject.Properties[$Key]
    if ($null -eq $property) { Fail "$Label is missing $Key" }
    return [string]$property.Value
}

function Assert-HashMap($Actual, $Expected, [string]$Label) {
    foreach ($relative in $profilePaths) {
        $actualValue = Get-MapValue $Actual $relative "$Label actual hash map"
        $expectedValue = Get-MapValue $Expected $relative "$Label expected hash map"
        if ($actualValue.ToUpperInvariant() -ne $expectedValue.ToUpperInvariant()) {
            Fail "$Label hash mismatch at ${relative}: actual $actualValue, expected $expectedValue"
        }
    }
}

function Get-ProfileState([string]$Root, [string]$Label) {
    $profile = Get-Profile $Root $Label
    $isInput = $true
    $isTarget = $true
    foreach ($relative in $profilePaths) {
        if ($profile[$relative] -ne $inputHashes[$relative]) { $isInput = $false }
        if ($profile[$relative] -ne $targetHashes[$relative]) { $isTarget = $false }
    }
    if ($isInput) { return [PSCustomObject]@{ name = 'input'; hashes = $profile } }
    if ($isTarget) { return [PSCustomObject]@{ name = 'target'; hashes = $profile } }
    $mismatches = @()
    foreach ($relative in $profilePaths) {
        if (($profile[$relative] -ne $inputHashes[$relative]) -and ($profile[$relative] -ne $targetHashes[$relative])) {
            $mismatches += "$relative=$($profile[$relative])"
        }
    }
    Fail "$Label is neither the approved input nor Wave 6 target profile: $($mismatches -join '; ')"
}

function Assert-GameStopped {
    $names = @('nobu16', 'nobu16pk', 'nobu16pk_en', 'nobu16_launcher', 'nobu16_sd', 'nobu16pk_sd', 'nobu16pk_en_sd')
    $running = @(Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $names -contains $_.ProcessName.ToLowerInvariant() } |
        Select-Object -ExpandProperty ProcessName -Unique)
    if ($running.Count -gt 0) { Fail ('close the game and official launcher before applying: ' + ($running -join ', ')) }
}

function Replace-From([string]$Source, [string]$Destination, [string]$ExpectedHash, [string]$Label) {
    $directory = Split-Path -Parent $Destination
    $name = [System.IO.Path]::GetFileName($Destination)
    $temporary = Join-Path $directory ('.' + $name + '.n16kr.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $replaceBackup = Join-Path $directory ('.' + $name + '.n16kr.' + [Guid]::NewGuid().ToString('N') + '.bak')
    try {
        Copy-Item -LiteralPath $Source -Destination $temporary -Force
        if ((Get-Sha256 $temporary) -ne $ExpectedHash) { Fail "$Label temporary hash mismatch" }
        Assert-GameStopped
        [System.IO.File]::Replace($temporary, $Destination, $replaceBackup, $true)
        if ((Get-Sha256 $Destination) -ne $ExpectedHash) { Fail "$Label live hash mismatch" }
    }
    finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue }
        if (Test-Path -LiteralPath $replaceBackup) { Remove-Item -LiteralPath $replaceBackup -Force -ErrorAction SilentlyContinue }
    }
}

function Write-State([string]$Path, $State) {
    $State | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Path -Encoding UTF8
}

function Restore-Written([System.Collections.Generic.List[string]]$Written, [string]$OriginalRoot) {
    for ($index = $Written.Count - 1; $index -ge 0; $index--) {
        $relative = $Written[$index]
        $live = Join-Path $SteamRoot ($relative -replace '/', '\')
        $original = Join-Path $OriginalRoot ($relative -replace '/', '\')
        Replace-From $original $live $inputHashes[$relative] "rollback $relative"
    }
}

$SteamRoot = FullPath $SteamRoot
$tmpRoot = FullPath $tmpRoot
$stagingRoot = FullPath $stagingRoot
$approvedStorageRoots = @($tmpRoot, $stagingRoot)
$BackupRoot = Assert-Under-OneOf $BackupRoot $approvedStorageRoots 'backup root'
if (-not (Test-Path -LiteralPath $SteamRoot -PathType Container)) { Fail "Steam root does not exist: $SteamRoot" }

if ($Operation -eq 'RESTORE') {
    if (-not (Test-Path -LiteralPath $BackupRoot -PathType Container)) { Fail "restore backup is absent: $BackupRoot" }
    $statePath = Join-Path $BackupRoot 'state.json'
    $originalRoot = Join-Path $BackupRoot 'originals'
    if ((-not (Test-Path -LiteralPath $statePath -PathType Leaf)) -or (-not (Test-Path -LiteralPath $originalRoot -PathType Container))) {
        Fail 'restore requires an applied Wave 6 backup state and originals'
    }
    $state = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (($state.schema -ne $applySchema) -or ($state.status -ne 'applied')) { Fail 'restore state is not an applied Wave 6 transaction' }
    $original = Join-Path $originalRoot 'MSG_PK\JP\msggame.bin'
    if ((Get-Sha256 $original) -ne $inputHashes['MSG_PK/JP/msggame.bin']) { Fail 'restore original hash mismatch' }
    $liveState = Get-ProfileState $SteamRoot 'Steam profile before restore'
    if ($liveState.name -eq 'input') {
        [PSCustomObject]@{ status = 'PASS'; result = 'already_restored'; writes_performed = $false } | ConvertTo-Json -Compress
        return
    }
    if ($DryRun) {
        [PSCustomObject]@{ status = 'PASS'; result = 'restore_dry_run'; writes_performed = $false } | ConvertTo-Json -Compress
        return
    }
    Assert-GameStopped
    Replace-From $original (Join-Path $SteamRoot 'MSG_PK\JP\msggame.bin') $inputHashes['MSG_PK/JP/msggame.bin'] 'restore MSG_PK/JP/msggame.bin'
    if ((Get-ProfileState $SteamRoot 'Steam profile after restore').name -ne 'input') { Fail 'post-restore profile is not the approved input' }
    $state.status = 'restored'
    $state.restored_at_utc = [DateTime]::UtcNow.ToString('o')
    Write-State $statePath $state
    [PSCustomObject]@{ status = 'PASS'; result = 'restored'; writes_performed = $true; backup_root = $BackupRoot } | ConvertTo-Json -Compress
    return
}

if (-not $CandidateRoot) { Fail 'apply requires -CandidateRoot' }
if (-not $ManifestPath) { Fail 'apply requires -ManifestPath' }
$CandidateRoot = Assert-Under-OneOf $CandidateRoot $approvedStorageRoots 'candidate root'
$ManifestPath = Assert-Under-OneOf $ManifestPath $approvedStorageRoots 'manifest path'
if (-not (Test-Path -LiteralPath $CandidateRoot -PathType Container)) { Fail "candidate root is absent: $CandidateRoot" }
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) { Fail "candidate manifest is absent: $ManifestPath" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (($manifest.schema -ne $manifestSchema) -or ($manifest.transaction_id -ne $transactionId)) { Fail 'candidate manifest is not the pinned Wave 6 transaction' }
$manifestPaths = @($manifest.changed_paths)
if (@(Compare-Object -ReferenceObject $changedPaths -DifferenceObject $manifestPaths).Count -ne 0) { Fail 'candidate manifest changed paths differ' }
Assert-HashMap $manifest.input_sha256 $inputHashes 'candidate manifest input'
Assert-HashMap $manifest.output_sha256 $targetHashes 'candidate manifest output'
if ($null -eq $manifest.pinned_output_sha256) { Fail 'candidate manifest output profile is not pinned' }
Assert-HashMap $manifest.pinned_output_sha256 $targetHashes 'candidate manifest pinned output'
Assert-HashMap (Get-Profile $CandidateRoot 'candidate profile') $targetHashes 'candidate profile'

$liveState = Get-ProfileState $SteamRoot 'Steam profile before apply'
if ($liveState.name -eq 'target') {
    [PSCustomObject]@{ status = 'PASS'; result = 'already_target'; writes_performed = $false } | ConvertTo-Json -Compress
    return
}
if (Test-Path -LiteralPath $BackupRoot) { Fail "backup root already exists: $BackupRoot" }
if ($DryRun) {
    [PSCustomObject]@{ status = 'PASS'; result = 'apply_dry_run'; writes_performed = $false; changed_paths = $changedPaths } | ConvertTo-Json -Compress
    return
}

Assert-GameStopped
New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
$originalRoot = Join-Path $BackupRoot 'originals'
$statePath = Join-Path $BackupRoot 'state.json'
$original = Join-Path $originalRoot 'MSG_PK\JP\msggame.bin'
New-Item -ItemType Directory -Path (Split-Path -Parent $original) -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $SteamRoot 'MSG_PK\JP\msggame.bin') -Destination $original -Force
if ((Get-Sha256 $original) -ne $inputHashes['MSG_PK/JP/msggame.bin']) { Fail 'saved backup hash mismatch' }
$state = [ordered]@{
    schema = $applySchema
    status = 'backed_up'
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    steam_root = $SteamRoot
    candidate_root = $CandidateRoot
    manifest_path = $ManifestPath
    changed_paths = $changedPaths
    input_sha256 = $inputHashes
    output_sha256 = $targetHashes
    written_paths = @()
}
Write-State $statePath $state

$written = [System.Collections.Generic.List[string]]::new()
try {
    $relative = 'MSG_PK/JP/msggame.bin'
    $candidate = Join-Path $CandidateRoot 'MSG_PK\JP\msggame.bin'
    $live = Join-Path $SteamRoot 'MSG_PK\JP\msggame.bin'
    # Persist the written path before replacing it: a post-replace hash failure
    # must still trigger rollback from the captured original.
    $written.Add($relative)
    $state.written_paths = @($written)
    Write-State $statePath $state
    Replace-From $candidate $live $targetHashes[$relative] "apply $relative"
    if ((Get-ProfileState $SteamRoot 'Steam profile after apply').name -ne 'target') { Fail 'post-apply profile is not the pinned Wave 6 target' }
    $state.status = 'applied'
    $state.applied_at_utc = [DateTime]::UtcNow.ToString('o')
    $state.written_paths = @($written)
    Write-State $statePath $state
}
catch {
    $applyError = $_
    try {
        Restore-Written $written $originalRoot
        $state.status = 'rolled_back_after_failure'
        $state.rollback_at_utc = [DateTime]::UtcNow.ToString('o')
        Write-State $statePath $state
    }
    catch {
        $state.status = 'rollback_failed'
        $state.rollback_error = $_.Exception.Message
        Write-State $statePath $state
        throw "apply failed: $($applyError.Exception.Message); automatic rollback also failed: $($_.Exception.Message)"
    }
    throw "apply failed and written files were restored: $($applyError.Exception.Message)"
}
[PSCustomObject]@{ status = 'PASS'; result = 'applied'; writes_performed = $true; changed_paths = $changedPaths; backup_root = $BackupRoot } | ConvertTo-Json -Compress
