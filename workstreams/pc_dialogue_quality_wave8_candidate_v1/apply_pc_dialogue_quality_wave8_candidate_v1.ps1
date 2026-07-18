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

# This is intentionally a separate Steam writer from the candidate builder.
# It accepts only the pinned Wave 7 input and Wave 8 output profiles, creates
# a complete backup before the first replacement, and restores written files
# automatically if any postcondition fails.
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$workspaceCandidateRoot = Join-Path $repoRoot 'tmp\pc_dialogue_quality_wave8_candidate_v1'
$stagingCandidateRoot = Join-Path $env:TEMP 'nobu16_wave8_apply_stage'
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
$changedPaths = @('MSG/JP/msggame.bin', 'MSG_PK/JP/msggame.bin', 'MSG_PK/JP/msgev.bin')
$inputHashes = [ordered]@{
    'MSG/JP/ev_strdata.bin' = '25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834'
    'MSG/JP/msggame.bin' = '83C4DF9326DB1487707FDABE9CF2A00380144D14D3AC4A4FCD02513C8E3C279E'
    'MSG/JP/strdata.bin' = '10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE'
    'MSG_PK/JP/msgbre.bin' = 'E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939'
    'MSG_PK/JP/msgdata.bin' = '8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752'
    'MSG_PK/JP/msgev.bin' = '134F6356B194AE319125D369A23EBDA11CA8C75FB79EFA7C987D956EDD4CF154'
    'MSG_PK/JP/msggame.bin' = '31950B8213AC80C9BCB866163EE7B4B655440ADF863DED21186273E3F8A34BDB'
    'MSG_PK/JP/msgire.bin' = '46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB'
    'MSG_PK/JP/msgstf.bin' = '13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B'
    'MSG_PK/JP/msgstf_ce.bin' = '06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63'
    'MSG_PK/JP/msgui.bin' = '5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7'
}
$targetHashes = [ordered]@{}
foreach ($relative in $profilePaths) { $targetHashes[$relative] = $inputHashes[$relative] }
$targetHashes['MSG/JP/msggame.bin'] = '7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492'
$targetHashes['MSG_PK/JP/msggame.bin'] = '454A18B0F0ED5E39A3AC823AD0A30086C25226BF6E48D4580962DFEE84E24A32'
$targetHashes['MSG_PK/JP/msgev.bin'] = '1880A8052C916FAC7F262CCC8638477F5AA124F248A6468E0533A8E252AB55C5'
$transactionId = 'pc-dialogue-quality-wave8-candidate-v1'
$manifestSchema = 'nobu16.kr.pc-dialogue-quality-wave8-candidate.v1'
$stateSchema = 'nobu16.kr.pc-dialogue-quality-wave8-candidate-apply.v1'

function Fail([string]$Message) { throw $Message }

function Full-Path([string]$Path) {
    return [System.IO.Path]::GetFullPath($Path)
}

