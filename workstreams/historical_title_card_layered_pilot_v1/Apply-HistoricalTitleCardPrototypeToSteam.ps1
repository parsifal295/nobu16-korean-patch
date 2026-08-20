[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$CandidateRoot,

    [Parameter(Mandatory = $true)]
    [string]$SteamRoot,

    [Parameter(Mandatory = $true)]
    [string]$BackupRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Assert-ChildPath([string]$Parent, [string]$Child, [string]$Label) {
    $parentFull = [IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
    $childFull = [IO.Path]::GetFullPath($Child)
    if (-not $childFull.StartsWith($parentFull, [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label escapes the required root: $childFull"
    }
    return $childFull
}

$candidateFull = [IO.Path]::GetFullPath($CandidateRoot)
$steamFull = [IO.Path]::GetFullPath($SteamRoot)
$backupFull = [IO.Path]::GetFullPath($BackupRoot)
if (-not [IO.Directory]::Exists($candidateFull)) { throw "Candidate root is missing: $candidateFull" }
if (-not [IO.Directory]::Exists($steamFull)) { throw "Steam root is missing: $steamFull" }
if ([IO.Directory]::Exists($backupFull) -and (Get-ChildItem -LiteralPath $backupFull -Force | Select-Object -First 1)) {
    throw "Backup root must be empty: $backupFull"
}
[IO.Directory]::CreateDirectory($backupFull) | Out-Null

$running = @(Get-Process -Name 'NOBU16PK' -ErrorAction SilentlyContinue)
if ($running.Count -ne 0) { throw 'NOBU16PK.exe must be fully exited before applying image archives.' }

$reportPath = Join-Path ([IO.Directory]::GetParent($candidateFull).FullName) 'build_report.json'
if (-not [IO.File]::Exists($reportPath)) { throw "Candidate build report is missing: $reportPath" }
$buildJson = [IO.File]::ReadAllText($reportPath, [Text.Encoding]::UTF8)
$build = $buildJson | ConvertFrom-Json
if ($build.status -ne 'PASS' -or $build.steam_written -ne $false) { throw 'Candidate build report is not a verified pre-Steam build.' }

$rows = @($build.routes)
if ($rows.Count -ne 2) { throw "Expected two candidate routes, got $($rows.Count)" }
$applied = [Collections.Generic.List[object]]::new()
try {
    foreach ($row in $rows) {
        $relativeWindows = ([string]$row.relative_path).Replace('/', '\')
        $source = Assert-ChildPath $candidateFull (Join-Path $candidateFull $relativeWindows) 'Candidate file'
        $destination = Assert-ChildPath $steamFull (Join-Path $steamFull $relativeWindows) 'Steam destination'
        $backup = Assert-ChildPath $backupFull (Join-Path $backupFull $relativeWindows) 'Backup destination'
        if (-not [IO.File]::Exists($source)) { throw "Candidate file is missing: $source" }
        if (-not [IO.File]::Exists($destination)) { throw "Steam destination is missing: $destination" }
        $candidateHash = Get-Sha256 $source
        if ($candidateHash -ne ([string]$row.candidate.sha256).ToUpperInvariant()) {
            throw "Candidate hash differs: $source"
        }
        $beforeHash = Get-Sha256 $destination
        if ($beforeHash -ne ([string]$row.source.sha256).ToUpperInvariant()) {
            throw "Steam baseline hash differs for $destination; expected $($row.source.sha256), got $beforeHash"
        }
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($backup)) | Out-Null
        Copy-Item -LiteralPath $destination -Destination $backup
        if ((Get-Sha256 $backup) -ne $beforeHash) { throw "Backup verification failed: $backup" }
        Copy-Item -LiteralPath $source -Destination $destination -Force
        $afterHash = Get-Sha256 $destination
        if ($afterHash -ne $candidateHash) { throw "Steam candidate verification failed: $destination" }
        $applied.Add([ordered]@{
            relative_path = [string]$row.relative_path
            destination = $destination
            backup = $backup
            before_sha256 = $beforeHash
            after_sha256 = $afterHash
            size = (Get-Item -LiteralPath $destination).Length
        })
    }
} catch {
    foreach ($item in $applied) {
        if ([IO.File]::Exists([string]$item.backup)) {
            Copy-Item -LiteralPath ([string]$item.backup) -Destination ([string]$item.destination) -Force
        }
    }
    throw
}

$applyReport = [ordered]@{
    schema = 'nobu16.kr.historical-title-card-prototype.steam-apply.v1'
    status = 'PASS'
    approved_purpose = 'release-candidate in-game QA'
    game_process_running_during_apply = $false
    steam_root = $steamFull
    candidate_root = $candidateFull
    backup_root = $backupFull
    build_report = $reportPath
    files = @($applied)
}
$applyReportPath = Join-Path $backupFull 'steam_apply_report.json'
$applyReport | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $applyReportPath -Encoding utf8
Write-Output 'status=PASS'
Write-Output "apply_report=$applyReportPath"
foreach ($item in $applied) { Write-Output "$($item.relative_path)=$($item.after_sha256)" }
