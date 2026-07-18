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

# This is the explicit writer for the candidate-only Python build.  It accepts
# only the full 11-file Steam Wave 9 profile and writes only the two declared
# msggame resources.  Asset work outside those paths is not part of this
# transaction.
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$transactionTmpRoot = Join-Path $repoRoot 'tmp\steam_jp_wave10_12_combined_transaction_v1'
$approvedBackupRoot = Join-Path $transactionTmpRoot 'backups'
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
$changedPaths = @(
    'MSG/JP/msggame.bin',
    'MSG_PK/JP/msggame.bin'
)
$inputHashes = [ordered]@{
    'MSG/JP/ev_strdata.bin' = '3A7BE17B7DA97B89BD82DFFF44EBC28DA2D3AA91D2E970A0F6C26DE22C657A22'
    'MSG/JP/msggame.bin' = '7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492'
    'MSG/JP/strdata.bin' = '10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE'
    'MSG_PK/JP/msgbre.bin' = 'E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939'
    'MSG_PK/JP/msgdata.bin' = '8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752'
    'MSG_PK/JP/msgev.bin' = '73DEC80A85B5441AFFFA725DAB72CF02D334D29B297AD08050BC496D532CB8F3'
    'MSG_PK/JP/msggame.bin' = '209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930'
    'MSG_PK/JP/msgire.bin' = '46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB'
    'MSG_PK/JP/msgstf.bin' = '13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B'
    'MSG_PK/JP/msgstf_ce.bin' = '06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63'
    'MSG_PK/JP/msgui.bin' = '5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7'
}
$targetHashes = [ordered]@{
    'MSG/JP/ev_strdata.bin' = '3A7BE17B7DA97B89BD82DFFF44EBC28DA2D3AA91D2E970A0F6C26DE22C657A22'
    'MSG/JP/msggame.bin' = 'C74A5D2382D809FAF3EF6A78751872C6B99DAC15FCAB21CEA73E0C904736A347'
    'MSG/JP/strdata.bin' = '10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE'
    'MSG_PK/JP/msgbre.bin' = 'E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939'
    'MSG_PK/JP/msgdata.bin' = '8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752'
    'MSG_PK/JP/msgev.bin' = '73DEC80A85B5441AFFFA725DAB72CF02D334D29B297AD08050BC496D532CB8F3'
    'MSG_PK/JP/msggame.bin' = '6557733B50CBA6435FB51EC71472FF4B06A321AF92F825EAA3C531DE7722E0A6'
    'MSG_PK/JP/msgire.bin' = '46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB'
    'MSG_PK/JP/msgstf.bin' = '13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B'
    'MSG_PK/JP/msgstf_ce.bin' = '06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63'
    'MSG_PK/JP/msgui.bin' = '5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7'
}
$transactionId = 'steam-jp-wave10-12-combined-transaction-v1'
$manifestSchema = 'nobu16.kr.steam-jp-wave10-12-combined-transaction.v1'
$stateSchema = 'nobu16.kr.steam-jp-wave10-12-combined-transaction-apply.v1'

function Fail([string]$Message) {
    throw $Message
}

function Full-Path([string]$Path) {
    return [System.IO.Path]::GetFullPath($Path)
}

