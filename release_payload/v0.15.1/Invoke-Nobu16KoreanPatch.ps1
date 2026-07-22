[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GameRoot,

    [switch]$Apply,

    [switch]$Restore,

    [ValidateSet('Vertical', 'Horizontal')]
    [string]$CastleNameLayout
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Version = 'v0.15.1'
$OriginalExeSha256 = '29BC1ED66D27B9AEF5EB6CE3D126BA2BDBF86099E12B09615FE9F988F41E2246'
$TargetExeSha256 = @{
    Vertical = '3964E160B789982E1E197F77CBA3F592AFF0144F063E7AFCAC4DCEB4C6C99CB4'
    Horizontal = 'C1E9123539506055C1ACB96A15A446C43952AED607DEA2C9646F690813FA53D5'
}
$script:SelectedCastleNameLayout = ''

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Select-CastleNameLayout([string]$RequestedLayout) {
    if (-not [string]::IsNullOrWhiteSpace($RequestedLayout)) {
        return $RequestedLayout
    }
    while ($true) {
        Write-Host ''
        Write-Host '성이름 표시 방식을 선택하세요.' -ForegroundColor Cyan
        Write-Host '  1. 세로쓰기 — 가로쓰기와 지도 아이콘 이동 패치를 설치하지 않음'
        Write-Host '  2. 가로쓰기 — 가로 라벨과 관련 지도 아이콘 이동 패치를 설치'
        $choice = (Read-Host '번호 입력 [1/2]').Trim()
        if ($choice -eq '1') {
            return 'Vertical'
        }
        if ($choice -eq '2') {
            return 'Horizontal'
        }
        Write-Host '1 또는 2를 입력하세요.' -ForegroundColor Yellow
    }
}

function Write-TransactionState([string]$ResolvedGameRoot, [string]$Status, [string]$Detail) {
    $directory = Join-Path $ResolvedGameRoot 'KR_PATCH_BACKUP\v0.15.1-unified-patcher'
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $journal = Join-Path $directory 'transaction.json'
    $temporary = $journal + '.new'
    $value = [ordered]@{
        schema = 'nobu16.kr.unified-patcher-transaction.v1'
        release = $Version
        status = $Status
        detail = $Detail
        castle_name_layout = if ([string]::IsNullOrWhiteSpace($script:SelectedCastleNameLayout)) { $null } else { $script:SelectedCastleNameLayout }
        updated_utc = [DateTime]::UtcNow.ToString('o')
    }
    $json = $value | ConvertTo-Json -Depth 4
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($temporary, $json + [Environment]::NewLine, $encoding)
    if (Test-Path -LiteralPath $journal -PathType Leaf) {
        $rollback = $journal + '.previous'
        if (Test-Path -LiteralPath $rollback -PathType Leaf) {
            Remove-Item -LiteralPath $rollback -Force -ErrorAction Stop
        }
        [System.IO.File]::Replace($temporary, $journal, $rollback)
        if (Test-Path -LiteralPath $rollback -PathType Leaf) {
            Remove-Item -LiteralPath $rollback -Force -ErrorAction Stop
        }
    } else {
        [System.IO.File]::Move($temporary, $journal)
    }
}

function Invoke-StaticPatcher(
    [string]$ResolvedGameRoot,
    [ValidateSet('Apply', 'Restore', 'Status')][string]$Mode,
    [string]$Layout = ''
) {
    $script = Join-Path $PSScriptRoot 'OfficerEditorStaticFix\Invoke-Nobu16StaticPatches.ps1'
    if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
        throw "Missing static patch engine: $script"
    }
    $arguments = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $script, '-GameRoot', $ResolvedGameRoot)
    if (-not [string]::IsNullOrWhiteSpace($Layout)) {
        $arguments += @('-CastleNameLayout', $Layout)
    }
    if ($Mode -eq 'Restore') {
        $arguments += '-Restore'
    } elseif ($Mode -eq 'Status') {
        $arguments += '-Status'
    }
    & powershell.exe @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Static EXE stage failed. exit=$LASTEXITCODE"
    }
}

