param(
    [Parameter(Mandatory = $true)]
    [string]$FontPathInput,
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ExpectedFontSha256 = 'D27E1B26B55E507BEC1045962C954CF426D79605009C720FAD1C9EF808E312CB'
$ExpectedFamily = 'SeoulHangang M'
function New-UnicodeString([int[]]$Codepoints) {
    return -join @($Codepoints | ForEach-Object { [char]$_ })
}

# Keep the executable script ASCII-only so Windows PowerShell 5.1 cannot
# reinterpret UTF-8 Korean literals through the active ANSI code page.
$Labels = [ordered]@{
    38 = New-UnicodeString @(0xBD80, 0xB300, 0x20, 0xD3B8, 0xC131)
    74 = New-UnicodeString @(0xACF5, 0xC8FC, 0x20, 0xC815, 0xBCF4)
}

function Get-FileSha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Get-AlphaBounds([Drawing.Bitmap]$Bitmap) {
    $minX = $Bitmap.Width; $minY = $Bitmap.Height; $maxX = -1; $maxY = -1; $count = 0
    for ($y = 0; $y -lt $Bitmap.Height; $y++) {
        for ($x = 0; $x -lt $Bitmap.Width; $x++) {
            if ($Bitmap.GetPixel($x, $y).A -ne 0) {
                $count++
                if ($x -lt $minX) { $minX = $x }
                if ($x -gt $maxX) { $maxX = $x }
                if ($y -lt $minY) { $minY = $y }
                if ($y -gt $maxY) { $maxY = $y }
            }
        }
    }
    if ($count -eq 0) { throw 'Rendered title is blank.' }
    return [ordered]@{ left = $minX; top = $minY; right = $maxX; bottom = $maxY; nonzero_alpha_pixels = $count }
}

$fontPath = (Resolve-Path -LiteralPath $FontPathInput).Path
if ((Get-FileSha256 $fontPath) -ne $ExpectedFontSha256) {
    throw "Official SeoulHangang M TTF hash mismatch: $fontPath"
}
$outputRoot = [IO.Path]::GetFullPath($OutputDirectory)
[IO.Directory]::CreateDirectory($outputRoot) | Out-Null

Add-Type -AssemblyName System.Drawing
$privateFonts = New-Object Drawing.Text.PrivateFontCollection
try {
    $privateFonts.AddFontFile($fontPath)
    $families = @($privateFonts.Families | Where-Object Name -eq $ExpectedFamily)
    if ($families.Count -ne 1) {
        throw "Expected one private font family '$ExpectedFamily', found $($families.Count)."
    }
    $family = $families[0]
    $rows = [Collections.Generic.List[object]]::new()
    foreach ($entry in $Labels.GetEnumerator()) {
        $index = [int]$entry.Key
        $text = [string]$entry.Value
        $bitmap = [Drawing.Bitmap]::new(
            512,
            64,
            [Drawing.Imaging.PixelFormat]::Format32bppArgb
        )
        $bitmap.SetResolution(72, 72)
        $graphics = [Drawing.Graphics]::FromImage($bitmap)
        $path = New-Object Drawing.Drawing2D.GraphicsPath
        $shadowPath = New-Object Drawing.Drawing2D.GraphicsPath
        $format = [Drawing.StringFormat]::GenericTypographic.Clone()
        $outline = New-Object Drawing.Pen([Drawing.Color]::FromArgb(255, 39, 43, 44), 4.0)
        $shadowOutline = New-Object Drawing.Pen([Drawing.Color]::FromArgb(220, 73, 77, 65), 5.0)
        $fill = New-Object Drawing.SolidBrush([Drawing.Color]::FromArgb(255, 202, 205, 201))
        $shadowFill = New-Object Drawing.SolidBrush([Drawing.Color]::FromArgb(205, 64, 68, 58))
        try {
            $graphics.Clear([Drawing.Color]::Transparent)
            $graphics.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
            $graphics.CompositingQuality = [Drawing.Drawing2D.CompositingQuality]::HighQuality
            $graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $graphics.TextRenderingHint = [Drawing.Text.TextRenderingHint]::AntiAliasGridFit
            $format.FormatFlags = $format.FormatFlags -bor [Drawing.StringFormatFlags]::NoWrap
            $path.AddString(
                $text,
                $family,
                [int][Drawing.FontStyle]::Regular,
                42.0,
                [Drawing.PointF]::new(6.0, 3.0),
                $format
            )
            $shadowPath.AddPath($path, $false)
            $matrix = New-Object Drawing.Drawing2D.Matrix
            try {
                $matrix.Translate(3.0, 3.0)
                $shadowPath.Transform($matrix)
            } finally { $matrix.Dispose() }
            $outline.LineJoin = [Drawing.Drawing2D.LineJoin]::Round
            $shadowOutline.LineJoin = [Drawing.Drawing2D.LineJoin]::Round
            $graphics.DrawPath($shadowOutline, $shadowPath)
            $graphics.FillPath($shadowFill, $shadowPath)
            $graphics.DrawPath($outline, $path)
            $graphics.FillPath($fill, $path)
            $bounds = Get-AlphaBounds $bitmap
            if ($bounds.left -lt 1 -or $bounds.top -lt 1 -or $bounds.right -gt 510 -or $bounds.bottom -gt 62) {
                throw "Rendered label $index touches the 512x64 safety margin."
            }
            $fileName = ('{0:D3}.png' -f $index)
            $pathOut = Join-Path $outputRoot $fileName
            $bitmap.Save($pathOut, [Drawing.Imaging.ImageFormat]::Png)
            $rows.Add([ordered]@{
                index = $index
                label = $text
                file = $fileName
                sha256 = Get-FileSha256 $pathOut
                alpha_bbox = $bounds
            })
        } finally {
            $shadowFill.Dispose(); $fill.Dispose(); $shadowOutline.Dispose(); $outline.Dispose()
            $format.Dispose(); $shadowPath.Dispose(); $path.Dispose(); $graphics.Dispose(); $bitmap.Dispose()
        }
    }
    $report = [ordered]@{
        schema = 'nobu16.pc-pk-title-corrected-label-raster.v1'
        font = [ordered]@{ family = $ExpectedFamily; path = $fontPath; sha256 = $ExpectedFontSha256 }
        canvas = @(512, 64)
        renderer = 'System.Drawing GraphicsPath; SeoulHangang M 42px; rounded dark outline and offset muted shadow; 72DPI'
        labels = $rows
        source_free = $true
        installed_game_files_modified = $false
    }
    $jsonPath = Join-Path $outputRoot 'render_report.json'
    [IO.File]::WriteAllText($jsonPath, ($report | ConvertTo-Json -Depth 8), (New-Object Text.UTF8Encoding($false)))
    Write-Output "report=$jsonPath"
    foreach ($row in $rows) { Write-Output ("{0:D3}={1}" -f [int]$row.index, (Join-Path $outputRoot $row.file)) }
} finally {
    $privateFonts.Dispose()
}