function Assert-Under([string]$Path, [string]$Root, [string]$Label) {
    $fullPath = Full-Path $Path
    $fullRoot = (Full-Path $Root).TrimEnd('\')
    if (($fullPath -eq $fullRoot) -or $fullPath.StartsWith($fullRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        return $fullPath
    }
    Fail "$Label is outside its approved root: $fullPath"
}

function Get-Sha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Fail "missing file: $Path"
    }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Get-Profile([string]$Root, [string]$Label) {
    $profile = [ordered]@{}
    foreach ($relative in $profilePaths) {
        $path = Join-Path $Root ($relative -replace '/', '\')
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            Fail "$Label is missing $relative"
        }
        $profile[$relative] = Get-Sha256 $path
    }
    return $profile
}

function Get-MapValue($Map, [string]$Key, [string]$Label) {
    if ($Map -is [System.Collections.IDictionary]) {
        if (-not $Map.Contains($Key)) {
            Fail "$Label is missing $Key"
        }
        return [string]$Map[$Key]
    }
    $property = $Map.PSObject.Properties[$Key]
    if ($null -eq $property) {
        Fail "$Label is missing $Key"
    }
    return [string]$property.Value
}

function Get-MapKeys($Map) {
    if ($Map -is [System.Collections.IDictionary]) {
        return @($Map.Keys | ForEach-Object { [string]$_ })
    }
    return @($Map.PSObject.Properties.Name | ForEach-Object { [string]$_ })
}

function Assert-ExactArray($Actual, $Expected, [string]$Label) {
    $actualValues = @($Actual | ForEach-Object { [string]$_ })
    $expectedValues = @($Expected | ForEach-Object { [string]$_ })
    if ($actualValues.Count -ne $expectedValues.Count) {
        Fail "$Label count differs"
    }
    for ($index = 0; $index -lt $expectedValues.Count; $index++) {
        if ($actualValues[$index] -cne $expectedValues[$index]) {
            Fail "$Label differs at index $index"
        }
    }
}

function Assert-HashMap($Actual, $Expected, [string]$Label) {
    $actualKeys = @(Get-MapKeys $Actual | Sort-Object)
    $expectedKeys = @(Get-MapKeys $Expected | Sort-Object)
    Assert-ExactArray $actualKeys $expectedKeys "$Label keys"
    foreach ($relative in $profilePaths) {
        $value = (Get-MapValue $Actual $relative $Label).ToUpperInvariant()
        if ($value -cne $Expected[$relative]) {
            Fail "$Label hash mismatch at $relative"
        }
    }
}

function Test-Profile($Actual, $Expected) {
    foreach ($relative in $profilePaths) {
        if ($Actual[$relative] -cne $Expected[$relative]) {
            return $false
        }
    }
    return $true
}

function Get-ProfileState([string]$Root, [string]$Label) {
    $profile = Get-Profile $Root $Label
    if (Test-Profile $profile $inputHashes) {
        return [PSCustomObject]@{ name = 'input'; hashes = $profile }
    }
    if (Test-Profile $profile $targetHashes) {
        return [PSCustomObject]@{ name = 'target'; hashes = $profile }
    }
    Fail "$Label is neither the pinned Wave9 input nor Wave10--12 target profile"
}

function Assert-Game-Stopped {
    $names = @(
        'nobu16',
        'nobu16pk',
        'nobu16pk_en',
        'nobu16_launcher',
        'nobu16_sd',
        'nobu16pk_sd',
        'nobu16pk_en_sd'
    )
    $running = @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $names -contains $_.ProcessName.ToLowerInvariant() } |
            Select-Object -ExpandProperty ProcessName -Unique
    )
    if ($running.Count -gt 0) {
        Fail ('close the game and official launcher before this transaction: ' + ($running -join ', '))
    }
}

function Replace-Atomically(
    [string]$Source,
    [string]$Destination,
    [string]$ExpectedHash,
    [string]$Label
) {
    $directory = Split-Path -Parent $Destination
    $name = [System.IO.Path]::GetFileName($Destination)
    $temporary = Join-Path $directory ('.' + $name + '.n16kr.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $replaceBackup = Join-Path $directory ('.' + $name + '.n16kr.' + [Guid]::NewGuid().ToString('N') + '.bak')
    try {
        Copy-Item -LiteralPath $Source -Destination $temporary -Force
        if ((Get-Sha256 $temporary) -cne $ExpectedHash) {
            Fail "$Label temporary hash mismatch"
        }
        Assert-Game-Stopped
        try {
            [System.IO.File]::Replace($temporary, $Destination, $replaceBackup, $true)
        }
        catch {
            Fail ("$Label atomic replacement failed: source=[$temporary]; destination=[$Destination]; backup=[$replaceBackup]; error=$($_.Exception.Message)")
        }
        if ((Get-Sha256 $Destination) -cne $ExpectedHash) {
            Fail "$Label live hash mismatch"
        }
    }
    finally {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $replaceBackup) {
            Remove-Item -LiteralPath $replaceBackup -Force -ErrorAction SilentlyContinue
        }
    }
}

function Write-State([string]$Path, $State) {
    $directory = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $temporary = Join-Path $directory ('.state.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $stateBackup = Join-Path $directory ('.state.' + [Guid]::NewGuid().ToString('N') + '.bak')
    try {
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($temporary, ($State | ConvertTo-Json -Depth 12), $encoding)
        if (Test-Path -LiteralPath $Path) {
            [System.IO.File]::Replace($temporary, $Path, $stateBackup, $true)
        }
        else {
            [System.IO.File]::Move($temporary, $Path)
        }
    }
    finally {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $stateBackup) {
            Remove-Item -LiteralPath $stateBackup -Force -ErrorAction SilentlyContinue
        }
    }
}

