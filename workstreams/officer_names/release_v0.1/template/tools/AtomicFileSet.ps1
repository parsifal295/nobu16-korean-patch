Set-StrictMode -Version Latest

function Get-AtomicSha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Get-ExactKnownVectorId {
    param(
        [Parameter(Mandatory = $true)][string[]]$ActualHashes,
        [Parameter(Mandatory = $true)][object[]]$KnownVectors
    )
    if ($ActualHashes.Count -ne 4 -or $KnownVectors.Count -lt 2) {
        throw 'Known hash-vector contract is malformed.'
    }
    $ids = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    $vectors = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($vector in $KnownVectors) {
        if ([string]::IsNullOrWhiteSpace([string]$vector.id) -or -not $ids.Add([string]$vector.id)) {
            throw 'Known hash-vector ids are missing, duplicate, or case-colliding.'
        }
        [string[]]$hashes = @($vector.hashes | ForEach-Object { ([string]$_).ToUpperInvariant() })
        if ($hashes.Count -ne 4 -or @($hashes | Where-Object { $_ -notmatch '\A[0-9A-F]{64}\z' }).Count -ne 0) {
            throw "Known hash vector $($vector.id) is malformed."
        }
        $key = $hashes -join ','
        if (-not $vectors.Add($key)) {
            throw "Known hash vector $($vector.id) duplicates another vector."
        }
        $matches = $true
        for ($index = 0; $index -lt 4; $index++) {
            if ($ActualHashes[$index].ToUpperInvariant() -ne $hashes[$index]) { $matches = $false; break }
        }
        if ($matches) { return [string]$vector.id }
    }
    return $null
}

function Assert-KnownHashVector {
    param(
        [Parameter(Mandatory = $true)][string[]]$ActualHashes,
        [Parameter(Mandatory = $true)][object[]]$KnownVectors,
        [string]$Label = 'installed resource vector'
    )
    $id = Get-ExactKnownVectorId $ActualHashes $KnownVectors
    if ([string]::IsNullOrWhiteSpace($id)) {
        throw "$Label is not one of the exact pinned four-resource vectors."
    }
    return $id
}

function Remove-AtomicTemporary {
    param([string[]]$Paths)
    foreach ($path in @($Paths)) {
        if ([string]::IsNullOrWhiteSpace($path)) { continue }
        try {
            if (Test-Path -LiteralPath $path -PathType Leaf) {
                $item = Get-Item -LiteralPath $path -Force
                if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                    Write-Warning "Refusing to remove a reparse-point temporary file: $path"
                    continue
                }
                [System.IO.File]::Delete($path)
            }
        }
        catch {
            Write-Warning "Could not remove transaction temporary file: $path"
        }
    }
}

function Write-AtomicJournal {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value
    )
    $parent = Split-Path -Parent $Path
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $temporary = Join-Path $parent ('.' + [System.IO.Path]::GetFileName($Path) + '.tmp.' + [Guid]::NewGuid().ToString('N'))
    $discard = Join-Path $parent ('.' + [System.IO.Path]::GetFileName($Path) + '.old.' + [Guid]::NewGuid().ToString('N'))
    try {
        $json = ConvertTo-Json -InputObject $Value -Depth 12
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($temporary, $json + "`n", $encoding)
        $stream = [System.IO.File]::Open($temporary, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        try { $stream.Flush($true) } finally { $stream.Dispose() }
        if (Test-Path -LiteralPath $Path -PathType Leaf) {
            [System.IO.File]::Replace($temporary, $Path, $discard, $true)
        }
        else {
            [System.IO.File]::Move($temporary, $Path)
        }
    }
    finally {
        Remove-AtomicTemporary @($temporary, $discard)
    }
}

