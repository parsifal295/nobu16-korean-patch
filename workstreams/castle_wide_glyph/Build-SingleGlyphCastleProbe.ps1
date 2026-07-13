param(
    [string]$Python = 'python',
    [string]$WorkspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ProbeRoot = $PSScriptRoot
$RasterRoot = Join-Path $ProbeRoot 'raster'
$CandidateRoot = Join-Path $ProbeRoot 'private\candidate'
$PrivateInputRoot = Join-Path $ProbeRoot 'private\input'
$Tool = Join-Path $WorkspaceRoot 'KR_PATCH_WORK\tools\nobu16_lz4.py'
$StockMessageWrapper = Join-Path $WorkspaceRoot 'MSG_PK\SC\msgdata.bin'
$StockFontArchive = Join-Path $WorkspaceRoot 'RES_SC\res_lang.bin'
$StockMessage = Join-Path $PrivateInputRoot 'msgdata.raw'
$FontBases = @{
    6 = Join-Path $PrivateInputRoot 'SC_6.stock.g1n'
    7 = Join-Path $PrivateInputRoot 'SC_7.stock.g1n'
}
$PinnedHashes = @{
    message_wrapper = '0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E'
    font_archive = '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99'
    message = '1290BCDF6B00C6E4516061888C618BC66A246375E271C9D1330A9D168037FBCF'
    font6 = '414A8E98DCF0F52633CD039A74E97AE61A97D98A96684D450EBADD4C3C85CAEB'
    font7 = 'DADBE4EEA223FD48CEFA9A93A08EF1F2458B3BD543ADFCEBD6D888B9EE2AFBB0'
}

$CastleFirstId = 9151
$CastleLastId = 9542
$ProbeMessageId = 9168
$CastleSuffixId = 9936
$ProxyCodepoint = 0xD792 # 18th member of the frozen descending, collision-filtered 392-codepoint pool.
$CompositeCodepoints = @(0xC624, 0xB2E4, 0xC640, 0xB77C, 0xC131)
$CompositeText = -join @($CompositeCodepoints | ForEach-Object { [char]$_ })
$ReservationPath = Join-Path $ProbeRoot 'metadata\proxy_reservation_9151_9542.json'

function Get-Sha256([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return (($sha.ComputeHash($Bytes) | ForEach-Object { $_.ToString('X2') }) -join '')
    } finally {
        $sha.Dispose()
    }
}

function Get-FileSha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Assert-Hash([string]$Path, [string]$Expected, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing ${Label}: $Path" }
    $actual = Get-FileSha256 $Path
    if ($actual -ne $Expected) { throw "${Label} hash mismatch: expected=$Expected actual=$actual" }
}

function Invoke-Tool([string[]]$Arguments) {
    & $Python $Tool @Arguments
    if ($LASTEXITCODE -ne 0) { throw "nobu16_lz4.py failed with exit code $LASTEXITCODE" }
}

function Get-RegionSha256([byte[]]$Bytes, [int]$Offset, [int]$Length) {
    $stream = [IO.MemoryStream]::new($Bytes, $Offset, $Length, $false, $true)
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return (($sha.ComputeHash($stream) | ForEach-Object { $_.ToString('X2') }) -join '')
    } finally {
        $sha.Dispose()
        $stream.Dispose()
    }
}

function Read-U16([byte[]]$Bytes, [int]$Offset) {
    return [BitConverter]::ToUInt16($Bytes, $Offset)
}

function Read-U32([byte[]]$Bytes, [int]$Offset) {
    return [BitConverter]::ToUInt32($Bytes, $Offset)
}

function Write-U16([byte[]]$Bytes, [int]$Offset, [int]$Value) {
    [Buffer]::BlockCopy([BitConverter]::GetBytes([uint16]$Value), 0, $Bytes, $Offset, 2)
}

