param(
    [Parameter(Mandatory = $true)]
    [string]$RequestPathInput,
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Get-FileSha256([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return (($sha.ComputeHash($stream) | ForEach-Object { $_.ToString('X2') }) -join '')
    } finally {
        $sha.Dispose()
        $stream.Dispose()
    }
}

function Get-BytesSha256([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return (($sha.ComputeHash($Bytes) | ForEach-Object { $_.ToString('X2') }) -join '')
    } finally {
        $sha.Dispose()
    }
}

$requestPath = (Resolve-Path -LiteralPath $RequestPathInput).Path
$request = Get-Content -Raw -Encoding UTF8 -LiteralPath $requestPath | ConvertFrom-Json
if ([string]$request.schema -cne 'nobu16.kr.font-jp-griun-polsensibility-v1.raster-request.v1') {
    throw 'Unsupported raster request schema.'
}

$font = $request.font
$fontPath = [IO.Path]::GetFullPath([string]$font.path)
$expectedFamily = -join @(
    44536, 47532, 50868, 32, 44221, 52272, 44048, 49457, 52404 |
        ForEach-Object { [char]$_ }
)
if ([string]$font.file_name -cne 'Griun_PolSensibility-Rg.ttf' -or
    [string]$font.family -cne $expectedFamily -or
    [int64]$font.size -ne 1936424 -or
    [string]$font.sha256 -cne '057472E1B8E4528421A5B30953A33992FFCE06F2BF9546993C364E264CD1887F' -or
    [IO.Path]::GetFileName($fontPath) -cne 'Griun_PolSensibility-Rg.ttf') {
    throw 'Official Griun font descriptor mismatch.'
}
if (-not (Test-Path -LiteralPath $fontPath -PathType Leaf) -or
    (Get-Item -LiteralPath $fontPath).Length -ne 1936424 -or
    (Get-FileSha256 $fontPath) -cne '057472E1B8E4528421A5B30953A33992FFCE06F2BF9546993C364E264CD1887F') {
    throw 'Official Griun font file pin mismatch.'
}

$codepoints = [Collections.Generic.List[int]]::new()
$previous = -1
foreach ($text in @($request.codepoints)) {
    if ([string]$text -cnotmatch '^U\+[0-9A-F]{4}$') {
        throw "Non-canonical codepoint: $text"
    }
    $cp = [Convert]::ToInt32(([string]$text).Substring(2), 16)
    if ($cp -le $previous -or $cp -lt 0xAC00 -or $cp -gt 0xD7A3) {
        throw "Invalid or unsorted Hangul codepoint: $text"
    }
    if ($cp -eq 0xCE4C -or $cp -eq 0xD07F) {
        throw "A retained cmap exception reached the rasterizer: $text"
    }
    $codepoints.Add($cp)
    $previous = $cp
}
if ($codepoints.Count -ne 2352) {
    throw "Expected 2,352 directly covered mapped Hangul codepoints; got $($codepoints.Count)."
}

$expectedProfiles = [ordered]@{
    cell32 = [ordered]@{ cell = 32; raster_size = 32 }
    cell48 = [ordered]@{ cell = 48; raster_size = 46 }
    cell64 = [ordered]@{ cell = 64; raster_size = 64 }
    cell96 = [ordered]@{ cell = 96; raster_size = 92 }
}
$profiles = @($request.profiles)
if ($profiles.Count -ne $expectedProfiles.Count) {
    throw 'Expected exactly four G1N raster profiles.'
}
$seenProfiles = @{}
foreach ($profile in $profiles) {
    $profileId = [string]$profile.profile
    if (-not $expectedProfiles.Contains($profileId) -or $seenProfiles.ContainsKey($profileId)) {
        throw "Unexpected or duplicate raster profile: $profileId"
    }
    $expected = $expectedProfiles[$profileId]
    if ([int]$profile.cell -ne [int]$expected.cell -or
        [int]$profile.raster_size -ne [int]$expected.raster_size) {
        throw "Raster geometry mismatch: $profileId"
    }
    $seenProfiles[$profileId] = $true
}

$out = [IO.Path]::GetFullPath($OutputDirectory)
[IO.Directory]::CreateDirectory($out) | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Drawing.Text;
using System.Runtime.InteropServices;

public sealed class GriunRasterProfileResult
{
    public byte[] Payload;
    public int MinimumMargin;
    public int BlankGlyphCount;
    public int ScaledToMarginCount;
}

public static class GriunRasterEngine
{
    private static int RedNibble(byte[] pixels, int stride, int x, int y)
    {
        return pixels[y * stride + x * 4 + 2] >> 4;
    }

    public static GriunRasterProfileResult RenderProfile(
        FontFamily family, int[] codepoints, int cell, float rasterSize)
    {
        if (cell <= 0 || (cell & 1) != 0 || rasterSize <= 0)
            throw new ArgumentException("Invalid raster geometry.");
        if (!family.IsStyleAvailable(FontStyle.Regular))
            throw new InvalidOperationException("Griun Regular style is unavailable.");

        int bytesPerGlyph = (cell / 2) * cell;
        byte[] payload = new byte[checked(bytesPerGlyph * codepoints.Length)];
        int minimumMargin = cell;
        int blankCount = 0;
        int scaledCount = 0;
        int canvas = cell * 2;

        using (Font font = new Font(family, rasterSize, FontStyle.Regular, GraphicsUnit.Pixel))
        using (Bitmap bitmap = new Bitmap(canvas, canvas, PixelFormat.Format32bppArgb))
        using (Graphics graphics = Graphics.FromImage(bitmap))
        using (StringFormat format = (StringFormat)StringFormat.GenericTypographic.Clone())
        {
            bitmap.SetResolution(72, 72);
            graphics.TextRenderingHint = TextRenderingHint.AntiAliasGridFit;
            graphics.TextContrast = 4;
            format.Alignment = StringAlignment.Center;
            format.LineAlignment = StringAlignment.Center;
            format.FormatFlags |= StringFormatFlags.NoWrap;
            RectangleF drawRect = new RectangleF(0, 0, canvas, canvas);
            Rectangle lockRect = new Rectangle(0, 0, canvas, canvas);

            for (int glyphIndex = 0; glyphIndex < codepoints.Length; glyphIndex++)
            {
                int cp = codepoints[glyphIndex];
                if (cp < 0 || cp > 0xFFFF)
                    throw new InvalidOperationException(String.Format("Non-BMP codepoint U+{0:X}.", cp));

                graphics.Clear(Color.Black);
                graphics.DrawString(((char)cp).ToString(), font, Brushes.White, drawRect, format);
                graphics.Flush();

                BitmapData bits = bitmap.LockBits(lockRect, ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
                byte[] source;
                int stride;
                try
                {
                    stride = Math.Abs(bits.Stride);
                    source = new byte[checked(stride * canvas)];
                    Marshal.Copy(bits.Scan0, source, 0, source.Length);
                }
                finally
                {
                    bitmap.UnlockBits(bits);
                }

                int sourceMinX = canvas, sourceMinY = canvas, sourceMaxX = -1, sourceMaxY = -1;
                for (int y = 0; y < canvas; y++)
                {
                    for (int x = 0; x < canvas; x++)
                    {
                        if (RedNibble(source, stride, x, y) == 0) continue;
                        if (x < sourceMinX) sourceMinX = x;
                        if (x > sourceMaxX) sourceMaxX = x;
                        if (y < sourceMinY) sourceMinY = y;
                        if (y > sourceMaxY) sourceMaxY = y;
                    }
                }
                if (sourceMaxX < 0)
                {
                    blankCount++;
                    throw new InvalidOperationException(String.Format("Blank raster for U+{0:X4}.", cp));
                }

                int sourceWidth = sourceMaxX - sourceMinX + 1;
                int sourceHeight = sourceMaxY - sourceMinY + 1;
                int targetWidth = sourceWidth;
                int targetHeight = sourceHeight;
                bool scaled = sourceWidth > cell - 2 || sourceHeight > cell - 2;
                if (scaled)
                {
                    double scale = Math.Min((cell - 2) / (double)sourceWidth, (cell - 2) / (double)sourceHeight);
                    targetWidth = Math.Min(cell - 2, Math.Max(1, (int)Math.Round(sourceWidth * scale)));
                    targetHeight = Math.Min(cell - 2, Math.Max(1, (int)Math.Round(sourceHeight * scale)));
                    scaledCount++;
                }
                int destX = (int)Math.Floor((cell - targetWidth) / 2.0);
                int destY = (int)Math.Floor((cell - targetHeight) / 2.0);
                int baseOffset = glyphIndex * bytesPerGlyph;
                int pixelIndex = 0;
                int minX = cell, minY = cell, maxX = -1, maxY = -1;

                for (int y = 0; y < cell; y++)
                {
                    for (int x = 0; x < cell; x += 2)
                    {
                        int left = 0, right = 0;
                        if (y >= destY && y < destY + targetHeight)
                        {
                            int dy = y - destY;
                            int sampleY = sourceMinY + (scaled
                                ? Math.Min(sourceHeight - 1, (int)Math.Floor(((dy + 0.5) * sourceHeight) / targetHeight))
                                : dy);
                            for (int delta = 0; delta < 2; delta++)
                            {
                                int dx = x + delta - destX;
                                if (dx < 0 || dx >= targetWidth) continue;
                                int sampleX = sourceMinX + (scaled
                                    ? Math.Min(sourceWidth - 1, (int)Math.Floor(((dx + 0.5) * sourceWidth) / targetWidth))
                                    : dx);
                                int value = RedNibble(source, stride, sampleX, sampleY);
                                if (delta == 0) left = value; else right = value;
                            }
                        }
                        payload[baseOffset + pixelIndex++] = (byte)((left << 4) | right);
                        if (left != 0)
                        {
                            if (x < minX) minX = x; if (x > maxX) maxX = x;
                            if (y < minY) minY = y; if (y > maxY) maxY = y;
                        }
                        if (right != 0)
                        {
                            int rightX = x + 1;
                            if (rightX < minX) minX = rightX; if (rightX > maxX) maxX = rightX;
                            if (y < minY) minY = y; if (y > maxY) maxY = y;
                        }
                    }
                }
                if (maxX < 0 || pixelIndex != bytesPerGlyph)
                    throw new InvalidOperationException(String.Format("4bpp packing failed for U+{0:X4}.", cp));
                int margin = Math.Min(Math.Min(minX, minY), Math.Min(cell - 1 - maxX, cell - 1 - maxY));
                if (margin < 1)
                    throw new InvalidOperationException(String.Format("Glyph U+{0:X4} touches the cell edge.", cp));
                if (margin < minimumMargin) minimumMargin = margin;
            }
        }

        return new GriunRasterProfileResult {
            Payload = payload,
            MinimumMargin = minimumMargin,
            BlankGlyphCount = blankCount,
            ScaledToMarginCount = scaledCount
        };
    }
}
'@ -ReferencedAssemblies 'System.Drawing'

$privateFonts = New-Object Drawing.Text.PrivateFontCollection
try {
    $privateFonts.AddFontFile($fontPath)
    # The TTF carries localized name records.  Windows PowerShell/.NET
    # Framework exposes its English family record, while newer .NET exposes
    # the Korean record pinned in the request.  The file hash and the private
    # collection prevent system-font fallback in both cases.
    $families = @($privateFonts.Families)
    if ($families.Count -ne 1 -or
        ([string]$families[0].Name -cne 'Griun PolSensibility' -and
         [string]$families[0].Name -cne $expectedFamily)) {
        throw "Expected one pinned private Griun family; found $($families.Count)."
    }
    $family = $families[0]
    if (-not $family.IsStyleAvailable([Drawing.FontStyle]::Regular)) {
        throw 'Griun Regular style is unavailable.'
    }

    $cpArray = [int[]]$codepoints.ToArray()
    $profileResults = [Collections.Generic.List[object]]::new()
    foreach ($profile in $profiles) {
        $profileId = [string]$profile.profile
        $cell = [int]$profile.cell
        $rasterSize = [int]$profile.raster_size
        $rendered = [GriunRasterEngine]::RenderProfile($family, $cpArray, $cell, [single]$rasterSize)
        $name = "glyph_pixels_${profileId}.pixels"
        $path = Join-Path $out $name
        [IO.File]::WriteAllBytes($path, $rendered.Payload)
        $profileResults.Add([ordered]@{
            profile = $profileId
            cell = $cell
            raster_size = $rasterSize
            path = $name
            size = $rendered.Payload.Length
            sha256 = Get-BytesSha256 $rendered.Payload
            glyph_count = $codepoints.Count
            minimum_margin = $rendered.MinimumMargin
            blank_glyph_count = $rendered.BlankGlyphCount
            scaled_to_margin_count = $rendered.ScaledToMarginCount
        })
    }

    $result = [ordered]@{
        schema = 'nobu16.kr.font-jp-griun-polsensibility-v1.raster-result.v1'
        request_sha256 = Get-FileSha256 $requestPath
        rasterizer = 'System.Drawing GDI+ AntiAliasGridFit TextContrast=4 72DPI; 2x scratch full-ink extraction; centered 4bpp copy'
        font_family = $family.Name
        codepoints = @($request.codepoints)
        profiles = $profileResults
        process_memory_access = $false
        registry_access = $false
        installed_game_files_modified = $false
    }
    [IO.File]::WriteAllText(
        (Join-Path $out 'raster_result.json'),
        ($result | ConvertTo-Json -Depth 8),
        (New-Object Text.UTF8Encoding($false))
    )
    Write-Output "result=$(Join-Path $out 'raster_result.json')"
} finally {
    $privateFonts.Dispose()
}