function Restore-Written(
    [System.Collections.Generic.List[string]]$Written,
    [string]$OriginalRoot
) {
    for ($index = $Written.Count - 1; $index -ge 0; $index--) {
        $relative = $Written[$index]
        $source = Join-Path $OriginalRoot ($relative -replace '/', '\')
        $destination = Join-Path $SteamRoot ($relative -replace '/', '\')
        Replace-Atomically $source $destination $inputHashes[$relative] "rollback $relative"
    }
}

function Assert-CandidateManifest([string]$CandidateRootValue, [string]$ManifestPathValue) {
    if (-not (Test-Path -LiteralPath $CandidateRootValue -PathType Container)) {
        Fail "candidate root is absent: $CandidateRootValue"
    }
    if (-not (Test-Path -LiteralPath $ManifestPathValue -PathType Leaf)) {
        Fail "candidate manifest is absent: $ManifestPathValue"
    }
    $manifest = Get-Content -LiteralPath $ManifestPathValue -Raw -Encoding utf8 | ConvertFrom-Json
    if (([string]$manifest.schema -cne $manifestSchema) -or ([string]$manifest.transaction_id -cne $transactionId)) {
        Fail 'candidate manifest is not the pinned Wave10--12 combined transaction'
    }
    Assert-ExactArray @($manifest.profile_paths) $profilePaths 'candidate manifest profile path order'
    Assert-ExactArray @($manifest.changed_paths) $changedPaths 'candidate manifest changed path order'
    Assert-HashMap $manifest.input_sha256 $inputHashes 'candidate manifest input'
    Assert-HashMap $manifest.output_sha256 $targetHashes 'candidate manifest output'
    Assert-HashMap $manifest.pinned_output_sha256 $targetHashes 'candidate manifest pinned output'
    Assert-HashMap (Get-Profile $CandidateRootValue 'candidate profile') $targetHashes 'candidate profile'
    return $manifest
}

$SteamRoot = Full-Path $SteamRoot
$transactionTmpRoot = Full-Path $transactionTmpRoot
$approvedBackupRoot = Full-Path $approvedBackupRoot
$BackupRoot = Assert-Under $BackupRoot $approvedBackupRoot 'backup root'
if (-not (Test-Path -LiteralPath $SteamRoot -PathType Container)) {
    Fail "Steam root does not exist: $SteamRoot"
}
if ((-not $DryRun) -and $SteamRoot.StartsWith((Full-Path (Join-Path $repoRoot 'tmp')).TrimEnd('\') + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    Fail 'a non-dry-run transaction may not target a tmp candidate directory'
}

if ($Operation -eq 'RESTORE') {
    $statePath = Join-Path $BackupRoot 'state.json'
    $originalRoot = Join-Path $BackupRoot 'originals'
    if ((-not (Test-Path -LiteralPath $statePath -PathType Leaf)) -or (-not (Test-Path -LiteralPath $originalRoot -PathType Container))) {
        Fail 'restore backup is absent or incomplete'
    }
    $state = Get-Content -LiteralPath $statePath -Raw -Encoding utf8 | ConvertFrom-Json
    if (([string]$state.schema -cne $stateSchema) -or ([string]$state.transaction_id -cne $transactionId) -or ([string]$state.status -cne 'applied')) {
        Fail 'restore state is not an applied Wave10--12 combined transaction'
    }
    if ((Full-Path ([string]$state.steam_root)) -cne $SteamRoot) {
        Fail 'restore state Steam root differs from the requested Steam root'
    }
    Assert-ExactArray @($state.changed_paths) $changedPaths 'restore state changed path order'
    Assert-HashMap $state.input_sha256 $inputHashes 'restore state input'
    Assert-HashMap $state.output_sha256 $targetHashes 'restore state output'
    foreach ($relative in $changedPaths) {
        $original = Join-Path $originalRoot ($relative -replace '/', '\')
        if ((Get-Sha256 $original) -cne $inputHashes[$relative]) {
            Fail "backup hash differs: $relative"
        }
    }
    $live = Get-ProfileState $SteamRoot 'Steam profile before restore'
    if ($live.name -eq 'input') {
        [PSCustomObject]@{ status='PASS'; result='already_restored'; writes_performed=$false } | ConvertTo-Json -Compress
        return
    }
    Assert-Game-Stopped
    if ($DryRun) {
        [PSCustomObject]@{ status='PASS'; result='restore_dry_run'; writes_performed=$false; changed_paths=$changedPaths; full_profile_verified=$true } | ConvertTo-Json -Compress
        return
    }
    foreach ($relative in $changedPaths) {
        Replace-Atomically (Join-Path $originalRoot ($relative -replace '/', '\')) (Join-Path $SteamRoot ($relative -replace '/', '\')) $inputHashes[$relative] "restore $relative"
    }
    if ((Get-ProfileState $SteamRoot 'Steam profile after restore').name -ne 'input') {
        Fail 'post-restore full profile mismatch'
    }
    $state.status = 'restored'
    $state.restored_at_utc = [DateTime]::UtcNow.ToString('o')
    Write-State $statePath $state
    [PSCustomObject]@{ status='PASS'; result='restored'; writes_performed=$true; backup_root=$BackupRoot } | ConvertTo-Json -Compress
    return
}

if (-not $CandidateRoot) {
    Fail 'apply requires -CandidateRoot'
}
if (-not $ManifestPath) {
    Fail 'apply requires -ManifestPath'
}
$CandidateRoot = Assert-Under $CandidateRoot $transactionTmpRoot 'candidate root'
$ManifestPath = Assert-Under $ManifestPath $transactionTmpRoot 'manifest path'
[void](Assert-CandidateManifest $CandidateRoot $ManifestPath)

$live = Get-ProfileState $SteamRoot 'Steam profile before apply'
if ($live.name -eq 'target') {
    [PSCustomObject]@{ status='PASS'; result='already_target'; writes_performed=$false } | ConvertTo-Json -Compress
    return
}
if (Test-Path -LiteralPath $BackupRoot) {
    Fail "backup root already exists: $BackupRoot"
}
Assert-Game-Stopped
if ($DryRun) {
    [PSCustomObject]@{
        status='PASS'
        result='apply_dry_run'
        writes_performed=$false
        changed_paths=$changedPaths
        full_profile_verified=$true
        backup_root=$BackupRoot
    } | ConvertTo-Json -Compress
    return
}

New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
$originalRoot = Join-Path $BackupRoot 'originals'
$statePath = Join-Path $BackupRoot 'state.json'
$state = [ordered]@{
    schema=$stateSchema
    transaction_id=$transactionId
    status='backed_up'
    timestamp_utc=[DateTime]::UtcNow.ToString('o')
    steam_root=$SteamRoot
    candidate_root=$CandidateRoot
    manifest_path=$ManifestPath
    changed_paths=$changedPaths
    input_sha256=$inputHashes
    output_sha256=$targetHashes
    written_paths=@()
}
$written = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($relative in $changedPaths) {
        $original = Join-Path $originalRoot ($relative -replace '/', '\')
        New-Item -ItemType Directory -Path (Split-Path -Parent $original) -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $SteamRoot ($relative -replace '/', '\')) -Destination $original -Force
        if ((Get-Sha256 $original) -cne $inputHashes[$relative]) {
            Fail "backup hash mismatch: $relative"
        }
    }
    Write-State $statePath $state
    foreach ($relative in $changedPaths) {
        $written.Add($relative)
        $state.written_paths = @($written)
        Write-State $statePath $state
        Replace-Atomically (Join-Path $CandidateRoot ($relative -replace '/', '\')) (Join-Path $SteamRoot ($relative -replace '/', '\')) $targetHashes[$relative] "apply $relative"
    }
    if ((Get-ProfileState $SteamRoot 'Steam profile after apply').name -ne 'target') {
        Fail 'post-apply full profile mismatch'
    }
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
        throw "apply failed: $($applyError.Exception.Message); rollback failed: $($_.Exception.Message)"
    }
    throw "apply failed and written files were restored: $($applyError.Exception.Message)"
}
[PSCustomObject]@{
    status='PASS'
    result='applied'
    writes_performed=$true
    changed_paths=$changedPaths
    backup_root=$BackupRoot
} | ConvertTo-Json -Compress
