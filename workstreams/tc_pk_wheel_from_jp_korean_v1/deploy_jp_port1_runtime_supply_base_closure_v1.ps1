param(
    [Parameter(Mandatory = $true)]
    [string]$GameRoot,

    [Parameter(Mandatory = $true)]
    [string]$CandidateRoot,

    [Parameter(Mandatory = $true)]
    [string]$BackupRoot
)

$ErrorActionPreference = 'Stop'

$GameRoot = (Resolve-Path -LiteralPath $GameRoot).Path
$CandidateRoot = (Resolve-Path -LiteralPath $CandidateRoot).Path
$BackupRoot = [System.IO.Path]::GetFullPath($BackupRoot)

if (Get-Process -Name 'NOBU16PK' -ErrorAction SilentlyContinue) {
    throw 'NOBU16PK.exe is running'
}
if (Test-Path -LiteralPath $BackupRoot) {
    throw "Backup root already exists: $BackupRoot"
}

$relative = 'RES_JP_PK_PORT\res_lang_pk_port1.bin'
$expectedOld = 'BC4C87DD1D93BF944929E6341517828365C59203913E98302DF1A843571623D2'
$expectedNew = '94F7602CCD41D750FFB3A5493ABE083E9F652B60374F82294FF3722EF9933AD1'
$target = Join-Path $GameRoot $relative
$candidate = Join-Path $CandidateRoot $relative

$liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash
$candidateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $candidate).Hash
if ($liveHash -ne $expectedOld) {
    throw "Live precondition differs: $target $liveHash"
}
if ($candidateHash -ne $expectedNew) {
    throw "Candidate hash differs: $candidate $candidateHash"
}

$temporary = "$target.codex-resource42-build001.tmp"
if (Test-Path -LiteralPath $temporary) {
    throw "Stage path already exists: $temporary"
}

$backup = Join-Path $BackupRoot $relative
Copy-Item -LiteralPath $candidate -Destination $temporary
try {
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $temporary).Hash -ne $expectedNew) {
        throw "Staged hash differs: $temporary"
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $backup) -Force | Out-Null
    [System.IO.File]::Replace($temporary, $target, $backup, $true)
}
catch {
    if (Test-Path -LiteralPath $temporary) {
        Remove-Item -LiteralPath $temporary -Force
    }
    throw
}

$deployedHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash
$backupHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $backup).Hash
if ($deployedHash -ne $expectedNew -or $backupHash -ne $expectedOld) {
    if ($backupHash -ne $expectedOld) {
        throw 'Post-replace backup verification failed; refusing to use an invalid rollback source'
    }

    $rollback = "$target.codex-resource42-build001-rollback.tmp"
    Copy-Item -LiteralPath $backup -Destination $rollback
    [System.IO.File]::Replace($rollback, $target, $null, $true)
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash -ne $expectedOld) {
        throw 'Post-replace verification and rollback verification both failed'
    }
    throw 'Post-replace verification failed; original file restored'
}

[PSCustomObject]@{
    Status = 'PASS'
    BackupRoot = $BackupRoot
    NOBU16PKRunning = [bool](Get-Process -Name 'NOBU16PK' -ErrorAction SilentlyContinue)
    Target = $target
    LiveSHA256 = $deployedHash
    LiveSize = (Get-Item -LiteralPath $target).Length
    Backup = $backup
    BackupSHA256 = $backupHash
    BackupSize = (Get-Item -LiteralPath $backup).Length
} | ConvertTo-Json -Depth 4