function Write-U32([byte[]]$Bytes, [int]$Offset, [long]$Value) {
    if ($Value -lt 0 -or $Value -gt [uint32]::MaxValue) { throw "u32 overflow: $Value" }
    [Buffer]::BlockCopy([BitConverter]::GetBytes([uint32]$Value), 0, $Bytes, $Offset, 4)
}

function Join-CellGlyphs(
    [byte[]]$Payload,
    [int]$ProfileOffset,
    [int]$Cell,
    [int[]]$RasterCodepoints,
    [int[]]$DesiredCodepoints
) {
    if (($Cell % 2) -ne 0) { throw "Odd 4bpp cell is unsupported: $Cell" }
    $cellStride = [int]($Cell / 2)
    $cellBytes = $cellStride * $Cell
    $outputStride = $cellStride * $DesiredCodepoints.Count
    if ($outputStride -gt 128) { throw "Composite signed row stride exceeds 128: $outputStride" }
    $output = [byte[]]::new($outputStride * $Cell)
    for ($characterIndex = 0; $characterIndex -lt $DesiredCodepoints.Count; $characterIndex++) {
        $cp = $DesiredCodepoints[$characterIndex]
        $rasterIndex = [Array]::IndexOf($RasterCodepoints, $cp)
        if ($rasterIndex -lt 0) { throw ('Raster payload lacks U+{0:X4}' -f $cp) }
        $glyphStart = $ProfileOffset + $rasterIndex * $cellBytes
        for ($row = 0; $row -lt $Cell; $row++) {
            $source = $glyphStart + $row * $cellStride
            $target = $row * $outputStride + $characterIndex * $cellStride
            [Buffer]::BlockCopy($Payload, $source, $output, $target, $cellStride)
        }
    }
    if (-not ($output | Where-Object { $_ -ne 0 } | Select-Object -First 1)) {
        throw 'Composite raster is blank'
    }
    return ,$output
}

function New-WideRecord([int]$Width, [int]$Height, [int]$Advance, [int]$Stride, [long]$Pointer) {
    if ($Width -lt 1 -or $Width -gt 255) { throw "Width outside u8: $Width" }
    if ($Height -lt 1 -or $Height -gt 255) { throw "Height outside u8: $Height" }
    if ($Advance -lt 1 -or $Advance -gt 255) { throw "Advance outside u8: $Advance" }
    if ($Stride -lt -128 -or $Stride -gt -1) { throw "Negative signed stride outside int8: $Stride" }
    if ([Math]::Abs($Stride) -lt [Math]::Ceiling($Width / 2.0)) { throw 'Stride cannot contain width at 4bpp' }
    $record = [byte[]]::new(12)
    $record[0] = [byte]$Width
    $record[1] = [byte]$Height
    $record[2] = 0
    $record[3] = [byte]$Height
    $record[4] = [byte]$Advance
    $record[5] = [byte](256 + $Stride)
    $record[6] = 0
    $record[7] = [byte]$Height
    Write-U32 $record 8 $Pointer
    return ,$record
}

