param(
    [string]$FontRootInput,
    [string]$CurrentDashboardRootInput,
    [string]$OutputRootInput,
    [string]$CatalogInput
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function New-UnicodeString([int[]]$Codepoints) {
    return -join @($Codepoints | ForEach-Object { [char]$_ })
}

function Get-FileSha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Get-AlphaBounds([Drawing.Bitmap]$Bitmap) {
    $minX = $Bitmap.Width
    $minY = $Bitmap.Height
    $maxX = -1
    $maxY = -1
    $count = 0
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
    return [ordered]@{
        left = $minX
        top = $minY
        right = $maxX
        bottom = $maxY
        width = $maxX - $minX + 1
        height = $maxY - $minY + 1
        nonzero_alpha_pixels = $count
    }
}

function Assert-UnderTmp([string]$Candidate, [string]$TmpRoot) {
    $candidateFull = [IO.Path]::GetFullPath($Candidate)
    $tmpFull = [IO.Path]::GetFullPath($TmpRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
    if (-not $candidateFull.StartsWith($tmpFull + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Output must stay below tmp: $candidateFull"
    }
    return $candidateFull
}

function New-TitleBitmap {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,
        [Parameter(Mandatory = $true)]
        [Drawing.FontFamily]$FontFamily,
        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    $scale = 4.0
    $canvasWidth = 1024
    $canvasHeight = 256
    $workWidth = [int]($canvasWidth * $scale)
    $workHeight = [int]($canvasHeight * $scale)
    $safeWidth = 920.0 * $scale
    $safeHeight = 154.0 * $scale
    $inkLeft = 24.0 * $scale
    $inkCenterY = 76.0 * $scale
    $firstGlyphFontSize = 136.0
    $remainingFontTiers = @(112.0, 102.0, 92.0, 84.0)
    $glyphJoinGap = 2.0 * $scale
    $outerBlurOutlineWidth = 18.0 * $scale
    $middleBlurOutlineWidth = 13.0 * $scale
    $mainOutlineWidth = 8.0 * $scale
    $shadowOutlineWidth = 12.0 * $scale
    $shadowDx = 3.0 * $scale
    $shadowDy = 4.0 * $scale

    $format = [Drawing.StringFormat]::GenericTypographic.Clone()
    $selectedPath = $null
    $selectedRemainingSize = $null
    $selectedExtents = $null
    try {
        $format.FormatFlags = $format.FormatFlags -bor [Drawing.StringFormatFlags]::NoWrap
        $firstText = $Text.Substring(0, 1)
        $remainingText = if ($Text.Length -gt 1) { $Text.Substring(1) } else { '' }
        foreach ($remainingSize in $remainingFontTiers) {
            $candidatePath = New-Object Drawing.Drawing2D.GraphicsPath
            $firstPath = New-Object Drawing.Drawing2D.GraphicsPath
            $remainingPath = New-Object Drawing.Drawing2D.GraphicsPath
            try {
                $firstPath.AddString(
                    $firstText,
                    $FontFamily,
                    [int][Drawing.FontStyle]::Regular,
                    [single]($firstGlyphFontSize * $scale),
                    [Drawing.PointF]::new(0.0, 0.0),
                    $format
                )
                $candidatePath.AddPath($firstPath, $false)
                if ($remainingText.Length -gt 0) {
                    $remainingPath.AddString(
                        $remainingText,
                        $FontFamily,
                        [int][Drawing.FontStyle]::Regular,
                        [single]($remainingSize * $scale),
                        [Drawing.PointF]::new(0.0, 0.0),
                        $format
                    )
                    $firstBounds = $firstPath.GetBounds()
                    $remainingBounds = $remainingPath.GetBounds()
                    $remainingMatrix = New-Object Drawing.Drawing2D.Matrix
                    try {
                        $remainingMatrix.Translate(
                            [single]($firstBounds.Right + $glyphJoinGap - $remainingBounds.Left),
                            [single]($firstBounds.Bottom - $remainingBounds.Bottom)
                        )
                        $remainingPath.Transform($remainingMatrix)
                    } finally { $remainingMatrix.Dispose() }
                    $candidatePath.AddPath($remainingPath, $false)
                }
            } finally {
                $remainingPath.Dispose()
                $firstPath.Dispose()
            }
            $bounds = $candidatePath.GetBounds()
            $left = [Math]::Min($bounds.Left - $outerBlurOutlineWidth / 2.0, $bounds.Left + $shadowDx - $shadowOutlineWidth / 2.0)
            $top = [Math]::Min($bounds.Top - $outerBlurOutlineWidth / 2.0, $bounds.Top + $shadowDy - $shadowOutlineWidth / 2.0)
            $right = [Math]::Max($bounds.Right + $outerBlurOutlineWidth / 2.0, $bounds.Right + $shadowDx + $shadowOutlineWidth / 2.0)
            $bottom = [Math]::Max($bounds.Bottom + $outerBlurOutlineWidth / 2.0, $bounds.Bottom + $shadowDy + $shadowOutlineWidth / 2.0)
            if (($right - $left) -le $safeWidth -and ($bottom - $top) -le $safeHeight) {
                $selectedPath = $candidatePath
                $selectedRemainingSize = $remainingSize
                $selectedExtents = @($left, $top, $right, $bottom)
                break
            }
            $candidatePath.Dispose()
        }
        if ($null -eq $selectedPath) { throw "No fixed size tier fits title: $Text" }

        $translateX = $inkLeft - $selectedExtents[0]
        $translateY = $inkCenterY - (($selectedExtents[1] + $selectedExtents[3]) / 2.0)
        $matrix = New-Object Drawing.Drawing2D.Matrix
        try {
            $matrix.Translate([single]$translateX, [single]$translateY)
            $selectedPath.Transform($matrix)
        } finally { $matrix.Dispose() }

        $shadowPath = New-Object Drawing.Drawing2D.GraphicsPath
        $shadowMatrix = New-Object Drawing.Drawing2D.Matrix
        try {
            $shadowPath.AddPath($selectedPath, $false)
            $shadowMatrix.Translate([single]$shadowDx, [single]$shadowDy)
            $shadowPath.Transform($shadowMatrix)

            $workBitmap = [Drawing.Bitmap]::new($workWidth, $workHeight, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
            $graphics = [Drawing.Graphics]::FromImage($workBitmap)
            $outerBlurOutline = New-Object Drawing.Pen([Drawing.Color]::FromArgb(52, 222, 222, 214), [single]$outerBlurOutlineWidth)
            $middleBlurOutline = New-Object Drawing.Pen([Drawing.Color]::FromArgb(112, 222, 222, 214), [single]$middleBlurOutlineWidth)
            $mainOutline = New-Object Drawing.Pen([Drawing.Color]::FromArgb(225, 222, 222, 214), [single]$mainOutlineWidth)
            $shadowOutline = New-Object Drawing.Pen([Drawing.Color]::FromArgb(170, 42, 45, 43), [single]$shadowOutlineWidth)
            $mainFill = New-Object Drawing.SolidBrush([Drawing.Color]::FromArgb(255, 55, 58, 60))
            $shadowFill = New-Object Drawing.SolidBrush([Drawing.Color]::FromArgb(145, 42, 45, 43))
            try {
                $graphics.Clear([Drawing.Color]::Transparent)
                $graphics.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
                $graphics.CompositingQuality = [Drawing.Drawing2D.CompositingQuality]::HighQuality
                $graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
                $graphics.TextRenderingHint = [Drawing.Text.TextRenderingHint]::AntiAliasGridFit
                $outerBlurOutline.LineJoin = [Drawing.Drawing2D.LineJoin]::Round
                $middleBlurOutline.LineJoin = [Drawing.Drawing2D.LineJoin]::Round
                $mainOutline.LineJoin = [Drawing.Drawing2D.LineJoin]::Round
                $shadowOutline.LineJoin = [Drawing.Drawing2D.LineJoin]::Round
                $graphics.DrawPath($shadowOutline, $shadowPath)
                $graphics.FillPath($shadowFill, $shadowPath)
                $graphics.DrawPath($outerBlurOutline, $selectedPath)
                $graphics.DrawPath($middleBlurOutline, $selectedPath)
                $graphics.DrawPath($mainOutline, $selectedPath)
                $graphics.FillPath($mainFill, $selectedPath)

                $finalBitmap = [Drawing.Bitmap]::new($canvasWidth, $canvasHeight, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
                $finalGraphics = [Drawing.Graphics]::FromImage($finalBitmap)
                try {
                    $finalGraphics.Clear([Drawing.Color]::Transparent)
                    $finalGraphics.CompositingMode = [Drawing.Drawing2D.CompositingMode]::SourceCopy
                    $finalGraphics.CompositingQuality = [Drawing.Drawing2D.CompositingQuality]::HighQuality
                    $finalGraphics.InterpolationMode = [Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
                    $finalGraphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
                    $finalGraphics.DrawImage(
                        $workBitmap,
                        [Drawing.Rectangle]::new(0, 0, $canvasWidth, $canvasHeight),
                        0,
                        0,
                        $workWidth,
                        $workHeight,
                        [Drawing.GraphicsUnit]::Pixel
                    )
                    $boundsOut = Get-AlphaBounds $finalBitmap
                    if ($boundsOut.left -lt 1 -or $boundsOut.top -lt 1 -or $boundsOut.right -gt 1022 -or $boundsOut.bottom -gt 158) {
                        throw "Rendered label is outside the PORT3 title safety band: $Text"
                    }
                    $finalBitmap.Save($OutputPath, [Drawing.Imaging.ImageFormat]::Png)
                    return [ordered]@{
                        first_glyph_font_size_px = $firstGlyphFontSize
                        remaining_font_size_px = $selectedRemainingSize
                        render_scale = [int]$scale
                        alpha_bbox = $boundsOut
                    }
                } finally {
                    $finalGraphics.Dispose()
                    $finalBitmap.Dispose()
                }
            } finally {
                $shadowFill.Dispose()
                $mainFill.Dispose()
                $shadowOutline.Dispose()
                $mainOutline.Dispose()
                $middleBlurOutline.Dispose()
                $outerBlurOutline.Dispose()
                $graphics.Dispose()
                $workBitmap.Dispose()
            }
        } finally {
            $shadowMatrix.Dispose()
            $shadowPath.Dispose()
        }
    } finally {
        if ($null -ne $selectedPath) { $selectedPath.Dispose() }
        $format.Dispose()
    }
}

$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$tmpRoot = Join-Path $repoRoot 'tmp'
if ([string]::IsNullOrWhiteSpace($FontRootInput)) {
    $FontRootInput = Join-Path $tmpRoot 'third_party_fonts\yeongyang_eumsikdimibang'
}
if ([string]::IsNullOrWhiteSpace($CurrentDashboardRootInput)) {
    $CurrentDashboardRootInput = Join-Path $tmpRoot 'atlas_dashboard\current_20260722_1345\details\port3-high'
}
if ([string]::IsNullOrWhiteSpace($OutputRootInput)) {
    $OutputRootInput = Join-Path $tmpRoot 'atlas_dashboard\port3_title_consistency_dimibang_v1'
}
if ([string]::IsNullOrWhiteSpace($CatalogInput)) {
    $CatalogInput = Join-Path $PSScriptRoot 'title_catalog.v1.json'
}

$fontRoot = [IO.Path]::GetFullPath($FontRootInput)
$currentRoot = [IO.Path]::GetFullPath($CurrentDashboardRootInput)
$outputRoot = Assert-UnderTmp $OutputRootInput $tmpRoot
[IO.Directory]::CreateDirectory($outputRoot) | Out-Null
[IO.Directory]::CreateDirectory((Join-Path $outputRoot 'current')) | Out-Null
[IO.Directory]::CreateDirectory((Join-Path $outputRoot 'dimibang')) | Out-Null

$catalogPath = [IO.Path]::GetFullPath($CatalogInput)
$catalog = Get-Content -LiteralPath $catalogPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($catalog.schema -ne 'nobu16.kr.port3-title-catalog.v1') { throw "Unexpected title catalog schema: $($catalog.schema)" }
$labels = @($catalog.entries)
if ($labels.Count -ne 110) { throw "Title catalog must contain 110 entries, found $($labels.Count)." }
for ($index = 0; $index -lt $labels.Count; $index++) {
    if ([int]$labels[$index].slot -ne $index) { throw "Title catalog slot order differs at $index." }
    if ([string]::IsNullOrWhiteSpace([string]$labels[$index].text)) { throw "Title catalog text is blank at $index." }
}

$variants = @(
    [ordered]@{
        id = 'dimibang'
        display = 'Yeongyang-gun Eumsikdimibang'
        file = 'Yydimibang.ttf'
        family = 'Yydimibang Bold'
        sha256 = '647D7710ED205C005892D96A468996C1F8FCBA135F41BF975A5EBA2C86DE7326'
    }
)

Add-Type -AssemblyName System.Drawing
$fontCollections = @{}
$fontRows = [Collections.Generic.List[object]]::new()
$rows = [Collections.Generic.List[object]]::new()
try {
    foreach ($variant in $variants) {
        $fontPath = Join-Path $fontRoot $variant.file
        if (-not [IO.File]::Exists($fontPath)) { throw "Missing font: $fontPath" }
        if ((Get-FileSha256 $fontPath) -ne $variant.sha256) { throw "Font hash mismatch: $fontPath" }
        $collection = New-Object Drawing.Text.PrivateFontCollection
        $collection.AddFontFile($fontPath)
        $families = @($collection.Families | Where-Object Name -eq $variant.family)
        if ($families.Count -ne 1) { throw "Expected font family '$($variant.family)' in $fontPath" }
        $fontCollections[$variant.id] = $collection
        $fontRows.Add([ordered]@{
            id = $variant.id
            display = $variant.display
            family = $variant.family
            file = $variant.file
            sha256 = $variant.sha256
        })
    }

    foreach ($label in $labels) {
        $slot = [int]$label.slot
        $currentSource = Join-Path $currentRoot (('outer_000_slot_{0:D3}\texture_000_1024x256.png') -f $slot)
        if (-not [IO.File]::Exists($currentSource)) { throw "Missing current dashboard PNG: $currentSource" }
        $currentFile = ('current/{0:D3}.png' -f $slot)
        $currentOutput = Join-Path $outputRoot $currentFile
        [IO.File]::Copy($currentSource, $currentOutput, $true)
        $currentBitmap = [Drawing.Bitmap]::new($currentOutput)
        try { $currentBounds = Get-AlphaBounds $currentBitmap } finally { $currentBitmap.Dispose() }

        $variantRows = [ordered]@{}
        foreach ($variant in $variants) {
            $relativeFile = ('{0}/{1:D3}.png' -f $variant.id, $slot)
            $outputPath = Join-Path $outputRoot $relativeFile
            $collection = $fontCollections[$variant.id]
            $render = New-TitleBitmap -Text $label.text -FontFamily $collection.Families[0] -OutputPath $outputPath
            $render.file = $relativeFile
            $render.sha256 = Get-FileSha256 $outputPath
            $variantRows[$variant.id] = $render
        }
        $rows.Add([ordered]@{
            slot = $slot
            text = $label.text
            note = $label.note
            current = [ordered]@{
                file = $currentFile
                sha256 = Get-FileSha256 $currentOutput
                alpha_bbox = $currentBounds
            }
            variants = $variantRows
        })
    }

    $report = [ordered]@{
        schema = 'nobu16.kr.port3-title-consistency-dimibang-preview.v1'
        source_free = $false
        private_review_output = $true
        installed_game_files_modified = $false
        archive_candidate_built = $false
        canvas = @(1024, 256)
        target_ink_band = [ordered]@{ left_x = 24; center_y = 76; bottom_safety_limit = 158; max_width = 920 }
        policy = [ordered]@{
            deterministic_font_renderer = 'System.Drawing GraphicsPath at 4x, HighQualityBicubic downsample'
            first_glyph_font_size_px = 136
            remaining_font_size_tiers_px = @(112, 102, 92, 84)
            glyph_join_gap_px = 2
            mixed_size_alignment = 'ink bottoms aligned'
            continuous_per_title_scaling = $false
            horizontal_alignment = 'fixed left ink origin at x=24'
            vertical_alignment = 'fixed ink band center'
            fill_rgba = @(55, 58, 60, 255)
            outline_rgba = @(222, 222, 214, 255)
            outline_blur_layers = @(
                [ordered]@{ width_px = 18; alpha = 52 },
                [ordered]@{ width_px = 13; alpha = 112 },
                [ordered]@{ width_px = 8; alpha = 225 }
            )
            shadow_offset_px = @(3, 4)
        }
        translations_added = [ordered]@{
            '108' = New-UnicodeString @(0xBAA9,0xD45C,0x20,0xBB34,0xC7A5,0x20,0xC120,0xD0DD)
            '109' = New-UnicodeString @(0xAD6D,0xC778,0xC911,0x20,0xC120,0xD0DD)
        }
        catalog = [ordered]@{ path = $catalogPath; sha256 = Get-FileSha256 $catalogPath; entry_count = $labels.Count }
        target_slots = @($labels | ForEach-Object { [int]$_.slot })
        fonts = $fontRows
        entries = $rows
    }
    $jsonPath = Join-Path $outputRoot 'report.json'
    [IO.File]::WriteAllText($jsonPath, ($report | ConvertTo-Json -Depth 12), (New-Object Text.UTF8Encoding($false)))

    $htmlRows = [Text.StringBuilder]::new()
    foreach ($row in $rows) {
        $slotText = ('{0:D3}' -f [int]$row.slot)
        $safeText = [Net.WebUtility]::HtmlEncode([string]$row.text)
        $safeNote = [Net.WebUtility]::HtmlEncode([string]$row.note)
        $currentBox = $row.current.alpha_bbox
        $dimibangBox = $row.variants.dimibang.alpha_bbox
        [void]$htmlRows.AppendLine("<section class='row'>")
        [void]$htmlRows.AppendLine("<header><b>slot $slotText</b><span class='ko'>$safeText</span><span class='note'>$safeNote</span></header>")
        [void]$htmlRows.AppendLine("<div class='compare'>")
        [void]$htmlRows.AppendLine("<article><h2>Current</h2><button class='image-stage' data-src='$($row.current.file)'><img src='$($row.current.file)' alt='slot $slotText current'></button><p>$($currentBox.width)x$($currentBox.height), y $($currentBox.top)-$($currentBox.bottom)</p></article>")
        [void]$htmlRows.AppendLine("<article><h2>Unified - Eumsikdimibang</h2><button class='image-stage' data-src='$($row.variants.dimibang.file)'><img src='$($row.variants.dimibang.file)' alt='slot $slotText Eumsikdimibang'></button><p>$($dimibangBox.width)x$($dimibangBox.height), y $($dimibangBox.top)-$($dimibangBox.bottom), first $($row.variants.dimibang.first_glyph_font_size_px)px / rest $($row.variants.dimibang.remaining_font_size_px)px</p></article>")
        [void]$htmlRows.AppendLine("</div></section>")
    }

    $html = @"
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PORT3 title consistency - Eumsikdimibang</title>
<style>
:root{color-scheme:dark;font-family:"Segoe UI",sans-serif;background:#151719;color:#eef0e9}*{box-sizing:border-box}body{margin:0}.top{position:sticky;top:0;z-index:5;padding:14px 22px;background:#151719ee;border-bottom:1px solid #444}.top h1{margin:0 0 5px;font-size:20px}.top p{margin:2px 0;color:#bfc4bd;font-size:13px}.legend{display:flex;gap:16px;margin-top:8px;font-size:12px}.legend b{color:#f0dfae}main{padding:14px;max-width:1500px;margin:auto}.row{margin:0 0 18px;border:1px solid #3e4243;background:#202325;border-radius:8px;overflow:hidden}.row>header{display:flex;align-items:baseline;gap:14px;padding:9px 13px;border-bottom:1px solid #3e4243}.row>header b{color:#f0dfae}.ko{font-size:18px}.note{color:#9ba29e;font-size:12px}.compare{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:#3e4243}.compare article{background:#202325;padding:8px}.compare h2{font-size:13px;margin:0 0 6px;color:#d5d9d4}.compare p{font:11px Consolas,monospace;color:#9fa6a1;margin:4px 0 0}.image-stage{display:block;width:100%;padding:0;border:0;cursor:zoom-in;background-color:#292c2e;background-image:linear-gradient(45deg,#3b3e40 25%,transparent 25%),linear-gradient(-45deg,#3b3e40 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#3b3e40 75%),linear-gradient(-45deg,transparent 75%,#3b3e40 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}.image-stage img{display:block;width:100%;height:auto}.modal{display:none;position:fixed;inset:0;z-index:20;background:#0a0b0ced;align-items:center;justify-content:center;padding:24px;cursor:zoom-out}.modal.open{display:flex}.modal img{width:min(1024px,95vw);height:auto;max-height:90vh;object-fit:contain;background-color:#292c2e;background-image:linear-gradient(45deg,#3b3e40 25%,transparent 25%),linear-gradient(-45deg,#3b3e40 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#3b3e40 75%),linear-gradient(-45deg,transparent 75%,#3b3e40 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}@media(max-width:900px){.compare{grid-template-columns:1fr}.top{position:static}}
</style>
</head>
<body>
<div class="top"><h1>PORT3 title consistency - Eumsikdimibang</h1><p>Current vs deterministic Yeongyang-gun Eumsikdimibang. Click an image for native 1024x256 view.</p><p>All candidate ink starts at x=24. The first glyph remains 136px; following glyphs use smaller fixed tiers with bottom alignment.</p><div class="legend"><span><b>Font</b> Yydimibang Bold</span><span>Internal render 4x; review PNG 1024x256</span></div></div>
<main>$($htmlRows.ToString())</main>
<div class="modal" id="modal"><img alt="native preview"></div>
<script>const modal=document.getElementById('modal'),preview=modal.querySelector('img');document.querySelectorAll('[data-src]').forEach(b=>b.addEventListener('click',()=>{preview.src=b.dataset.src;modal.classList.add('open')}));modal.addEventListener('click',()=>{modal.classList.remove('open');preview.removeAttribute('src')});addEventListener('keydown',e=>{if(e.key==='Escape')modal.click()});</script>
</body>
</html>
"@
    $indexPath = Join-Path $outputRoot 'index.html'
    [IO.File]::WriteAllText($indexPath, $html, (New-Object Text.UTF8Encoding($false)))
    Write-Output "dashboard=$indexPath"
    Write-Output "report=$jsonPath"
    Write-Output "slots=$($rows.Count)"
} finally {
    foreach ($collection in $fontCollections.Values) { $collection.Dispose() }
}
