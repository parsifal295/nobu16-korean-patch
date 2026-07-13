param(
    [Parameter(Mandatory = $true)]
    [string]$Request,
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
        throw "Missing $Label file: $Path"
    }
    $actual = Get-FileSha256 $Path
    if ($actual -ne $Expected.ToUpperInvariant()) {
        throw "$Label hash mismatch. expected=$Expected actual=$actual"
    }
}

function Get-PrivateFamily([string]$Name) {
    $matches = @($script:PrivateFonts.Families | Where-Object Name -eq $Name)
    if ($matches.Count -ne 1) {
        throw "Expected exactly one private font family '$Name', found $($matches.Count)."
    }
    return $matches[0]
}

function New-RasterGlyph([int]$Codepoint, [object]$Profile) {
    $cell = [int]$Profile.cell
    $rasterSize = [single]$Profile.raster_size
    if ($cell -le 0 -or ($cell % 2) -ne 0) {
        throw "4bpp cell width must be a positive even integer: $cell"
    }
    if ($Codepoint -lt 0 -or $Codepoint -gt 0xFFFF) {
        throw ('G1N font-v3 supports BMP codepoints only: U+{0:X}' -f $Codepoint)
    }

    $family = Get-PrivateFamily ([string]$Profile.family)
    $style = [Enum]::Parse([Drawing.FontStyle], [string]$Profile.style)
    if (-not $family.IsStyleAvailable($style)) {
        throw "Font style is unavailable: $($Profile.family) $style"
    }

    # This intentionally reproduces the runtime-tested raster-v2 profile:
    # GDI+ AntiAliasGridFit, TextContrast=4, 72 DPI, a 2x scratch canvas,
    # complete-ink extraction, and an unscaled centered copy into the cell.
    $canvas = $cell * 2
    $font = New-Object Drawing.Font($family, $rasterSize, $style, [Drawing.GraphicsUnit]::Pixel)
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

        $sourceMinX = $canvas
        $sourceMinY = $canvas
        $sourceMaxX = -1
        $sourceMaxY = -1
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
        if ($sourceMaxX -lt 0) {
            throw ('Rasterization was blank for U+{0:X4}.' -f $Codepoint)
        }

        $sourceWidth = $sourceMaxX - $sourceMinX + 1
        $sourceHeight = $sourceMaxY - $sourceMinY + 1
        if ($sourceWidth -gt ($cell - 2) -or $sourceHeight -gt ($cell - 2)) {
            throw ('U+{0:X4} is not clipping-safe: {1}x{2} ink in {3}px cell.' -f $Codepoint, $sourceWidth, $sourceHeight, $cell)
        }
        $destX = [int][Math]::Floor(($cell - $sourceWidth) / 2)
        $destY = [int][Math]::Floor(($cell - $sourceHeight) / 2)

        $pixels = [byte[]]::new(($cell / 2) * $cell)
        $pixelIndex = 0
        $inkCount = 0
        $minX = $cell
        $minY = $cell
        $maxX = -1
        $maxY = -1
        for ($y = 0; $y -lt $cell; $y++) {
            for ($x = 0; $x -lt $cell; $x += 2) {
                $left = 0
                $right = 0
                if ($y -ge $destY -and $y -lt ($destY + $sourceHeight)) {
                    $sampleY = $sourceMinY + $y - $destY
                    if ($x -ge $destX -and $x -lt ($destX + $sourceWidth)) {
                        $left = [int]($bitmap.GetPixel($sourceMinX + $x - $destX, $sampleY).R -shr 4)
                    }
                    if (($x + 1) -ge $destX -and ($x + 1) -lt ($destX + $sourceWidth)) {
                        $right = [int]($bitmap.GetPixel($sourceMinX + $x + 1 - $destX, $sampleY).R -shr 4)
                    }
                }
                $pixels[$pixelIndex++] = [byte](($left -shl 4) -bor $right)
                if ($left -ne 0) {
                    $inkCount++
                    if ($x -lt $minX) { $minX = $x }
                    if ($x -gt $maxX) { $maxX = $x }
                    if ($y -lt $minY) { $minY = $y }
                    if ($y -gt $maxY) { $maxY = $y }
                }
                if ($right -ne 0) {
                    $inkCount++
                    if (($x + 1) -lt $minX) { $minX = $x + 1 }
                    if (($x + 1) -gt $maxX) { $maxX = $x + 1 }
                    if ($y -lt $minY) { $minY = $y }
                    if ($y -gt $maxY) { $maxY = $y }
                }
            }
        }
        if ($pixelIndex -ne $pixels.Length -or $inkCount -eq 0) {
            throw ('4bpp packing failed for U+{0:X4}.' -f $Codepoint)
        }
        $margin = [Math]::Min(
            [Math]::Min($minX, $minY),
            [Math]::Min($cell - 1 - $maxX, $cell - 1 - $maxY)
        )
        if ($margin -lt 1) {
            throw ('Centered glyph U+{0:X4} touches the {1}px cell edge.' -f $Codepoint, $cell)
        }

        return [pscustomobject]@{
            pixel_data = $pixels
            metric = [ordered]@{
                codepoint = ('U+{0:X4}' -f $Codepoint)
                character = [string][char]$Codepoint
                ink_count = $inkCount
                ink_bbox = [ordered]@{
                    x = $minX
                    y = $minY
                    width = $maxX - $minX + 1
                    height = $maxY - $minY + 1
                }
                minimum_margin = $margin
                pixel_size = $pixels.Length
                pixel_sha256 = Get-BytesSha256 $pixels
            }
        }
    } finally {
        $format.Dispose()
        $graphics.Dispose()
        $bitmap.Dispose()
        $font.Dispose()
    }
}

