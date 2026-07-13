[CmdletBinding()]
param(
    [string]$OutputRoot,
    [string]$OfflineEvidencePath,
    [string]$RuntimeEvidencePath,
    [string]$MessageSource,
    [string]$FontPublicSource,
    [switch]$Overwrite,
    [switch]$CreateZip
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ReleaseId = 'msgui-full-font-v4-v0.3'
$ReleaseFolderName = 'msgui_full_file_only_v0.3-dev_2026-07-14'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$KrPatchRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$GameRoot = Split-Path -Parent $KrPatchRoot
$TemplateRoot = Join-Path $PSScriptRoot 'template'
if ([string]::IsNullOrWhiteSpace($MessageSource)) {
    $MessageSource = Join-Path $PSScriptRoot 'inputs\message\msgui_sc.recipe.json'
}
if ([string]::IsNullOrWhiteSpace($FontPublicSource)) {
    $FontPublicSource = Join-Path $PSScriptRoot 'inputs\font'
}
$MessageSource = [IO.Path]::GetFullPath($MessageSource)
$FontPublicSource = [IO.Path]::GetFullPath($FontPublicSource)
if (-not $OutputRoot) {
    $OutputRoot = Join-Path $KrPatchRoot "releases\$ReleaseFolderName"
}

function Get-FullPath([string]$Path) {
    return [System.IO.Path]::GetFullPath($Path)
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Get-BytesSha256([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '')
    }
    finally {
        $sha.Dispose()
    }
}

function Get-CompactJsonSha256($Value) {
    $json = ConvertTo-Json -InputObject $Value -Compress
    return Get-BytesSha256 ([Text.Encoding]::UTF8.GetBytes($json))
}

function Read-Json([string]$Path) {
    [byte[]]$bytes = [IO.File]::ReadAllBytes($Path)
    [N16KrFileOnly.JsonKeyGuard]::AssertNoDuplicateKeys($bytes)
    $strictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    return ($strictUtf8.GetString($bytes) | ConvertFrom-Json)
}

function Write-Utf8Json([string]$Path, $Value, [int]$Depth = 20) {
    $json = (($Value | ConvertTo-Json -Depth $Depth) -replace "`r`n", "`n") + "`n"
    [IO.File]::WriteAllText($Path, $json, $Utf8NoBom)
}

function Assert-OrdinaryLeaf([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "$Label must not be a reparse point: $Path"
    }
}

function Assert-NoLegacyReleaseIdentity([string]$Root) {
    $legacyValues = @(
        [string]::Concat('msgui-', 'p', '3-font-', 'v', '3-v0', '.2'),
        [string]::Concat('NOBU16 Korean MSGUI ', 'P', '3 / Font-', 'v', '3 file-only v0', '.2'),
        [string]::Concat('msgui_', 'p', '3_font_', 'v', '3_v0', '_2'),
        [string]::Concat('msgui-', 'p', '4-font-', 'v', '4-v0', '.3'),
        [string]::Concat('NOBU16 Korean MSGUI ', 'P', '4 / Font-', 'v', '4 file-only v0', '.3'),
        [string]::Concat('msgui_', 'p', '4_font_', 'v', '4_v0', '_3')
    )
    $strictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    foreach ($file in @(Get-ChildItem -LiteralPath $Root -Recurse -File)) {
        if ([IO.Path]::GetExtension($file.Name) -in @('.ps1', '.cs', '.md', '.bat', '.json', '.jsonl')) {
            $text = $strictUtf8.GetString([IO.File]::ReadAllBytes($file.FullName))
            foreach ($legacyValue in $legacyValues) {
                if ($text.Contains($legacyValue)) {
                    throw "Staging contains a legacy release identity: $($file.FullName)"
                }
            }
        }
    }
}

function Assert-TrueChecks($Evidence, [string[]]$Names, [string]$Label) {
    foreach ($name in $Names) {
        $property = $Evidence.checks.PSObject.Properties[$name]
        if ($null -eq $property -or $property.Value -ne $true) {
            throw "$Label check is not true: $name"
        }
    }
}

function New-StrictZip([string]$SourceRoot, [string]$Destination) {
    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::Open($Destination, [IO.Compression.ZipArchiveMode]::Create)
    try {
        $prefix = [IO.Path]::GetFileName($SourceRoot) + '/'
        foreach ($file in @(Get-ChildItem -LiteralPath $SourceRoot -Recurse -File | Sort-Object FullName)) {
            $relative = $file.FullName.Substring($SourceRoot.TrimEnd('\').Length + 1).Replace('\', '/')
            $entry = $archive.CreateEntry($prefix + $relative, [IO.Compression.CompressionLevel]::Optimal)
            $entry.LastWriteTime = [DateTimeOffset]::new(2000, 1, 1, 0, 0, 0, [TimeSpan]::Zero)
            $input = [IO.File]::OpenRead($file.FullName)
            $output = $entry.Open()
            try { $input.CopyTo($output) }
            finally {
                $output.Dispose()
                $input.Dispose()
            }
        }
    }
    finally {
        $archive.Dispose()
    }
}

foreach ($required in @(
    $MessageSource,
    (Join-Path $FontPublicSource 'recipe.json'),
    (Join-Path $FontPublicSource 'payload\glyph_pixels_entry_6.bin'),
    (Join-Path $FontPublicSource 'payload\glyph_pixels_entry_7.bin'),
    (Join-Path $FontPublicSource 'metrics\glyphs.jsonl'),
    (Join-Path $FontPublicSource 'licenses\OFL-NotoSansKR.txt'),
    (Join-Path $FontPublicSource 'licenses\OFL-NotoSerifKR.txt'),
    (Join-Path $TemplateRoot 'tools\Invoke-FileOnlyPatch.ps1'),
    (Join-Path $TemplateRoot 'tools\FileRecipeCore.cs'),
    (Join-Path $TemplateRoot 'tools\JsonKeyGuard.cs'),
    (Join-Path $TemplateRoot 'README_KO.md.in'),
    (Join-Path $TemplateRoot 'FILE_ONLY_POLICY_KO.md'),
    (Join-Path $TemplateRoot 'APPLY_KOREAN_PATCH.bat'),
    (Join-Path $TemplateRoot 'RESTORE_ORIGINALS.bat'),
    (Join-Path $TemplateRoot 'VERIFY_PACKAGE.bat')
)) {
    Assert-OrdinaryLeaf $required 'release input'
}

$jsonGuardSource = Join-Path $TemplateRoot 'tools\JsonKeyGuard.cs'
if ([int64](Get-Item -LiteralPath $jsonGuardSource).Length -ne 11304 -or
    (Get-Sha256 $jsonGuardSource) -ne '6A1ABEC0899A1D4256153E49E8204DAE343EC5D7887DB3047192A8168678DA60') {
    throw 'JSON key guard does not match the pinned raw UTF-8 verifier'
}
Add-Type -Path $jsonGuardSource

$message = Read-Json $MessageSource
$font = Read-Json (Join-Path $FontPublicSource 'recipe.json')
$operations = @($message.operations)
[int[]]$operationIds = @($operations | ForEach-Object { [int]$_.id })
[string[]]$rasterCodepoints = @($font.corpus.raster_codepoints | ForEach-Object { [string]$_ })
$operationIdsSha256 = Get-CompactJsonSha256 $operationIds
$rasterCodepointsSha256 = Get-CompactJsonSha256 $rasterCodepoints

if ($message.schema -ne 'nobu16.file-only-msg-recipe.v1' -or
    $message.scope -ne 'msgui_catalog_v2' -or
    $message.language -ne 'SC' -or
    $message.file_only -ne $true -or
    $operations.Count -ne 3819 -or
    $message.operation_index.count -ne 3819 -or
    $message.operation_index.sorted_unique -ne $true -or
    $message.operation_index.id_encoding -ne 'UTF-8 compact JSON integer array' -or
    $operationIdsSha256 -ne ([string]$message.operation_index.ids_sha256).ToUpperInvariant()) {
    throw 'Full message source recipe contract failed'
}
if ([int64](Get-Item -LiteralPath $MessageSource).Length -ne 688338 -or
    (Get-Sha256 $MessageSource) -ne '3F5CAC974C95B19B78319DBF97C2289FFF82B4ED23A4950013DB94C19A6948AB') {
    throw 'Full message recipe does not match the pinned public artifact'
}
if ($message.version -ne '0.2-dev' -or
    [int64]$message.source.size -ne 60829 -or
    ([string]$message.source.sha256).ToUpperInvariant() -ne 'C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82' -or
    [int64]$message.target.size -ne 114448 -or
    ([string]$message.target.sha256).ToUpperInvariant() -ne 'E119ED2375389FB8B05984534E0BC190788B5DC2B94EABFF9E6AF1B591C11746' -or
    $operationIdsSha256 -ne '0F336EAF33E34461C7D6CA7D8667B02DC103786595CF783139E16912D99461FD') {
    throw 'Full message source/target pins are invalid'
}
for ($index = 0; $index -lt $operationIds.Count; $index++) {
    if (($index -gt 0 -and $operationIds[$index] -le $operationIds[$index - 1]) -or
        $operationIds[$index] -lt 0 -or $operationIds[$index] -ge 5100) {
        throw "Full operation index is not sorted/unique at $index"
    }
}
if ($font.schema -ne 'nobu16.file-only-g1n-tail-recipe.v2' -or
    $font.file_only -ne $true -or
    $font.process_memory_access -ne $false -or
    $font.registry_access -ne $false -or
    $font.payload_policy.commercial_original_bytes_in_public_payload -ne $false -or
    $rasterCodepoints.Count -ne 562 -or
    $rasterCodepointsSha256 -ne '72FA45F51EADB2827F220891D3A0FBDA0D46BC8A4673DE8AD1806E417372D7AC') {
    throw 'Font-v4 public recipe contract failed'
}
$fontRecipeSource = Join-Path $FontPublicSource 'recipe.json'
$fontPayload6Source = Join-Path $FontPublicSource 'payload\glyph_pixels_entry_6.bin'
$fontPayload7Source = Join-Path $FontPublicSource 'payload\glyph_pixels_entry_7.bin'
$fontMetricsSource = Join-Path $FontPublicSource 'metrics\glyphs.jsonl'
$fontSansLicenseSource = Join-Path $FontPublicSource 'licenses\OFL-NotoSansKR.txt'
$fontSerifLicenseSource = Join-Path $FontPublicSource 'licenses\OFL-NotoSerifKR.txt'
if ([int64](Get-Item -LiteralPath $fontRecipeSource).Length -ne 481533 -or
    (Get-Sha256 $fontRecipeSource) -ne '561477D6312FF02DDD18C09CBF4A2802E00BFA42015B325CFE6F04BDED04C109' -or
    [int64](Get-Item -LiteralPath $fontPayload6Source).Length -ne 1251072 -or
    (Get-Sha256 $fontPayload6Source) -ne '53898FD6039F8CAD63BC85D50791DD3451D9EDCB69EB6F15EE08550EF50A91ED' -or
    [int64](Get-Item -LiteralPath $fontPayload7Source).Length -ne 556032 -or
    (Get-Sha256 $fontPayload7Source) -ne 'CD34058F3C85554900314394AB3C1CFD92DF6CA7007068F44F2D12968DCA168D' -or
    [int64](Get-Item -LiteralPath $fontMetricsSource).Length -ne 691550 -or
    (Get-Sha256 $fontMetricsSource) -ne '1AF2EF974E0E6E3670F2FF3AAC127C28717128C86573DF759EBCFF73C01A9074' -or
    [int64](Get-Item -LiteralPath $fontSansLicenseSource).Length -ne 4388 -or
    (Get-Sha256 $fontSansLicenseSource) -ne '1C05C68C34F9708415AADA51F17E1B0092D2CEA709BF4A94CD38114F9E73D7D9' -or
    [int64](Get-Item -LiteralPath $fontSerifLicenseSource).Length -ne 4350 -or
    (Get-Sha256 $fontSerifLicenseSource) -ne '5E0DA210FB04058A8C0087985D2D456B931C2579811A49655721D3CF0C36B6D6') {
    throw 'Font-v4 recipe, glyph payload, metrics, or licenses do not match the pinned public artifacts'
}
if ($font.corpus.schema -ne 'nobu16.kr.font-v4-corpus-union.v1' -or
    [int]$font.corpus.source_non_whitespace_character_count -ne 645 -or
    ([string]$font.corpus.source_non_whitespace_codepoints_sha256).ToUpperInvariant() -ne 'F279DD93CA82142767E7C24F9640E017C3F6FABDB0FDD63D0D52F24511EA5B01' -or
    [int]$font.corpus.excluded_font_token_count -ne 19 -or
    ([string]$font.corpus.excluded_font_tokens_sha256).ToUpperInvariant() -ne '6579C55EFF39DCA50D8152BCFE3686072DB1F07B185B50BAF363840F4C772E38' -or
    ([string]$font.corpus.excluded_font_codepoints_sha256).ToUpperInvariant() -ne 'B88CD9A68EBB6FC6221D01FFE7F89AA014FECA46EF1A2B13CCDCC8730D36F2FF' -or
    [int]$font.corpus.character_count -ne 626 -or
    ([string]$font.corpus.union_codepoints_sha256).ToUpperInvariant() -ne 'BAD72B2E09A71127243F9966FB70B08A4613B01F4596EF0FF10169A88FA12DCF' -or
    [int]$font.corpus.hangul_syllable_count -ne 523 -or
    ([string]$font.corpus.hangul_codepoints_sha256).ToUpperInvariant() -ne '89E62D3B4438C8DF7541E10A9D4C90B8F37EB2DCB314789E3C446F3855794873' -or
    [int]$font.corpus.non_hangul_character_count -ne 103 -or
    [int]$font.corpus.non_hangul_fully_stock_covered_count -ne 64 -or
    [int]$font.corpus.non_hangul_rasterized_count -ne 39 -or
    [int]$font.corpus.raster_codepoint_count -ne 562 -or
    ([string]$font.corpus.raster_codepoints_sha256).ToUpperInvariant() -ne '1853386D46EAAAD385E909AE04BCC88DF1B42FCAAD741B87C9EBA1467BFE4229' -or
    [int64]$font.languages.SC.stock_archive.size -ne 160318119 -or
    ([string]$font.languages.SC.stock_archive.sha256).ToUpperInvariant() -ne '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99' -or
    [int64]$font.languages.SC.target_archive.size -ne 181011663 -or
    ([string]$font.languages.SC.target_archive.sha256).ToUpperInvariant() -ne '02F0D4E09F8F1B13CD90D23A92F75302F49E34059CB659C4E59C1569EE2D3A8A') {
    throw 'Font-v4 corpus or archive pins are invalid'
}
foreach ($entryNumber in @(6, 7)) {
    $entry = $font.languages.SC.entries.([string]$entryNumber)
    $tables = @($entry.tables)
    if ($tables.Count -ne 2 -or
        @($tables[0].append_codepoints).Count -ne 524 -or
        @($tables[1].append_codepoints).Count -ne 562 -or
        ([string]$tables[0].append_codepoints_sha256).ToUpperInvariant() -ne 'D8DDD31D385CB364EACCE677A4FE22752CEFD16DDE65DE92C2189C9959F734E1' -or
        ([string]$tables[1].append_codepoints_sha256).ToUpperInvariant() -ne '1853386D46EAAAD385E909AE04BCC88DF1B42FCAAD741B87C9EBA1467BFE4229' -or
        [int]$entry.pixel_payload.glyph_count_by_table.'0' -ne 524 -or
        [int]$entry.pixel_payload.glyph_count_by_table.'1' -ne 562) {
        throw "Font-v4 entry $entryNumber per-table contract is invalid"
    }
}

$offlineValidated = $false
$offlineEvidence = $null
if ($OfflineEvidencePath) {
    $OfflineEvidencePath = Get-FullPath $OfflineEvidencePath
    Assert-OrdinaryLeaf $OfflineEvidencePath 'offline evidence'
    $offlineEvidence = Read-Json $OfflineEvidencePath
    if ($offlineEvidence.schema -ne 'nobu16.file-only-offline-validation.v2' -or
        $offlineEvidence.passed -ne $true -or
        ([string]$offlineEvidence.artifacts.message_target_sha256).ToUpperInvariant() -ne
            ([string]$message.target.sha256).ToUpperInvariant() -or
        ([string]$offlineEvidence.artifacts.font_target_sha256).ToUpperInvariant() -ne
            ([string]$font.languages.SC.target_archive.sha256).ToUpperInvariant()) {
        throw 'Offline validation evidence does not match the current full targets'
    }
    Assert-TrueChecks $offlineEvidence @(
        'verify_passed', 'apply_passed', 'restore_passed', 'bad_stock_rejected',
        'mixed_state_recovered', 'running_process_refused', 'package_tamper_rejected',
        'json_duplicate_keys_rejected', 'build_duplicate_keys_rejected',
        'audit_duplicate_keys_rejected', 'untrusted_installer_not_executed',
        'installed_game_files_unchanged'
    ) 'offline evidence'
    $offlineValidated = $true
}

$runtimeValidated = $false
$runtimeEvidence = $null
if ($RuntimeEvidencePath) {
    if (-not $offlineValidated) {
        throw 'Runtime evidence can only be assembled with passing offline evidence'
    }
    $RuntimeEvidencePath = Get-FullPath $RuntimeEvidencePath
    Assert-OrdinaryLeaf $RuntimeEvidencePath 'runtime evidence'
    $runtimeEvidence = Read-Json $RuntimeEvidencePath
    if ($runtimeEvidence.schema -ne 'nobu16.file-only-runtime-validation.v2' -or
        $runtimeEvidence.passed -ne $true -or
        ([string]$runtimeEvidence.artifacts.message_target_sha256).ToUpperInvariant() -ne
            ([string]$message.target.sha256).ToUpperInvariant() -or
        ([string]$runtimeEvidence.artifacts.font_target_sha256).ToUpperInvariant() -ne
            ([string]$font.languages.SC.target_archive.sha256).ToUpperInvariant()) {
        throw 'Runtime validation evidence does not match the current full targets'
    }
    Assert-TrueChecks $runtimeEvidence @(
        'boot_completed', 'korean_ui_visible', 'missing_glyphs_checked',
        'clipping_checked', 'normal_exit', 'stock_restored_after_qa'
    ) 'runtime evidence'
    $castleNameHorizontal = $runtimeEvidence.checks.PSObject.Properties['castle_name_horizontal']
    if ($null -eq $castleNameHorizontal -or $castleNameHorizontal.Value -isnot [bool]) {
        throw 'Runtime evidence check must be present and boolean: castle_name_horizontal'
    }
    $screens = @($runtimeEvidence.screens)
    if ($screens.Count -lt 1 -or $screens.Count -gt 20 -or
        @($runtimeEvidence.scope.observed_labels).Count -lt 1 -or
        @($runtimeEvidence.scope.untested_areas).Count -lt 1) {
        throw 'Runtime validation scope is incomplete'
    }
    $seenScreens = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($screen in $screens) {
        $file = [string]$screen.file
        $expectedHash = ([string]$screen.sha256).ToUpperInvariant()
        if ($file -notmatch '\A[A-Za-z0-9_.-]{1,128}\z' -or
            $expectedHash -notmatch '\A[0-9A-F]{64}\z' -or
            -not $seenScreens.Add($file)) {
            throw 'Runtime screenshot evidence contains an unsafe or duplicate record'
        }
        $screenshotPath = Join-Path $KrPatchRoot "reports\screenshots\$file"
        Assert-OrdinaryLeaf $screenshotPath 'runtime screenshot evidence'
        if ((Get-Sha256 $screenshotPath) -ne $expectedHash) {
            throw "Runtime screenshot hash mismatch: $file"
        }
    }
    $runtimeValidated = $true
}

$releaseEligible = $offlineValidated -and $runtimeValidated

$outputFull = Get-FullPath $OutputRoot
$releasesRoot = Get-FullPath (Join-Path $KrPatchRoot 'releases')
$allowedPrefix = $releasesRoot.TrimEnd('\') + '\'
if (-not $outputFull.StartsWith($allowedPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "OutputRoot must remain below $releasesRoot"
}
if (Test-Path -LiteralPath $outputFull) {
    if (-not $Overwrite) {
        throw "Output already exists; pass -Overwrite: $outputFull"
    }
    $item = Get-Item -LiteralPath $outputFull -Force
    if (-not $item.PSIsContainer -or
        ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'Refusing to overwrite a non-directory or reparse-point output'
    }
    Remove-Item -LiteralPath $outputFull -Recurse -Force
}

$staging = Join-Path $releasesRoot ('.' + [IO.Path]::GetFileName($outputFull) + '.staging.' + [Guid]::NewGuid().ToString('N'))
try {
    [IO.Directory]::CreateDirectory($staging) | Out-Null
    foreach ($directory in @(
        'components\message', 'components\font\payload', 'components\font\licenses',
        'components\font\metrics', 'tools'
    )) {
        [IO.Directory]::CreateDirectory((Join-Path $staging $directory)) | Out-Null
    }

    Copy-Item -LiteralPath $MessageSource -Destination (Join-Path $staging 'components\message\msgui_sc.recipe.json')
    Copy-Item -LiteralPath (Join-Path $FontPublicSource 'recipe.json') `
        -Destination (Join-Path $staging 'components\font\recipe.json')
    foreach ($entry in @(6, 7)) {
        Copy-Item -LiteralPath (Join-Path $FontPublicSource "payload\glyph_pixels_entry_$entry.bin") `
            -Destination (Join-Path $staging "components\font\payload\glyph_pixels_entry_$entry.bin")
    }
    Copy-Item -LiteralPath (Join-Path $FontPublicSource 'metrics\glyphs.jsonl') `
        -Destination (Join-Path $staging 'components\font\metrics\glyphs.jsonl')
    foreach ($license in @('OFL-NotoSansKR.txt', 'OFL-NotoSerifKR.txt')) {
        Copy-Item -LiteralPath (Join-Path $FontPublicSource "licenses\$license") `
            -Destination (Join-Path $staging "components\font\licenses\$license")
    }
    foreach ($name in @(
        'APPLY_KOREAN_PATCH.bat', 'RESTORE_ORIGINALS.bat', 'VERIFY_PACKAGE.bat',
        'FILE_ONLY_POLICY_KO.md'
    )) {
        Copy-Item -LiteralPath (Join-Path $TemplateRoot $name) -Destination (Join-Path $staging $name)
    }
    Copy-Item -LiteralPath (Join-Path $TemplateRoot 'tools\Invoke-FileOnlyPatch.ps1') `
        -Destination (Join-Path $staging 'tools\Invoke-FileOnlyPatch.ps1')
    Copy-Item -LiteralPath (Join-Path $TemplateRoot 'tools\FileRecipeCore.cs') `
        -Destination (Join-Path $staging 'tools\FileRecipeCore.cs')
    Copy-Item -LiteralPath (Join-Path $TemplateRoot 'tools\JsonKeyGuard.cs') `
        -Destination (Join-Path $staging 'tools\JsonKeyGuard.cs')

    $status = if ($releaseEligible) {
        [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(
            '7Jik7ZSE65287J24IOyEpOy5mC/rs7Xsm5Dqs7wg7Iuk7KCcIOqyjOyehCDtmZTrqbQg6rKA7IiY66W8IO2GteqzvO2VnCDrsLDtj6wg7ZuE67O0'))
    }
    else {
        [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(
            '6rCc67CcIOuniOydvOyKpO2GpCDigJQg7Iuk7KCcIOqyjOyehCDtmZTrqbQg6rKA7IiYIOyghOydtOuvgOuhnCDsoJXsi50g67Cw7Y+sIOuwjyDsnbzrsJgg7ISk7LmY6rCAIOywqOuLqOuQqA=='))
    }
    $readme = [IO.File]::ReadAllText((Join-Path $TemplateRoot 'README_KO.md.in'), [Text.Encoding]::UTF8)
    $readme = $readme.Replace('{{RELEASE_STATUS}}', $status)
    [IO.File]::WriteAllText((Join-Path $staging 'README_KO.md'), $readme, $Utf8NoBom)

    $evidenceGeneratedUtc = if ($runtimeValidated) {
        [string]$runtimeEvidence.artifacts.validated_utc
    }
    elseif ($offlineValidated) {
        [string]$offlineEvidence.validated_utc
    }
    else {
        '2026-07-14T00:00:00Z'
    }
    $evidence = [ordered]@{
        schema = 'nobu16.file-only-validation-evidence.v2'
        generated_utc = $evidenceGeneratedUtc
        release_id = $ReleaseId
        release_eligible = $releaseEligible
        offline = [ordered]@{
            passed = $offlineValidated
            source_sha256 = if ($offlineValidated) { Get-Sha256 $OfflineEvidencePath } else { $null }
            checks = if ($offlineValidated) {
                [ordered]@{
                    verify_passed = [bool]$offlineEvidence.checks.verify_passed
                    apply_passed = [bool]$offlineEvidence.checks.apply_passed
                    restore_passed = [bool]$offlineEvidence.checks.restore_passed
                    bad_stock_rejected = [bool]$offlineEvidence.checks.bad_stock_rejected
                    mixed_state_recovered = [bool]$offlineEvidence.checks.mixed_state_recovered
                    running_process_refused = [bool]$offlineEvidence.checks.running_process_refused
                    package_tamper_rejected = [bool]$offlineEvidence.checks.package_tamper_rejected
                    json_duplicate_keys_rejected = [bool]$offlineEvidence.checks.json_duplicate_keys_rejected
                    build_duplicate_keys_rejected = [bool]$offlineEvidence.checks.build_duplicate_keys_rejected
                    audit_duplicate_keys_rejected = [bool]$offlineEvidence.checks.audit_duplicate_keys_rejected
                    untrusted_installer_not_executed = [bool]$offlineEvidence.checks.untrusted_installer_not_executed
                    installed_game_files_unchanged = [bool]$offlineEvidence.checks.installed_game_files_unchanged
                }
            }
            else { $null }
            artifacts = if ($offlineValidated) {
                [ordered]@{
                    message_stock_sha256 = ([string]$offlineEvidence.artifacts.message_stock_sha256).ToUpperInvariant()
                    message_target_sha256 = ([string]$offlineEvidence.artifacts.message_target_sha256).ToUpperInvariant()
                    font_stock_sha256 = ([string]$offlineEvidence.artifacts.font_stock_sha256).ToUpperInvariant()
                    font_target_sha256 = ([string]$offlineEvidence.artifacts.font_target_sha256).ToUpperInvariant()
                    powershell_version = [string]$offlineEvidence.artifacts.powershell_version
                }
            }
            else { $null }
        }
        runtime = [ordered]@{
            passed = $runtimeValidated
            source_sha256 = if ($runtimeValidated) { Get-Sha256 $RuntimeEvidencePath } else { $null }
            checks = if ($runtimeValidated) {
                [ordered]@{
                    boot_completed = [bool]$runtimeEvidence.checks.boot_completed
                    korean_ui_visible = [bool]$runtimeEvidence.checks.korean_ui_visible
                    castle_name_horizontal = [bool]$runtimeEvidence.checks.castle_name_horizontal
                    missing_glyphs_checked = [bool]$runtimeEvidence.checks.missing_glyphs_checked
                    clipping_checked = [bool]$runtimeEvidence.checks.clipping_checked
                    normal_exit = [bool]$runtimeEvidence.checks.normal_exit
                    stock_restored_after_qa = [bool]$runtimeEvidence.checks.stock_restored_after_qa
                }
            }
            else { $null }
            artifacts = if ($runtimeValidated) {
                [ordered]@{
                    message_target_sha256 = ([string]$runtimeEvidence.artifacts.message_target_sha256).ToUpperInvariant()
                    font_target_sha256 = ([string]$runtimeEvidence.artifacts.font_target_sha256).ToUpperInvariant()
                    validated_utc = [string]$runtimeEvidence.artifacts.validated_utc
                }
            }
            else { $null }
            screens = if ($runtimeValidated) {
                @($runtimeEvidence.screens | ForEach-Object {
                    [ordered]@{
                        file = [string]$_.file
                        sha256 = ([string]$_.sha256).ToUpperInvariant()
                    }
                })
            }
            else { $null }
            scope = if ($runtimeValidated) {
                [ordered]@{
                    observed_labels = @($runtimeEvidence.scope.observed_labels | ForEach-Object { [string]$_ })
                    untested_areas = @($runtimeEvidence.scope.untested_areas | ForEach-Object { [string]$_ })
                }
            }
            else { $null }
        }
    }
    Write-Utf8Json (Join-Path $staging 'VALIDATION_EVIDENCE.json') $evidence 20

    $fontRecipePath = Join-Path $staging 'components\font\recipe.json'
    $messageRecipePath = Join-Path $staging 'components\message\msgui_sc.recipe.json'
    $payloadSpecs = @()
    foreach ($entry in @(6, 7)) {
        $relative = "components/font/payload/glyph_pixels_entry_$entry.bin"
        $path = Join-Path $staging ($relative.Replace('/', '\'))
        $payloadSpecs += [ordered]@{
            path = $relative
            size = [int64](Get-Item -LiteralPath $path).Length
            sha256 = Get-Sha256 $path
        }
    }

    $fileSpecs = @()
    $files = @(Get-ChildItem -LiteralPath $staging -Recurse -File | Sort-Object FullName)
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($staging.TrimEnd('\').Length + 1).Replace('\', '/')
        $fileSpecs += [ordered]@{
            path = $relative
            size = [int64]$file.Length
            sha256 = Get-Sha256 $file.FullName
        }
    }

    if ($fileSpecs.Count -ne 16) {
        throw "Staging public inventory must contain exactly 16 manifest-listed files; found $($fileSpecs.Count)"
    }

    $manifest = [ordered]@{
        schema = 'nobu16.korean-file-only-release.v2'
        release_id = $ReleaseId
        release_name = 'NOBU16 Korean MSGUI Full / Font-v4 file-only v0.3'
        version = if ($releaseEligible) { '0.3' } else { '0.3-dev' }
        architecture = 'file-only-offline'
        development_milestone = (-not $releaseEligible)
        release_eligible = $releaseEligible
        runtime_validation = if ($runtimeValidated) { 'passed' } else { 'pending' }
        install_restore_tested = $offlineValidated
        process_memory_access = $false
        executable_modified = $false
        registry_modified = $false
        registry_write = $false
        launches_game = $false
        resident_component = $false
        commercial_full_files_included = $false
        requires_process_running = $false
        payload_format = 'recipes-and-deltas-only'
        python_required_by_end_user = $false
        official_launcher_language = 'Simplified Chinese'
        target_files = @('MSG_PK/SC/msgui.bin', 'RES_SC/res_lang.bin')
        backup_directory_name = 'msgui_full_font_v4_v0_3'
        transaction_journal = $true
        message = [ordered]@{
            recipe_path = 'components/message/msgui_sc.recipe.json'
            recipe_size = [int64](Get-Item -LiteralPath $messageRecipePath).Length
            recipe_sha256 = Get-Sha256 $messageRecipePath
            recipe_shape_sha256 = '489D31EA78B3C00DFEE458B586D7169CE65E3FFB5C59C16FD571E1FBD1C2D464'
            operation_count = $operations.Count
            operation_ids_encoding = 'UTF-8 compact JSON integer array'
            operation_ids_sha256 = $operationIdsSha256
            stock = [ordered]@{ size = [int64]$message.source.size; sha256 = ([string]$message.source.sha256).ToUpperInvariant() }
            target = [ordered]@{ size = [int64]$message.target.size; sha256 = ([string]$message.target.sha256).ToUpperInvariant() }
        }
        font = [ordered]@{
            recipe_path = 'components/font/recipe.json'
            recipe_size = [int64](Get-Item -LiteralPath $fontRecipePath).Length
            recipe_sha256 = Get-Sha256 $fontRecipePath
            recipe_shape_sha256 = '3BE6D316FF28A8D921BAB068B20D04F3932795FB684CD0CF8DF4749BD72A0C8C'
            raster_codepoint_count = $rasterCodepoints.Count
            raster_codepoints_encoding = 'UTF-8 compact JSON string array'
            raster_codepoints_sha256 = $rasterCodepointsSha256
            append_codepoints_encoding = 'ASCII U+XXXX LF-delimited lines'
            table0_append_count = 524
            table1_append_count = 562
            table0_codepoints_sha256 = 'D8DDD31D385CB364EACCE677A4FE22752CEFD16DDE65DE92C2189C9959F734E1'
            table1_codepoints_sha256 = '1853386D46EAAAD385E909AE04BCC88DF1B42FCAAD741B87C9EBA1467BFE4229'
            stock = [ordered]@{ size = [int64]$font.languages.SC.stock_archive.size; sha256 = ([string]$font.languages.SC.stock_archive.sha256).ToUpperInvariant() }
            target = [ordered]@{ size = [int64]$font.languages.SC.target_archive.size; sha256 = ([string]$font.languages.SC.target_archive.sha256).ToUpperInvariant() }
            payloads = $payloadSpecs
        }
        files = $fileSpecs
    }
    Write-Utf8Json (Join-Path $staging 'release_manifest.json') $manifest 20
    Assert-NoLegacyReleaseIdentity $staging

    [IO.Directory]::Move($staging, $outputFull)
    $staging = $null
}
finally {
    if ($staging -and (Test-Path -LiteralPath $staging -PathType Container)) {
        Remove-Item -LiteralPath $staging -Recurse -Force
    }
}

$zipPath = $null
if ($CreateZip) {
    $zipPath = $outputFull + '.zip'
    if (Test-Path -LiteralPath $zipPath -PathType Leaf) {
        if (-not $Overwrite) {
            throw "ZIP already exists; pass -Overwrite: $zipPath"
        }
        Remove-Item -LiteralPath $zipPath -Force
    }
    New-StrictZip $outputFull $zipPath
}

$auditScript = Join-Path $PSScriptRoot 'Audit-ReleaseP4VNext.ps1'
Assert-OrdinaryLeaf $auditScript 'vNext public audit'
if ($zipPath) {
    & $auditScript -PackageRoot $outputFull -ZipPath $zipPath | Out-Null
}
else {
    & $auditScript -PackageRoot $outputFull | Out-Null
}

$sidecarPath = $null
if ($zipPath) {
    $sidecarPath = $zipPath + '.sha256'
    $zipHash = Get-Sha256 $zipPath
    $sidecar = $zipHash + '  ' + [IO.Path]::GetFileName($zipPath) + "`n"
    [IO.File]::WriteAllText($sidecarPath, $sidecar, $Utf8NoBom)
}

[pscustomobject]@{
    output_root = $outputFull
    manifest_sha256 = Get-Sha256 (Join-Path $outputFull 'release_manifest.json')
    release_eligible = $releaseEligible
    operation_count = $operations.Count
    operation_ids_sha256 = $operationIdsSha256
    raster_codepoint_count = $rasterCodepoints.Count
    table0_append_count = 524
    table1_append_count = 562
    zip_path = $zipPath
    zip_sha256 = if ($zipPath) { Get-Sha256 $zipPath } else { $null }
    sidecar_path = $sidecarPath
    sidecar_sha256 = if ($sidecarPath) { Get-Sha256 $sidecarPath } else { $null }
}
