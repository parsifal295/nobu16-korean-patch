param(
    [string]$WorkstreamRoot = $PSScriptRoot,
    [string]$OutputPath = (Join-Path $PSScriptRoot 'audit\public_artifact_audit.json')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$root = (Resolve-Path -LiteralPath $WorkstreamRoot).Path
$outputFull = [IO.Path]::GetFullPath($OutputPath)
$utf8NoBom = New-Object Text.UTF8Encoding($false)
$textExtensions = @('.md', '.json', '.ps1', '.py', '.txt')
$forbiddenMetadataKeys = @('source_sc', 'before', 'id_9168_before')
$expectedPixels = @{
    'raster/glyph_pixels_entry_6.bin' = @{ size = 11520; sha256 = 'CF7558B284EF9A3D3C26D73E7376F1AF1257D4AAA2FF0D555C8BF897F58F00E8' }
    'raster/glyph_pixels_entry_7.bin' = @{ size = 5120; sha256 = 'CA33DD93DE1DAC06A202FA44F8871C8292371904CE061E8527095BC6603A3768' }
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Get-Relative([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    $prefix = $root.TrimEnd('\') + '\'
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw "Path escaped workstream: $full" }
    return $full.Substring($prefix.Length).Replace('\', '/')
}

function Test-CjkCodepoint([int]$Codepoint) {
    return (
        ($Codepoint -ge 0x3400 -and $Codepoint -le 0x4DBF) -or
        ($Codepoint -ge 0x4E00 -and $Codepoint -le 0x9FFF) -or
        ($Codepoint -ge 0xF900 -and $Codepoint -le 0xFAFF) -or
        ($Codepoint -ge 0x20000 -and $Codepoint -le 0x2FA1F) -or
        ($Codepoint -ge 0x30000 -and $Codepoint -le 0x3134F)
    )
}

function Get-CjkFindings([string]$Text) {
    $actual = [Collections.Generic.List[string]]::new()
    for ($index = 0; $index -lt $Text.Length; $index++) {
        $codepoint = [char]::ConvertToUtf32($Text, $index)
        if ([char]::IsHighSurrogate($Text[$index])) { $index++ }
        if (Test-CjkCodepoint $codepoint) { $actual.Add(('U+{0:X}' -f $codepoint)) }
    }
    $escaped = [Collections.Generic.List[string]]::new()
    foreach ($match in [regex]::Matches($Text, '\\u(?<hex>[0-9A-Fa-f]{4})')) {
        $codepoint = [Convert]::ToInt32($match.Groups['hex'].Value, 16)
        if (Test-CjkCodepoint $codepoint) { $escaped.Add(('U+{0:X4}' -f $codepoint)) }
    }
    return [ordered]@{
        literal = @($actual | Sort-Object -Unique)
        escaped_bmp = @($escaped | Sort-Object -Unique)
    }
}

function Get-JsonForbiddenKeys([object]$Value, [string]$Path = '$') {
    $hits = [Collections.Generic.List[string]]::new()
    if ($null -eq $Value) { return $hits }
    if ($Value -is [pscustomobject]) {
        foreach ($property in $Value.PSObject.Properties) {
            $child = "$Path.$($property.Name)"
            if ($forbiddenMetadataKeys -contains [string]$property.Name) { $hits.Add($child) }
            foreach ($hit in Get-JsonForbiddenKeys $property.Value $child) { $hits.Add($hit) }
        }
    } elseif ($Value -is [Collections.IEnumerable] -and $Value -isnot [string]) {
        $index = 0
        foreach ($item in $Value) {
            foreach ($hit in Get-JsonForbiddenKeys $item "${Path}[$index]") { $hits.Add($hit) }
            $index++
        }
    }
    return $hits
}

$files = @(
    Get-ChildItem -LiteralPath $root -File -Recurse |
        Where-Object {
            $relative = Get-Relative $_.FullName
            -not $relative.StartsWith('private/', [StringComparison]::OrdinalIgnoreCase) -and
            [IO.Path]::GetFullPath($_.FullName) -ne $outputFull -and
            $_.Name -ne '.keep'
        } |
        Sort-Object FullName
)

$inventory = [Collections.Generic.List[object]]::new()
$cjkFiles = [Collections.Generic.List[object]]::new()
$magicFailures = [Collections.Generic.List[string]]::new()
$sizeFailures = [Collections.Generic.List[string]]::new()
$jsonFailures = [Collections.Generic.List[string]]::new()
$metadataKeyFailures = [Collections.Generic.List[string]]::new()

foreach ($file in $files) {
    $relative = Get-Relative $file.FullName
    $bytes = [IO.File]::ReadAllBytes($file.FullName)
    $headLength = [Math]::Min(8, $bytes.Length)
    $head = if ($headLength -eq 0) { '' } else { ($bytes[0..($headLength - 1)] | ForEach-Object { $_.ToString('X2') }) -join ' ' }
    $category = switch ($file.Extension.ToLowerInvariant()) {
        '.png' { 'project-preview' }
        '.bin' { 'project-raster-pixels' }
        '.json' { 'metadata' }
        default { 'source' }
    }
    $inventory.Add([ordered]@{
        path = $relative
        size = $file.Length
        sha256 = Get-Sha256 $file.FullName
        first_8_bytes_hex = $head
        category = $category
    })

    if ($file.Length -gt 1MB) { $sizeFailures.Add("$relative exceeds 1 MiB") }
    $signature = $head.Replace(' ', '')
    if ($signature.StartsWith('5F4E314730303030') -or $signature.StartsWith('4C494E4B') -or $signature.StartsWith('0101C4C1FA7F0000')) {
        $magicFailures.Add("$relative has a forbidden commercial-resource signature: $head")
    }
    if ($file.Extension -eq '.g1n' -or $relative.EndsWith('/msgdata.bin') -or $relative.EndsWith('/res_lang.bin')) {
        $magicFailures.Add("$relative has a forbidden commercial-resource name or extension")
    }
    if ($file.Extension -eq '.png' -and -not $signature.StartsWith('89504E470D0A1A0A')) {
        $magicFailures.Add("$relative does not have PNG magic")
    }
    if ($file.Extension -eq '.bin') {
        if (-not $expectedPixels.ContainsKey($relative)) {
            $magicFailures.Add("$relative is an unapproved binary payload")
        } else {
            $expected = $expectedPixels[$relative]
            if ($file.Length -ne [int]$expected.size -or (Get-Sha256 $file.FullName) -ne [string]$expected.sha256) {
                $magicFailures.Add("$relative project pixel payload hash/size mismatch")
            }
        }
    }

    if ($textExtensions -contains $file.Extension.ToLowerInvariant()) {
        $text = [IO.File]::ReadAllText($file.FullName, [Text.Encoding]::UTF8)
        $findings = Get-CjkFindings $text
        if ($findings.literal.Count -gt 0 -or $findings.escaped_bmp.Count -gt 0) {
            $cjkFiles.Add([ordered]@{ path = $relative; literal = $findings.literal; escaped_bmp = $findings.escaped_bmp })
        }
        if ($file.Extension -eq '.json') {
            try {
                $parsed = $text | ConvertFrom-Json
            } catch {
                $jsonFailures.Add("$relative JSON parse failed: $($_.Exception.Message)")
                continue
            }
            if ($relative.StartsWith('metadata/', [StringComparison]::OrdinalIgnoreCase)) {
                foreach ($hit in Get-JsonForbiddenKeys $parsed) { $metadataKeyFailures.Add("$relative $hit") }
                if ($parsed.commercial_source_strings_included -ne $false) {
                    $metadataKeyFailures.Add("$relative lacks commercial_source_strings_included=false")
                }
            }
        }
    }
}

$status = if (
    $cjkFiles.Count -eq 0 -and
    $magicFailures.Count -eq 0 -and
    $sizeFailures.Count -eq 0 -and
    $jsonFailures.Count -eq 0 -and
    $metadataKeyFailures.Count -eq 0
) { 'PASS' } else { 'FAIL' }

$totalSize = [long]0
foreach ($entry in $inventory) { $totalSize += [long]$entry['size'] }

$result = [ordered]@{
    schema = 'nobu16.kr.castle-wide-glyph-public-artifact-audit.v1'
    status = $status
    scope = [ordered]@{
        root = 'KR_PATCH_WORK/workstreams/castle_wide_glyph'
        private_directory_excluded = $true
        audit_output_excluded_from_self_inventory = 'audit/public_artifact_audit.json'
        complete_commercial_resources_allowed = $false
    }
    checks = [ordered]@{
        file_count = $inventory.Count
        total_size = $totalSize
        cjk_literal_or_escape_files = @($cjkFiles)
        forbidden_magic_or_payload_failures = @($magicFailures)
        size_failures = @($sizeFailures)
        json_failures = @($jsonFailures)
        forbidden_metadata_key_failures = @($metadataKeyFailures)
        approved_pixel_payload_count = $expectedPixels.Count
    }
    files = @($inventory)
}

[IO.Directory]::CreateDirectory((Split-Path -Parent $outputFull)) | Out-Null
[IO.File]::WriteAllText($outputFull, ($result | ConvertTo-Json -Depth 20) + "`n", $utf8NoBom)
Write-Output "audit=$outputFull"
Write-Output "audit_sha256=$(Get-Sha256 $outputFull)"
Write-Output "status=$status"
if ($status -ne 'PASS') { exit 1 }
