param(
    [Parameter(Mandatory = $true)]
    [string]$BuildA,
    [Parameter(Mandatory = $true)]
    [string]$BuildB
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$a = (Resolve-Path -LiteralPath $BuildA).Path
$b = (Resolve-Path -LiteralPath $BuildB).Path
if ([string]::Equals($a, $b, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'BuildA and BuildB must be distinct directories.'
}
$publicA = Join-Path $a 'public'
$publicB = Join-Path $b 'public'
if (-not (Test-Path -LiteralPath $publicA -PathType Container) -or
    -not (Test-Path -LiteralPath $publicB -PathType Container)) {
    throw 'Both builds must contain a public directory.'
}

function Get-RelativeFiles([string]$Root) {
    return @(
        Get-ChildItem -Recurse -File -LiteralPath $Root |
            ForEach-Object { $_.FullName.Substring($Root.Length + 1).Replace('\', '/') } |
            Sort-Object
    )
}

$filesA = Get-RelativeFiles $publicA
$filesB = Get-RelativeFiles $publicB
if (($filesA -join "`n") -ne ($filesB -join "`n")) {
    throw 'Public file sets differ.'
}

$rows = @()
foreach ($relative in $filesA) {
    $pathA = Join-Path $publicA $relative
    $pathB = Join-Path $publicB $relative
    $hashA = (Get-FileHash -Algorithm SHA256 -LiteralPath $pathA).Hash.ToUpperInvariant()
    $hashB = (Get-FileHash -Algorithm SHA256 -LiteralPath $pathB).Hash.ToUpperInvariant()
    if ($hashA -ne $hashB) { throw "Public output differs: $relative" }
    $rows += [ordered]@{ path = $relative; sha256 = $hashA; exact = $true }
}

$manifestA = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $a 'manifest.json')).Hash.ToUpperInvariant()
$manifestB = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $b 'manifest.json')).Hash.ToUpperInvariant()
if ($manifestA -ne $manifestB) { throw 'Build manifests differ.' }

$validationA = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $a 'validation.json')).Hash.ToUpperInvariant()
$validationB = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $b 'validation.json')).Hash.ToUpperInvariant()
if ($validationA -ne $validationB) { throw 'Build validations differ.' }

$privateA = Join-Path $a 'private'
$privateB = Join-Path $b 'private'
$privateFilesA = Get-RelativeFiles $privateA
$privateFilesB = Get-RelativeFiles $privateB
if (($privateFilesA -join "`n") -ne ($privateFilesB -join "`n")) {
    throw 'Private validation file sets differ.'
}
$privateRows = @()
foreach ($relative in $privateFilesA) {
    $pathA = Join-Path $privateA $relative
    $pathB = Join-Path $privateB $relative
    $hashA = (Get-FileHash -Algorithm SHA256 -LiteralPath $pathA).Hash.ToUpperInvariant()
    $hashB = (Get-FileHash -Algorithm SHA256 -LiteralPath $pathB).Hash.ToUpperInvariant()
    if ($hashA -ne $hashB) { throw "Private validation output differs: $relative" }
    $privateRows += [ordered]@{ path = $relative; sha256 = $hashA; exact = $true }
}

$candidateRelative = 'private\candidate\res_lang.SC.font-v6.bin'
$candidateA = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $a $candidateRelative)).Hash.ToUpperInvariant()
$candidateB = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $b $candidateRelative)).Hash.ToUpperInvariant()
if ($candidateA -ne $candidateB) { throw 'Private validation candidates differ.' }

$result = [ordered]@{
    schema = 'nobu16.kr.font-v6-determinism-comparison.v1'
    exact = $true
    public_file_count = $rows.Count
    public_files = $rows
    manifest_sha256 = $manifestA
    validation_sha256 = $validationA
    private_file_count = $privateRows.Count
    private_files = $privateRows
    private_candidate_archive_sha256 = $candidateA
    installed_game_files_modified = $false
    process_memory_access = $false
    registry_access = $false
}
$result | ConvertTo-Json -Depth 6
