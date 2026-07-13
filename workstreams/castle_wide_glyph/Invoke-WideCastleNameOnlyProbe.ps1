param(
    [ValidateSet('Status', 'ApplyMessageOnly', 'ApplyFontOnly', 'ApplyBoth', 'Restore')]
    [string]$Action = 'Status'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# This diagnostic deliberately has no game-launch option.  It changes only the
# two resource files listed below and accepts only their pinned stock/probe hashes.
$gameRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$workRoot = Join-Path $gameRoot 'KR_PATCH_WORK'
$candidateRoot = Join-Path $PSScriptRoot 'private\wrapper_candidate'
$backupRoot = Join-Path $workRoot 'backups\single_glyph_castle_ab_probe'
$lockPath = Join-Path $backupRoot 'operation.lock'
$journalPath = Join-Path $backupRoot 'journal.json'
$journalSchema = 'nobu16.kr.wide-castle-ab-journal.v2'

$targets = @(
    [ordered]@{
        key = 'message'
        label = 'SC msgdata'
        path = Join-Path $gameRoot 'MSG_PK\SC\msgdata.bin'
        stock_hash = '0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E'
        probe_hash = '165353713703A2A1D72C24D6C9A7D5709F21FA3D2B641993BE786BA14B2B17CC'
        probe = Join-Path $candidateRoot 'MSG_PK\SC\msgdata.bin'
        backup = Join-Path $backupRoot 'msgdata.SC.stock.bin'
    },
    [ordered]@{
        key = 'font'
        label = 'SC font archive'
        path = Join-Path $gameRoot 'RES_SC\res_lang.bin'
        stock_hash = '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99'
        probe_hash = 'AFBB287B5418FBCB44B083F7D77E5F53426AE7E1AB23C6B69F17EC98E0EB7258'
        probe = Join-Path $candidateRoot 'RES_SC\res_lang.bin'
        backup = Join-Path $backupRoot 'res_lang.SC.stock.bin'
    }
)

$desiredByAction = @{
    ApplyMessageOnly = @{ message = 'probe'; font = 'stock' }
    ApplyFontOnly = @{ message = 'stock'; font = 'probe' }
    ApplyBoth = @{ message = 'probe'; font = 'probe' }
    Restore = @{ message = 'stock'; font = 'stock' }
}

function Get-Sha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Assert-Hash([string]$Path, [string]$Expected, [string]$Label) {
    $actual = Get-Sha256 $Path
    if ($null -eq $actual) { throw "Missing ${Label}: $Path" }
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
    return $full.Substring($prefix.Length).Replace('\', '/')
}

function Assert-NoGameProcess {
    $running = @(
        Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $_.ProcessName -like 'NOBU16*' }
    )
    if ($running.Count -gt 0) {
        $summary = ($running | ForEach-Object { "$($_.ProcessName):$($_.Id)" }) -join ', '
        throw "Close every NOBU16 process before using this diagnostic. running=$summary"
    }
}

function Get-TargetState([System.Collections.IDictionary]$Spec) {
    $hash = Get-Sha256 $Spec.path
    if ($hash -eq $Spec.stock_hash) { return 'stock' }
    if ($hash -eq $Spec.probe_hash) { return 'probe' }
    return 'unknown'
}

function Get-InstalledStates {
    $states = @{}
    foreach ($spec in $targets) { $states[$spec.key] = Get-TargetState $spec }
    return $states
}

function Assert-KnownInstalledStates([hashtable]$States) {
    foreach ($spec in $targets) {
        if ($States[$spec.key] -eq 'unknown') {
            $actual = Get-Sha256 $spec.path
            if ($null -eq $actual) { $actual = '<missing>' }
            throw "Unknown installed hash; refusing $Action. path=$($spec.path) sha256=$actual"
        }
    }
}

function Get-CombinationName([hashtable]$States) {
    if ($States.message -eq 'stock' -and $States.font -eq 'stock') { return 'stock' }
    if ($States.message -eq 'probe' -and $States.font -eq 'stock') { return 'message-only' }
    if ($States.message -eq 'stock' -and $States.font -eq 'probe') { return 'font-only' }
    if ($States.message -eq 'probe' -and $States.font -eq 'probe') { return 'both' }
    return 'unknown'
}

function Get-SourceState([System.Collections.IDictionary]$Spec, [string]$State) {
    if ($State -eq 'stock') {
        return [ordered]@{ path = $Spec.backup; hash = $Spec.stock_hash }
    }
    if ($State -eq 'probe') {
        return [ordered]@{ path = $Spec.probe; hash = $Spec.probe_hash }
    }
    throw "Unsupported source state: $State"
}

function Get-CandidateStatus([System.Collections.IDictionary]$Spec) {
    $actual = Get-Sha256 $Spec.probe
    if ($null -eq $actual) { return 'missing-private-candidate' }
    if ($actual -eq $Spec.probe_hash) { return 'verified' }
    return 'hash-mismatch'
}

function Get-BackupStatus([System.Collections.IDictionary]$Spec) {
    $actual = Get-Sha256 $Spec.backup
    if ($null -eq $actual) { return 'missing' }
    if ($actual -eq $Spec.stock_hash) { return 'verified' }
    return 'hash-mismatch'
}

function Read-ValidatedJournal {
    if (-not (Test-Path -LiteralPath $journalPath -PathType Leaf)) { return $null }
    try {
        $journal = [IO.File]::ReadAllText($journalPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    } catch {
        throw "Journal is unreadable; refusing to continue: $journalPath"
    }
    if ($journal.schema -ne $journalSchema) {
        throw "Unknown journal schema; refusing to continue: $($journal.schema)"
    }
    $expectedPaths = @($targets | ForEach-Object { Get-GameRelativePath $_.path })
    $actualPaths = @($journal.files | ForEach-Object { [string]$_.path })
    if ($actualPaths.Count -ne 2 -or $expectedPaths.Count -ne 2) {
        throw 'Journal target count is not exactly two; refusing to continue.'
    }
    foreach ($expectedPath in $expectedPaths) {
        if ($actualPaths -notcontains $expectedPath) {
            throw "Journal contains an unexpected target; refusing to continue: $expectedPath"
        }
    }
    return $journal
}

function Write-Journal(
    [string]$Phase,
    [string]$RequestedAction,
    [hashtable]$BeforeStates,
    [hashtable]$DesiredStates,
    [int]$Completed,
    [string]$RecoveryMode
) {
    $current = Get-InstalledStates
    $record = [ordered]@{
        schema = $journalSchema
        architecture = 'file-only-offline'
        purpose = 'single-wide-glyph-castle-ab-runtime-diagnostic'
        executable_modified = $false
        registry_modified = $false
        launches_game = $false
        process_memory_access = $false
        fixed_target_count = 2
        phase = $Phase
        requested_action = $RequestedAction
        recovery_mode = $RecoveryMode
        completed_replacements = $Completed
        before_combination = Get-CombinationName $BeforeStates
        desired_combination = Get-CombinationName $DesiredStates
        installed_combination = Get-CombinationName $current
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        files = @($targets | ForEach-Object {
            [ordered]@{
                key = $_.key
                path = Get-GameRelativePath $_.path
                before_state = $BeforeStates[$_.key]
                desired_state = $DesiredStates[$_.key]
                installed_state = $current[$_.key]
                installed_sha256 = Get-Sha256 $_.path
                stock_sha256 = $_.stock_hash
                probe_sha256 = $_.probe_hash
                stock_backup_sha256 = Get-Sha256 $_.backup
            }
        })
    }
    $stage = $journalPath + '.new'
    [IO.File]::WriteAllText(
        $stage,
        ($record | ConvertTo-Json -Depth 10) + "`n",
        (New-Object Text.UTF8Encoding($false))
    )
    Move-Item -LiteralPath $stage -Destination $journalPath -Force
}

function New-VerifiedStockBackup([System.Collections.IDictionary]$Spec) {
    Assert-WorkspacePath $Spec.path
    Assert-WorkspacePath $Spec.backup
    if (Test-Path -LiteralPath $Spec.backup -PathType Leaf) {
        Assert-Hash $Spec.backup $Spec.stock_hash "$($Spec.label) existing stock backup"
        return
    }
    if ((Get-TargetState $Spec) -ne 'stock') {
        throw "Verified stock backup is missing while $($Spec.label) is not stock; refusing to continue."
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
    $stage = $Target + '.n16kr.wide-castle-ab.new'
    $swap = $Target + '.n16kr.wide-castle-ab.swap.bak'
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

function Show-Status([hashtable]$States, [object]$Journal) {
    $journalSummary = if ($null -eq $Journal) {
        [ordered]@{ present = $false; phase = $null; recovery_required = $false }
    } else {
        [ordered]@{
            present = $true
            phase = [string]$Journal.phase
            requested_action = [string]$Journal.requested_action
            installed_combination_at_last_write = [string]$Journal.installed_combination
            recovery_required = ([string]$Journal.phase -ne 'stable')
        }
    }
    [pscustomobject]@{
        architecture = 'file-only-offline'
        purpose = 'single-wide-glyph-castle-ab-runtime-diagnostic'
        executable_modified = $false
        registry_modified = $false
        launches_game = $false
        process_memory_access = $false
        fixed_target_count = 2
        installed_combination = Get-CombinationName $States
        test_castle_id = 9168
        proxy_codepoint = 'U+D792'
        shared_castle_suffix_changed = $false
        journal = $journalSummary
        targets = @($targets | ForEach-Object {
            [ordered]@{
                key = $_.key
                path = Get-GameRelativePath $_.path
                installed_state = $States[$_.key]
                installed_sha256 = Get-Sha256 $_.path
                stock_sha256 = $_.stock_hash
                probe_sha256 = $_.probe_hash
                private_candidate_status = Get-CandidateStatus $_
                stock_backup_status = Get-BackupStatus $_
            }
        })
    } | ConvertTo-Json -Depth 10
}

Assert-NoGameProcess
$initialStates = Get-InstalledStates
Assert-KnownInstalledStates $initialStates
$existingJournal = Read-ValidatedJournal

if ($Action -eq 'Status') {
    Show-Status $initialStates $existingJournal
    exit 0
}

[IO.Directory]::CreateDirectory($backupRoot) | Out-Null
$lock = $null
try {
    $lock = [IO.File]::Open(
        $lockPath,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None
    )

    # Re-read after acquiring the lock so the transaction is based on the exact
    # hashes it will replace.  A non-stable prior journal is reconciled from these
    # known hashes; no inferred or unknown state is ever accepted.
    $beforeStates = Get-InstalledStates
    Assert-KnownInstalledStates $beforeStates
    $priorJournal = Read-ValidatedJournal
    $recoveryMode = if ($null -ne $priorJournal -and [string]$priorJournal.phase -ne 'stable') {
        'reconcile-known-installed-hashes'
    } else {
        'none'
    }

    $desiredStates = @{
        message = [string]$desiredByAction[$Action].message
        font = [string]$desiredByAction[$Action].font
    }

    # Both verified stock backups are mandatory before the first target changes.
    # The probe source is also verified whenever it is needed either for the
    # requested state or for automatic rollback to the starting state.
    foreach ($spec in $targets) {
        New-VerifiedStockBackup $spec
        # Restore is deliberately independent of the private probe files: once a
        # verified stock backup exists, recovery must remain possible even if the
        # local build directory was removed.  Apply actions also verify their
        # starting probe source so they can roll back to the exact starting A/B
        # combination if a later replacement fails.
        $neededStates = if ($Action -eq 'Restore') {
            @('stock')
        } else {
            @($beforeStates[$spec.key], $desiredStates[$spec.key]) | Sort-Object -Unique
        }
        foreach ($neededState in $neededStates) {
            $source = Get-SourceState $spec $neededState
            Assert-Hash $source.path $source.hash "$($spec.label) $neededState transaction source"
        }
    }

    Write-Journal 'changing' $Action $beforeStates $desiredStates 0 $recoveryMode
    $completed = 0
    try {
        foreach ($spec in $targets) {
            if ($beforeStates[$spec.key] -eq $desiredStates[$spec.key]) { continue }
            $source = Get-SourceState $spec $desiredStates[$spec.key]
            Invoke-AtomicReplace $source.path $source.hash $spec.path "$($spec.label) $Action"
            $completed++
            Write-Journal 'changing' $Action $beforeStates $desiredStates $completed $recoveryMode
        }
        $finalStates = Get-InstalledStates
        Assert-KnownInstalledStates $finalStates
        foreach ($spec in $targets) {
            if ($finalStates[$spec.key] -ne $desiredStates[$spec.key]) {
                throw "$($spec.label) did not reach its requested state."
            }
        }
        Write-Journal 'stable' $Action $beforeStates $desiredStates $completed $recoveryMode
    } catch {
        $operationError = $_
        $rollbackErrors = [Collections.Generic.List[string]]::new()
        $failurePhase = if ($Action -eq 'Restore') { 'restore-convergence' } else { 'automatic-rollback' }
        try { Write-Journal $failurePhase $Action $beforeStates $desiredStates $completed $recoveryMode } catch {
            $rollbackErrors.Add("journal: $($_.Exception.Message)")
        }
        for ($index = $targets.Count - 1; $index -ge 0; $index--) {
            $spec = $targets[$index]
            try {
                $currentState = Get-TargetState $spec
                if ($currentState -eq 'unknown') {
                    throw "installed hash became unknown: $($spec.path)"
                }
                $recoveryState = if ($Action -eq 'Restore') { 'stock' } else { $beforeStates[$spec.key] }
                if ($currentState -ne $recoveryState) {
                    $source = Get-SourceState $spec $recoveryState
                    $recoveryLabel = if ($Action -eq 'Restore') { 'restore convergence' } else { 'automatic rollback' }
                    Invoke-AtomicReplace $source.path $source.hash $spec.path "$($spec.label) $recoveryLabel"
                }
            } catch {
                $rollbackErrors.Add("$($spec.key): $($_.Exception.Message)")
            }
        }
        if ($rollbackErrors.Count -eq 0) {
            $recoveredStates = if ($Action -eq 'Restore') {
                @{ message = 'stock'; font = 'stock' }
            } else {
                $beforeStates
            }
            $recoveryAction = if ($Action -eq 'Restore') { 'RestoreConvergence' } else { 'AutomaticRollback' }
            try { Write-Journal 'stable' $recoveryAction $recoveredStates $recoveredStates 0 $recoveryMode } catch {
                $rollbackErrors.Add("final journal: $($_.Exception.Message)")
            }
        }
        if ($rollbackErrors.Count -gt 0) {
            throw "Operation failed: $($operationError.Exception.Message); rollback errors: $($rollbackErrors -join ' | ')"
        }
        throw $operationError
    }

    $installedStates = Get-InstalledStates
    Show-Status $installedStates (Read-ValidatedJournal)
} finally {
    if ($null -ne $lock) { $lock.Dispose() }
    if (Test-Path -LiteralPath $lockPath) { Remove-Item -LiteralPath $lockPath -Force }
}
