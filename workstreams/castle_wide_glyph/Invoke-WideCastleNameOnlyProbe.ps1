param(
    [ValidateSet('Status', 'Apply', 'Restore')]
    [string]$Action = 'Status'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$gameRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$workRoot = Join-Path $gameRoot 'KR_PATCH_WORK'
$candidateRoot = Join-Path $PSScriptRoot 'private\wrapper_candidate'
$backupRoot = Join-Path $workRoot 'backups\single_glyph_castle_name_only_wrapper'
$lockPath = Join-Path $backupRoot 'operation.lock'
$journalPath = Join-Path $backupRoot 'journal.json'

$targets = @(
    [ordered]@{
        label = 'SC msgdata'
        path = Join-Path $gameRoot 'MSG_PK\SC\msgdata.bin'
        stock_hash = '0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E'
        probe_hash = '165353713703A2A1D72C24D6C9A7D5709F21FA3D2B641993BE786BA14B2B17CC'
        probe = Join-Path $candidateRoot 'MSG_PK\SC\msgdata.bin'
        backup = Join-Path $backupRoot 'msgdata.SC.stock.bin'
    },
    [ordered]@{
        label = 'SC font archive'
        path = Join-Path $gameRoot 'RES_SC\res_lang.bin'
        stock_hash = '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99'
        probe_hash = 'AFBB287B5418FBCB44B083F7D77E5F53426AE7E1AB23C6B69F17EC98E0EB7258'
        probe = Join-Path $candidateRoot 'RES_SC\res_lang.bin'
        backup = Join-Path $backupRoot 'res_lang.SC.stock.bin'
    }
)

function Get-Sha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Assert-Hash([string]$Path, [string]$Expected, [string]$Label) {
    $actual = Get-Sha256 $Path
    if ($null -eq $actual) { throw "Missing $Label`: $Path" }
    if ($actual -ne $Expected) {
        throw "$Label hash mismatch. expected=$Expected actual=$actual path=$Path"
    }
}

function Assert-WorkspacePath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    $prefix = $gameRoot.TrimEnd('\') + '\'
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing path outside the game workspace: $full"
    }
}

function Get-GameRelativePath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    $prefix = $gameRoot.TrimEnd('\') + '\'
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing path outside the game workspace: $full"
    }
    return $full.Substring($prefix.Length)
}

function Assert-NoGameProcess {
    $names = @(
        'NOBU16', 'NOBU16_SD', 'NOBU16PK', 'NOBU16PK_SD',
        'NOBU16PK_EN', 'NOBU16PK_EN_SD', 'NOBU16_Launcher'
    )
    $running = @(Get-Process -Name $names -ErrorAction SilentlyContinue)
    if ($running.Count -gt 0) {
        $summary = ($running | ForEach-Object { "$($_.ProcessName):$($_.Id)" }) -join ', '
        throw "Close every NOBU16 process before changing disk resources. running=$summary"
    }
}

function Get-State([System.Collections.IDictionary]$Spec) {
    $hash = Get-Sha256 $Spec.path
    if ($hash -eq $Spec.stock_hash) { return 'stock' }
    if ($hash -eq $Spec.probe_hash) { return 'probe' }
    return 'unknown'
}

function Write-Journal([string]$Phase, [int]$Completed) {
    $record = [ordered]@{
        schema = 1
        architecture = 'file-only-offline'
        purpose = 'single-wide-glyph-castle-name-only-runtime-probe'
        executable_modified = $false
        registry_modified = $false
        launches_game = $false
        phase = $Phase
        completed_targets = $Completed
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        files = @($targets | ForEach-Object {
            [ordered]@{
                path = Get-GameRelativePath $_.path
                installed_sha256 = Get-Sha256 $_.path
                stock_sha256 = $_.stock_hash
                probe_sha256 = $_.probe_hash
            }
        })
    }
    $stage = $journalPath + '.new'
    [IO.File]::WriteAllText(
        $stage,
        ($record | ConvertTo-Json -Depth 8),
        (New-Object Text.UTF8Encoding($false))
    )
    Move-Item -LiteralPath $stage -Destination $journalPath -Force
}