function Build-G1NWideCandidate(
    [string]$SourcePath,
    [string]$OutputPath,
    [int]$Entry,
    [byte[][]]$TablePixels,
    [int]$Cell
) {
    $stock = [IO.File]::ReadAllBytes($SourcePath)
    if ([Text.Encoding]::ASCII.GetString($stock, 0, 8) -ne '_N1G0000') { throw "Bad G1N signature: $SourcePath" }
    if ((Read-U32 $stock 0x08) -ne $stock.Length) { throw "G1N declared size mismatch: $SourcePath" }
    if ((Read-U32 $stock 0x1C) -ne 2) { throw "Expected two G1N tables: $SourcePath" }

    $table0 = Read-U32 $stock 0x20
    $table1 = Read-U32 $stock 0x24
    $atlas = Read-U32 $stock 0x14
    $headerSize = Read-U32 $stock 0x0C
    if ($table0 -ne $headerSize) { throw 'Table 0 does not start at header end' }
    $count0 = [int](($table1 - $table0 - 0x20000) / 12)
    $count1 = [int](($atlas - $table1 - 0x20000) / 12)
    if ($count0 -ge 0xFFFF -or $count1 -ge 0xFFFF) { throw '16-bit ordinal capacity exhausted' }
    foreach ($tableOffset in @($table0, $table1)) {
        if ((Read-U16 $stock ($tableOffset + 2 * $ProxyCodepoint)) -ne 0) {
            throw ('Proxy U+{0:X4} already mapped in {1}' -f $ProxyCodepoint, $SourcePath)
        }
    }

    $stockAtlasLength = $stock.Length - $atlas
    $targetTable0 = $table0
    $targetTable1 = $table1 + 12
    $targetAtlas = $atlas + 24
    $targetLength = $stock.Length + 24 + $TablePixels[0].Length + $TablePixels[1].Length
    $targetAtlasLength = $stockAtlasLength + $TablePixels[0].Length + $TablePixels[1].Length
    if ($targetAtlasLength -ge 0x10000000) { throw '28-bit raw-font atlas capacity exceeded' }
    $output = [byte[]]::new($targetLength)

    [Buffer]::BlockCopy($stock, 0, $output, 0, $headerSize)
    Write-U32 $output 0x08 $targetLength
    Write-U32 $output 0x14 $targetAtlas
    Write-U32 $output 0x20 $targetTable0
    Write-U32 $output 0x24 $targetTable1

    # Table 0: exact stock map except one zero -> appended ordinal, exact old records, one record.
    [Buffer]::BlockCopy($stock, $table0, $output, $targetTable0, 0x20000)
    Write-U16 $output ($targetTable0 + 2 * $ProxyCodepoint) $count0
    $oldRecords0 = $table1 - ($table0 + 0x20000)
    [Buffer]::BlockCopy($stock, $table0 + 0x20000, $output, $targetTable0 + 0x20000, $oldRecords0)
    $record0 = New-WideRecord ($Cell * $CompositeCodepoints.Count) $Cell ($Cell * $CompositeCodepoints.Count) (-($Cell * $CompositeCodepoints.Count / 2)) $stockAtlasLength
    [Buffer]::BlockCopy($record0, 0, $output, $targetTable0 + 0x20000 + $oldRecords0, 12)

    # Table 1 follows the inserted table-0 record.
    [Buffer]::BlockCopy($stock, $table1, $output, $targetTable1, 0x20000)
    Write-U16 $output ($targetTable1 + 2 * $ProxyCodepoint) $count1
    $oldRecords1 = $atlas - ($table1 + 0x20000)
    [Buffer]::BlockCopy($stock, $table1 + 0x20000, $output, $targetTable1 + 0x20000, $oldRecords1)
    $record1 = New-WideRecord ($Cell * $CompositeCodepoints.Count) $Cell ($Cell * $CompositeCodepoints.Count) (-($Cell * $CompositeCodepoints.Count / 2)) ($stockAtlasLength + $TablePixels[0].Length)
    [Buffer]::BlockCopy($record1, 0, $output, $targetTable1 + 0x20000 + $oldRecords1, 12)

    # The complete commercial stock atlas is preserved byte-exactly as a prefix.
    [Buffer]::BlockCopy($stock, $atlas, $output, $targetAtlas, $stockAtlasLength)
    [Buffer]::BlockCopy($TablePixels[0], 0, $output, $targetAtlas + $stockAtlasLength, $TablePixels[0].Length)
    [Buffer]::BlockCopy($TablePixels[1], 0, $output, $targetAtlas + $stockAtlasLength + $TablePixels[0].Length, $TablePixels[1].Length)

    # Independent local preservation checks before writing.
    if ((Get-RegionSha256 $output $targetAtlas $stockAtlasLength) -ne (Get-RegionSha256 $stock $atlas $stockAtlasLength)) {
        throw "Stock atlas prefix changed for entry $Entry"
    }
    if ((Read-U16 $output ($targetTable0 + 2 * $ProxyCodepoint)) -ne $count0 -or
        (Read-U16 $output ($targetTable1 + 2 * $ProxyCodepoint)) -ne $count1) {
        throw "Proxy map verification failed for entry $Entry"
    }
    [IO.File]::WriteAllBytes($OutputPath, $output)
    return [ordered]@{
        entry = $Entry
        source = $SourcePath
        source_sha256 = Get-Sha256 $stock
        target = $OutputPath
        target_sha256 = Get-Sha256 $output
        source_size = $stock.Length
        target_size = $output.Length
        source_atlas_length = $stockAtlasLength
        target_atlas_length = $targetAtlasLength
        table_0_old_records = $count0
        table_1_old_records = $count1
        appended_records_per_table = 1
        composite_width = $Cell * $CompositeCodepoints.Count
        composite_height = $Cell
        signed_stride = -($Cell * $CompositeCodepoints.Count / 2)
        advance = $Cell * $CompositeCodepoints.Count
        pixels_per_table = $TablePixels[0].Length
        old_maps_except_proxy_exact = $true
        old_records_exact = $true
        stock_atlas_exact_prefix = $true
    }
}

