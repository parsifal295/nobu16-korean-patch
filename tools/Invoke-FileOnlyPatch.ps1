[CmdletBinding()]
param(
    [ValidateSet('Apply', 'Restore', 'Verify')]
    [string]$Action = 'Apply',
    [string]$GameRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PackageRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $PackageRoot 'release_manifest.json'
$CorePath = Join-Path $PSScriptRoot 'FileRecipeCore.cs'

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
    return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json)
}

function Set-StateField($State, [string]$Name, $Value) {
    if ($State -is [System.Collections.IDictionary]) {
        $State[$Name] = $Value
    }
    else {
        $State | Add-Member -NotePropertyName $Name -NotePropertyValue $Value -Force
    }
}

function Assert-RecipeContracts($MessageRecipe, $FontRecipe) {
    if ($MessageRecipe.schema -ne 'nobu16.file-only-msg-recipe.v1' -or
        $MessageRecipe.scope -ne 'main_menu' -or
        $MessageRecipe.version -ne '0.1' -or
        $MessageRecipe.language -ne 'SC' -or
        $MessageRecipe.file_only -ne $true -or
        $MessageRecipe.source.relative_path -ne 'MSG_PK/SC/msgui.bin') {
        throw 'Message recipe contract is invalid'
    }
    $expectedMessageIds = @(85, 1, 2, 178, 87, 97, 56, 88, 5)
    $expectedMessageBase64 = @(
        '7J207Ja07ZWY6riw', '7IOIIOqyjOyehA==', '67aI65+s7Jik6riw',
        '66y07J6lIO2OuOynkQ==', '7LaU6rCAIOy9mO2FkOy4oA==', '6rCk65+s66as',
        '7ISk7KCV', '65287J207ISg7Iqk', '6rKM7J6EIOyiheujjA=='
    )
    $expectedMessages = @($expectedMessageBase64 | ForEach-Object {
        [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_))
    })
    $operations = @($MessageRecipe.operations)
    if ($operations.Count -ne $expectedMessageIds.Count) {
        throw 'Message recipe operation count is invalid'
    }
    for ($index = 0; $index -lt $operations.Count; $index++) {
        if ([int]$operations[$index].id -ne $expectedMessageIds[$index] -or
            [string]$operations[$index].replacement -ne $expectedMessages[$index]) {
            throw "Message recipe operation $index is not approved for this release"
        }
    }

    $allowedCodepoints = @(
        'U+AC00', 'U+AC24', 'U+AC8C', 'U+AE30', 'U+B77C', 'U+B7EC', 'U+B8CC',
        'U+B9AC', 'U+BB34', 'U+BD88', 'U+C0C8', 'U+C120', 'U+C124', 'U+C2A4',
        'U+C5B4', 'U+C624', 'U+C774', 'U+C784', 'U+C7A5', 'U+C815', 'U+C885',
        'U+C9D1', 'U+CD94', 'U+CE20', 'U+CF58', 'U+D150', 'U+D3B8', 'U+D558'
    )
    $recipeCodepoints = @($FontRecipe.codepoints)
    if ($FontRecipe.schema -ne 'nobu16.file-only-g1n-tail-recipe.v1' -or
        $FontRecipe.release_eligible -ne $true -or
        $FontRecipe.runtime_direct_lookup_verified -ne $true -or
        $FontRecipe.file_only -ne $true -or
        @($FontRecipe.runtime_patch_features).Count -ne 0 -or
        $recipeCodepoints.Count -ne $allowedCodepoints.Count -or
        $FontRecipe.languages.SC.stock_archive.relative_path -ne 'RES_SC/res_lang.bin') {
        throw 'Font recipe contract is invalid'
    }
    for ($index = 0; $index -lt $allowedCodepoints.Count; $index++) {
        if ([string]$recipeCodepoints[$index] -ne $allowedCodepoints[$index]) {
            throw "Font recipe codepoint $index is not approved for this release"
        }
    }
    $entryNames = @($FontRecipe.languages.SC.entries.PSObject.Properties.Name)
    if ($entryNames.Count -ne 2 -or $entryNames -notcontains '6' -or $entryNames -notcontains '7') {
        throw 'Font recipe must contain exactly SC entries 6 and 7'
    }
    foreach ($entryNumber in @(6, 7)) {
        $entry = $FontRecipe.languages.SC.entries.([string]$entryNumber)
        $tables = @($entry.tables)
        $expectedPayload = "payload/glyph_pixels_entry_$entryNumber.bin"
        if ([int]$entry.entry -ne $entryNumber -or $tables.Count -ne 2 -or
            [string]$entry.pixel_payload.file -ne $expectedPayload -or
            [int]$entry.target.size -ne
                ([int]$entry.stock.size + 672 + [int]$entry.pixel_payload.size) -or
            [int]$entry.target.atlas_offset -ne ([int]$entry.stock.atlas_offset + 672)) {
            throw "Font entry $entryNumber structure is not approved"
        }
        for ($tableIndex = 0; $tableIndex -lt 2; $tableIndex++) {
            $table = $tables[$tableIndex]
            $changes = @($table.map_changes)
            if ([int]$table.table -ne $tableIndex -or
                [int]$table.target_record_count -ne ([int]$table.source_record_count + 28) -or
                $changes.Count -ne 28 -or
                ([string]$table.appended_records_hex).Length -ne 672) {
                throw "Font entry $entryNumber table $tableIndex structure is not approved"
            }
            for ($index = 0; $index -lt $changes.Count; $index++) {
                if ([string]$changes[$index].codepoint -ne $allowedCodepoints[$index] -or
                    [int]$changes[$index].expected_old_ordinal -ne 0 -or
                    [int]$changes[$index].new_ordinal -ne
                        ([int]$table.source_record_count + $index)) {
                    throw "Font entry $entryNumber table $tableIndex map change $index is not approved"
                }
            }
        }
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

function Test-Package {
    Assert-OrdinaryPath $PackageRoot 'package root'
    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw "Release manifest is missing: $ManifestPath"
    }
    Assert-OrdinaryPath $ManifestPath 'release manifest'
    $manifest = Read-Json $ManifestPath
    $targetFiles = @($manifest.target_files)
    if ($manifest.architecture -ne 'file-only-offline' -or
        $manifest.process_memory_access -ne $false -or
        $manifest.executable_modified -ne $false -or
        $manifest.registry_modified -ne $false -or
        $manifest.launches_game -ne $false -or
        $manifest.resident_component -ne $false -or
        $manifest.commercial_full_files_included -ne $false -or
        $manifest.requires_process_running -ne $false -or
        $manifest.runtime_validation -ne 'passed' -or
        $manifest.install_restore_tested -ne $true -or
        $manifest.release_eligible -ne $true -or
        $targetFiles.Count -ne 2 -or
        $targetFiles[0] -ne 'MSG_PK/SC/msgui.bin' -or
        $targetFiles[1] -ne 'RES_SC/res_lang.bin' -or
        $manifest.payload_format -ne 'recipes-and-deltas-only' -or
        $manifest.python_required_by_end_user -ne $false -or
        $manifest.registry_write -ne $false) {
        throw 'Release manifest contract is invalid'
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
        Assert-OrdinaryPath $full "package file $relative"
        Assert-FileSpec $full $file "package file $relative"
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
    return $manifest
}

function Ensure-Backup([string]$Source, [string]$Backup, [string]$ExpectedHash) {
    if (Test-Path -LiteralPath $Backup -PathType Leaf) {
        Assert-OrdinaryPath $Backup 'existing stock backup'
        $actual = Get-Sha256 $Backup
        if ($actual -ne $ExpectedHash) {
            throw "Existing backup has an unexpected hash: $Backup"
        }
        return
    }
    $temporary = $Backup + '.' + [Guid]::NewGuid().ToString('N') + '.tmp'
    try {
        [N16KrFileOnly.FileRecipeCore]::CopyDurable($Source, $temporary)
        if ((Get-Sha256 $temporary) -ne $ExpectedHash) {
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
    if ((Get-Sha256 $MessageBackup) -ne $stockMessageHash -or
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
    [int[]]$codepoints = @($tables[0].map_changes | ForEach-Object {
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
        $targetOffsets, $codepoints, $ordinals0, $ordinals1,
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
$manifest = Test-Package
Add-Type -Path $CorePath
$MessageRecipePath = Join-Path $PackageRoot 'components\message\main_menu_sc.recipe.json'
$FontComponentRoot = Join-Path $PackageRoot 'components\font'
$FontRecipePath = Join-Path $FontComponentRoot 'recipe.json'
$messageRecipe = Read-Json $MessageRecipePath
$fontRecipe = Read-Json $FontRecipePath
Assert-RecipeContracts $messageRecipe $fontRecipe
$fontLanguage = $fontRecipe.languages.SC

if ($Action -eq 'Verify') {
    Write-Host 'Package verification: OK'
    Write-Host 'Use the official launcher and select Simplified Chinese before starting the game.'
    exit 0
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
$BackupRoot = Join-Path $BackupParent 'mainmenu_file_only_v0_1'
$MessageBackup = Join-Path $BackupRoot 'message_sc.stock.bak'
$FontBackup = Join-Path $BackupRoot 'font_sc.stock.bak'
$StatePath = Join-Path $BackupRoot 'install_state.json'
$OperationLockPath = Join-Path $BackupRoot 'operation.lock'

$stockMessageHash = ([string]$messageRecipe.source.sha256).ToUpperInvariant()
$targetMessageHash = ([string]$messageRecipe.target.sha256).ToUpperInvariant()
$stockFontHash = ([string]$fontLanguage.stock_archive.sha256).ToUpperInvariant()
$targetFontHash = ([string]$fontLanguage.target_archive.sha256).ToUpperInvariant()
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

    Write-Host 'Rebuilding the Korean main-menu message resource...'
    [byte[]]$messageTarget = Build-Message $MessagePath $MessageRecipePath
    Write-Host 'Rebuilding the Korean font resource...'
    [byte[]]$fontTarget = Build-Font $FontPath $FontRecipePath $FontComponentRoot

    [System.IO.Directory]::CreateDirectory($BackupRoot) | Out-Null
    Ensure-Backup $MessagePath $MessageBackup $stockMessageHash
    Ensure-Backup $FontPath $FontBackup $stockFontHash

    $state = [ordered]@{
        schema = 'nobu16.file-only-install-state.v1'
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
if ((Get-Sha256 $MessageBackup) -ne $stockMessageHash -or
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