$requestPath = (Resolve-Path -LiteralPath $Request).Path
$requestData = Get-Content -Raw -Encoding UTF8 -LiteralPath $requestPath | ConvertFrom-Json
if ($requestData.schema -ne 'nobu16.kr.font-v3-raster-request.v1') {
    throw "Unsupported raster request schema: $($requestData.schema)"
}

$codepointStrings = @($requestData.codepoints)
if ($codepointStrings.Count -eq 0) { throw 'Raster request has no codepoints.' }
$codepoints = [Collections.Generic.List[int]]::new()
$previous = -1
foreach ($text in $codepointStrings) {
    if ([string]$text -notmatch '^U\+[0-9A-F]{4}$') { throw "Non-canonical codepoint: $text" }
    $cp = [Convert]::ToInt32(([string]$text).Substring(2), 16)
    if ($cp -le $previous) { throw 'Raster codepoints must be unique and strictly ascending.' }
    $codepoints.Add($cp)
    $previous = $cp
}

$sansPath = [string]$requestData.fonts.sans.path
$serifPath = [string]$requestData.fonts.serif.path
Assert-FileHash $sansPath ([string]$requestData.fonts.sans.sha256) 'Noto Sans KR'
Assert-FileHash $serifPath ([string]$requestData.fonts.serif.sha256) 'Noto Serif KR'

$out = [IO.Path]::GetFullPath($OutputDirectory)
[IO.Directory]::CreateDirectory($out) | Out-Null
Add-Type -AssemblyName System.Drawing
$script:PrivateFonts = New-Object Drawing.Text.PrivateFontCollection
try {
    # Keep the same single-collection/profile order used by raster-v2. The
    # separate seed regression run makes any host rasterizer drift fail closed.
    $script:PrivateFonts.AddFontFile($sansPath)
    $script:PrivateFonts.AddFontFile($serifPath)

    $profileResults = [Collections.Generic.List[object]]::new()
    $payloadResults = [Collections.Generic.List[object]]::new()
    $profiles = @($requestData.profiles | Sort-Object @{Expression = {[int]$_.entry}}, @{Expression = {[int]$_.table}})
    if ($profiles.Count -ne 4) { throw "Expected four entry/table profiles, found $($profiles.Count)." }
    foreach ($entry in @(6, 7)) {
        $entryProfiles = @($profiles | Where-Object { [int]$_.entry -eq $entry })
        if ($entryProfiles.Count -ne 2 -or [int]$entryProfiles[0].table -ne 0 -or [int]$entryProfiles[1].table -ne 1) {
            throw "Entry $entry does not have exactly table 0 and table 1 profiles."
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
                    entry = $entry
                    table = [int]$profile.table
                    family = [string]$profile.family
                    style = [string]$profile.style
                    raster_size = [int]$profile.raster_size
                    cell = [int]$profile.cell
                    glyph_count = $glyphMetrics.Count
                    minimum_margin = ($glyphMetrics | ForEach-Object minimum_margin | Measure-Object -Minimum).Minimum
                    glyphs = $glyphMetrics
                })
            }
            $payload = $stream.ToArray()
        } finally {
            $stream.Dispose()
        }
        $payloadPath = Join-Path $out "glyph_pixels_entry_${entry}.bin"
        [IO.File]::WriteAllBytes($payloadPath, $payload)
        $payloadResults.Add([ordered]@{
            entry = $entry
            path = [IO.Path]::GetFileName($payloadPath)
            size = $payload.Length
            sha256 = Get-BytesSha256 $payload
        })
    }

    $result = [ordered]@{
        schema = 'nobu16.kr.font-v3-raster-result.v1'
        request_sha256 = Get-FileSha256 $requestPath
        rasterizer = 'System.Drawing GDI+ AntiAliasGridFit TextContrast=4 72DPI; 2x scratch full-ink extraction; unscaled centered 4bpp copy'
        codepoint_count = $codepoints.Count
        codepoints = $codepointStrings
        payloads = $payloadResults
        profiles = $profileResults
        process_memory_access = $false
        registry_access = $false
        installed_game_files_modified = $false
    }
    $resultPath = Join-Path $out 'raster_result.json'
    [IO.File]::WriteAllText(
        $resultPath,
        ($result | ConvertTo-Json -Depth 14),
        (New-Object Text.UTF8Encoding($false))
    )
    Write-Output "result=$resultPath"
    foreach ($payload in $payloadResults) {
        Write-Output "entry=$($payload.entry) size=$($payload.size) sha256=$($payload.sha256)"
    }
} finally {
    $script:PrivateFonts.Dispose()
}