function Parse-MessageTable([byte[]]$Blob) {
    if ((Read-U32 $Blob 0) -ne 1) { throw 'Message table block count is not one' }
    $blockOffset = Read-U32 $Blob 4
    $logicalSize = Read-U32 $Blob 8
    $logicalEnd = $blockOffset + $logicalSize
    if ($logicalEnd -gt $Blob.Length) { throw 'Message logical end exceeds file' }
    for ($i = $logicalEnd; $i -lt $Blob.Length; $i++) { if ($Blob[$i] -ne 0) { throw 'Nonzero message alignment padding' } }
    $tableOffset = $blockOffset + (Read-U32 $Blob ($blockOffset + 0x0C))
    $firstOffset = Read-U32 $Blob $tableOffset
    if (($firstOffset % 4) -ne 0) { throw 'Message first offset is not divisible by four' }
    $count = [int]($firstOffset / 4)
    $offsets = [int[]]::new($count)
    $texts = [string[]]::new($count)
    for ($id = 0; $id -lt $count; $id++) { $offsets[$id] = Read-U32 $Blob ($tableOffset + 4 * $id) }
    for ($id = 0; $id -lt $count; $id++) {
        $start = $tableOffset + $offsets[$id]
        $next = if ($id + 1 -lt $count) { $tableOffset + $offsets[$id + 1] } else { $logicalEnd }
        if ($next -lt $start + 2 -or $Blob[$next - 2] -ne 0 -or $Blob[$next - 1] -ne 0) { throw "Bad UTF-16 terminator at message id $id" }
        $texts[$id] = [Text.Encoding]::Unicode.GetString($Blob, $start, $next - $start - 2)
    }
    return [pscustomobject]@{
        Blob = $Blob
        BlockOffset = $blockOffset
        LogicalEnd = $logicalEnd
        TableOffset = $tableOffset
        FirstOffset = $firstOffset
        StringStart = $tableOffset + $firstOffset
        Texts = $texts
    }
}