function New-VerifiedBackup([System.Collections.IDictionary]$Spec) {
    Assert-WorkspacePath $Spec.path
    Assert-WorkspacePath $Spec.backup
    if (Test-Path -LiteralPath $Spec.backup -PathType Leaf) {
        Assert-Hash $Spec.backup $Spec.stock_hash "$($Spec.label) existing stock backup"
        return
    }
    Assert-Hash $Spec.path $Spec.stock_hash "$($Spec.label) installed stock source"
    $stage = $Spec.backup + '.new'
    Copy-Item -LiteralPath $Spec.path -Destination $stage -Force
    Assert-Hash $stage $Spec.stock_hash "$($Spec.label) staged stock backup"
    Move-Item -LiteralPath $stage -Destination $Spec.backup
    Assert-Hash $Spec.backup $Spec.stock_hash "$($Spec.label) committed stock backup"
}

function Invoke-AtomicReplace(
    [string]$Source,
    [string]$ExpectedHash,
    [string]$Target,
    [string]$Label
) {
    Assert-WorkspacePath $Source
    Assert-WorkspacePath $Target
    Assert-Hash $Source $ExpectedHash "$Label source"
    $stage = $Target + '.n16kr.wide-castle.new'
    $swap = $Target + '.n16kr.wide-castle.swap.bak'
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Force }
    if (Test-Path -LiteralPath $swap) { Remove-Item -LiteralPath $swap -Force }
    Copy-Item -LiteralPath $Source -Destination $stage -Force
    Assert-Hash $stage $ExpectedHash "$Label staged file"
    [IO.File]::Replace($stage, $Target, $swap, $true)
    try {
        Assert-Hash $Target $ExpectedHash "$Label installed file"
    } catch {
        if (Test-Path -LiteralPath $swap -PathType Leaf) {
            [IO.File]::Replace($swap, $Target, $null, $true)
        }
        throw
    }
    if (Test-Path -LiteralPath $swap) { Remove-Item -LiteralPath $swap -Force }
}

function Show-Status {
    [pscustomobject]@{
        architecture = 'file-only-offline'
        purpose = 'single-wide-glyph-castle-name-only-runtime-probe'
        executable_modified = $false
        registry_modified = $false
        launches_game = $false
        test_castle_id = 9168
        proxy_codepoint = 'U+D792'
        shared_castle_suffix_changed = $false
        targets = @($targets | ForEach-Object {
            [ordered]@{
                path = Get-GameRelativePath $_.path
                state = Get-State $_
                sha256 = Get-Sha256 $_.path
            }
        })
    } | ConvertTo-Json -Depth 8
}

if ($Action -eq 'Status') {
    Show-Status
    exit 0
}

Assert-NoGameProcess
[IO.Directory]::CreateDirectory($backupRoot) | Out-Null
$lock = $null
try {
    $lock = [IO.File]::Open(
        $lockPath,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None
    )

    foreach ($spec in $targets) {
        $state = Get-State $spec
        if ($state -eq 'unknown') {
            throw "Unknown installed hash; refusing to overwrite $($spec.path)"
        }
    }

    if ($Action -eq 'Restore') {
        foreach ($spec in $targets) { New-VerifiedBackup $spec }
        Write-Journal 'restoring' 0
        $completed = 0
        for ($index = $targets.Count - 1; $index -ge 0; $index--) {
            $spec = $targets[$index]
            if ((Get-State $spec) -eq 'probe') {
                Invoke-AtomicReplace $spec.backup $spec.stock_hash $spec.path "$($spec.label) restore"
            }
            $completed++
            Write-Journal 'restoring' $completed
        }
        Write-Journal 'stock' $targets.Count
        Show-Status
        exit 0
    }

    foreach ($spec in $targets) {
        Assert-Hash $spec.path $spec.stock_hash "$($spec.label) pre-apply stock"
        Assert-Hash $spec.probe $spec.probe_hash "$($spec.label) probe candidate"
        New-VerifiedBackup $spec
    }

    Write-Journal 'applying' 0
    $completed = 0
    try {
        foreach ($spec in $targets) {
            Invoke-AtomicReplace $spec.probe $spec.probe_hash $spec.path "$($spec.label) apply"
            $completed++
            Write-Journal 'applying' $completed
        }
    } catch {
        for ($index = $completed - 1; $index -ge 0; $index--) {
            $spec = $targets[$index]
            Invoke-AtomicReplace $spec.backup $spec.stock_hash $spec.path "$($spec.label) automatic-rollback"
        }
        Write-Journal 'stock-after-automatic-rollback' $completed
        throw
    }
    Write-Journal 'probe-installed' $targets.Count
    Show-Status
} finally {
    if ($null -ne $lock) { $lock.Dispose() }
    if (Test-Path -LiteralPath $lockPath) { Remove-Item -LiteralPath $lockPath -Force }
}
