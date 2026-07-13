[CmdletBinding()]
param(
    [ValidateSet('Apply', 'Restore', 'Verify')]
    [string]$Action = 'Apply',
    [string]$GameRoot,
    [switch]$AllowDevelopmentMilestone
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PackageRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $PackageRoot 'release_manifest.json'
$CorePath = Join-Path $PSScriptRoot 'FileRecipeCore.cs'
$JsonGuardPath = Join-Path $PSScriptRoot 'JsonKeyGuard.cs'

function Get-NormalizedPath([string]$Path) {
    return [System.IO.Path]::GetFullPath($Path)
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Assert-FileSpec([string]$Path, $Spec, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path
    if ([int64]$item.Length -ne [int64]$Spec.size) {
        throw "$Label size mismatch: $($item.Length), expected $($Spec.size)"
    }
    $actual = Get-Sha256 $Path
    $expected = ([string]$Spec.sha256).ToUpperInvariant()
    if ($actual -ne $expected) {
        throw "$Label SHA-256 mismatch: $actual, expected $expected"
    }
}

function Assert-Bytes([byte[]]$Bytes, $Spec, [string]$Label) {
    if ([int64]$Bytes.Length -ne [int64]$Spec.size) {
        throw "$Label size mismatch: $($Bytes.Length), expected $($Spec.size)"
    }
    $actual = [N16KrFileOnly.FileRecipeCore]::Sha256($Bytes)
    $expected = ([string]$Spec.sha256).ToUpperInvariant()
    if ($actual -ne $expected) {
        throw "$Label SHA-256 mismatch: $actual, expected $expected"
    }
}

function Read-Json([string]$Path) {
    [byte[]]$bytes = [IO.File]::ReadAllBytes($Path)
    [N16KrFileOnly.JsonKeyGuard]::AssertNoDuplicateKeys($bytes)
    $strictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    $text = $strictUtf8.GetString($bytes)
    return ($text | ConvertFrom-Json)
}

function Set-StateField($State, [string]$Name, $Value) {
    if ($State -is [System.Collections.IDictionary]) {
        $State[$Name] = $Value
    }
    else {
        $State | Add-Member -NotePropertyName $Name -NotePropertyValue $Value -Force
    }
}

function Get-CompactJsonSha256($Value) {
    $json = ConvertTo-Json -InputObject $Value -Compress
    [byte[]]$bytes = [Text.Encoding]::UTF8.GetBytes($json)
    return [N16KrFileOnly.FileRecipeCore]::Sha256($bytes)
}

function Get-CodepointLinesSha256([string[]]$Values) {
    $text = [string]::Join("`n", $Values) + "`n"
    [byte[]]$bytes = [Text.Encoding]::ASCII.GetBytes($text)
    return [N16KrFileOnly.FileRecipeCore]::Sha256($bytes)
}

function Get-JsonShapeSha256($Root) {
    $lines = New-Object 'System.Collections.Generic.List[string]'
    function Add-JsonShapeNode($Value, [string]$Path) {
        if ($null -eq $Value) {
            $lines.Add("$Path|null")
            return
        }
        if ($Value -is [Management.Automation.PSCustomObject]) {
            $lines.Add("$Path|object")
            [string[]]$names = @($Value.PSObject.Properties.Name)
            [Array]::Sort($names, [StringComparer]::Ordinal)
            foreach ($name in $names) {
                Add-JsonShapeNode $Value.PSObject.Properties[$name].Value ($Path + '/' + $name)
            }
            return
        }
        if ($Value -is [Array]) {
            $lines.Add("$Path|array|$($Value.Count)")
            for ($index = 0; $index -lt $Value.Count; $index++) {
                Add-JsonShapeNode $Value[$index] ($Path + '/' + $index)
            }
            return
        }
        $type = if ($Value -is [bool]) { 'boolean' }
            elseif ($Value -is [string]) { 'string' }
            elseif ($Value -is [ValueType]) { 'number' }
            else { $Value.GetType().FullName }
        $lines.Add("$Path|$type")
    }
    Add-JsonShapeNode $Root '$'
    [byte[]]$bytes = [Text.Encoding]::UTF8.GetBytes([string]::Join("`n", $lines))
    return [N16KrFileOnly.FileRecipeCore]::Sha256($bytes)
}

function Assert-JsonStringLimits($Root, [string]$Label) {
    function Test-JsonStringNode($Value, [string]$Path) {
        if ($null -eq $Value) { return }
        if ($Value -is [Management.Automation.PSCustomObject]) {
            foreach ($property in $Value.PSObject.Properties) {
                Test-JsonStringNode $property.Value ($Path + '/' + $property.Name)
            }
            return
        }
        if ($Value -is [Array]) {
            for ($index = 0; $index -lt $Value.Count; $index++) {
                Test-JsonStringNode $Value[$index] ($Path + '/' + $index)
            }
            return
        }
        if ($Value -is [string]) {
            $limit = if ($Path.EndsWith('/appended_records_hex', [StringComparison]::Ordinal)) { 16384 } else { 1024 }
            if ($Value.Length -gt $limit) {
                throw "$Label contains an oversized string field: $Path"
            }
        }
    }
    Test-JsonStringNode $Root '$'
}

function Assert-ExactProperties($Object, [string[]]$Expected, [string]$Label) {
    if ($null -eq $Object -or $Object -isnot [Management.Automation.PSCustomObject]) {
        throw "$Label must be a JSON object"
    }
    [string[]]$actual = @($Object.PSObject.Properties.Name)
    [Array]::Sort($actual, [StringComparer]::Ordinal)
    [Array]::Sort($Expected, [StringComparer]::Ordinal)
    if ($actual.Count -ne $Expected.Count) {
        throw "$Label has an unexpected property count"
    }
    for ($index = 0; $index -lt $actual.Count; $index++) {
        if ($actual[$index] -ne $Expected[$index]) {
            throw "$Label contains a missing or additional property: $($actual[$index])"
        }
    }
}

function Assert-RecipeContracts($Manifest, $MessageRecipe, $FontRecipe) {
    $messageShape = Get-JsonShapeSha256 $MessageRecipe
    $fontShape = Get-JsonShapeSha256 $FontRecipe
    Assert-JsonStringLimits $MessageRecipe 'message recipe'
    Assert-JsonStringLimits $FontRecipe 'font recipe'
    if ($messageShape -ne '9B6EDAA4B01889251F0EECE361B6B336DBB408C8AFA1BFA84973E15732BB3E88' -or
        $messageShape -ne ([string]$Manifest.message.recipe_shape_sha256).ToUpperInvariant() -or
        $fontShape -ne '53652DD2518A8DC2EA0F85861E24AC886527F3F045281AE4381A05E6B626AA4E' -or
        $fontShape -ne ([string]$Manifest.font.recipe_shape_sha256).ToUpperInvariant()) {
        throw 'Recipe JSON schema contains missing, extra, or mistyped fields'
    }
    if ($MessageRecipe.schema -ne 'nobu16.file-only-msg-recipe.v1' -or
        $MessageRecipe.scope -ne 'msgui_catalog_v2' -or
        $MessageRecipe.version -ne '0.2-dev' -or
        $MessageRecipe.language -ne 'SC' -or
        $MessageRecipe.file_only -ne $true -or
        $MessageRecipe.source.relative_path -ne 'MSG_PK/SC/msgui.bin' -or
        [int]$MessageRecipe.source.string_count -ne 5100 -or
        [int64]$MessageRecipe.source.size -ne 60829 -or
        ([string]$MessageRecipe.source.sha256).ToUpperInvariant() -ne 'C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82' -or
        [int64]$MessageRecipe.target.size -ne 87274 -or
        ([string]$MessageRecipe.target.sha256).ToUpperInvariant() -ne '5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984' -or
        [int64]$MessageRecipe.source.size -ne [int64]$Manifest.message.stock.size -or
        ([string]$MessageRecipe.source.sha256).ToUpperInvariant() -ne ([string]$Manifest.message.stock.sha256).ToUpperInvariant() -or
        [int64]$MessageRecipe.target.size -ne [int64]$Manifest.message.target.size -or
        ([string]$MessageRecipe.target.sha256).ToUpperInvariant() -ne ([string]$Manifest.message.target.sha256).ToUpperInvariant()) {
        throw 'Message recipe contract is invalid'
    }
    if ((Get-Sha256 $MessageRecipePath) -ne 'E6CC464E01F9D86A8AC995FD47FBE1EF6AD51DCD67C05117A7BF8ECC573460D2' -or
        (Get-Sha256 $MessageRecipePath) -ne ([string]$Manifest.message.recipe_sha256).ToUpperInvariant()) {
        throw 'Message recipe bytes do not match the pinned P4 public artifact'
    }

    $operations = @($MessageRecipe.operations)
    if ($operations.Count -ne 931 -or
        $operations.Count -ne [int]$Manifest.message.operation_count -or
        $operations.Count -ne [int]$MessageRecipe.operation_index.count -or
        $MessageRecipe.operation_index.sorted_unique -ne $true -or
        $MessageRecipe.operation_index.id_encoding -ne 'UTF-8 compact JSON integer array') {
        throw 'Message recipe operation index is invalid'
    }
    [int[]]$ids = @($operations | ForEach-Object { [int]$_.id })
    for ($index = 0; $index -lt $operations.Count; $index++) {
        $operation = $operations[$index]
        if ($ids[$index] -lt 0 -or $ids[$index] -ge 5100 -or
            ($index -gt 0 -and $ids[$index] -le $ids[$index - 1]) -or
            [string]$operation.source_utf16le_sha256 -notmatch '\A[0-9A-F]{64}\z' -or
            [string]::IsNullOrEmpty([string]$operation.replacement) -or
            ([string]$operation.replacement).IndexOf([char]0) -ge 0) {
            throw "Message operation $index is invalid"
        }
    }
    $idsSha256 = Get-CompactJsonSha256 $ids
    if ($idsSha256 -ne '7F95C3EDB26F6C53990B35C5C2C4C3552B4789E1F8BA4D140A77948C9B57E187' -or
        $idsSha256 -ne ([string]$MessageRecipe.operation_index.ids_sha256).ToUpperInvariant() -or
        $idsSha256 -ne ([string]$Manifest.message.operation_ids_sha256).ToUpperInvariant()) {
        throw 'Message operation ID hash mismatch'
    }

    $languageNames = @($FontRecipe.languages.PSObject.Properties.Name)
    $fontLanguage = $FontRecipe.languages.SC
    if ($FontRecipe.schema -ne 'nobu16.file-only-g1n-tail-recipe.v2' -or
        $FontRecipe.file_only -ne $true -or
        $FontRecipe.process_memory_access -ne $false -or
        $FontRecipe.registry_access -ne $false -or
        $FontRecipe.installed_game_files_modified -ne $false -or
        @($FontRecipe.runtime_patch_features).Count -ne 0 -or
        $FontRecipe.payload_policy.commercial_original_bytes_in_public_payload -ne $false -or
        $languageNames.Count -ne 1 -or $languageNames[0] -ne 'SC' -or
        $fontLanguage.stock_archive.path -ne 'RES_SC/res_lang.bin' -or
        [int64]$fontLanguage.stock_archive.size -ne 160318119 -or
        ([string]$fontLanguage.stock_archive.sha256).ToUpperInvariant() -ne '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99' -or
        [int64]$fontLanguage.target_archive.size -ne 180350761 -or
        ([string]$fontLanguage.target_archive.sha256).ToUpperInvariant() -ne '3BC57379D9AF95E83A77C96C1EE2D104AAF4A8BEA1733EA33FC3D1BCF056D1A9' -or
        [int64]$fontLanguage.stock_archive.size -ne [int64]$Manifest.font.stock.size -or
        ([string]$fontLanguage.stock_archive.sha256).ToUpperInvariant() -ne ([string]$Manifest.font.stock.sha256).ToUpperInvariant() -or
        [int64]$fontLanguage.target_archive.size -ne [int64]$Manifest.font.target.size -or
        ([string]$fontLanguage.target_archive.sha256).ToUpperInvariant() -ne ([string]$Manifest.font.target.sha256).ToUpperInvariant()) {
        throw 'Font recipe contract is invalid'
    }
    if ((Get-Sha256 $FontRecipePath) -ne 'EC4B9C68A1FF62DD06F53C55A30F45A3F12F62D1D1C7654196C780021288EA07' -or
        (Get-Sha256 $FontRecipePath) -ne ([string]$Manifest.font.recipe_sha256).ToUpperInvariant()) {
        throw 'Font recipe bytes do not match the pinned Font-v4 public artifact'
    }
    if ($FontRecipe.release_eligible -ne $false -or
        $FontRecipe.runtime_direct_lookup_verified -ne $false) {
        throw 'Packaged Font-v4 build recipe must remain the byte-exact public build artifact'
    }

    [string[]]$allowedCodepoints = @($FontRecipe.corpus.raster_codepoints | ForEach-Object { [string]$_ })
    [string[]]$hangulCodepoints = @($allowedCodepoints | Where-Object {
        $value = [Convert]::ToInt32($_.Substring(2), 16)
        $value -ge 0xAC00 -and $value -le 0xD7A3
    })
    [string[]]$nonHangulCodepoints = @($allowedCodepoints | Where-Object {
        $value = [Convert]::ToInt32($_.Substring(2), 16)
        $value -lt 0xAC00 -or $value -gt 0xD7A3
    })
    if ($FontRecipe.corpus.schema -ne 'nobu16.kr.font-v4-corpus-union.v1' -or
        [int]$FontRecipe.corpus.character_count -ne 387 -or
        [int]$FontRecipe.corpus.hangul_syllable_count -ne 342 -or
        [int]$FontRecipe.corpus.non_hangul_character_count -ne 45 -or
        [int]$FontRecipe.corpus.non_hangul_fully_stock_covered_count -ne 33 -or
        [int]$FontRecipe.corpus.non_hangul_rasterized_count -ne 12 -or
        [int]$FontRecipe.corpus.raster_codepoint_count -ne 354 -or
        $allowedCodepoints.Count -ne 354 -or
        $hangulCodepoints.Count -ne 342 -or
        $nonHangulCodepoints.Count -ne 12 -or
        $allowedCodepoints.Count -ne [int]$Manifest.font.raster_codepoint_count -or
        (Get-CompactJsonSha256 $allowedCodepoints) -ne '7EEE2CD1CD8C111108E23707CF80E48444611EB5239AEE700EF607679560B04F' -or
        (Get-CompactJsonSha256 $hangulCodepoints) -ne '70FDC71001D91EC3B62FA1E4588B811372608FCFEA4C6E484B960CC9010DF4A6' -or
        (Get-CodepointLinesSha256 $allowedCodepoints) -ne '700D935F92E05FFD806A8AD267EE7A9A2F46C393E945890AECBEED887CEC5BB7' -or
        (Get-CodepointLinesSha256 $hangulCodepoints) -ne '5254670AE29E925240BCC980155B78CFE2698094833B0D69B084715857B9D94D' -or
        ([string]$FontRecipe.corpus.raster_codepoints_sha256).ToUpperInvariant() -ne '700D935F92E05FFD806A8AD267EE7A9A2F46C393E945890AECBEED887CEC5BB7' -or
        (Get-CompactJsonSha256 $allowedCodepoints) -ne ([string]$Manifest.font.raster_codepoints_sha256).ToUpperInvariant()) {
        throw 'Font corpus contract is invalid'
    }
    for ($index = 0; $index -lt $allowedCodepoints.Count; $index++) {
        if ($allowedCodepoints[$index] -notmatch '\AU\+[0-9A-F]{4,6}\z' -or
            ($index -gt 0 -and [string]::CompareOrdinal($allowedCodepoints[$index - 1], $allowedCodepoints[$index]) -ge 0)) {
            throw "Font corpus codepoint $index is invalid"
        }
    }

    $appendContracts = @($FontRecipe.corpus.per_table_append_contract)
    if ($appendContracts.Count -ne 4) {
        throw 'Font corpus per-table append contract count is invalid'
    }
    for ($contractIndex = 0; $contractIndex -lt 4; $contractIndex++) {
        $expectedEntry = if ($contractIndex -lt 2) { 6 } else { 7 }
        $expectedTable = $contractIndex % 2
        $expectedCount = if ($expectedTable -eq 0) { 342 } else { 354 }
        $expectedHash = if ($expectedTable -eq 0) {
            '5254670AE29E925240BCC980155B78CFE2698094833B0D69B084715857B9D94D'
        }
        else {
            '700D935F92E05FFD806A8AD267EE7A9A2F46C393E945890AECBEED887CEC5BB7'
        }
        $contract = $appendContracts[$contractIndex]
        if ([int]$contract.entry -ne $expectedEntry -or [int]$contract.table -ne $expectedTable -or
            [int]$contract.count -ne $expectedCount -or
            ([string]$contract.codepoints_sha256).ToUpperInvariant() -ne $expectedHash) {
            throw "Font corpus per-table append contract $contractIndex is invalid"
        }
    }

    $entryNames = @($fontLanguage.entries.PSObject.Properties.Name)
    if ($entryNames.Count -ne 2 -or $entryNames -notcontains '6' -or $entryNames -notcontains '7') {
        throw 'Font recipe must contain exactly SC entries 6 and 7'
    }
    foreach ($entryNumber in @(6, 7)) {
        $entry = $fontLanguage.entries.([string]$entryNumber)
        $tables = @($entry.tables)
        $expectedPayload = "payload/glyph_pixels_entry_$entryNumber.bin"
        $manifestPayloadPath = "components/font/payload/glyph_pixels_entry_$entryNumber.bin"
        $manifestPayload = @($Manifest.font.payloads | Where-Object {
            [string]$_.path -eq $manifestPayloadPath
        })
        $recordBytes = @(($hangulCodepoints.Count * 12), ($allowedCodepoints.Count * 12))
        $pinnedPayloadSize = if ($entryNumber -eq 6) { 801792 } else { 356352 }
        $pinnedPayloadHash = if ($entryNumber -eq 6) {
            '7131812389A78D10296BF7B5786E1CA387960C6F4A6875E0E793BAAFB1A13082'
        }
        else {
            'FD320B8D1ED831559B3F7C2E1F236D1D38376EDDC5EF59F345D99D7F93864EEC'
        }
        $pinnedStockSize = if ($entryNumber -eq 6) { 25817936 } else { 11771536 }
        $pinnedStockHash = if ($entryNumber -eq 6) {
            '414A8E98DCF0F52633CD039A74E97AE61A97D98A96684D450EBADD4C3C85CAEB'
        }
        else {
            'DADBE4EEA223FD48CEFA9A93A08EF1F2458B3BD543ADFCEBD6D888B9EE2AFBB0'
        }
        $pinnedTargetSize = if ($entryNumber -eq 6) { 26628080 } else { 12136240 }
        $pinnedTargetHash = if ($entryNumber -eq 6) {
            '951906C6870F60F9342E9A90DF8DBF920D555092D3E06B1B822A41448740DD61'
        }
        else {
            'C96704BF3A7FE1B29E3CB29361D1E56FCA8062CA73210CBCFCD73BE2E7C7CC66'
        }
        $pinnedCell = if ($entryNumber -eq 6) { 48 } else { 32 }
        $pinnedBytesPerGlyph = if ($entryNumber -eq 6) { 1152 } else { 512 }
        $pinnedPayloadLengths = if ($entryNumber -eq 6) { @(393984, 407808) } else { @(175104, 181248) }
        $pinnedRecordHashes = if ($entryNumber -eq 6) {
            @('B388BBFA64C999A2E898E24B3BB213032FE37BA47A38A74FD4CA2921D170C3F2',
              '793ED59B8401B729A9EFE1331CCA8293F271266AE1EF692BF84AE79334F1E952')
        }
        else {
            @('17F1B16A954406D8612F18CA3D412433BB49C51B1594D7262E1AA46DB33D1540',
              '5259BE5DB61FDAFB752AA116AB7587245BD4AAADE8284D33FEB4F36B6A243C47')
        }
        if ([int]$entry.entry -ne $entryNumber -or $tables.Count -ne 2 -or
            [int64]$entry.stock.size -ne $pinnedStockSize -or
            ([string]$entry.stock.sha256).ToUpperInvariant() -ne $pinnedStockHash -or
            [int64]$entry.target.size -ne $pinnedTargetSize -or
            ([string]$entry.target.sha256).ToUpperInvariant() -ne $pinnedTargetHash -or
            [int]$entry.stock.atlas_offset -ne 534416 -or
            [int]$entry.target.atlas_offset -ne 542768 -or
            @($entry.stock.table_offsets).Count -ne 2 -or
            [int]$entry.stock.table_offsets[0] -ne 8296 -or
            [int]$entry.stock.table_offsets[1] -ne 402144 -or
            @($entry.target.table_offsets).Count -ne 2 -or
            [int]$entry.target.table_offsets[0] -ne 8296 -or
            [int]$entry.target.table_offsets[1] -ne 406248 -or
            [string]$entry.pixel_payload.file -ne $expectedPayload -or
            [int64]$entry.pixel_payload.size -ne $pinnedPayloadSize -or
            ([string]$entry.pixel_payload.sha256).ToUpperInvariant() -ne $pinnedPayloadHash -or
            [int]$entry.pixel_payload.cell -ne $pinnedCell -or
            [int]$entry.pixel_payload.bytes_per_glyph -ne $pinnedBytesPerGlyph -or
            [int]$entry.pixel_payload.raster_union_codepoint_count -ne 354 -or
            [int]$entry.pixel_payload.glyph_count_by_table.'0' -ne 342 -or
            [int]$entry.pixel_payload.glyph_count_by_table.'1' -ne 354 -or
            $manifestPayload.Count -ne 1 -or
            [int64]$manifestPayload[0].size -ne [int64]$entry.pixel_payload.size -or
            ([string]$manifestPayload[0].sha256).ToUpperInvariant() -ne ([string]$entry.pixel_payload.sha256).ToUpperInvariant() -or
            [int]$tables[0].pixel_payload_offset -ne 0 -or
            [int]$tables[1].pixel_payload_offset -ne [int]$tables[0].pixel_payload_length -or
            [int]$entry.pixel_payload.size -ne
                ([int]$tables[0].pixel_payload_length + [int]$tables[1].pixel_payload_length) -or
            [int]$entry.target.size -ne
                ([int]$entry.stock.size + $recordBytes[0] + $recordBytes[1] + [int]$entry.pixel_payload.size) -or
            [int]$entry.target.atlas_offset -ne
                ([int]$entry.stock.atlas_offset + $recordBytes[0] + $recordBytes[1])) {
            throw "Font entry $entryNumber structure is invalid"
        }
        $payloadPath = Join-Path $PackageRoot ("components\font\" + $expectedPayload.Replace('/', '\'))
        Assert-FileSpec $payloadPath $entry.pixel_payload "font pixel payload entry $entryNumber"
        for ($tableIndex = 0; $tableIndex -lt 2; $tableIndex++) {
            $table = $tables[$tableIndex]
            $changes = @($table.map_changes)
            [string[]]$expectedCodepoints = $(if ($tableIndex -eq 0) {
                $hangulCodepoints
            }
            else {
                $allowedCodepoints
            })
            if ([int]$table.table -ne $tableIndex -or
                [int]$table.source_record_count -ne $(if ($tableIndex -eq 0) { 21898 } else { 100 }) -or
                [int]$table.target_record_count -ne ([int]$table.source_record_count + $expectedCodepoints.Count) -or
                @($table.append_codepoints).Count -ne $expectedCodepoints.Count -or
                $changes.Count -ne $expectedCodepoints.Count -or
                [int]$table.pixel_payload_offset -ne $(if ($tableIndex -eq 0) { 0 } else { $pinnedPayloadLengths[0] }) -or
                [int]$table.pixel_payload_length -ne $pinnedPayloadLengths[$tableIndex] -or
                ([string]$table.append_codepoints_sha256).ToUpperInvariant() -ne
                    $(if ($tableIndex -eq 0) { '5254670AE29E925240BCC980155B78CFE2698094833B0D69B084715857B9D94D' } else { '700D935F92E05FFD806A8AD267EE7A9A2F46C393E945890AECBEED887CEC5BB7' }) -or
                ([string]$table.appended_records_sha256).ToUpperInvariant() -ne $pinnedRecordHashes[$tableIndex] -or
                ([string]$table.appended_records_hex).Length -ne ($recordBytes[$tableIndex] * 2)) {
                throw "Font entry $entryNumber table $tableIndex structure is invalid"
            }
            for ($index = 0; $index -lt $changes.Count; $index++) {
                if ([string]$table.append_codepoints[$index] -ne $expectedCodepoints[$index] -or
                    [string]$changes[$index].codepoint -ne $expectedCodepoints[$index] -or
                    [int]$changes[$index].expected_old_ordinal -ne 0 -or
                    [int]$changes[$index].new_ordinal -ne
                        ([int]$table.source_record_count + $index)) {
                    throw "Font entry $entryNumber table $tableIndex map change $index is invalid"
                }
            }
        }
    }
}

function Assert-EvidenceContract($Manifest, $Evidence) {
    Assert-JsonStringLimits $Evidence 'validation evidence'
    Assert-ExactProperties $Evidence @(
        'schema', 'generated_utc', 'release_id', 'release_eligible', 'offline', 'runtime'
    ) 'validation evidence'
    Assert-ExactProperties $Evidence.offline @(
        'passed', 'source_sha256', 'checks', 'artifacts'
    ) 'offline evidence'
    Assert-ExactProperties $Evidence.runtime @(
        'passed', 'source_sha256', 'checks', 'artifacts', 'screens', 'scope'
    ) 'runtime evidence'
    if ($Evidence.schema -ne 'nobu16.file-only-validation-evidence.v2' -or
        $Evidence.release_id -ne 'msgui-p4-font-v4-v0.3' -or
        $Evidence.release_eligible -ne $Manifest.release_eligible -or
        $Evidence.offline.passed -ne $Manifest.install_restore_tested) {
        throw 'Validation evidence contract is invalid'
    }
    if ($Manifest.runtime_validation -eq 'passed') {
        if ($Evidence.runtime.passed -ne $true) {
            throw 'Runtime-passed manifest is missing runtime evidence'
        }
    }
    elseif ($Evidence.runtime.passed -ne $false) {
        throw 'Pending runtime manifest contains contradictory evidence'
    }
    if ($Evidence.offline.passed -eq $true) {
        Assert-ExactProperties $Evidence.offline.checks @(
            'verify_passed', 'apply_passed', 'restore_passed', 'bad_stock_rejected',
            'mixed_state_recovered', 'running_process_refused', 'package_tamper_rejected',
            'json_duplicate_keys_rejected', 'build_duplicate_keys_rejected',
            'audit_duplicate_keys_rejected', 'untrusted_installer_not_executed',
            'installed_game_files_unchanged'
        ) 'offline evidence checks'
        Assert-ExactProperties $Evidence.offline.artifacts @(
            'message_stock_sha256', 'message_target_sha256', 'font_stock_sha256',
            'font_target_sha256', 'powershell_version'
        ) 'offline evidence artifacts'
        if ([string]$Evidence.offline.source_sha256 -notmatch '\A[0-9A-F]{64}\z' -or
            [string]$Evidence.offline.artifacts.message_stock_sha256 -ne 'C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82' -or
            [string]$Evidence.offline.artifacts.font_stock_sha256 -ne '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99' -or
            ([string]$Evidence.offline.artifacts.powershell_version).Length -gt 64) {
            throw 'Offline validation evidence contains invalid artifact metadata'
        }
        foreach ($name in @(
            'verify_passed', 'apply_passed', 'restore_passed', 'bad_stock_rejected',
            'mixed_state_recovered', 'running_process_refused', 'package_tamper_rejected',
            'json_duplicate_keys_rejected', 'build_duplicate_keys_rejected',
            'audit_duplicate_keys_rejected', 'untrusted_installer_not_executed',
            'installed_game_files_unchanged'
        )) {
            if ($Evidence.offline.checks.$name -ne $true) {
                throw "Offline validation evidence is missing check: $name"
            }
        }
        if (([string]$Evidence.offline.artifacts.message_target_sha256).ToUpperInvariant() -ne
                ([string]$Manifest.message.target.sha256).ToUpperInvariant() -or
            ([string]$Evidence.offline.artifacts.font_target_sha256).ToUpperInvariant() -ne
                ([string]$Manifest.font.target.sha256).ToUpperInvariant()) {
            throw 'Offline evidence target hashes do not match the manifest'
        }
    }
    elseif ($null -ne $Evidence.offline.source_sha256 -or
        $null -ne $Evidence.offline.checks -or $null -ne $Evidence.offline.artifacts) {
        throw 'Unvalidated offline evidence must contain null details'
    }
    if ($Evidence.runtime.passed -eq $true) {
        Assert-ExactProperties $Evidence.runtime.checks @(
            'boot_completed', 'korean_ui_visible', 'castle_name_horizontal',
            'missing_glyphs_checked',
            'clipping_checked', 'normal_exit', 'stock_restored_after_qa'
        ) 'runtime evidence checks'
        Assert-ExactProperties $Evidence.runtime.artifacts @(
            'message_target_sha256', 'font_target_sha256', 'validated_utc'
        ) 'runtime evidence artifacts'
        Assert-ExactProperties $Evidence.runtime.scope @(
            'observed_labels', 'untested_areas'
        ) 'runtime evidence scope'
        foreach ($name in @(
            'boot_completed', 'korean_ui_visible', 'castle_name_horizontal',
            'missing_glyphs_checked',
            'clipping_checked', 'normal_exit', 'stock_restored_after_qa'
        )) {
            if ($Evidence.runtime.checks.$name -ne $true) {
                throw "Runtime validation evidence is missing check: $name"
            }
        }
        if ([string]$Evidence.runtime.source_sha256 -notmatch '\A[0-9A-F]{64}\z' -or
            ([string]$Evidence.runtime.artifacts.message_target_sha256).ToUpperInvariant() -ne
                ([string]$Manifest.message.target.sha256).ToUpperInvariant() -or
            ([string]$Evidence.runtime.artifacts.font_target_sha256).ToUpperInvariant() -ne
                ([string]$Manifest.font.target.sha256).ToUpperInvariant() -or
            @($Evidence.runtime.screens).Count -lt 1 -or @($Evidence.runtime.screens).Count -gt 20 -or
            @($Evidence.runtime.scope.observed_labels).Count -lt 1 -or
            @($Evidence.runtime.scope.observed_labels).Count -gt 64 -or
            @($Evidence.runtime.scope.untested_areas).Count -lt 1 -or
            @($Evidence.runtime.scope.untested_areas).Count -gt 16) {
            throw 'Runtime validation evidence contains invalid artifact metadata'
        }
        $seenScreens = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
        foreach ($screen in @($Evidence.runtime.screens)) {
            Assert-ExactProperties $screen @('file', 'sha256') 'runtime screenshot evidence'
            if ([string]$screen.file -notmatch '\A[A-Za-z0-9_.-]{1,128}\z' -or
                [string]$screen.sha256 -notmatch '\A[0-9A-F]{64}\z' -or
                -not $seenScreens.Add([string]$screen.file)) {
                throw 'Runtime evidence screenshot reference is invalid'
            }
        }
        foreach ($label in @($Evidence.runtime.scope.observed_labels)) {
            if ([string]::IsNullOrWhiteSpace([string]$label) -or ([string]$label).Length -gt 128) {
                throw 'Runtime evidence contains an invalid observed label'
            }
        }
        foreach ($area in @($Evidence.runtime.scope.untested_areas)) {
            if ([string]::IsNullOrWhiteSpace([string]$area) -or ([string]$area).Length -gt 128) {
                throw 'Runtime evidence contains an invalid untested-area marker'
            }
        }
    }
    elseif ($null -ne $Evidence.runtime.source_sha256 -or
        $null -ne $Evidence.runtime.checks -or $null -ne $Evidence.runtime.artifacts -or
        $null -ne $Evidence.runtime.screens -or $null -ne $Evidence.runtime.scope) {
        throw 'Pending runtime evidence must contain null details and a null screen list'
    }
}

function Convert-HexToBytes([string]$Hex) {
    if (($Hex.Length -band 1) -ne 0 -or $Hex -notmatch '\A[0-9A-Fa-f]*\z') {
        throw 'Invalid hexadecimal recipe field'
    }
    [byte[]]$bytes = New-Object byte[] ($Hex.Length / 2)
    for ($index = 0; $index -lt $bytes.Length; $index++) {
        $bytes[$index] = [Convert]::ToByte($Hex.Substring($index * 2, 2), 16)
    }
    return ,$bytes
}

function New-SiblingTemp([string]$Destination, [string]$Tag) {
    $directory = Split-Path -Parent $Destination
    $name = [System.IO.Path]::GetFileName($Destination)
    return Join-Path $directory ('.' + $name + '.n16kr.' + $Tag + '.' + [Guid]::NewGuid().ToString('N'))
}

function Remove-Temporary([string[]]$Paths) {
    foreach ($path in $Paths) {
        if ($path -and (Test-Path -LiteralPath $path -PathType Leaf)) {
            try {
                [System.IO.File]::Delete($path)
            }
            catch {
                Write-Warning "Could not remove temporary file: $path"
            }
        }
    }
}

function Write-JsonAtomic([string]$Path, $Value) {
    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        [System.IO.Directory]::CreateDirectory($directory) | Out-Null
    }
    $temporary = Join-Path $directory ('.state.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $discard = Join-Path $directory ('.state-discard.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $json = ($Value | ConvertTo-Json -Depth 12) + "`n"
    [byte[]]$encoded = [System.Text.Encoding]::UTF8.GetBytes($json)
    try {
        [N16KrFileOnly.FileRecipeCore]::WriteDurable($temporary, $encoded)
        if (Test-Path -LiteralPath $Path -PathType Leaf) {
            [System.IO.File]::Replace($temporary, $Path, $discard, $true)
        }
        else {
            [System.IO.File]::Move($temporary, $Path)
        }
    }
    finally {
        Remove-Temporary @($temporary, $discard)
    }
}

function Resolve-GameRoot([string]$Requested) {
    if ($Requested) {
        $candidate = Get-NormalizedPath $Requested
        if (-not (Test-Path -LiteralPath $candidate -PathType Container)) {
            throw "Game root does not exist: $candidate"
        }
        return $candidate
    }
    $candidates = @($PackageRoot, (Split-Path -Parent $PackageRoot))
    foreach ($candidate in $candidates) {
        $message = Join-Path $candidate 'MSG_PK\SC\msgui.bin'
        $font = Join-Path $candidate 'RES_SC\res_lang.bin'
        if ((Test-Path -LiteralPath $message -PathType Leaf) -and
            (Test-Path -LiteralPath $font -PathType Leaf)) {
            return (Get-NormalizedPath $candidate)
        }
    }
    throw 'Game root was not found. Place this release folder directly inside the game folder or pass -GameRoot.'
}

function Assert-GameStopped {
    $names = @('NOBU16', 'NOBU16PK', 'NOBU16PK_EN', 'NOBU16_Launcher')
    $running = @(Get-Process -Name $names -ErrorAction SilentlyContinue)
    if ($running.Count -gt 0) {
        $found = ($running | Select-Object -ExpandProperty ProcessName -Unique) -join ', '
        throw "Close the game and official launcher before continuing: $found"
    }
}

function Assert-OrdinaryPath([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Label is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "$Label must not be a symbolic link, junction, or other reparse point: $Path"
    }
}

function Assert-NoCommercialFullResource([string]$Path, [string]$Relative) {
    $item = Get-Item -LiteralPath $Path
    $forbiddenSizes = @(
        [int64]60829, [int64]87274,
        [int64]160318119, [int64]180350761,
        [int64]25817936, [int64]26628080,
        [int64]11771536, [int64]12136240
    )
    $forbiddenHashes = @(
        'C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82',
        '5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984',
        '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99',
        '3BC57379D9AF95E83A77C96C1EE2D104AAF4A8BEA1733EA33FC3D1BCF056D1A9',
        '414A8E98DCF0F52633CD039A74E97AE61A97D98A96684D450EBADD4C3C85CAEB',
        '951906C6870F60F9342E9A90DF8DBF920D555092D3E06B1B822A41448740DD61',
        'DADBE4EEA223FD48CEFA9A93A08EF1F2458B3BD543ADFCEBD6D888B9EE2AFBB0',
        'C96704BF3A7FE1B29E3CB29361D1E56FCA8062CA73210CBCFCD73BE2E7C7CC66'
    )
    if ($forbiddenSizes -contains [int64]$item.Length) {
        throw "Package contains a file with a forbidden complete-resource size: $Relative"
    }
    $hash = Get-Sha256 $Path
    if ($forbiddenHashes -contains $hash) {
        throw "Package contains a known complete commercial resource: $Relative"
    }
    if ($item.Length -ge 8) {
        [byte[]]$header = New-Object byte[] 8
        $stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        try {
            [void]$stream.Read($header, 0, 8)
        }
        finally {
            $stream.Dispose()
        }
        $prefix8 = ([BitConverter]::ToString($header)).Replace('-', '')
        if ($prefix8 -eq '0101C4C1FA7F0000' -or
            [Text.Encoding]::ASCII.GetString($header, 0, 4) -eq 'LINK') {
            throw "Package contains a complete-resource file signature: $Relative"
        }
    }
}

function Test-Package {
    Assert-OrdinaryPath $PackageRoot 'package root'
    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw "Release manifest is missing: $ManifestPath"
    }
    Assert-OrdinaryPath $ManifestPath 'release manifest'
    if ([int64](Get-Item -LiteralPath $ManifestPath).Length -gt 65536) {
        throw 'Release manifest exceeds the strict size limit'
    }
    $manifest = Read-Json $ManifestPath
    Assert-JsonStringLimits $manifest 'release manifest'
    Assert-ExactProperties $manifest @(
        'schema', 'release_id', 'release_name', 'version', 'architecture',
        'development_milestone', 'release_eligible', 'runtime_validation',
        'install_restore_tested', 'process_memory_access', 'executable_modified',
        'registry_modified', 'registry_write', 'launches_game', 'resident_component',
        'commercial_full_files_included', 'requires_process_running', 'payload_format',
        'python_required_by_end_user', 'official_launcher_language', 'target_files',
        'backup_directory_name', 'transaction_journal', 'message', 'font', 'files'
    ) 'release manifest'
    Assert-ExactProperties $manifest.message @(
        'recipe_path', 'recipe_size', 'recipe_sha256', 'recipe_shape_sha256',
        'operation_count', 'operation_ids_encoding', 'operation_ids_sha256', 'stock', 'target'
    ) 'manifest message contract'
    Assert-ExactProperties $manifest.font @(
        'recipe_path', 'recipe_size', 'recipe_sha256', 'recipe_shape_sha256',
        'raster_codepoint_count', 'raster_codepoints_encoding',
        'raster_codepoints_sha256', 'append_codepoints_encoding',
        'table0_append_count', 'table1_append_count',
        'table0_codepoints_sha256', 'table1_codepoints_sha256',
        'stock', 'target', 'payloads'
    ) 'manifest font contract'
    foreach ($spec in @($manifest.message.stock, $manifest.message.target,
        $manifest.font.stock, $manifest.font.target)) {
        Assert-ExactProperties $spec @('size', 'sha256') 'manifest resource hash contract'
    }
    foreach ($payload in @($manifest.font.payloads)) {
        Assert-ExactProperties $payload @('path', 'size', 'sha256') 'manifest payload contract'
    }
    foreach ($file in @($manifest.files)) {
        Assert-ExactProperties $file @('path', 'size', 'sha256') 'manifest file contract'
    }
    $targetFiles = @($manifest.target_files)
    $releaseGateValid = (($manifest.release_eligible -eq $true -and
            $manifest.runtime_validation -eq 'passed' -and
            $manifest.install_restore_tested -eq $true) -or
        ($manifest.release_eligible -eq $false -and
            $manifest.development_milestone -eq $true -and
            $manifest.runtime_validation -eq 'pending'))
    if ($manifest.schema -ne 'nobu16.korean-file-only-release.v2' -or
        $manifest.release_id -ne 'msgui-p4-font-v4-v0.3' -or
        $manifest.release_name -ne 'NOBU16 Korean MSGUI P4 / Font-v4 file-only v0.3' -or
        (($manifest.release_eligible -eq $true -and $manifest.version -ne '0.3') -or
            ($manifest.release_eligible -eq $false -and $manifest.version -ne '0.3-dev')) -or
        $manifest.architecture -ne 'file-only-offline' -or
        $manifest.process_memory_access -ne $false -or
        $manifest.executable_modified -ne $false -or
        $manifest.registry_modified -ne $false -or
        $manifest.launches_game -ne $false -or
        $manifest.resident_component -ne $false -or
        $manifest.commercial_full_files_included -ne $false -or
        $manifest.requires_process_running -ne $false -or
        -not $releaseGateValid -or
        $targetFiles.Count -ne 2 -or
        $targetFiles[0] -ne 'MSG_PK/SC/msgui.bin' -or
        $targetFiles[1] -ne 'RES_SC/res_lang.bin' -or
        $manifest.payload_format -ne 'recipes-and-deltas-only' -or
        $manifest.python_required_by_end_user -ne $false -or
        $manifest.official_launcher_language -ne 'Simplified Chinese' -or
        $manifest.registry_write -ne $false -or
        $manifest.transaction_journal -ne $true -or
        $manifest.message.recipe_path -ne 'components/message/msgui_sc.recipe.json' -or
        $manifest.font.recipe_path -ne 'components/font/recipe.json' -or
        $manifest.message.operation_ids_encoding -ne 'UTF-8 compact JSON integer array' -or
        $manifest.font.raster_codepoints_encoding -ne 'UTF-8 compact JSON string array' -or
        $manifest.font.append_codepoints_encoding -ne 'ASCII U+XXXX LF-delimited lines' -or
        [int]$manifest.font.raster_codepoint_count -ne 354 -or
        ([string]$manifest.font.raster_codepoints_sha256).ToUpperInvariant() -ne '7EEE2CD1CD8C111108E23707CF80E48444611EB5239AEE700EF607679560B04F' -or
        [int]$manifest.font.table0_append_count -ne 342 -or
        [int]$manifest.font.table1_append_count -ne 354 -or
        ([string]$manifest.font.table0_codepoints_sha256).ToUpperInvariant() -ne '5254670AE29E925240BCC980155B78CFE2698094833B0D69B084715857B9D94D' -or
        ([string]$manifest.font.table1_codepoints_sha256).ToUpperInvariant() -ne '700D935F92E05FFD806A8AD267EE7A9A2F46C393E945890AECBEED887CEC5BB7' -or
        @($manifest.font.payloads).Count -ne 2 -or
        @($manifest.files).Count -ne 16 -or
        [int64]$manifest.message.recipe_size -ne 153571 -or
        ([string]$manifest.message.recipe_sha256).ToUpperInvariant() -ne 'E6CC464E01F9D86A8AC995FD47FBE1EF6AD51DCD67C05117A7BF8ECC573460D2' -or
        [int64]$manifest.font.recipe_size -ne 311007 -or
        ([string]$manifest.font.recipe_sha256).ToUpperInvariant() -ne 'EC4B9C68A1FF62DD06F53C55A30F45A3F12F62D1D1C7654196C780021288EA07' -or
        $manifest.backup_directory_name -ne 'msgui_p4_font_v4_v0_3' -or
        [int]$manifest.message.operation_count -ne 931 -or
        ([string]$manifest.message.operation_ids_sha256).ToUpperInvariant() -ne '7F95C3EDB26F6C53990B35C5C2C4C3552B4789E1F8BA4D140A77948C9B57E187') {
        throw 'Release manifest contract is invalid'
    }
    $expectedPaths = @(
        'APPLY_KOREAN_PATCH.bat',
        'components\font\licenses\OFL-NotoSansKR.txt',
        'components\font\licenses\OFL-NotoSerifKR.txt',
        'components\font\metrics\glyphs.jsonl',
        'components\font\payload\glyph_pixels_entry_6.bin',
        'components\font\payload\glyph_pixels_entry_7.bin',
        'components\font\recipe.json',
        'components\message\msgui_sc.recipe.json',
        'FILE_ONLY_POLICY_KO.md',
        'README_KO.md',
        'RESTORE_ORIGINALS.bat',
        'tools\FileRecipeCore.cs',
        'tools\Invoke-FileOnlyPatch.ps1',
        'tools\JsonKeyGuard.cs',
        'VALIDATION_EVIDENCE.json',
        'VERIFY_PACKAGE.bat'
    )
    $allowed = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($relative in $expectedPaths) {
        [void]$allowed.Add($relative)
    }
    $maximumSizes = @{
        'APPLY_KOREAN_PATCH.bat' = 1024
        'components\font\licenses\OFL-NotoSansKR.txt' = 8192
        'components\font\licenses\OFL-NotoSerifKR.txt' = 8192
        'components\font\metrics\glyphs.jsonl' = 443134
        'components\font\payload\glyph_pixels_entry_6.bin' = 801792
        'components\font\payload\glyph_pixels_entry_7.bin' = 356352
        'components\font\recipe.json' = 311007
        'components\message\msgui_sc.recipe.json' = 153571
        'FILE_ONLY_POLICY_KO.md' = 32768
        'README_KO.md' = 32768
        'RESTORE_ORIGINALS.bat' = 1024
        'tools\FileRecipeCore.cs' = 65536
        'tools\Invoke-FileOnlyPatch.ps1' = 131072
        'tools\JsonKeyGuard.cs' = 16384
        'VALIDATION_EVIDENCE.json' = 32768
        'VERIFY_PACKAGE.bat' = 1024
    }
    $listed = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($file in @($manifest.files)) {
        $relative = ([string]$file.path).Replace('/', [System.IO.Path]::DirectorySeparatorChar)
        $full = Get-NormalizedPath (Join-Path $PackageRoot $relative)
        $prefix = $PackageRoot.TrimEnd('\') + '\'
        if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Manifest path escapes the package: $relative"
        }
        if (-not $listed.Add($relative)) {
            throw "Manifest contains a duplicate path: $relative"
        }
        if (-not $allowed.Contains($relative)) {
            throw "Manifest contains a path outside the strict public allowlist: $relative"
        }
        if ([int64]$file.size -gt [int64]$maximumSizes[$relative]) {
            throw "Manifest file exceeds its strict path-specific size limit: $relative"
        }
        Assert-OrdinaryPath $full "package file $relative"
        Assert-FileSpec $full $file "package file $relative"
        Assert-NoCommercialFullResource $full $relative
    }
    if ($listed.Count -ne $allowed.Count) {
        throw 'Manifest does not contain the complete strict public allowlist'
    }
    foreach ($relative in $expectedPaths) {
        if (-not $listed.Contains($relative)) {
            throw "Manifest omits a required public file: $relative"
        }
    }
    $packageItems = @(Get-ChildItem -LiteralPath $PackageRoot -Recurse -Force)
    foreach ($item in $packageItems) {
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Package contains a reparse point: $($item.FullName)"
        }
    }
    $actual = @($packageItems | Where-Object { -not $_.PSIsContainer } | Where-Object {
        $_.FullName -ne $ManifestPath
    })
    foreach ($file in $actual) {
        $relative = $file.FullName.Substring($PackageRoot.TrimEnd('\').Length + 1)
        if (-not $listed.Contains($relative)) {
            throw "Package contains an unlisted file: $relative"
        }
    }
    if ($actual.Count -ne $listed.Count) {
        throw 'Package inventory count does not match the release manifest'
    }
    $legacyReleaseId = [string]::Concat('msgui-', 'p', '3-font-', 'v', '3-v0', '.2')
    $legacyReleaseName = [string]::Concat('NOBU16 Korean MSGUI ', 'P', '3 / Font-', 'v', '3 file-only v0', '.2')
    $legacyBackupName = [string]::Concat('msgui_', 'p', '3_font_', 'v', '3_v0', '_2')
    $strictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    foreach ($file in $actual) {
        if ([IO.Path]::GetExtension($file.Name) -in @('.ps1', '.cs', '.md', '.bat', '.json', '.jsonl')) {
            $text = $strictUtf8.GetString([IO.File]::ReadAllBytes($file.FullName))
            if ($text.Contains($legacyReleaseId) -or $text.Contains($legacyReleaseName) -or
                $text.Contains($legacyBackupName)) {
                throw "Package contains a legacy release identity: $($file.FullName)"
            }
        }
    }
    return $manifest
}

function Ensure-Backup([string]$Source, [string]$Backup, [int64]$ExpectedSize, [string]$ExpectedHash) {
    if (Test-Path -LiteralPath $Backup -PathType Leaf) {
        Assert-OrdinaryPath $Backup 'existing stock backup'
        $item = Get-Item -LiteralPath $Backup
        $actual = Get-Sha256 $Backup
        if ([int64]$item.Length -ne $ExpectedSize -or $actual -ne $ExpectedHash) {
            throw "Existing backup has an unexpected hash: $Backup"
        }
        return
    }
    $temporary = $Backup + '.' + [Guid]::NewGuid().ToString('N') + '.tmp'
    try {
        [N16KrFileOnly.FileRecipeCore]::CopyDurable($Source, $temporary)
        $item = Get-Item -LiteralPath $temporary
        if ([int64]$item.Length -ne $ExpectedSize -or (Get-Sha256 $temporary) -ne $ExpectedHash) {
            throw "New backup verification failed: $Backup"
        }
        [System.IO.File]::Move($temporary, $Backup)
    }
    finally {
        Remove-Temporary @($temporary)
    }
}

function Get-InstalledPairStatus {
    if (-not (Test-Path -LiteralPath $MessagePath -PathType Leaf) -or
        -not (Test-Path -LiteralPath $FontPath -PathType Leaf)) {
        return 'missing'
    }
    $messageHash = Get-Sha256 $MessagePath
    $fontHash = Get-Sha256 $FontPath
    if ($messageHash -eq $stockMessageHash -and $fontHash -eq $stockFontHash) {
        return 'stock'
    }
    if ($messageHash -eq $targetMessageHash -and $fontHash -eq $targetFontHash) {
        return 'target'
    }
    if (($messageHash -eq $stockMessageHash -or $messageHash -eq $targetMessageHash) -and
        ($fontHash -eq $stockFontHash -or $fontHash -eq $targetFontHash)) {
        return 'mixed'
    }
    return 'unknown'
}

function Assert-InstalledPairHashes([string]$ExpectedMessage, [string]$ExpectedFont, [string]$Label) {
    $actualMessage = Get-Sha256 $MessagePath
    $actualFont = Get-Sha256 $FontPath
    if ($actualMessage -ne $ExpectedMessage -or $actualFont -ne $ExpectedFont) {
        throw "$Label hash gate failed; installed files changed during the operation."
    }
}

function Assert-StockBackups {
    if (-not (Test-Path -LiteralPath $MessageBackup -PathType Leaf) -or
        -not (Test-Path -LiteralPath $FontBackup -PathType Leaf)) {
        throw 'Verified stock backups are required for transaction recovery.'
    }
    Assert-OrdinaryPath $MessageBackup 'message stock backup'
    Assert-OrdinaryPath $FontBackup 'font stock backup'
    if ([int64](Get-Item -LiteralPath $MessageBackup).Length -ne $stockMessageSize -or
        [int64](Get-Item -LiteralPath $FontBackup).Length -ne $stockFontSize -or
        (Get-Sha256 $MessageBackup) -ne $stockMessageHash -or
        (Get-Sha256 $FontBackup) -ne $stockFontHash) {
        throw 'Stock backup hash verification failed.'
    }
}

function Force-StockPair {
    Assert-StockBackups
    $pairs = @(
        [pscustomobject]@{ Current = $MessagePath; Backup = $MessageBackup; Stock = $stockMessageHash; Target = $targetMessageHash },
        [pscustomobject]@{ Current = $FontPath; Backup = $FontBackup; Stock = $stockFontHash; Target = $targetFontHash }
    )
    $failures = New-Object 'System.Collections.Generic.List[string]'
    foreach ($pair in $pairs) {
        $temporary = $null
        $discard = $null
        try {
            $currentHash = Get-Sha256 $pair.Current
            if ($currentHash -eq $pair.Stock) {
                continue
            }
            if ($currentHash -ne $pair.Target) {
                throw "Cannot recover an unrecognized installed file: $($pair.Current)"
            }
            $temporary = New-SiblingTemp $pair.Current 'stock-recovery'
            $discard = New-SiblingTemp $pair.Current 'discard'
            [N16KrFileOnly.FileRecipeCore]::CopyDurable($pair.Backup, $temporary)
            if ((Get-Sha256 $temporary) -ne $pair.Stock) {
                throw "Recovery staging hash failed: $($pair.Current)"
            }
            Assert-GameStopped
            $preReplaceHash = Get-Sha256 $pair.Current
            if ($preReplaceHash -eq $pair.Stock) {
                continue
            }
            if ($preReplaceHash -ne $pair.Target) {
                throw "Recovery hash gate failed before replacement: $($pair.Current)"
            }
            [System.IO.File]::Replace($temporary, $pair.Current, $discard, $true)
            if ((Get-Sha256 $pair.Current) -ne $pair.Stock) {
                throw "Recovery replacement hash failed: $($pair.Current)"
            }
        }
        catch {
            $failures.Add($_.Exception.Message)
        }
        finally {
            Remove-Temporary @($temporary, $discard)
        }
    }
    if ($failures.Count -gt 0) {
        throw ('Stock-pair recovery failures: ' + ($failures -join ' | '))
    }
    if ((Get-InstalledPairStatus) -ne 'stock') {
        throw 'Stock-pair recovery did not reach a consistent state.'
    }
}

function Recover-InterruptedTransaction {
    $pairStatus = Get-InstalledPairStatus
    if ($pairStatus -eq 'missing' -or $pairStatus -eq 'unknown') {
        throw "Installed target pair has an unsafe status: $pairStatus"
    }
    if ($pairStatus -eq 'mixed') {
        if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) {
            throw 'A mixed target pair was found without a transaction journal.'
        }
        $state = Read-Json $StatePath
        try {
            Force-StockPair
        }
        catch {
            $recoveryError = $_.Exception.Message
            try {
                Set-StateField $state 'status' 'recovery_failed'
                Set-StateField $state 'error' $recoveryError
                Write-JsonAtomic $StatePath $state
            }
            catch {
                throw "Stock recovery failed ($recoveryError); journal update also failed: $($_.Exception.Message)"
            }
            throw "Stock recovery failed: $recoveryError"
        }
        try {
            Set-StateField $state 'status' 'recovered_stock'
            Set-StateField $state 'recovered_utc' ([DateTime]::UtcNow.ToString('o'))
            Write-JsonAtomic $StatePath $state
        }
        catch {
            throw "Both files were recovered to stock, but the transaction journal could not be updated: $($_.Exception.Message)"
        }
        return 'stock'
    }
    if (Test-Path -LiteralPath $StatePath -PathType Leaf) {
        $state = Read-Json $StatePath
        if ($pairStatus -eq 'target') {
            Assert-StockBackups
            if ($state.status -ne 'applied') {
                Set-StateField $state 'status' 'applied'
                Set-StateField $state 'inferred_utc' ([DateTime]::UtcNow.ToString('o'))
                Write-JsonAtomic $StatePath $state
            }
        }
        elseif ($pairStatus -eq 'stock' -and
            $state.status -notin @('restored', 'recovered_stock', 'inferred_stock')) {
            Set-StateField $state 'status' 'recovered_stock'
            Set-StateField $state 'inferred_utc' ([DateTime]::UtcNow.ToString('o'))
            Write-JsonAtomic $StatePath $state
        }
    }
    return $pairStatus
}

function Build-Message([string]$StockPath, [string]$RecipePath) {
    $recipe = Read-Json $RecipePath
    $stock = [System.IO.File]::ReadAllBytes($StockPath)
    Assert-Bytes $stock $recipe.source 'stock SC message resource'
    $operations = @($recipe.operations)
    [int[]]$ids = @($operations | ForEach-Object { [int]$_.id })
    [string[]]$sourceHashes = @($operations | ForEach-Object { [string]$_.source_utf16le_sha256 })
    [string[]]$replacements = @($operations | ForEach-Object { [string]$_.replacement })
    [byte[]]$target = [N16KrFileOnly.FileRecipeCore]::ApplyMessageRecipe(
        $stock, [int]$recipe.source.string_count, $ids, $sourceHashes, $replacements)
    Assert-Bytes $target $recipe.target 'rebuilt SC message resource'
    return ,$target
}

function Build-FontEntry([byte[]]$StockArchive, $EntryRecipe, [string]$ComponentRoot) {
    $entry = [int]$EntryRecipe.entry
    [byte[]]$stockRaw = [N16KrFileOnly.FileRecipeCore]::ExtractLinkEntryRaw($StockArchive, $entry)
    Assert-Bytes $stockRaw $EntryRecipe.stock "stock SC font entry $entry"

    $payloadRelative = ([string]$EntryRecipe.pixel_payload.file).Replace('/', '\')
    $payloadPath = Get-NormalizedPath (Join-Path $ComponentRoot $payloadRelative)
    $componentPrefix = (Get-NormalizedPath $ComponentRoot).TrimEnd('\') + '\'
    if (-not $payloadPath.StartsWith($componentPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Font entry $entry payload path escapes the package"
    }
    Assert-OrdinaryPath $payloadPath "font pixel payload entry $entry"
    [byte[]]$pixels = [System.IO.File]::ReadAllBytes($payloadPath)
    Assert-Bytes $pixels $EntryRecipe.pixel_payload "font pixel payload entry $entry"

    $tables = @($EntryRecipe.tables)
    if ($tables.Count -ne 2) {
        throw "Font entry $entry recipe does not contain two tables"
    }
    [int[]]$codepoints0 = @($tables[0].map_changes | ForEach-Object {
        [Convert]::ToInt32(([string]$_.codepoint).Substring(2), 16)
    })
    [int[]]$codepoints1 = @($tables[1].map_changes | ForEach-Object {
        [Convert]::ToInt32(([string]$_.codepoint).Substring(2), 16)
    })
    [int[]]$ordinals0 = @($tables[0].map_changes | ForEach-Object { [int]$_.new_ordinal })
    [int[]]$ordinals1 = @($tables[1].map_changes | ForEach-Object { [int]$_.new_ordinal })
    [byte[]]$appended0 = Convert-HexToBytes ([string]$tables[0].appended_records_hex)
    [byte[]]$appended1 = Convert-HexToBytes ([string]$tables[1].appended_records_hex)
    if ([N16KrFileOnly.FileRecipeCore]::Sha256($appended0) -ne ([string]$tables[0].appended_records_sha256).ToUpperInvariant() -or
        [N16KrFileOnly.FileRecipeCore]::Sha256($appended1) -ne ([string]$tables[1].appended_records_sha256).ToUpperInvariant()) {
        throw "Font entry $entry appended-record hash mismatch"
    }
    [int[]]$targetOffsets = @($EntryRecipe.target.table_offsets | ForEach-Object { [int]$_ })
    [byte[]]$targetRaw = [N16KrFileOnly.FileRecipeCore]::BuildG1n(
        $stockRaw, [int]$EntryRecipe.target.size, [int]$EntryRecipe.target.atlas_offset,
        $targetOffsets, $codepoints0, $ordinals0, $codepoints1, $ordinals1,
        $appended0, $appended1, $pixels)
    Assert-Bytes $targetRaw $EntryRecipe.target "rebuilt SC font entry $entry"
    return ,$targetRaw
}

function Build-Font([string]$StockPath, [string]$RecipePath, [string]$ComponentRoot) {
    $recipe = Read-Json $RecipePath
    $language = $recipe.languages.SC
    [byte[]]$stockArchive = [System.IO.File]::ReadAllBytes($StockPath)
    Assert-Bytes $stockArchive $language.stock_archive 'stock SC font archive'
    [byte[]]$entry6 = Build-FontEntry $stockArchive $language.entries.'6' $ComponentRoot
    [byte[]]$entry7 = Build-FontEntry $stockArchive $language.entries.'7' $ComponentRoot
    [int[]]$indices = @(6, 7)
    [byte[][]]$entries = [byte[][]]::new(2)
    $entries[0] = $entry6
    $entries[1] = $entry7
    [byte[]]$targetArchive = [N16KrFileOnly.FileRecipeCore]::ReplaceLinkRawEntries(
        $stockArchive, $indices, $entries)
    Assert-Bytes $targetArchive $language.target_archive 'rebuilt SC font archive'
    return ,$targetArchive
}

if (-not (Test-Path -LiteralPath $CorePath -PathType Leaf)) {
    throw "Recipe core source is missing: $CorePath"
}
if (-not (Test-Path -LiteralPath $JsonGuardPath -PathType Leaf)) {
    throw "JSON key guard source is missing: $JsonGuardPath"
}
Assert-OrdinaryPath $JsonGuardPath 'JSON key guard source'
if ([int64](Get-Item -LiteralPath $JsonGuardPath).Length -ne 11304 -or
    (Get-Sha256 $JsonGuardPath) -ne '6A1ABEC0899A1D4256153E49E8204DAE343EC5D7887DB3047192A8168678DA60') {
    throw 'JSON key guard source does not match the pinned verifier'
}
Add-Type -Path $JsonGuardPath
$manifest = Test-Package
Add-Type -Path $CorePath
$MessageRecipePath = Join-Path $PackageRoot 'components\message\msgui_sc.recipe.json'
$FontComponentRoot = Join-Path $PackageRoot 'components\font'
$FontRecipePath = Join-Path $FontComponentRoot 'recipe.json'
$messageRecipe = Read-Json $MessageRecipePath
$fontRecipe = Read-Json $FontRecipePath
$validationEvidence = Read-Json (Join-Path $PackageRoot 'VALIDATION_EVIDENCE.json')
Assert-RecipeContracts $manifest $messageRecipe $fontRecipe
Assert-EvidenceContract $manifest $validationEvidence
$fontLanguage = $fontRecipe.languages.SC

if ($Action -eq 'Verify') {
    Write-Host 'Package verification: OK'
    if ($manifest.release_eligible -ne $true) {
        Write-Warning 'This package is a development milestone and is not release-eligible until in-game runtime QA passes.'
    }
    Write-Host 'Use the official launcher and select Simplified Chinese before starting the game.'
    exit 0
}

if ($manifest.release_eligible -ne $true -and -not $AllowDevelopmentMilestone) {
    throw 'This development milestone is not approved for end-user installation. Runtime validation is still pending.'
}

$ResolvedGameRoot = Resolve-GameRoot $GameRoot
Assert-GameStopped

$MessagePath = Join-Path $ResolvedGameRoot 'MSG_PK\SC\msgui.bin'
$FontPath = Join-Path $ResolvedGameRoot 'RES_SC\res_lang.bin'
Assert-OrdinaryPath $ResolvedGameRoot 'game root'
Assert-OrdinaryPath (Join-Path $ResolvedGameRoot 'MSG_PK') 'message directory'
Assert-OrdinaryPath (Join-Path $ResolvedGameRoot 'MSG_PK\SC') 'SC message directory'
Assert-OrdinaryPath $MessagePath 'SC message resource'
Assert-OrdinaryPath (Join-Path $ResolvedGameRoot 'RES_SC') 'SC font directory'
Assert-OrdinaryPath $FontPath 'SC font resource'

$BackupParent = Join-Path $ResolvedGameRoot 'KR_PATCH_BACKUP'
$BackupRoot = Join-Path $BackupParent 'msgui_p4_font_v4_v0_3'
$MessageBackup = Join-Path $BackupRoot 'message_sc.stock.bak'
$FontBackup = Join-Path $BackupRoot 'font_sc.stock.bak'
$StatePath = Join-Path $BackupRoot 'install_state.json'
$OperationLockPath = Join-Path $BackupRoot 'operation.lock'

$stockMessageHash = ([string]$messageRecipe.source.sha256).ToUpperInvariant()
$targetMessageHash = ([string]$messageRecipe.target.sha256).ToUpperInvariant()
$stockFontHash = ([string]$fontLanguage.stock_archive.sha256).ToUpperInvariant()
$targetFontHash = ([string]$fontLanguage.target_archive.sha256).ToUpperInvariant()
$stockMessageSize = [int64]$messageRecipe.source.size
$stockFontSize = [int64]$fontLanguage.stock_archive.size
if (Test-Path -LiteralPath $BackupParent) {
    Assert-OrdinaryPath $BackupParent 'patch backup directory'
}
[System.IO.Directory]::CreateDirectory($BackupRoot) | Out-Null
Assert-OrdinaryPath $BackupParent 'patch backup directory'
Assert-OrdinaryPath $BackupRoot 'patch transaction directory'
foreach ($existingStateFile in @($MessageBackup, $FontBackup, $StatePath, $OperationLockPath)) {
    if (Test-Path -LiteralPath $existingStateFile) {
        Assert-OrdinaryPath $existingStateFile 'patch transaction file'
    }
}
try {
    $OperationLock = [System.IO.File]::Open(
        $OperationLockPath, [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
}
catch {
    throw 'Another patch operation is already using this game folder.'
}

try {
$pairStatus = Recover-InterruptedTransaction

if ($Action -eq 'Apply') {
    $currentMessageHash = Get-Sha256 $MessagePath
    $currentFontHash = Get-Sha256 $FontPath
    if ($currentMessageHash -eq $targetMessageHash -and $currentFontHash -eq $targetFontHash) {
        if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) {
            throw 'Target files are already present, but no local backup state exists; refusing an unsafe no-op.'
        }
        Write-Host 'The file-only patch is already applied.'
        exit 0
    }
    if ($currentMessageHash -ne $stockMessageHash -or $currentFontHash -ne $stockFontHash) {
        throw 'Installed files do not match the supported stock hashes. Restore or verify the game first.'
    }

    Write-Host 'Rebuilding the Korean msgui resource from the compact recipe...'
    [byte[]]$messageTarget = Build-Message $MessagePath $MessageRecipePath
    Write-Host 'Rebuilding the Korean font resource...'
    [byte[]]$fontTarget = Build-Font $FontPath $FontRecipePath $FontComponentRoot

    [System.IO.Directory]::CreateDirectory($BackupRoot) | Out-Null
    Ensure-Backup $MessagePath $MessageBackup $stockMessageSize $stockMessageHash
    Ensure-Backup $FontPath $FontBackup $stockFontSize $stockFontHash

    $state = [ordered]@{
        schema = 'nobu16.file-only-install-state.v1'
        release_id = 'msgui-p4-font-v4-v0.3'
        release_manifest_sha256 = Get-Sha256 $ManifestPath
        status = 'apply_ready'
        game_root = $ResolvedGameRoot
        stock_message_sha256 = $stockMessageHash
        target_message_sha256 = $targetMessageHash
        stock_font_sha256 = $stockFontHash
        target_font_sha256 = $targetFontHash
        prepared_utc = [DateTime]::UtcNow.ToString('o')
    }
    Write-JsonAtomic $StatePath $state

    $messageTemporary = New-SiblingTemp $MessagePath 'candidate'
    $fontTemporary = New-SiblingTemp $FontPath 'candidate'
    $messageRollback = New-SiblingTemp $MessagePath 'rollback'
    $fontRollback = New-SiblingTemp $FontPath 'rollback'
    $messageReplaced = $false
    $fontReplaced = $false
    try {
        [N16KrFileOnly.FileRecipeCore]::WriteDurable($messageTemporary, $messageTarget)
        [N16KrFileOnly.FileRecipeCore]::WriteDurable($fontTemporary, $fontTarget)
        if ((Get-Sha256 $messageTemporary) -ne $targetMessageHash -or
            (Get-Sha256 $fontTemporary) -ne $targetFontHash) {
            throw 'Staged output hash verification failed'
        }
        $messageTarget = $null
        $fontTarget = $null
        [GC]::Collect()

        Assert-GameStopped
        Assert-InstalledPairHashes $stockMessageHash $stockFontHash 'Apply message replacement'
        [System.IO.File]::Replace($messageTemporary, $MessagePath, $messageRollback, $true)
        $messageReplaced = $true
        Set-StateField $state 'status' 'apply_message_replaced'
        Write-JsonAtomic $StatePath $state
        Assert-GameStopped
        Assert-InstalledPairHashes $targetMessageHash $stockFontHash 'Apply font replacement'
        [System.IO.File]::Replace($fontTemporary, $FontPath, $fontRollback, $true)
        $fontReplaced = $true
        Set-StateField $state 'status' 'apply_both_replaced'
        Write-JsonAtomic $StatePath $state
        if ((Get-Sha256 $MessagePath) -ne $targetMessageHash -or
            (Get-Sha256 $FontPath) -ne $targetFontHash) {
            throw 'Installed output hash verification failed'
        }
        Set-StateField $state 'status' 'applied'
        Set-StateField $state 'applied_utc' ([DateTime]::UtcNow.ToString('o'))
        Write-JsonAtomic $StatePath $state
        Remove-Temporary @($messageRollback, $fontRollback)
        Write-Host 'File-only patch application: OK'
        Write-Host 'Use the official launcher and select Simplified Chinese before starting the game.'
    }
    catch {
        $originalError = $_.Exception.Message
        $journalErrors = New-Object 'System.Collections.Generic.List[string]'
        try {
            Set-StateField $state 'status' 'apply_error_recovering'
            Set-StateField $state 'error' $originalError
            Write-JsonAtomic $StatePath $state
        }
        catch {
            $journalErrors.Add('initial error journal: ' + $_.Exception.Message)
        }
        $recoveryError = $null
        try {
            Force-StockPair
        }
        catch {
            $recoveryError = $_.Exception.Message
        }
        if ($null -ne $recoveryError) {
            try {
                Set-StateField $state 'status' 'recovery_failed'
                Set-StateField $state 'recovery_error' $recoveryError
                Write-JsonAtomic $StatePath $state
            }
            catch {
                $journalErrors.Add('recovery-failure journal: ' + $_.Exception.Message)
            }
            $journalSuffix = if ($journalErrors.Count) {
                '; journal errors: ' + ($journalErrors -join ' | ')
            }
            else { '' }
            throw "Apply failed ($originalError); stock recovery also failed: $recoveryError$journalSuffix"
        }
        try {
            Set-StateField $state 'status' 'rolled_back_stock'
            Set-StateField $state 'recovered_utc' ([DateTime]::UtcNow.ToString('o'))
            Write-JsonAtomic $StatePath $state
        }
        catch {
            $journalErrors.Add('recovered-state journal: ' + $_.Exception.Message)
        }
        $journalSuffix = if ($journalErrors.Count) {
            '; journal errors: ' + ($journalErrors -join ' | ')
        }
        else { '' }
        throw "Apply failed and both files were restored to stock: $originalError$journalSuffix"
    }
    finally {
        Remove-Temporary @($messageTemporary, $fontTemporary, $messageRollback, $fontRollback)
    }
    exit 0
}

if (-not (Test-Path -LiteralPath $MessageBackup -PathType Leaf) -or
    -not (Test-Path -LiteralPath $FontBackup -PathType Leaf)) {
    throw 'Original backups are missing; restoration was not attempted.'
}
if ([int64](Get-Item -LiteralPath $MessageBackup).Length -ne $stockMessageSize -or
    [int64](Get-Item -LiteralPath $FontBackup).Length -ne $stockFontSize -or
    (Get-Sha256 $MessageBackup) -ne $stockMessageHash -or
    (Get-Sha256 $FontBackup) -ne $stockFontHash) {
    throw 'Original backup hash verification failed; restoration was not attempted.'
}
$currentMessageHash = Get-Sha256 $MessagePath
$currentFontHash = Get-Sha256 $FontPath
if ($currentMessageHash -eq $stockMessageHash -and $currentFontHash -eq $stockFontHash) {
    Write-Host 'Original files are already restored.'
    exit 0
}
if ($currentMessageHash -ne $targetMessageHash -or $currentFontHash -ne $targetFontHash) {
    throw 'Installed files are neither the supported target pair nor the stock pair; restoration was not attempted.'
}

$messageTemporary = New-SiblingTemp $MessagePath 'restore'
$fontTemporary = New-SiblingTemp $FontPath 'restore'
$messageRollback = New-SiblingTemp $MessagePath 'rollback'
$fontRollback = New-SiblingTemp $FontPath 'rollback'
$messageReplaced = $false
$fontReplaced = $false
$state = [ordered]@{
    schema = 'nobu16.file-only-install-state.v1'
    status = 'restore_initializing'
}
try {
    if (Test-Path -LiteralPath $StatePath -PathType Leaf) {
        $state = Read-Json $StatePath
    }
    Set-StateField $state 'status' 'restore_ready'
    Set-StateField $state 'restore_prepared_utc' ([DateTime]::UtcNow.ToString('o'))
    Write-JsonAtomic $StatePath $state
    [N16KrFileOnly.FileRecipeCore]::CopyDurable($MessageBackup, $messageTemporary)
    [N16KrFileOnly.FileRecipeCore]::CopyDurable($FontBackup, $fontTemporary)
    if ((Get-Sha256 $messageTemporary) -ne $stockMessageHash -or
        (Get-Sha256 $fontTemporary) -ne $stockFontHash) {
        throw 'Restore staging hash verification failed'
    }
    Assert-GameStopped
    Assert-InstalledPairHashes $targetMessageHash $targetFontHash 'Restore message replacement'
    [System.IO.File]::Replace($messageTemporary, $MessagePath, $messageRollback, $true)
    $messageReplaced = $true
    Set-StateField $state 'status' 'restore_message_replaced'
    Write-JsonAtomic $StatePath $state
    Assert-GameStopped
    Assert-InstalledPairHashes $stockMessageHash $targetFontHash 'Restore font replacement'
    [System.IO.File]::Replace($fontTemporary, $FontPath, $fontRollback, $true)
    $fontReplaced = $true
    Set-StateField $state 'status' 'restore_both_replaced'
    Write-JsonAtomic $StatePath $state
    if ((Get-Sha256 $MessagePath) -ne $stockMessageHash -or
        (Get-Sha256 $FontPath) -ne $stockFontHash) {
        throw 'Restored file hash verification failed'
    }
    Set-StateField $state 'status' 'restored'
    Set-StateField $state 'restored_utc' ([DateTime]::UtcNow.ToString('o'))
    Write-JsonAtomic $StatePath $state
    Remove-Temporary @($messageRollback, $fontRollback)
    Write-Host 'Original file restoration: OK'
}
catch {
    $originalError = $_.Exception.Message
    $journalErrors = New-Object 'System.Collections.Generic.List[string]'
    try {
        Set-StateField $state 'status' 'restore_error_recovering'
        Set-StateField $state 'error' $originalError
        Write-JsonAtomic $StatePath $state
    }
    catch {
        $journalErrors.Add('initial error journal: ' + $_.Exception.Message)
    }
    $recoveryError = $null
    try {
        Force-StockPair
    }
    catch {
        $recoveryError = $_.Exception.Message
    }
    if ($null -ne $recoveryError) {
        try {
            Set-StateField $state 'status' 'recovery_failed'
            Set-StateField $state 'recovery_error' $recoveryError
            Write-JsonAtomic $StatePath $state
        }
        catch {
            $journalErrors.Add('recovery-failure journal: ' + $_.Exception.Message)
        }
        $journalSuffix = if ($journalErrors.Count) {
            '; journal errors: ' + ($journalErrors -join ' | ')
        }
        else { '' }
        throw "Restore failed ($originalError); stock recovery also failed: $recoveryError$journalSuffix"
    }
    try {
        Set-StateField $state 'status' 'rolled_back_stock'
        Set-StateField $state 'recovered_utc' ([DateTime]::UtcNow.ToString('o'))
        Write-JsonAtomic $StatePath $state
    }
    catch {
        $journalErrors.Add('recovered-state journal: ' + $_.Exception.Message)
    }
    $journalSuffix = if ($journalErrors.Count) {
        '; journal errors: ' + ($journalErrors -join ' | ')
    }
    else { '' }
    throw "Restore encountered an error, but both files are now stock: $originalError$journalSuffix"
}
finally {
    Remove-Temporary @($messageTemporary, $fontTemporary, $messageRollback, $fontRollback)
}
}
finally {
    $OperationLock.Dispose()
}
