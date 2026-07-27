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

$items = @(
    [PSCustomObject]@{
        Relative = 'RES_TC_PK\res_lang_pk.bin'
        Old = '19C0149A7B4F9A5CA2672F61D4D8F3C3674FC343E33AEF3E4E1ED04BAFDC5B7B'
        New = '72C91E02272AF96561D1F574DF734AFA0F561BD3F78FBAC66A1872EEAAE1ABFB'
    },
    [PSCustomObject]@{
        Relative = 'RES_TC_PK_PORT\res_lang_pk_port2.bin'
        Old = '42C82BEB4524FB0E4FC9ED61AFF1EDB24422F196EC7424A831EB9E687C94EB77'
        New = '6D9380CB26E7F9903ABD3516DDFFB7A67BC9BFB4ED0AD5220B45C1C6A19ED01A'
    }
)

$staged = @()
foreach ($item in $items) {
    $target = Join-Path $GameRoot $item.Relative
    $candidate = Join-Path $CandidateRoot $item.Relative
    $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash
    $candidateHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $candidate).Hash
    if ($liveHash -ne $item.Old) {
        throw "Live precondition differs: $target $liveHash"
    }
    if ($candidateHash -ne $item.New) {
        throw "Candidate hash differs: $candidate $candidateHash"
    }

    $temporary = "$target.codex-tc-wheel-build002.tmp"
    if (Test-Path -LiteralPath $temporary) {
        throw "Stage path already exists: $temporary"
    }
    Copy-Item -LiteralPath $candidate -Destination $temporary
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $temporary).Hash -ne $item.New) {
        throw "Staged hash differs: $temporary"
    }

    $backup = Join-Path $BackupRoot $item.Relative
    New-Item -ItemType Directory -Path (Split-Path -Parent $backup) -Force | Out-Null
    $staged += [PSCustomObject]@{
        Item = $item
        Target = $target
        Temporary = $temporary
        Backup = $backup
    }
}

$completed = @()
try {
    foreach ($entry in $staged) {
        [System.IO.File]::Replace(
            $entry.Temporary,
            $entry.Target,
            $entry.Backup,
            $true
        )
        $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Target).Hash
        $backupHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Backup).Hash
        if ($liveHash -ne $entry.Item.New -or $backupHash -ne $entry.Item.Old) {
            throw "Post-replace verification failed: $($entry.Target)"
        }
        $completed += $entry
    }
}
catch {
    $originalFailure = $_
    foreach ($entry in ($completed | Select-Object -Reverse)) {
        $rollback = "$($entry.Target).codex-tc-wheel-rollback.tmp"
        Copy-Item -LiteralPath $entry.Backup -Destination $rollback
        [System.IO.File]::Replace($rollback, $entry.Target, $null, $true)
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Target).Hash -ne $entry.Item.Old) {
            throw "Rollback verification failed after: $($originalFailure.Exception.Message)"
        }
    }
    throw $originalFailure
}

$results = foreach ($entry in $completed) {
    [PSCustomObject]@{
        Target = $entry.Target
        LiveSHA256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Target).Hash
        LiveSize = (Get-Item -LiteralPath $entry.Target).Length
        Backup = $entry.Backup
        BackupSHA256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Backup).Hash
        BackupSize = (Get-Item -LiteralPath $entry.Backup).Length
    }
}

[PSCustomObject]@{
    Status = 'PASS'
    BackupRoot = $BackupRoot
    NOBU16PKRunning = $false
    Files = $results
} | ConvertTo-Json -Depth 5
