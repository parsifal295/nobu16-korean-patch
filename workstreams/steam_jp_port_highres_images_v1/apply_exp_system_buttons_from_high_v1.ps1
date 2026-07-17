param(
    [Parameter(Mandatory = $true)]
    [string]$GameRoot,

    [string]$CandidateRoot
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($CandidateRoot)) {
    $CandidateRoot = Join-Path $PSScriptRoot '..\..\tmp\wheel_system_goal_v1\exp_system_buttons_from_high_v1\build_003\candidate'
}
$GameRoot = (Resolve-Path -LiteralPath $GameRoot).Path
$CandidateRoot = (Resolve-Path -LiteralPath $CandidateRoot).Path

$target = Join-Path $GameRoot 'RES_JP\res_lang_exp.bin'
$candidate = Join-Path $CandidateRoot 'RES_JP\res_lang_exp.bin'
$oldHash = '09DDC867E0B6F5A8210332C12F180A24A52C0B94D0AEE5E00E622CEA25A06D74'
$newHash = 'AC55622FC5C78ECA4ECFE37D1D890D5B26F6200ED7BAF1506B784541E158B7B7'

if (Get-Process -Name 'NOBU16PK' -ErrorAction SilentlyContinue) {
    throw 'NOBU16PK is still running'
}

$candidateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $candidate).Hash
if ($candidateHash -ne $newHash) {
    throw "Candidate hash differs: $candidate $candidateHash"
}

$liveBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash
if ($liveBefore -eq $newHash) {
    [PSCustomObject]@{
        Target = $target
        LiveSHA256 = $liveBefore
        Status = 'already-current'
    } | ConvertTo-Json -Compress
    exit 0
}
if ($liveBefore -ne $oldHash) {
    throw "Live precondition differs: $target $liveBefore"
}

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backup = "$target.pre-exp-buttons-from-high-$stamp.bak"
$temp = "$target.codex-$stamp.tmp"
if ((Test-Path -LiteralPath $backup) -or (Test-Path -LiteralPath $temp)) {
    throw 'Backup or temporary path already exists'
}

Copy-Item -LiteralPath $candidate -Destination $temp
$tempHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $temp).Hash
if ($tempHash -ne $newHash) {
    Remove-Item -LiteralPath $temp -Force
    throw "Staged hash differs: $tempHash"
}

[System.IO.File]::Replace($temp, $target, $backup, $true)
$liveAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash
$backupHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $backup).Hash
if (($liveAfter -ne $newHash) -or ($backupHash -ne $oldHash)) {
    throw 'Post-replace verification failed'
}

[PSCustomObject]@{
    Target = $target
    BeforeSHA256 = $liveBefore
    LiveSHA256 = $liveAfter
    Backup = $backup
    BackupSHA256 = $backupHash
    Status = 'applied'
} | ConvertTo-Json -Compress