function Assert-Under-OneOf([string]$Path, [string[]]$Roots, [string]$Label) {
    $fullPath = Full-Path $Path
    foreach ($root in $Roots) {
        $fullRoot = (Full-Path $root).TrimEnd('\')
        if (($fullPath -eq $fullRoot) -or $fullPath.StartsWith($fullRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
            return $fullPath
        }
    }
    Fail "$Label is outside approved Wave 8 roots: $fullPath"
}

function Get-Sha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { Fail "missing file: $Path" }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Get-Profile([string]$Root, [string]$Label) {
    $profile = [ordered]@{}
    foreach ($relative in $profilePaths) {
        $path = Join-Path $Root ($relative -replace '/', '\')
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { Fail "$Label is missing $relative" }
        $profile[$relative] = Get-Sha256 $path
    }
    return $profile
}

function Get-PropertyValue($Object, [string]$Key, [string]$Label) {
    $property = $Object.PSObject.Properties[$Key]
    if ($null -eq $property) { Fail "$Label is missing $Key" }
    return $property.Value
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

function Assert-Profile($Actual, $Expected, [string]$Label) {
    foreach ($relative in $profilePaths) {
        if ((Get-MapValue $Actual $relative $Label).ToUpperInvariant() -ne $Expected[$relative]) {
            Fail "$Label hash mismatch at ${relative}"
        }
    }
}

function Test-Profile($Actual, $Expected) {
    foreach ($relative in $profilePaths) {
        if ($Actual[$relative] -ne $Expected[$relative]) { return $false }
    }
    return $true
}

function Get-ProfileState([string]$Root, [string]$Label) {
    $profile = Get-Profile $Root $Label
    if (Test-Profile $profile $inputHashes) { return [PSCustomObject]@{ name = 'input'; hashes = $profile } }
    if (Test-Profile $profile $targetHashes) { return [PSCustomObject]@{ name = 'target'; hashes = $profile } }
    Fail "$Label is neither the pinned Wave 7 input nor Wave 8 target profile"
}

function Assert-Game-Stopped {
    $names = @('nobu16', 'nobu16pk', 'nobu16pk_en', 'nobu16_launcher', 'nobu16_sd', 'nobu16pk_sd', 'nobu16pk_en_sd')
    $running = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName.ToLowerInvariant() } | Select-Object -ExpandProperty ProcessName -Unique)
    if ($running.Count -gt 0) { Fail ('close the game and official launcher before applying: ' + ($running -join ', ')) }
}

function Replace-Atomically([string]$Source, [string]$Destination, [string]$ExpectedHash, [string]$Label) {
    $directory = Split-Path -Parent $Destination
    $name = [System.IO.Path]::GetFileName($Destination)
    $temporary = Join-Path $directory ('.' + $name + '.n16kr.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $replaceBackup = Join-Path $directory ('.' + $name + '.n16kr.' + [Guid]::NewGuid().ToString('N') + '.bak')
    try {
        Copy-Item -LiteralPath $Source -Destination $temporary -Force
        if ((Get-Sha256 $temporary) -ne $ExpectedHash) { Fail "$Label temporary hash mismatch" }
        Assert-Game-Stopped
        [System.IO.File]::Replace($temporary, $Destination, $replaceBackup, $true)
        if ((Get-Sha256 $Destination) -ne $ExpectedHash) { Fail "$Label live hash mismatch" }
    }
    finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue }
        if (Test-Path -LiteralPath $replaceBackup) { Remove-Item -LiteralPath $replaceBackup -Force -ErrorAction SilentlyContinue }
    }
}

function Write-State([string]$Path, $State) {
    $State | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Path -Encoding utf8
}

function Restore-Written([System.Collections.Generic.List[string]]$Written, [string]$OriginalRoot) {
    for ($index = $Written.Count - 1; $index -ge 0; $index--) {
        $relative = $Written[$index]
        Replace-Atomically (Join-Path $OriginalRoot ($relative -replace '/', '\')) (Join-Path $SteamRoot ($relative -replace '/', '\')) $inputHashes[$relative] "rollback $relative"
    }
}

$SteamRoot = Full-Path $SteamRoot
$workspaceCandidateRoot = Full-Path $workspaceCandidateRoot
$stagingCandidateRoot = Full-Path $stagingCandidateRoot
$approvedRoots = @($workspaceCandidateRoot, $stagingCandidateRoot)
$BackupRoot = Assert-Under-OneOf $BackupRoot $approvedRoots 'backup root'
if (-not (Test-Path -LiteralPath $SteamRoot -PathType Container)) { Fail "Steam root does not exist: $SteamRoot" }

if ($Operation -eq 'RESTORE') {
    $statePath = Join-Path $BackupRoot 'state.json'
    $originalRoot = Join-Path $BackupRoot 'originals'
    if ((-not (Test-Path -LiteralPath $statePath -PathType Leaf)) -or (-not (Test-Path -LiteralPath $originalRoot -PathType Container))) { Fail 'restore backup is absent or incomplete' }
    $state = Get-Content -LiteralPath $statePath -Raw -Encoding utf8 | ConvertFrom-Json
    if (([string]$state.schema -ne $stateSchema) -or ([string]$state.status -ne 'applied')) { Fail 'restore state is not an applied Wave 8 transaction' }
    foreach ($relative in $changedPaths) {
        if ((Get-Sha256 (Join-Path $originalRoot ($relative -replace '/', '\'))) -ne $inputHashes[$relative]) { Fail "backup hash differs: $relative" }
    }
    $live = Get-ProfileState $SteamRoot 'Steam profile before restore'
    if ($live.name -eq 'input') { [PSCustomObject]@{ status='PASS'; result='already_restored'; writes_performed=$false } | ConvertTo-Json -Compress; return }
    if ($DryRun) { [PSCustomObject]@{ status='PASS'; result='restore_dry_run'; writes_performed=$false } | ConvertTo-Json -Compress; return }
    Assert-Game-Stopped
    foreach ($relative in $changedPaths) {
        Replace-Atomically (Join-Path $originalRoot ($relative -replace '/', '\')) (Join-Path $SteamRoot ($relative -replace '/', '\')) $inputHashes[$relative] "restore $relative"
    }
    if ((Get-ProfileState $SteamRoot 'Steam profile after restore').name -ne 'input') { Fail 'post-restore profile mismatch' }
    $state.status = 'restored'; $state.restored_at_utc = [DateTime]::UtcNow.ToString('o'); Write-State $statePath $state
    [PSCustomObject]@{ status='PASS'; result='restored'; writes_performed=$true; backup_root=$BackupRoot } | ConvertTo-Json -Compress
    return
}

if (-not $CandidateRoot) { Fail 'apply requires -CandidateRoot' }
if (-not $ManifestPath) { Fail 'apply requires -ManifestPath' }
$CandidateRoot = Assert-Under-OneOf $CandidateRoot $approvedRoots 'candidate root'
$ManifestPath = Assert-Under-OneOf $ManifestPath $approvedRoots 'manifest path'
if (-not (Test-Path -LiteralPath $CandidateRoot -PathType Container)) { Fail 'candidate root is absent' }
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) { Fail 'candidate manifest is absent' }
$manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding utf8 | ConvertFrom-Json
if (([string]$manifest.schema -ne $manifestSchema) -or ([string]$manifest.transaction_id -ne $transactionId)) { Fail 'candidate manifest is not the pinned Wave 8 transaction' }
if (@(Compare-Object -ReferenceObject $changedPaths -DifferenceObject @($manifest.changed_paths)).Count -ne 0) { Fail 'candidate changed paths differ' }
Assert-Profile (Get-PropertyValue $manifest 'input_sha256' 'candidate manifest') $inputHashes 'candidate manifest input'
Assert-Profile (Get-PropertyValue $manifest 'output_sha256' 'candidate manifest') $targetHashes 'candidate manifest output'
Assert-Profile (Get-PropertyValue $manifest 'pinned_output_sha256' 'candidate manifest') $targetHashes 'candidate manifest pinned output'
Assert-Profile (Get-Profile $CandidateRoot 'candidate profile') $targetHashes 'candidate profile'

$live = Get-ProfileState $SteamRoot 'Steam profile before apply'
if ($live.name -eq 'target') { [PSCustomObject]@{ status='PASS'; result='already_target'; writes_performed=$false } | ConvertTo-Json -Compress; return }
if (Test-Path -LiteralPath $BackupRoot) { Fail "backup root already exists: $BackupRoot" }
if ($DryRun) { [PSCustomObject]@{ status='PASS'; result='apply_dry_run'; writes_performed=$false; changed_paths=$changedPaths } | ConvertTo-Json -Compress; return }

Assert-Game-Stopped
New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
$originalRoot = Join-Path $BackupRoot 'originals'
$statePath = Join-Path $BackupRoot 'state.json'
$state = [ordered]@{ schema=$stateSchema; status='backed_up'; timestamp_utc=[DateTime]::UtcNow.ToString('o'); steam_root=$SteamRoot; candidate_root=$CandidateRoot; manifest_path=$ManifestPath; changed_paths=$changedPaths; input_sha256=$inputHashes; output_sha256=$targetHashes; written_paths=@() }
$written = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($relative in $changedPaths) {
        $original = Join-Path $originalRoot ($relative -replace '/', '\')
        New-Item -ItemType Directory -Path (Split-Path -Parent $original) -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $SteamRoot ($relative -replace '/', '\')) -Destination $original -Force
        if ((Get-Sha256 $original) -ne $inputHashes[$relative]) { Fail "backup hash mismatch: $relative" }
    }
    Write-State $statePath $state
    foreach ($relative in $changedPaths) {
        $written.Add($relative); $state.written_paths=@($written); Write-State $statePath $state
        Replace-Atomically (Join-Path $CandidateRoot ($relative -replace '/', '\')) (Join-Path $SteamRoot ($relative -replace '/', '\')) $targetHashes[$relative] "apply $relative"
    }
    if ((Get-ProfileState $SteamRoot 'Steam profile after apply').name -ne 'target') { Fail 'post-apply profile mismatch' }
    $state.status='applied'; $state.applied_at_utc=[DateTime]::UtcNow.ToString('o'); $state.written_paths=@($written); Write-State $statePath $state
}
catch {
    $applyError = $_
    try {
        Restore-Written $written $originalRoot
        $state.status='rolled_back_after_failure'; $state.rollback_at_utc=[DateTime]::UtcNow.ToString('o'); Write-State $statePath $state
    }
    catch {
        $state.status='rollback_failed'; $state.rollback_error=$_.Exception.Message; Write-State $statePath $state
        throw "apply failed: $($applyError.Exception.Message); rollback failed: $($_.Exception.Message)"
    }
    throw "apply failed and written files were restored: $($applyError.Exception.Message)"
}
[PSCustomObject]@{ status='PASS'; result='applied'; writes_performed=$true; changed_paths=$changedPaths; backup_root=$BackupRoot } | ConvertTo-Json -Compress