function Rebuild-MessageTable([object]$Table, [string[]]$Texts) {
    if ($Texts.Count -ne $Table.Texts.Count) { throw 'Message replacement count mismatch' }
    $prefix = [byte[]]::new($Table.StringStart)
    [Buffer]::BlockCopy($Table.Blob, 0, $prefix, 0, $prefix.Length)
    $pool = New-Object IO.MemoryStream
    try {
        $relative = $Table.FirstOffset
        for ($id = 0; $id -lt $Texts.Count; $id++) {
            Write-U32 $prefix ($Table.TableOffset + 4 * $id) $relative
            $encoded = [Text.Encoding]::Unicode.GetBytes($Texts[$id])
            $pool.Write($encoded, 0, $encoded.Length)
            $pool.WriteByte(0)
            $pool.WriteByte(0)
            $relative += $encoded.Length + 2
        }
        $poolBytes = $pool.ToArray()
    } finally {
        $pool.Dispose()
    }
    $unpaddedLength = $prefix.Length + $poolBytes.Length
    $padding = (4 - ($unpaddedLength % 4)) % 4
    $output = [byte[]]::new($unpaddedLength + $padding)
    [Buffer]::BlockCopy($prefix, 0, $output, 0, $prefix.Length)
    [Buffer]::BlockCopy($poolBytes, 0, $output, $prefix.Length, $poolBytes.Length)
    Write-U32 $output 8 ($unpaddedLength - $Table.BlockOffset)
    return ,$output
}

Assert-Hash $StockMessageWrapper $PinnedHashes.message_wrapper 'stock message wrapper'
Assert-Hash $StockFontArchive $PinnedHashes.font_archive 'stock font archive'
[IO.Directory]::CreateDirectory($PrivateInputRoot) | Out-Null
Invoke-Tool -Arguments @('decompress', $StockMessageWrapper, $StockMessage)
Invoke-Tool -Arguments @('extract-entry', $StockFontArchive, '6', $FontBases[6], '--decompress')
Invoke-Tool -Arguments @('extract-entry', $StockFontArchive, '7', $FontBases[7], '--decompress')
Assert-Hash $StockMessage $PinnedHashes.message 'stock decompressed msgdata'
Assert-Hash $FontBases[6] $PinnedHashes.font6 'stock SC entry 6'
Assert-Hash $FontBases[7] $PinnedHashes.font7 'stock SC entry 7'
[IO.Directory]::CreateDirectory($CandidateRoot) | Out-Null

$rasterResultPath = Join-Path $RasterRoot 'raster_result.json'
if (-not (Test-Path -LiteralPath $rasterResultPath -PathType Leaf)) { throw "Run rasterize_font_v4.ps1 first: $rasterResultPath" }
$raster = Get-Content -Raw -Encoding UTF8 -LiteralPath $rasterResultPath | ConvertFrom-Json
$rasterCodepoints = @($raster.codepoints | ForEach-Object { [Convert]::ToInt32(([string]$_).Substring(2), 16) })
$fontResults = [Collections.Generic.List[object]]::new()
foreach ($entry in @(6, 7)) {
    $payloadPath = Join-Path $RasterRoot "glyph_pixels_entry_${entry}.bin"
    $payload = [IO.File]::ReadAllBytes($payloadPath)
    $profiles = @($raster.profiles | Where-Object { [int]$_.entry -eq $entry } | Sort-Object { [int]$_.table })
    if ($profiles.Count -ne 2) { throw "Entry $entry raster profile count is not two" }
    $tablePixels = [byte[][]]::new(2)
    $profileOffset = 0
    for ($table = 0; $table -lt 2; $table++) {
        $profile = $profiles[$table]
        $cell = [int]$profile.cell
        $cellBytes = [int]($cell * $cell / 2)
        $tablePixels[$table] = Join-CellGlyphs $payload $profileOffset $cell $rasterCodepoints $CompositeCodepoints
        $profileOffset += $rasterCodepoints.Count * $cellBytes
    }
    if ($profileOffset -ne $payload.Length) { throw "Entry $entry raster payload accounting mismatch" }
    $target = Join-Path $CandidateRoot "SC_${entry}.probe-9168-wide.g1n"
    $fontResults.Add((Build-G1NWideCandidate $FontBases[$entry] $target $entry $tablePixels ([int]$profiles[0].cell)))
}

$stockMessageBytes = [IO.File]::ReadAllBytes($StockMessage)
$parsedMessage = Parse-MessageTable $stockMessageBytes
$unchanged = Rebuild-MessageTable $parsedMessage $parsedMessage.Texts
if ($unchanged.Length -ne $stockMessageBytes.Length -or (Get-Sha256 $unchanged) -ne (Get-Sha256 $stockMessageBytes)) { throw 'Unchanged message parse/rebuild was not byte-identical' }
$stockSuffixText = $parsedMessage.Texts[$CastleSuffixId]

