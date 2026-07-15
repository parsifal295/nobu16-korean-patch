param(
    [Parameter(Mandatory = $true)]
    [string]$RequestPathInput,
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Get-FileSha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Get-BytesSha256([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return (($sha.ComputeHash($Bytes) | ForEach-Object { $_.ToString('X2') }) -join '')
    } finally {
        $sha.Dispose()
    }
}

function Assert-FileHash([string]$Path, [string]$Expected, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Missing ${Label}: $Path"
    }
    $actual = Get-FileSha256 $Path
    if ($actual -ne $Expected.ToUpperInvariant()) {
        throw "$Label hash mismatch. expected=$Expected actual=$actual"
    }
}

function New-RasterGlyph([int]$Codepoint, [object]$Profile) {
    $cell = [int]$Profile.cell
    $rasterSize = [single]$Profile.raster_size
    if ($cell -le 0 -or ($cell % 2) -ne 0) {
        throw "4bpp cell must be positive and even: $cell"
    }
    if ($Codepoint -lt 0 -or $Codepoint -gt 0xFFFF) {
        throw ('G1N supports BMP only: U+{0:X}' -f $Codepoint)
    }
    $fontKey = [string]$Profile.font_key
    if (-not $script:FontFamilies.ContainsKey($fontKey)) {
        throw "Unexpected profile font key: $fontKey"
    }
    $fontFamily = $script:FontFamilies[$fontKey]
    if ([string]$Profile.family -ne $fontFamily.Name) {
        throw "Unexpected profile family: $($Profile.family)"
    }
    $style = [Enum]::Parse([Drawing.FontStyle], [string]$Profile.style)
    if (-not $fontFamily.IsStyleAvailable($style)) {
        throw "Unavailable SeoulHangang style: $style"
    }

    # This deliberately reuses the established PC G1N raster geometry: 72 DPI,
    # GDI+ AntiAliasGridFit, 2x scratch canvas, full-ink extraction and a
    # centered 4bpp packed target cell.  No game asset is read or written here.
    $canvas = $cell * 2
    $font = New-Object Drawing.Font($fontFamily, $rasterSize, $style, [Drawing.GraphicsUnit]::Pixel)
    $bitmap = New-Object Drawing.Bitmap($canvas, $canvas, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $bitmap.SetResolution(72, 72)
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $format = [Drawing.StringFormat]::GenericTypographic.Clone()
    try {
        $graphics.Clear([Drawing.Color]::Black)
        $graphics.TextRenderingHint = [Drawing.Text.TextRenderingHint]::AntiAliasGridFit
        $graphics.TextContrast = 4
        $format.Alignment = [Drawing.StringAlignment]::Center
        $format.LineAlignment = [Drawing.StringAlignment]::Center
        $format.FormatFlags = $format.FormatFlags -bor [Drawing.StringFormatFlags]::NoWrap
        $graphics.DrawString(
            [string][char]$Codepoint,
            $font,
            [Drawing.Brushes]::White,
            [Drawing.RectangleF]::new(0, 0, $canvas, $canvas),
            $format
        )

        $sourceMinX = $canvas; $sourceMinY = $canvas; $sourceMaxX = -1; $sourceMaxY = -1
        for ($y = 0; $y -lt $canvas; $y++) {
            for ($x = 0; $x -lt $canvas; $x++) {
                if (($bitmap.GetPixel($x, $y).R -shr 4) -ne 0) {
                    if ($x -lt $sourceMinX) { $sourceMinX = $x }
                    if ($x -gt $sourceMaxX) { $sourceMaxX = $x }
                    if ($y -lt $sourceMinY) { $sourceMinY = $y }
                    if ($y -gt $sourceMaxY) { $sourceMaxY = $y }
                }
            }
        }
        if ($sourceMaxX -lt 0) { throw ('Blank raster for U+{0:X4}.' -f $Codepoint) }

        $sourceWidth = $sourceMaxX - $sourceMinX + 1
        $sourceHeight = $sourceMaxY - $sourceMinY + 1
        $targetWidth = $sourceWidth; $targetHeight = $sourceHeight; $scaledToMargin = $false
        if ($sourceWidth -gt ($cell - 2) -or $sourceHeight -gt ($cell - 2)) {
            # All demands—including punctuation—are made clipping-safe.  Nearest
            # neighbour is deterministic and preserves the all-ink safety proof.
            $scale = [Math]::Min(($cell - 2) / [double]$sourceWidth, ($cell - 2) / [double]$sourceHeight)
            $targetWidth = [Math]::Max(1, [int][Math]::Round($sourceWidth * $scale))
            $targetHeight = [Math]::Max(1, [int][Math]::Round($sourceHeight * $scale))
            $targetWidth = [Math]::Min($cell - 2, $targetWidth)
            $targetHeight = [Math]::Min($cell - 2, $targetHeight)
            $scaledToMargin = $true
        }
        $destX = [int][Math]::Floor(($cell - $targetWidth) / 2)
        $destY = [int][Math]::Floor(($cell - $targetHeight) / 2)

        $pixels = [byte[]]::new(($cell / 2) * $cell)
        $pixelIndex = 0; $inkCount = 0
        $minX = $cell; $minY = $cell; $maxX = -1; $maxY = -1
        for ($y = 0; $y -lt $cell; $y++) {
            for ($x = 0; $x -lt $cell; $x += 2) {
                $left = 0; $right = 0
                if ($y -ge $destY -and $y -lt ($destY + $targetHeight)) {
                    $dy = $y - $destY
                    $sampleY = $sourceMinY + $(if ($scaledToMargin) {
                        [Math]::Min($sourceHeight - 1, [int][Math]::Floor((($dy + 0.5) * $sourceHeight) / $targetHeight))
                    } else { $dy })
                    foreach ($delta in @(0, 1)) {
                        $dx = $x + $delta - $destX
                        if ($dx -ge 0 -and $dx -lt $targetWidth) {
                            $sampleX = $sourceMinX + $(if ($scaledToMargin) {
                                [Math]::Min($sourceWidth - 1, [int][Math]::Floor((($dx + 0.5) * $sourceWidth) / $targetWidth))
                            } else { $dx })
                            $value = [int]($bitmap.GetPixel($sampleX, $sampleY).R -shr 4)
                            if ($delta -eq 0) { $left = $value } else { $right = $value }
                        }
                    }
                }
                $pixels[$pixelIndex++] = [byte](($left -shl 4) -bor $right)
                if ($left -ne 0) {
                    $inkCount++
                    if ($x -lt $minX) { $minX = $x }; if ($x -gt $maxX) { $maxX = $x }
                    if ($y -lt $minY) { $minY = $y }; if ($y -gt $maxY) { $maxY = $y }
                }
                if ($right -ne 0) {
                    $inkCount++
                    $rightX = $x + 1
                    if ($rightX -lt $minX) { $minX = $rightX }; if ($rightX -gt $maxX) { $maxX = $rightX }
                    if ($y -lt $minY) { $minY = $y }; if ($y -gt $maxY) { $maxY = $y }
                }
            }
        }
        if ($pixelIndex -ne $pixels.Length -or $inkCount -eq 0) {
            throw ('4bpp packing failed for U+{0:X4}.' -f $Codepoint)
        }
        $margin = [Math]::Min([Math]::Min($minX, $minY), [Math]::Min($cell - 1 - $maxX, $cell - 1 - $maxY))
        if ($margin -lt 1) { throw ('Glyph U+{0:X4} touches the cell edge.' -f $Codepoint) }
        return [pscustomobject]@{
            pixel_data = $pixels
            metric = [ordered]@{
                codepoint = ('U+{0:X4}' -f $Codepoint)
                ink_count = $inkCount
                ink_bbox = [ordered]@{ x = $minX; y = $minY; width = $maxX - $minX + 1; height = $maxY - $minY + 1 }
                minimum_margin = $margin
                scaled_to_margin = $scaledToMargin
                pixel_size = $pixels.Length
                pixel_sha256 = Get-BytesSha256 $pixels
            }
        }
    } finally {
        $format.Dispose(); $graphics.Dispose(); $bitmap.Dispose(); $font.Dispose()
    }
}

$requestPath = (Resolve-Path -LiteralPath $RequestPathInput).Path
$requestData = Get-Content -Raw -Encoding UTF8 -LiteralPath $requestPath | ConvertFrom-Json
if ($requestData.schema -ne 'nobu16.kr.font-seoulhangang-v1-raster-request.v2') { throw 'Unsupported raster request schema.' }
$expectedFonts = [ordered]@{
    entry6_48px_eb = [ordered]@{
        entry = 6; family = 'SeoulHangang EB'; file_name = 'SeoulHangangEB.ttf'
        sha256 = '60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1'
    }
    entry7_32px_b = [ordered]@{
        entry = 7; family = 'SeoulHangang B'; file_name = 'SeoulHangangB.ttf'
        sha256 = 'C33BAB9596C0B60ADA7EA9B3456E00E1CFD8EE63C599DB2F0EF71A84BA54769B'
    }
}
$fontRows = @($requestData.fonts)
if ($fontRows.Count -ne $expectedFonts.Count) { throw 'Expected exactly two official SeoulHangang font inputs.' }
$fontPaths = @{}
foreach ($fontRow in $fontRows) {
    $fontKey = [string]$fontRow.key
    if (-not $expectedFonts.Contains($fontKey) -or $fontPaths.ContainsKey($fontKey)) {
        throw "Unexpected or duplicate SeoulHangang font key: $fontKey"
    }
    $expected = $expectedFonts[$fontKey]
    $fontPath = [string]$fontRow.path
    if ([string]$fontRow.family -ne [string]$expected.family -or
        [int]$fontRow.entry -ne [int]$expected.entry -or
        [string]$fontRow.sha256 -ne [string]$expected.sha256 -or
        [IO.Path]::GetFileName($fontPath) -ne [string]$expected.file_name) {
        throw "SeoulHangang font descriptor mismatch: $fontKey"
    }
    Assert-FileHash $fontPath ([string]$expected.sha256) "official $($expected.family) TTF"
    $fontPaths[$fontKey] = $fontPath
}
if ($fontPaths.Count -ne $expectedFonts.Count) { throw 'Incomplete SeoulHangang font descriptor set.' }

$codepoints = [Collections.Generic.List[int]]::new(); $previous = -1
foreach ($text in @($requestData.codepoints)) {
    if ([string]$text -notmatch '^U\+[0-9A-F]{4}$') { throw "Non-canonical codepoint: $text" }
    $cp = [Convert]::ToInt32(([string]$text).Substring(2), 16)
    if ($cp -le $previous) { throw 'Codepoints must be unique and strictly ascending.' }
    $codepoints.Add($cp); $previous = $cp
}
if ($codepoints.Count -eq 0) { throw 'Raster request has no codepoints.' }
$profiles = @($requestData.profiles | Sort-Object @{Expression = {[int]$_.entry}}, @{Expression = {[int]$_.table}})
if ($profiles.Count -ne 4) { throw 'Expected four PC G1N profiles.' }
foreach ($profile in $profiles) {
    $fontKey = [string]$profile.font_key
    if (-not $expectedFonts.Contains($fontKey) -or
        [int]$profile.entry -ne [int]$expectedFonts[$fontKey].entry -or
        [string]$profile.family -ne [string]$expectedFonts[$fontKey].family) {
        throw "Profile/font assignment mismatch: entry=$($profile.entry) table=$($profile.table)"
    }
}

$out = [IO.Path]::GetFullPath($OutputDirectory)
[IO.Directory]::CreateDirectory($out) | Out-Null
Add-Type -AssemblyName System.Drawing
$script:PrivateFonts = New-Object Drawing.Text.PrivateFontCollection
try {
    foreach ($fontKey in $expectedFonts.Keys) {
        $script:PrivateFonts.AddFontFile([string]$fontPaths[$fontKey])
    }
    $script:FontFamilies = @{}
    foreach ($fontKey in $expectedFonts.Keys) {
        $expectedFamily = [string]$expectedFonts[$fontKey].family
        $families = @($script:PrivateFonts.Families | Where-Object Name -eq $expectedFamily)
        if ($families.Count -ne 1) { throw "Expected one private family '$expectedFamily', found $($families.Count)." }
        $script:FontFamilies[$fontKey] = $families[0]
    }

    $payloadResults = [Collections.Generic.List[object]]::new()
    $profileResults = [Collections.Generic.List[object]]::new()
    foreach ($entry in @(6, 7)) {
        $entryProfiles = @($profiles | Where-Object { [int]$_.entry -eq $entry })
        if ($entryProfiles.Count -ne 2 -or [int]$entryProfiles[0].table -ne 0 -or [int]$entryProfiles[1].table -ne 1) {
            throw "Entry $entry does not have tables 0 and 1."
        }
        $stream = New-Object IO.MemoryStream
        try {
            foreach ($profile in $entryProfiles) {
                $glyphMetrics = [Collections.Generic.List[object]]::new()
                foreach ($cp in $codepoints) {
                    $glyph = New-RasterGlyph $cp $profile
                    $stream.Write($glyph.pixel_data, 0, $glyph.pixel_data.Length)
                    $metric = $glyph.metric
                    $metric | Add-Member -NotePropertyName entry -NotePropertyValue $entry
                    $metric | Add-Member -NotePropertyName table -NotePropertyValue ([int]$profile.table)
                    $glyphMetrics.Add($metric)
                }
                $profileResults.Add([ordered]@{
                    entry = $entry; table = [int]$profile.table; font_key = [string]$profile.font_key; family = [string]$profile.family
                    style = [string]$profile.style; raster_size = [int]$profile.raster_size; cell = [int]$profile.cell
                    glyph_count = $glyphMetrics.Count; minimum_margin = ($glyphMetrics | ForEach-Object minimum_margin | Measure-Object -Minimum).Minimum
                    glyphs = $glyphMetrics
                })
            }
            $payload = $stream.ToArray()
        } finally { $stream.Dispose() }
        $payloadPath = Join-Path $out "glyph_pixels_entry_${entry}.pixels"
        [IO.File]::WriteAllBytes($payloadPath, $payload)
        $payloadResults.Add([ordered]@{ entry = $entry; path = [IO.Path]::GetFileName($payloadPath); size = $payload.Length; sha256 = Get-BytesSha256 $payload })
    }
    $result = [ordered]@{
        schema = 'nobu16.kr.font-seoulhangang-v1-raster-result.v2'
        request_sha256 = Get-FileSha256 $requestPath
        rasterizer = 'System.Drawing GDI+ AntiAliasGridFit TextContrast=4 72DPI; 2x scratch full-ink extraction; centered 4bpp copy'
        codepoints = @($requestData.codepoints)
        payloads = $payloadResults
        profiles = $profileResults
        process_memory_access = $false
        registry_access = $false
        installed_game_files_modified = $false
    }
    [IO.File]::WriteAllText((Join-Path $out 'raster_result.json'), ($result | ConvertTo-Json -Depth 14), (New-Object Text.UTF8Encoding($false)))
    Write-Output "result=$(Join-Path $out 'raster_result.json')"
} finally {
    $script:PrivateFonts.Dispose()
}