function Invoke-ResourcePatcher([string]$ResolvedGameRoot, [ValidateSet('Apply', 'Restore', 'Preflight')][string]$Mode, [switch]$CaptureJson) {
    $patcher = Join-Path $PSScriptRoot 'NOBU16_KR_RESOURCE_PATCHER.exe'
    if (-not (Test-Path -LiteralPath $patcher -PathType Leaf)) {
        throw "Missing resource patch engine: $patcher"
    }
    $arguments = @('--game-root', $ResolvedGameRoot, ('--' + $Mode.ToLowerInvariant()), '--yes')
    if ($Mode -eq 'Apply') {
        # The coordinator emits the banner only after both engines and the
        # final target-vector verification have completed.
        $arguments += '--no-banner'
    }
    if ($CaptureJson) {
        $output = @(& $patcher @arguments 2>&1)
        $exitCode = $LASTEXITCODE
        $text = ($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
        if (-not [string]::IsNullOrWhiteSpace($text)) {
            Write-Host $text
        }
        if ($exitCode -ne 0) {
            throw "Resource stage $Mode failed. exit=$exitCode"
        }
        try {
            return ($text | ConvertFrom-Json -ErrorAction Stop)
        } catch {
            throw "Resource stage $Mode did not return its required JSON report: $($_.Exception.Message)"
        }
    }
    & $patcher @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Resource stage $Mode failed. exit=$LASTEXITCODE"
    }
}

function Get-ResourcePreflight([string]$ResolvedGameRoot) {
    $report = Invoke-ResourcePatcher $ResolvedGameRoot 'Preflight' -CaptureJson
    if ($report.action -ne 'preflight' -or $report.result -notin @('ready', 'already_target')) {
        throw 'Resource preflight returned an unsupported state.'
    }
    return $report
}

function Assert-ApplyFinalState([string]$ResolvedGameRoot, [string]$Layout) {
    $resource = Get-ResourcePreflight $ResolvedGameRoot
    if ($resource.result -ne 'already_target') {
        throw 'Resource stage did not reach the complete v0.15.1 target vector.'
    }
    $actualExeHash = Get-Sha256 (Join-Path $ResolvedGameRoot 'NOBU16PK.exe')
    $expectedExeHash = $TargetExeSha256[$Layout]
    if ($actualExeHash -ne $expectedExeHash) {
        throw "Static EXE stage did not reach the $Layout profile target. expected=$expectedExeHash actual=$actualExeHash"
    }
}

function Assert-RestoreFinalState([string]$ResolvedGameRoot) {
    $resource = Get-ResourcePreflight $ResolvedGameRoot
    if ($resource.result -ne 'ready') {
        throw 'Resource stage did not return to the complete pristine vector.'
    }
    $actualExeHash = Get-Sha256 (Join-Path $ResolvedGameRoot 'NOBU16PK.exe')
    if ($actualExeHash -ne $OriginalExeSha256) {
        throw "Static EXE stage did not return to the pristine Steam target. sha256=$actualExeHash"
    }
}

function Show-CompletionBanner {
    $patcher = Join-Path $PSScriptRoot 'NOBU16_KR_RESOURCE_PATCHER.exe'
    & $patcher --show-banner
    if ($LASTEXITCODE -ne 0) {
        throw "Could not display the completion banner. exit=$LASTEXITCODE"
    }
}

