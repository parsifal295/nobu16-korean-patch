[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [switch]$Apply,

    [switch]$DryRun,

    [string]$SteamRoot = 'F:\SteamLibrary\steamapps\common\NOBU16',

    [string]$BackupRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$candidateRoot = Join-Path $repoRoot 'tmp\npc_name_component_quality_v1\candidate-v2'
$approvedBackupParent = Join-Path $SteamRoot 'KR_PATCH_BACKUP'
$transactionId = 'npc-name-component-quality-v1-20260718-v1'

$inputHashes = [ordered]@{
    'MSG/JP/strdata.bin'       = '10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE'
    'MSG_PK/JP/msgdata.bin'    = '8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752'
    'MSG/JP/ev_strdata.bin'    = '3A7BE17B7DA97B89BD82DFFF44EBC28DA2D3AA91D2E970A0F6C26DE22C657A22'
    'MSG_PK/JP/msgev.bin'      = '73DEC80A85B5441AFFFA725DAB72CF02D334D29B297AD08050BC496D532CB8F3'
}
$targetHashes = [ordered]@{
    'MSG/JP/strdata.bin'       = '5F308F416378976C1AB0B50D4A91C9DA38C637A0A842BAB04FB48256B2103E28'
    'MSG_PK/JP/msgdata.bin'    = '69090EC9EEE1DF9EAFB64BB35CEFD285A5089FDE78E9A4A855EAA0AE5991C168'
    'MSG/JP/ev_strdata.bin'    = 'CC77EE4B0587B371A901069FB3F39C2187886C3A3335D9748D275FA2881EB426'
    'MSG_PK/JP/msgev.bin'      = '3E2323DDFAD70DAA15713DD1C4D622508BD2E610C65683C0A06D3D1FAC9827A5'
}
$profilePaths = @($inputHashes.Keys)

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

function Assert-GameStopped {
    $names = @('nobu16', 'nobu16pk', 'nobu16pk_en', 'nobu16_launcher', 'nobu16_sd', 'nobu16pk_sd', 'nobu16pk_en_sd')
    $running = @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $names -contains $_.ProcessName.ToLowerInvariant() } |
            Select-Object -ExpandProperty ProcessName -Unique
    )
    if ($running.Count -gt 0) {
        Fail ('close the game and official launcher before applying this transaction: ' + ($running -join ', '))
    }
}

function Assert-Profile([string]$Root, $Expected, [string]$Label) {
    foreach ($relative in $profilePaths) {
        $path = Join-Path $Root ($relative -replace '/', '\')
        $actual = Get-Sha256 $path
        if ($actual -cne $Expected[$relative]) {
            Fail "$Label hash mismatch at ${relative}: $actual"
        }
    }
}

function Replace-Checked([string]$Source, [string]$Destination, [string]$ExpectedHash, [string]$Label) {
    $destinationDirectory = Split-Path -Parent $Destination
    $fileName = [System.IO.Path]::GetFileName($Destination)
    $temporary = Join-Path $destinationDirectory ('.' + $fileName + '.npc-name-v1.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    Copy-Item -LiteralPath $Source -Destination $temporary -Force
    if ((Get-Sha256 $temporary) -cne $ExpectedHash) {
        Fail "$Label temporary hash mismatch"
    }
    Assert-GameStopped
    [System.IO.File]::Replace($temporary, $Destination, $null, $true)
    if ((Get-Sha256 $Destination) -cne $ExpectedHash) {
        Fail "$Label live hash mismatch"
    }
}

if (-not $Apply) {
    Fail 'pass -Apply explicitly; this writer never applies by default'
}

$SteamRoot = Full-Path $SteamRoot
$candidateRoot = Assert-Under $candidateRoot (Join-Path $repoRoot 'tmp') 'candidate root'
$approvedBackupParent = Full-Path $approvedBackupParent
if (-not $BackupRoot) {
    $BackupRoot = Join-Path $approvedBackupParent $transactionId
}
$BackupRoot = Assert-Under $BackupRoot $approvedBackupParent 'backup root'

if (-not (Test-Path -LiteralPath $SteamRoot -PathType Container)) {
    Fail "Steam root does not exist: $SteamRoot"
}
if (-not (Test-Path -LiteralPath $candidateRoot -PathType Container)) {
    Fail "candidate root does not exist: $candidateRoot"
}

Assert-GameStopped
Assert-Profile $SteamRoot $inputHashes 'Steam input'
Assert-Profile $candidateRoot $targetHashes 'candidate'

if ($DryRun) {
    [PSCustomObject]@{
        status = 'PASS'
        result = 'dry_run'
        transaction_id = $transactionId
        changed_paths = $profilePaths
        backup_root = $BackupRoot
        writes_performed = $false
    } | ConvertTo-Json -Compress
    return
}

if (Test-Path -LiteralPath $BackupRoot) {
    Fail "backup root already exists: $BackupRoot"
}

New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
$originalRoot = Join-Path $BackupRoot 'originals'
$written = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($relative in $profilePaths) {
        $source = Join-Path $SteamRoot ($relative -replace '/', '\')
        $backup = Join-Path $originalRoot ($relative -replace '/', '\')
        New-Item -ItemType Directory -Path (Split-Path -Parent $backup) -Force | Out-Null
        Copy-Item -LiteralPath $source -Destination $backup -Force
        if ((Get-Sha256 $backup) -cne $inputHashes[$relative]) {
            Fail "backup hash mismatch at $relative"
        }
    }
    foreach ($relative in $profilePaths) {
        $candidate = Join-Path $candidateRoot ($relative -replace '/', '\')
        $destination = Join-Path $SteamRoot ($relative -replace '/', '\')
        Replace-Checked $candidate $destination $targetHashes[$relative] "apply $relative"
        $written.Add($relative)
    }
    Assert-Profile $SteamRoot $targetHashes 'Steam target'
}
catch {
    $applyError = $_
    try {
        for ($index = $written.Count - 1; $index -ge 0; $index--) {
            $relative = $written[$index]
            $backup = Join-Path $originalRoot ($relative -replace '/', '\')
            $destination = Join-Path $SteamRoot ($relative -replace '/', '\')
            Replace-Checked $backup $destination $inputHashes[$relative] "rollback $relative"
        }
        Assert-Profile $SteamRoot $inputHashes 'Steam rollback'
    }
    catch {
        throw "apply failed: $($applyError.Exception.Message); rollback failed: $($_.Exception.Message)"
    }
    throw "apply failed and written files were restored: $($applyError.Exception.Message)"
}

[PSCustomObject]@{
    status = 'PASS'
    result = 'applied'
    transaction_id = $transactionId
    changed_paths = $profilePaths
    backup_root = $BackupRoot
    writes_performed = $true
} | ConvertTo-Json -Compress
