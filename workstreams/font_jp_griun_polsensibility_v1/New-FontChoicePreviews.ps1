[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SeoulHangangCandidateRoot,

    [Parameter(Mandatory = $true)]
    [string]$GriunCandidateRoot,

    [Parameter(Mandatory = $true)]
    [string]$OutputRoot
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$renderer = Join-Path $scriptRoot 'render_table1_preview.py'
$output = [IO.Path]::GetFullPath($OutputRoot)
New-Item -ItemType Directory -Path $output -Force | Out-Null

function New-PngPreview {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Variant,
        [Parameter(Mandatory = $true)]
        [string]$CandidateRoot,
        [Parameter(Mandatory = $true)]
        [string]$OutputName
    )

    $png = Join-Path $output ($OutputName + '.png')
    $manifest = [IO.Path]::ChangeExtension($png, '.json')
    if (Test-Path -LiteralPath $png) {
        Remove-Item -LiteralPath $png -Force
    }
    if (Test-Path -LiteralPath $manifest) {
        Remove-Item -LiteralPath $manifest -Force
    }

    & python -B $renderer `
        --candidate-root $CandidateRoot `
        --variant $Variant `
        --layout cli `
        --output $png
    if ($LASTEXITCODE -ne 0) {
        throw "Preview renderer failed for $Variant"
    }

    [pscustomobject]@{
        Variant = $Variant
        Path = $png
        Size = (Get-Item -LiteralPath $png).Length
        Sha256 = (Get-FileHash -LiteralPath $png -Algorithm SHA256).Hash
    }
}

$rows = @(
    New-PngPreview `
        -Variant 'seoulhangang' `
        -CandidateRoot $SeoulHangangCandidateRoot `
        -OutputName 'font_preview_a_seoulhangang'
    New-PngPreview `
        -Variant 'griun' `
        -CandidateRoot $GriunCandidateRoot `
        -OutputName 'font_preview_b_griun'
)

$rows | Format-Table -AutoSize
