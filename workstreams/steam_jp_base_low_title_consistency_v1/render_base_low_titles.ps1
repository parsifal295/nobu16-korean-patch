[CmdletBinding()]
param(
    [string]$HighRenderRootInput = '',
    [string]$OutputRootInput = ''
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$workstream = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$repo = (Resolve-Path -LiteralPath (Join-Path $workstream '..\..')).Path
$highRoot = if ($HighRenderRootInput) {
    (Resolve-Path -LiteralPath $HighRenderRootInput).Path
} else {
    (Resolve-Path -LiteralPath (Join-Path $repo 'tmp\atlas_dashboard\port3_title_consistency_dimibang_v1')).Path
}
$outputRoot = if ($OutputRootInput) {
    [IO.Path]::GetFullPath($OutputRootInput)
} else {
    [IO.Path]::GetFullPath((Join-Path $repo 'tmp\atlas_dashboard\base_low_title_consistency_dimibang_v1'))
}
$tmpRoot = [IO.Path]::GetFullPath((Join-Path $repo 'tmp')).TrimEnd('\')
if (-not $outputRoot.StartsWith($tmpRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw "output must stay below tmp: $outputRoot"
}

$highReportPath = Join-Path $highRoot 'report.json'
$expectedHighReportSha256 = 'F1369C06BE7715E6B0D22B1ED10B83614BB6ABE60A14540C44292AAA347D2C43'
$actualHighReportSha256 = (Get-FileHash -LiteralPath $highReportPath -Algorithm SHA256).Hash
if ($actualHighReportSha256 -ne $expectedHighReportSha256) {
    throw "PORT3 render report pin differs: $actualHighReportSha256"
}
$highReport = Get-Content -LiteralPath $highReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($highReport.schema -ne 'nobu16.kr.port3-title-consistency-dimibang-preview.v1') {
    throw "PORT3 render report schema differs: $($highReport.schema)"
}
if (@($highReport.entries).Count -ne 110) {
    throw "PORT3 render report must contain 110 titles"
}
$inputSlots = @($highReport.entries | ForEach-Object { [int]$_.slot } | Sort-Object)
if (($inputSlots -join ',') -ne ((0..109) -join ',')) {
    throw 'PORT3 render report slot set differs'
}

$lowRoot = Join-Path $outputRoot 'low'
New-Item -ItemType Directory -Path $lowRoot -Force | Out-Null
$rows = New-Object System.Collections.Generic.List[object]

foreach ($entry in $highReport.entries) {
    $slot = [int]$entry.slot
    if ($slot -lt 0 -or $slot -ge 110) { throw "invalid title slot: $slot" }
    $name = '{0:D3}.png' -f $slot
    $sourcePath = Join-Path $highRoot $entry.variants.dimibang.file
    $targetPath = Join-Path $lowRoot $name
    $tempPath = $targetPath + '.tmp.png'
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw "missing high PNG: $sourcePath" }

    $source = New-Object System.Drawing.Bitmap($sourcePath)
    try {
        if ($source.Width -ne 1024 -or $source.Height -ne 256) {
            throw "HIGH geometry differs at slot $slot`: $($source.Width)x$($source.Height)"
        }
        $target = New-Object System.Drawing.Bitmap(512, 128, [System.Drawing.Imaging.PixelFormat]::Format32bppPArgb)
        try {
            $graphics = [System.Drawing.Graphics]::FromImage($target)
            try {
                $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
                $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::GammaCorrected
                $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
                $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
                $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
                $attributes = New-Object System.Drawing.Imaging.ImageAttributes
                try {
                    $attributes.SetWrapMode([System.Drawing.Drawing2D.WrapMode]::TileFlipXY)
                    $destination = New-Object System.Drawing.Rectangle(0, 0, 512, 128)
                    $graphics.DrawImage(
                        $source,
                        $destination,
                        0,
                        0,
                        1024,
                        256,
                        [System.Drawing.GraphicsUnit]::Pixel,
                        $attributes
                    )
                } finally {
                    $attributes.Dispose()
                }
            } finally {
                $graphics.Dispose()
            }
            if (Test-Path -LiteralPath $tempPath) { Remove-Item -LiteralPath $tempPath -Force }
            $target.Save($tempPath, [System.Drawing.Imaging.ImageFormat]::Png)
        } finally {
            $target.Dispose()
        }
    } finally {
        $source.Dispose()
    }
    Move-Item -LiteralPath $tempPath -Destination $targetPath -Force
    $targetBitmap = New-Object System.Drawing.Bitmap($targetPath)
    try {
        if ($targetBitmap.Width -ne 512 -or $targetBitmap.Height -ne 128) {
            throw "LOW geometry differs at slot $slot"
        }
    } finally {
        $targetBitmap.Dispose()
    }
    $rows.Add([ordered]@{
        slot = $slot
        text = [string]$entry.text
        source_high = [ordered]@{
            path = $sourcePath
            size = (Get-Item -LiteralPath $sourcePath).Length
            sha256 = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
        }
        low = [ordered]@{
            file = ('low/{0}' -f $name)
            size = (Get-Item -LiteralPath $targetPath).Length
            sha256 = (Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash
        }
    })
}

if ($rows.Count -ne 110) { throw 'rendered LOW title count differs' }
$report = [ordered]@{
    schema = 'nobu16.kr.base-low-title-dimibang-render.v1'
    installed_game_files_modified = $false
    title_count = 110
    source_high_render = [ordered]@{
        root = $highRoot
        report_sha256 = $actualHighReportSha256
        candidate_sha256 = 'BA739C28A8EE1A47C8085339F98FDCF4F317302316F93C3F74E413DB2AFEADC9'
    }
    canvas = [ordered]@{ source = @(1024, 256); target = @(512, 128); scale = 0.5 }
    policy = [ordered]@{
        alpha = 'System.Drawing Format32bppPArgb'
        resampler = 'HighQualityBicubic'
        crop = $false
        whole_canvas_downsample = $true
    }
    entries = @($rows | Sort-Object slot)
}
$reportPath = Join-Path $outputRoot 'report.json'
$json = $report | ConvertTo-Json -Depth 8
[IO.File]::WriteAllText($reportPath, $json, (New-Object Text.UTF8Encoding($false)))
Write-Output ($report | ConvertTo-Json -Depth 4)
Write-Output "report=$reportPath"
