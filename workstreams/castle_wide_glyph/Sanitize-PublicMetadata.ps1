param(
    [string]$SourceRoot = (Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path 'KR_PATCH_WORK\tmp\single_glyph_castle_probe'),
    [string]$DestinationRoot = (Join-Path $PSScriptRoot 'metadata')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$forbiddenKeys = @('source_sc', 'before', 'id_9168_before')
$pathKeys = @('path', 'source', 'target', 'raw_path', 'harness')
$utf8NoBom = New-Object Text.UTF8Encoding($false)

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Convert-PublicPath([string]$Value) {
    $normalized = $Value.Replace('\', '/')
    foreach ($marker in @(
        '/tmp/single_glyph_castle_probe/',
        '/tmp/lang_fonts/',
        '/backups/castle_hangul_orientation_probe/'
    )) {
        $position = $normalized.IndexOf($marker, [StringComparison]::OrdinalIgnoreCase)
        if ($position -ge 0) {
            $tail = $normalized.Substring($position + $marker.Length)
            $label = switch ($marker) {
                '/tmp/single_glyph_castle_probe/' { 'single_glyph_castle_probe' }
                '/tmp/lang_fonts/' { 'lang_fonts' }
                default { 'stock_wrappers' }
            }
            return "private-input/$label/$tail"
        }
    }
    if ([IO.Path]::IsPathRooted($Value)) {
        return 'private-input/' + [IO.Path]::GetFileName($Value)
    }
    return $normalized
}

function Convert-PublicValue([object]$Value, [string]$Key = '') {
    if ($null -eq $Value) { return $null }
    if ($Value -is [string]) {
        if ($pathKeys -contains $Key) { return Convert-PublicPath $Value }
        return $Value
    }
    if ($Value -is [Collections.IDictionary]) {
        $result = [ordered]@{}
        foreach ($entry in $Value.GetEnumerator()) {
            $name = [string]$entry.Key
            if ($forbiddenKeys -contains $name) { continue }
            $result[$name] = Convert-PublicValue $entry.Value $name
        }
        return $result
    }
    if ($Value -is [Collections.IEnumerable]) {
        $items = [Collections.Generic.List[object]]::new()
        foreach ($item in $Value) { $items.Add((Convert-PublicValue $item $Key)) }
        return ,$items.ToArray()
    }
    if ($Value -is [pscustomobject]) {
        $result = [ordered]@{}
        foreach ($property in $Value.PSObject.Properties) {
            $name = [string]$property.Name
            if ($forbiddenKeys -contains $name) { continue }
            $result[$name] = Convert-PublicValue $property.Value $name
        }
        return $result
    }
    return $Value
}

function Write-SanitizedDocument([string]$InputPath, [string]$OutputName) {
    if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) { throw "Missing metadata input: $InputPath" }
    $parsed = Get-Content -Raw -Encoding UTF8 -LiteralPath $InputPath | ConvertFrom-Json
    $content = Convert-PublicValue $parsed
    $schema = if ($content.Contains('schema')) { [string]$content['schema'] } else { 'unspecified' }
    $content['schema'] = $schema + '.public-sanitized.v1'
    $content['public_metadata'] = $true
    $content['commercial_source_strings_included'] = $false
    $content['sanitized_from_sha256'] = Get-Sha256 $InputPath
    $outputPath = Join-Path $DestinationRoot $OutputName
    [IO.File]::WriteAllText($outputPath, ($content | ConvertTo-Json -Depth 100) + "`n", $utf8NoBom)
    Write-Output "$OutputName`t$(Get-Sha256 $outputPath)"
}

[IO.Directory]::CreateDirectory($DestinationRoot) | Out-Null
Write-SanitizedDocument (Join-Path $SourceRoot 'proxy_reservation_9151_9542.json') 'proxy_reservation_9151_9542.json'
Write-SanitizedDocument (Join-Path $SourceRoot 'candidate_summary.json') 'candidate_summary.json'
Write-SanitizedDocument (Join-Path $SourceRoot 'wrapper_candidate\CANDIDATE_MANIFEST.json') 'private_candidate_manifest.json'
Write-SanitizedDocument (Join-Path $SourceRoot 'wrapper_candidate\WRAPPER_AUDIT.json') 'private_candidate_audit.json'
Write-SanitizedDocument (Join-Path $SourceRoot 'wrapper_candidate\HARNESS_STATIC_AUDIT.json') 'private_harness_static_audit.json'