$nameOnlyTexts = [string[]]$parsedMessage.Texts.Clone()
$nameOnlyTexts[$ProbeMessageId] = [string][char]$ProxyCodepoint
$nameOnlyMessage = Rebuild-MessageTable $parsedMessage $nameOnlyTexts
$nameOnlyPath = Join-Path $CandidateRoot 'msgdata.probe-9168-wide.name-only.raw'
[IO.File]::WriteAllBytes($nameOnlyPath, $nameOnlyMessage)
$nameOnlyCheck = Parse-MessageTable $nameOnlyMessage
if ($nameOnlyCheck.Texts[$ProbeMessageId] -ne [string][char]$ProxyCodepoint -or $nameOnlyCheck.Texts[$CastleSuffixId] -ne $stockSuffixText) {
    throw 'Name-only message roundtrip verification failed'
}

# This optional probe suppresses the globally shared Castle suffix.  It is intentionally
# not a final-patch design: every other name using id 9936 loses its suffix.
$fullLabelTexts = [string[]]$nameOnlyTexts.Clone()
$fullLabelTexts[$CastleSuffixId] = ''
$fullLabelMessage = Rebuild-MessageTable $parsedMessage $fullLabelTexts
$fullLabelPath = Join-Path $CandidateRoot 'msgdata.probe-9168-wide.global-castle-suffix-blank.raw'
[IO.File]::WriteAllBytes($fullLabelPath, $fullLabelMessage)
$fullLabelCheck = Parse-MessageTable $fullLabelMessage
if ($fullLabelCheck.Texts[$ProbeMessageId] -ne [string][char]$ProxyCodepoint -or $fullLabelCheck.Texts[$CastleSuffixId] -ne '') {
    throw 'Full-label message roundtrip verification failed'
}

$reservation = Get-Content -Raw -Encoding UTF8 -LiteralPath $ReservationPath | ConvertFrom-Json
$assignments = @($reservation.assignments)
if ($assignments.Count -ne ($CastleLastId - $CastleFirstId + 1)) { throw 'Proxy reservation count mismatch' }
$reservedCodepoints = [Collections.Generic.HashSet[int]]::new()
for ($index = 0; $index -lt $assignments.Count; $index++) {
    $assignment = $assignments[$index]
    if ([int]$assignment.id -ne ($CastleFirstId + $index)) { throw "Proxy reservation id mismatch at index $index" }
    $cp = [Convert]::ToInt32(([string]$assignment.proxy).Substring(2), 16)
    if (-not $reservedCodepoints.Add($cp)) { throw ('Duplicate reserved proxy U+{0:X4}' -f $cp) }
}
if ([Convert]::ToInt32(([string]$assignments[$ProbeMessageId - $CastleFirstId].proxy).Substring(2), 16) -ne $ProxyCodepoint) {
    throw 'Frozen reservation no longer maps probe id 9168 to U+D792'
}
$translationUsed = [Collections.Generic.HashSet[int]]::new()
Get-ChildItem -File (Join-Path $WorkspaceRoot 'KR_PATCH_WORK\data\translations') | ForEach-Object {
    $text = [IO.File]::ReadAllText($_.FullName, [Text.Encoding]::UTF8)
    foreach ($character in $text.ToCharArray()) {
        $cp = [int]$character
        if ($cp -ge 0xAC00 -and $cp -le 0xD7A3) { [void]$translationUsed.Add($cp) }
    }
}
$collisions = @($reservedCodepoints | Where-Object { $translationUsed.Contains($_) })
if ($collisions.Count -ne 0) {
    throw ('Reserved proxies now collide with translation text: {0}' -f (($collisions | ForEach-Object { 'U+{0:X4}' -f $_ }) -join ', '))
}