try {
    if (($Apply -and $Restore) -or (-not $Apply -and -not $Restore)) {
        throw 'Use exactly one of -Apply or -Restore.'
    }
    $resolvedGameRoot = (Resolve-Path -LiteralPath $GameRoot -ErrorAction Stop).Path
    $executablePath = Join-Path $resolvedGameRoot 'NOBU16PK.exe'
    if (-not (Test-Path -LiteralPath $executablePath -PathType Leaf)) {
        throw "NOBU16PK.exe is missing: $executablePath"
    }

    if ($Apply) {
        $script:SelectedCastleNameLayout = Select-CastleNameLayout $CastleNameLayout
        if ($script:SelectedCastleNameLayout -eq 'Vertical') {
            Write-Host '선택: 1번 세로쓰기 (가로쓰기 및 관련 지도 아이콘 이동 패치 제외)' -ForegroundColor Cyan
        } else {
            Write-Host '선택: 2번 가로쓰기 (관련 지도 아이콘 이동 패치 포함)' -ForegroundColor Cyan
        }
        # Validate both engines before either one writes.  The resource engine
        # additionally checks every required packaged BSDIFF payload hash here.
        $resourceBefore = Get-ResourcePreflight $resolvedGameRoot
        Invoke-StaticPatcher $resolvedGameRoot 'Status' $script:SelectedCastleNameLayout
        $staticBeforeHash = Get-Sha256 $executablePath
        $staticWasOriginal = $staticBeforeHash -eq $OriginalExeSha256
        $staticBeforeLayout = @(
            $TargetExeSha256.Keys |
                Where-Object { $TargetExeSha256[$_] -eq $staticBeforeHash }
        ) | Select-Object -First 1

        Write-TransactionState $resolvedGameRoot 'applying_static' 'Both engines passed preflight.'
        Invoke-StaticPatcher $resolvedGameRoot 'Apply' $script:SelectedCastleNameLayout
        try {
            Write-TransactionState $resolvedGameRoot 'applying_resources' 'Static EXE stage completed.'
            Invoke-ResourcePatcher $resolvedGameRoot 'Apply'
            Assert-ApplyFinalState $resolvedGameRoot $script:SelectedCastleNameLayout
        } catch {
            $resourceError = $_
            if ($staticWasOriginal) {
                try {
                    Write-TransactionState $resolvedGameRoot 'compensating_static_restore' 'Resource stage failed after a pristine EXE was patched.'
                    Invoke-StaticPatcher $resolvedGameRoot 'Restore'
                } catch {
                    Write-TransactionState $resolvedGameRoot 'rollback_failed' "Resource failure: $($resourceError.Exception.Message); static compensation failure: $($_.Exception.Message)"
                    throw
                }
            } elseif (
                -not [string]::IsNullOrWhiteSpace($staticBeforeLayout) -and
                $staticBeforeLayout -ne $script:SelectedCastleNameLayout
            ) {
                try {
                    Write-TransactionState $resolvedGameRoot 'compensating_static_profile' "Resource stage failed after changing the EXE profile from $staticBeforeLayout."
                    Invoke-StaticPatcher $resolvedGameRoot 'Apply' $staticBeforeLayout
                } catch {
                    Write-TransactionState $resolvedGameRoot 'rollback_failed' "Resource failure: $($resourceError.Exception.Message); static profile compensation failure: $($_.Exception.Message)"
                    throw
                }
            }
            Write-TransactionState $resolvedGameRoot 'apply_failed' $resourceError.Exception.Message
            throw $resourceError
        }
        Write-TransactionState $resolvedGameRoot 'applied' "All mandatory resources, installed DLC files, and the $($script:SelectedCastleNameLayout) static profile reached their v0.15.1 targets. Missing DLC files were skipped."
        Show-CompletionBanner
        if ($script:SelectedCastleNameLayout -eq 'Vertical') {
            Write-Host '성이름: 세로쓰기' -ForegroundColor Green
        } else {
            Write-Host '성이름: 가로쓰기' -ForegroundColor Green
        }
        Write-Host '패치 완료! Steam에서 게임을 시작하세요.' -ForegroundColor Green
    } else {
        # Resource restoration happens first.  If the EXE restoration then
        # fails, a resource target that this operation just removed is restored
        # so a normal retry is not left in an avoidable mixed state.
        $resourceBefore = Get-ResourcePreflight $resolvedGameRoot
        $resourceHadTargets = @($resourceBefore.installed_state.PSObject.Properties.Value) -contains 'target'
        Invoke-StaticPatcher $resolvedGameRoot 'Status'

        Write-TransactionState $resolvedGameRoot 'restoring_resources' 'Both engines passed preflight.'
        Invoke-ResourcePatcher $resolvedGameRoot 'Restore'
        try {
            Write-TransactionState $resolvedGameRoot 'restoring_static' 'Resource stage returned to the pristine vector.'
            Invoke-StaticPatcher $resolvedGameRoot 'Restore'
            Assert-RestoreFinalState $resolvedGameRoot
        } catch {
            $restoreError = $_
            if ($resourceHadTargets) {
                try {
                    Write-TransactionState $resolvedGameRoot 'compensating_resource_apply' 'Static restore failed after resources were restored.'
                    Invoke-ResourcePatcher $resolvedGameRoot 'Apply'
                } catch {
                    Write-TransactionState $resolvedGameRoot 'rollback_failed' "Static restore failure: $($restoreError.Exception.Message); resource compensation failure: $($_.Exception.Message)"
                    throw
                }
            }
            Write-TransactionState $resolvedGameRoot 'restore_failed' $restoreError.Exception.Message
            throw $restoreError
        }
        Write-TransactionState $resolvedGameRoot 'restored' 'All present patched resources and the static EXE returned to pristine Steam JP 1.1.7. Missing DLC files were skipped.'
        Write-Host 'Korean patch restored to the pristine Steam JP 1.1.7 state.' -ForegroundColor Green
    }
    exit 0
} catch {
    Write-Host ''
    Write-Host ('Failed: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