function Assert-AtomicItemSet {
    param([Parameter(Mandatory = $true)][object[]]$Items)
    if (@($Items).Count -ne 4) {
        throw 'A file-only officer-name transaction must contain exactly four resources.'
    }
    $ids = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    $destinations = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($item in $Items) {
        foreach ($name in @('Id', 'Destination', 'Staged', 'Rollback', 'BeforeSha256', 'AfterSha256')) {
            if ($null -eq $item.PSObject.Properties[$name] -or
                [string]::IsNullOrWhiteSpace([string]$item.$name)) {
                throw "Transaction item is missing $name."
            }
        }
        if (-not $ids.Add([string]$item.Id)) {
            throw "Duplicate transaction resource id: $($item.Id)"
        }
        $destination = [System.IO.Path]::GetFullPath([string]$item.Destination)
        $staged = [System.IO.Path]::GetFullPath([string]$item.Staged)
        $rollback = [System.IO.Path]::GetFullPath([string]$item.Rollback)
        if (-not $destinations.Add($destination)) {
            throw "Duplicate or case-colliding transaction destination: $destination"
        }
        $destinationParent = [System.IO.Path]::GetFullPath(
            [System.IO.Path]::GetDirectoryName($destination)).TrimEnd('\')
        $stagedParent = [System.IO.Path]::GetFullPath(
            [System.IO.Path]::GetDirectoryName($staged)).TrimEnd('\')
        $rollbackParent = [System.IO.Path]::GetFullPath(
            [System.IO.Path]::GetDirectoryName($rollback)).TrimEnd('\')
        if (-not [string]::Equals($stagedParent, $destinationParent, [StringComparison]::OrdinalIgnoreCase) -or
            -not [string]::Equals($rollbackParent, $destinationParent, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Transaction temporary paths must be siblings of the destination: $destination"
        }
        $temporaryPrefix = '.' + [System.IO.Path]::GetFileName($destination) + '.krpatch.'
        if (-not [System.IO.Path]::GetFileName($staged).StartsWith($temporaryPrefix, [StringComparison]::Ordinal) -or
            -not [System.IO.Path]::GetFileName($rollback).StartsWith($temporaryPrefix, [StringComparison]::Ordinal)) {
            throw "Transaction temporary names do not match the destination-specific prefix: $destination"
        }
        if ($destination -eq $staged -or $destination -eq $rollback -or $staged -eq $rollback) {
            throw "Transaction paths collide for $($item.Id)."
        }
        foreach ($candidate in @($destination, $staged, $rollback)) {
            if (Test-Path -LiteralPath $candidate) {
                $candidateItem = Get-Item -LiteralPath $candidate -Force
                if (($candidateItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                    throw "Transaction path must not be a symbolic link, junction, mount point, or other reparse point: $candidate"
                }
            }
        }
        if ([string]$item.BeforeSha256 -notmatch '\A[0-9A-Fa-f]{64}\z' -or
            [string]$item.AfterSha256 -notmatch '\A[0-9A-Fa-f]{64}\z') {
            throw "Transaction hash is malformed for $($item.Id)."
        }
    }
}

function Assert-AtomicVector {
    param(
        [Parameter(Mandatory = $true)][object[]]$Items,
        [Parameter(Mandatory = $true)][int]$ReplacedCount,
        [Parameter(Mandatory = $true)][string]$Label
    )
    for ($index = 0; $index -lt $Items.Count; $index++) {
        $expected = if ($index -lt $ReplacedCount) {
            ([string]$Items[$index].AfterSha256).ToUpperInvariant()
        }
        else {
            ([string]$Items[$index].BeforeSha256).ToUpperInvariant()
        }
        $actual = Get-AtomicSha256 ([string]$Items[$index].Destination)
        if ($actual -ne $expected) {
            throw "$Label vector mismatch for $($Items[$index].Id): $actual, expected $expected"
        }
    }
}

function Test-AtomicExclusiveAccess {
    param([Parameter(Mandatory = $true)][object[]]$Items)
    $handles = New-Object 'System.Collections.Generic.List[System.IO.FileStream]'
    try {
        foreach ($item in $Items) {
            $handles.Add([System.IO.File]::Open(
                [string]$item.Destination,
                [System.IO.FileMode]::Open,
                [System.IO.FileAccess]::Read,
                [System.IO.FileShare]::None))
        }
    }
    catch {
        throw "One or more game resources are in use. Close the game and launcher, then retry: $($_.Exception.Message)"
    }
    finally {
        foreach ($handle in $handles) { $handle.Dispose() }
    }
}

function New-AtomicJournalValue {
    param(
        [Parameter(Mandatory = $true)][object[]]$Items,
        [Parameter(Mandatory = $true)][string]$Operation
    )
    $journalItems = @()
    foreach ($item in $Items) {
        $journalItems += [ordered]@{
            id = [string]$item.Id
            destination = [System.IO.Path]::GetFullPath([string]$item.Destination)
            staged = [System.IO.Path]::GetFullPath([string]$item.Staged)
            rollback = [System.IO.Path]::GetFullPath([string]$item.Rollback)
            before_sha256 = ([string]$item.BeforeSha256).ToUpperInvariant()
            after_sha256 = ([string]$item.AfterSha256).ToUpperInvariant()
        }
    }
    return [ordered]@{
        schema = 'nobu16.file-only-four-resource-transaction.v1'
        transaction_id = [Guid]::NewGuid().ToString('N')
        operation = $Operation
        status = 'prepared'
        replaced_count = 0
        prepared_utc = [DateTime]::UtcNow.ToString('o')
        items = $journalItems
    }
}

function Invoke-AtomicFileSetTransaction {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][object[]]$Items,
        [Parameter(Mandatory = $true)][string]$JournalPath,
        [Parameter(Mandatory = $true)][ValidateSet('normalize-stock', 'apply', 'restore', 'rollback-input')][string]$Operation,
        [ValidateRange(-1, 3)][int]$FailureAfterReplaceCount = -1
    )

    Assert-AtomicItemSet $Items
    foreach ($item in $Items) {
        if (-not (Test-Path -LiteralPath ([string]$item.Destination) -PathType Leaf)) {
            throw "Transaction destination is missing: $($item.Destination)"
        }
        if (-not (Test-Path -LiteralPath ([string]$item.Staged) -PathType Leaf)) {
            throw "Transaction staged file is missing: $($item.Staged)"
        }
        if (Test-Path -LiteralPath ([string]$item.Rollback)) {
            throw "Transaction rollback path already exists: $($item.Rollback)"
        }
        if ((Get-AtomicSha256 ([string]$item.Destination)) -ne ([string]$item.BeforeSha256).ToUpperInvariant()) {
            throw "Transaction input hash mismatch for $($item.Id)."
        }
        if ((Get-AtomicSha256 ([string]$item.Staged)) -ne ([string]$item.AfterSha256).ToUpperInvariant()) {
            throw "Transaction staged hash mismatch for $($item.Id)."
        }
    }
    Test-AtomicExclusiveAccess $Items

    $journal = New-AtomicJournalValue $Items $Operation
    Write-AtomicJournal $JournalPath $journal
    $replacedCount = 0
    try {
        for ($index = 0; $index -lt $Items.Count; $index++) {
            if ($FailureAfterReplaceCount -ge 0 -and $replacedCount -eq $FailureAfterReplaceCount) {
                throw "Injected transaction failure after $replacedCount replacements."
            }
            Assert-AtomicVector $Items $replacedCount "$Operation pre-replace"
            Test-AtomicExclusiveAccess $Items
            $item = $Items[$index]
            [System.IO.File]::Replace(
                [string]$item.Staged,
                [string]$item.Destination,
                [string]$item.Rollback,
                $true)
            $replacedCount++
            if ((Get-AtomicSha256 ([string]$item.Destination)) -ne ([string]$item.AfterSha256).ToUpperInvariant() -or
                (Get-AtomicSha256 ([string]$item.Rollback)) -ne ([string]$item.BeforeSha256).ToUpperInvariant()) {
                throw "Transaction replacement verification failed for $($item.Id)."
            }
            $journal.status = 'replacing'
            $journal.replaced_count = $replacedCount
            Write-AtomicJournal $JournalPath $journal
        }
        Assert-AtomicVector $Items 4 "$Operation commit"
        $journal.status = 'committed'
        $journal.committed_utc = [DateTime]::UtcNow.ToString('o')
        Write-AtomicJournal $JournalPath $journal
        Remove-AtomicTemporary @($Items | ForEach-Object { [string]$_.Rollback })
        return $journal.transaction_id
    }
    catch {
        $originalError = $_.Exception.Message
        $rollbackErrors = New-Object 'System.Collections.Generic.List[string]'
        for ($index = $replacedCount - 1; $index -ge 0; $index--) {
            $item = $Items[$index]
            $discard = Join-Path ([System.IO.Path]::GetDirectoryName([string]$item.Destination)) (
                '.' + [System.IO.Path]::GetFileName([string]$item.Destination) + '.discard.' + [Guid]::NewGuid().ToString('N'))
            try {
                if (-not (Test-Path -LiteralPath ([string]$item.Rollback) -PathType Leaf) -or
                    (Get-AtomicSha256 ([string]$item.Rollback)) -ne ([string]$item.BeforeSha256).ToUpperInvariant()) {
                    throw 'verified rollback copy is missing'
                }
                [System.IO.File]::Replace(
                    [string]$item.Rollback,
                    [string]$item.Destination,
                    $discard,
                    $true)
                if ((Get-AtomicSha256 ([string]$item.Destination)) -ne ([string]$item.BeforeSha256).ToUpperInvariant()) {
                    throw 'rolled-back destination hash mismatch'
                }
            }
            catch {
                $rollbackErrors.Add("$($item.Id): $($_.Exception.Message)")
            }
            finally {
                Remove-AtomicTemporary @($discard)
            }
        }
        if ($rollbackErrors.Count -eq 0) {
            Assert-AtomicVector $Items 0 "$Operation rollback"
            $journal.status = 'rolled_back'
            $journal.error = $originalError
            $journal.rolled_back_utc = [DateTime]::UtcNow.ToString('o')
            Write-AtomicJournal $JournalPath $journal
            throw "$Operation failed; all four resources were rolled back to the transaction input state: $originalError"
        }
        $journal.status = 'rollback_failed'
        $journal.error = $originalError
        $journal.rollback_errors = @($rollbackErrors)
        try { Write-AtomicJournal $JournalPath $journal } catch { }
        throw "$Operation failed and rollback was incomplete: $originalError; $($rollbackErrors -join ' | ')"
    }
    finally {
        Remove-AtomicTemporary @($Items | ForEach-Object { [string]$_.Staged })
    }
}

function Recover-AtomicFileSetTransaction {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]$Journal,
        [Parameter(Mandatory = $true)][object[]]$ExpectedItems,
        [Parameter(Mandatory = $true)][string]$JournalPath
    )
    Assert-AtomicItemSet $ExpectedItems
    if ($Journal.schema -ne 'nobu16.file-only-four-resource-transaction.v1' -or
        @($Journal.items).Count -ne 4) {
        throw 'Interrupted transaction journal has an unsupported schema.'
    }
    for ($index = 0; $index -lt 4; $index++) {
        $actual = $Journal.items[$index]
        $expected = $ExpectedItems[$index]
        if ([string]$actual.id -ne [string]$expected.Id -or
            [System.IO.Path]::GetFullPath([string]$actual.destination) -ne [System.IO.Path]::GetFullPath([string]$expected.Destination) -or
            ([string]$actual.before_sha256).ToUpperInvariant() -ne ([string]$expected.BeforeSha256).ToUpperInvariant() -or
            ([string]$actual.after_sha256).ToUpperInvariant() -ne ([string]$expected.AfterSha256).ToUpperInvariant()) {
            throw 'Interrupted transaction journal does not match the pinned resource set.'
        }
        $expected.Staged = [System.IO.Path]::GetFullPath([string]$actual.staged)
        $expected.Rollback = [System.IO.Path]::GetFullPath([string]$actual.rollback)
    }
    Assert-AtomicItemSet $ExpectedItems

    $states = @()
    foreach ($item in $ExpectedItems) {
        $hash = Get-AtomicSha256 ([string]$item.Destination)
        if ($hash -eq ([string]$item.BeforeSha256).ToUpperInvariant()) { $states += 'before' }
        elseif ($hash -eq ([string]$item.AfterSha256).ToUpperInvariant()) { $states += 'after' }
        else { throw "Interrupted transaction contains an unrecognized installed hash for $($item.Id)." }
    }
    if (@($states | Where-Object { $_ -eq 'after' }).Count -eq 4 -and $Journal.status -eq 'committed') {
        Remove-AtomicTemporary @($ExpectedItems | ForEach-Object { @([string]$_.Staged, [string]$_.Rollback) })
        return 'committed'
    }
    if (@($states | Where-Object { $_ -eq 'before' }).Count -eq 4) {
        Remove-AtomicTemporary @($ExpectedItems | ForEach-Object { @([string]$_.Staged, [string]$_.Rollback) })
        return 'rolled_back'
    }

    for ($index = 3; $index -ge 0; $index--) {
        if ($states[$index] -ne 'after') { continue }
        $item = $ExpectedItems[$index]
        if (-not (Test-Path -LiteralPath ([string]$item.Rollback) -PathType Leaf) -or
            (Get-AtomicSha256 ([string]$item.Rollback)) -ne ([string]$item.BeforeSha256).ToUpperInvariant()) {
            throw "Interrupted transaction lacks a verified rollback file for $($item.Id)."
        }
        $discard = Join-Path ([System.IO.Path]::GetDirectoryName([string]$item.Destination)) (
            '.' + [System.IO.Path]::GetFileName([string]$item.Destination) + '.recover-discard.' + [Guid]::NewGuid().ToString('N'))
        try {
            [System.IO.File]::Replace([string]$item.Rollback, [string]$item.Destination, $discard, $true)
        }
        finally {
            Remove-AtomicTemporary @($discard)
        }
    }
    Assert-AtomicVector $ExpectedItems 0 'interrupted transaction recovery'
    $Journal.status = 'recovered_before'
    $Journal.recovered_utc = [DateTime]::UtcNow.ToString('o')
    Write-AtomicJournal $JournalPath $Journal
    Remove-AtomicTemporary @($ExpectedItems | ForEach-Object { @([string]$_.Staged, [string]$_.Rollback) })
    return 'rolled_back'
}
