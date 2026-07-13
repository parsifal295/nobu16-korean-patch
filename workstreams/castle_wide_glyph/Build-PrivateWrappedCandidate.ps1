param(
    [string]$Python = 'python',
    [string]$WorkspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$tool = Join-Path $WorkspaceRoot 'KR_PATCH_WORK\tools\nobu16_lz4.py'
$stockMessage = Join-Path $WorkspaceRoot 'MSG_PK\SC\msgdata.bin'
$stockFont = Join-Path $WorkspaceRoot 'RES_SC\res_lang.bin'
$rawRoot = Join-Path $PSScriptRoot 'private\candidate'
$outputRoot = Join-Path $PSScriptRoot 'private\wrapper_candidate'
$targetMessage = Join-Path $outputRoot 'MSG_PK\SC\msgdata.bin'
$targetFont = Join-Path $outputRoot 'RES_SC\res_lang.bin'
$stepFont = Join-Path $outputRoot 'res_lang.entry6.step.bin'
$rawMessage = Join-Path $rawRoot 'msgdata.probe-9168-wide.name-only.raw'
$rawFont6 = Join-Path $rawRoot 'SC_6.probe-9168-wide.g1n'
$rawFont7 = Join-Path $rawRoot 'SC_7.probe-9168-wide.g1n'

$expected = @{
    stock_message = '0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E'
    stock_font = '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99'
    raw_message = '2F83D99CAFD4E0291A2C33DFAFC9AB79B4DB2FE37CD5FD8DD6C101B4D724C48E'
    raw_font6 = '22E253653364A0F1F4FC6F597D2EBFA0B5B1B8A12B84F0380046C2C8106570A1'
    raw_font7 = 'E239E92F7F4E2AC866B9918D553EBE8FB657633B5875DA9B3664787EBD22C795'
    target_message = '165353713703A2A1D72C24D6C9A7D5709F21FA3D2B641993BE786BA14B2B17CC'
    target_font = 'AFBB287B5418FBCB44B083F7D77E5F53426AE7E1AB23C6B69F17EC98E0EB7258'
}

function Assert-Hash([string]$Path, [string]$Expected, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing ${Label}: $Path" }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
    if ($actual -ne $Expected) { throw "${Label} hash mismatch: expected=$Expected actual=$actual" }
}

function Invoke-Tool([string[]]$Arguments) {
    & $Python $tool @Arguments
    if ($LASTEXITCODE -ne 0) { throw "nobu16_lz4.py failed with exit code $LASTEXITCODE" }
}

Assert-Hash $stockMessage $expected.stock_message 'stock message wrapper'
Assert-Hash $stockFont $expected.stock_font 'stock font archive'
Assert-Hash $rawMessage $expected.raw_message 'raw message candidate'
Assert-Hash $rawFont6 $expected.raw_font6 'raw font entry 6 candidate'
Assert-Hash $rawFont7 $expected.raw_font7 'raw font entry 7 candidate'

[IO.Directory]::CreateDirectory((Split-Path -Parent $targetMessage)) | Out-Null
[IO.Directory]::CreateDirectory((Split-Path -Parent $targetFont)) | Out-Null

Invoke-Tool -Arguments @('recompress', $rawMessage, $targetMessage, '--template', $stockMessage)
Invoke-Tool -Arguments @('repack-entry', $stockFont, '6', $rawFont6, $stepFont, '--compress')
try {
    Invoke-Tool -Arguments @('repack-entry', $stepFont, '7', $rawFont7, $targetFont, '--compress')
} finally {
    if (Test-Path -LiteralPath $stepFont -PathType Leaf) { [IO.File]::Delete($stepFont) }
}
Invoke-Tool -Arguments @('verify', $targetMessage)
Invoke-Tool -Arguments @('verify-link', $targetFont)
Assert-Hash $targetMessage $expected.target_message 'wrapped message candidate'
Assert-Hash $targetFont $expected.target_font 'wrapped font candidate'

Write-Output "message=$targetMessage"
Write-Output "message_sha256=$($expected.target_message)"
Write-Output "font=$targetFont"
Write-Output "font_sha256=$($expected.target_font)"
Write-Output 'private_wrapped_candidate=OK'