$summary = [ordered]@{
    schema = 'nobu16.kr.single-wide-glyph-castle-probe.v0'
    status = 'offline-structural-candidate-only'
    runtime_verified = $false
    installed_game_files_modified = $false
    process_memory_access = $false
    executable_modified = $false
    registry_access = $false
    source_range = [ordered]@{
        first_id = $CastleFirstId
        last_id = $CastleLastId
        count = $CastleLastId - $CastleFirstId + 1
        unique_text_count = [int]$reservation.unique_source_text_count
        parallel_sc_pinyin_first_id = 9543
        parallel_sc_pinyin_last_id = 9934
        suffix_ids = @(9936, 9937, 9938, 9939, 9940)
        suffix_pinyin_ids = @(9942, 9943, 9944, 9945, 9946)
    }
    probe = [ordered]@{
        message_id = $ProbeMessageId
        proxy = ('U+{0:X4}' -f $ProxyCodepoint)
        proxy_character = [string][char]$ProxyCodepoint
        raster_text = $CompositeText
        castle_suffix_id = $CastleSuffixId
        suffix_is_globally_shared = $true
    }
    message_candidates = @(
        [ordered]@{
            path = $nameOnlyPath
            sha256 = Get-Sha256 $nameOnlyMessage
            size = $nameOnlyMessage.Length
            changes = @('id 9168: source name -> one proxy character')
            expected_visual_caveat = 'the separately appended shared Castle suffix remains and may still be vertical'
        },
        [ordered]@{
            path = $fullLabelPath
            sha256 = Get-Sha256 $fullLabelMessage
            size = $fullLabelMessage.Length
            changes = @('id 9168: source name -> one proxy character', 'id 9936: Castle suffix -> empty')
            expected_visual_caveat = 'global diagnostic only: all other names using Castle suffix lose it'
        }
    )
    fonts = $fontResults
    proxy_reservation = [ordered]@{
        path = $ReservationPath
        sha256 = Get-FileSha256 $ReservationPath
        count = $assignments.Count
        current_collision_count = $collisions.Count
    }
    structural_checks = [ordered]@{
        unchanged_message_roundtrip_byte_exact = $true
        candidate_message_parse_roundtrip = $true
        source_font_hashes_pinned = $true
        proxy_was_unmapped_in_all_four_stock_maps = $true
        only_proxy_map_cell_added_per_table = $true
        one_record_appended_per_table = $true
        all_stock_records_preserved = $true
        complete_stock_atlas_preserved_as_exact_prefix = $true
        atlas_below_28_bit_limit = $true
        width_stride_capacity_valid = $true
    }
    unresolved_runtime_questions = @(
        'whether the vertical label renderer draws a 240/160-pixel glyph quad without clipping or rotation',
        'which of entries 6/7 and tables 0/1 the strategic map actually selects',
        'whether the global suffix is drawn separately in the same label path',
        'how the proxy-rendered bitmap scales in non-map UI contexts that reuse the canonical castle-name id'
    )
}
$summaryPath = Join-Path $ProbeRoot 'private\candidate_summary.json'
[IO.File]::WriteAllText($summaryPath, ($summary | ConvertTo-Json -Depth 12), (New-Object Text.UTF8Encoding($false)))

Write-Output "summary=$summaryPath"
Write-Output "summary_sha256=$(Get-FileSha256 $summaryPath)"
Write-Output "reservation=$ReservationPath"
Write-Output "reservation_sha256=$(Get-FileSha256 $ReservationPath)"
foreach ($font in $fontResults) { Write-Output "font_entry_$($font.entry)=$($font.target_sha256)" }
Write-Output "message_name_only=$(Get-Sha256 $nameOnlyMessage)"
Write-Output "message_suffix_blank=$(Get-Sha256 $fullLabelMessage)"
Write-Output 'offline_candidate=OK'
