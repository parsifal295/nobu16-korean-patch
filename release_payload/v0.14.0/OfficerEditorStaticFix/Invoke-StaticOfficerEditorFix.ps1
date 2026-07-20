[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GameRoot,

    [switch]$Restore,

    [switch]$Status
)

# Backward-compatible entry point kept for v0.11.0-v0.11.5 users and the old BAT.
$master = Join-Path $PSScriptRoot 'Invoke-Nobu16StaticPatches.ps1'
if (-not (Test-Path -LiteralPath $master -PathType Leaf)) {
    Write-Host "Missing master installer: $master" -ForegroundColor Red
    exit 1
}

& $master @PSBoundParameters
