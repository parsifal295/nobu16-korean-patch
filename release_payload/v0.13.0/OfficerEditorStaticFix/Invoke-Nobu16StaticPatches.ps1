[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GameRoot,

    [switch]$Restore,

    [switch]$Status
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$OriginalSha256 = '29BC1ED66D27B9AEF5EB6CE3D126BA2BDBF86099E12B09615FE9F988F41E2246'
$UnpackedBaseSha256 = 'BC885875A5E4288E5A1A424D99974F6F215777C03569C7EA707FDE63BDBC2B39'
$OriginalSize = 31978264L
$UnpackedSize = 31747848L
$BackupName = 'NOBU16PK.exe.staticfix.original_1.1.7'
$ExpectedEntryRva = 0x012FE4D0
$UnpackedBaseChecksumBytes = [byte[]](0xE0,0x43,0xE5,0x01)
$ExpectedSteamlessFiles = @{
    'Steamless.CLI.exe' = @{ Size = 113152L; Sha256 = '70CD54354865EDE605EC0FBFADF15F5302AA85A777394F28B0DE6ACFD243E795' }
    'Steamless.CLI.exe.config' = @{ Size = 188L; Sha256 = '84C420F392B59E32409E308AA67D9CDC3BB1BC7496A2403EF5BB0EB8ADF62763' }
    'Plugins/Steamless.API.dll' = @{ Size = 34304L; Sha256 = 'D6ACC4B0CC768213A46FFAD0A6BF6070A6B13F79A22E0588F0AB50C950F9248C' }
    'Plugins/Steamless.Unpacker.Variant31.x64.dll' = @{ Size = 16384L; Sha256 = '790F1974F97258058CB57C20787E8A2FCB5C16CCA0911719B698580D74E38918' }
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Get-Sha256Bytes([byte[]]$Data) {
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($algorithm.ComputeHash($Data))).Replace('-', '')
    } finally {
        $algorithm.Dispose()
    }
}

function Copy-Bytes([byte[]]$Data) {
    $copy = New-Object byte[] $Data.Length
    [System.Buffer]::BlockCopy($Data, 0, $copy, 0, $Data.Length)
    return ,$copy
}

function Convert-HexBytes([string]$Hex, [string]$Label) {
    $clean = ($Hex -replace '[^0-9A-Fa-f]', '')
    if ($clean.Length -eq 0 -or ($clean.Length % 2) -ne 0) {
        throw "$Label has invalid hex bytes."
    }
    $result = New-Object byte[] ($clean.Length / 2)
    for ($index = 0; $index -lt $result.Length; $index++) {
        $result[$index] = [Convert]::ToByte($clean.Substring($index * 2, 2), 16)
    }
    return $result
}

function Assert-FileHash([string]$Path, [long]$ExpectedSize, [string]$ExpectedHash, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label is missing: $Path"
    }
    $actualSize = (Get-Item -LiteralPath $Path).Length
    if ($actualSize -ne $ExpectedSize) {
        throw "$Label size mismatch. expected=$ExpectedSize actual=$actualSize"
    }
    $actualHash = Get-Sha256 $Path
    if ($actualHash -ne $ExpectedHash) {
        throw "$Label SHA-256 mismatch. expected=$ExpectedHash actual=$actualHash"
    }
}

function Assert-NoRunningGameProcess([string]$TargetExecutablePath) {
    $running = @(Get-Process -Name 'NOBU16PK' -ErrorAction SilentlyContinue)
    $target = [System.IO.Path]::GetFullPath($TargetExecutablePath)
    foreach ($process in $running) {
        try {
            $processPath = [System.IO.Path]::GetFullPath($process.Path)
        } catch {
            throw 'Cannot inspect a running NOBU16PK.exe. Fully exit the game and launcher first.'
        }
        if ([string]::Equals($processPath, $target, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'The target NOBU16PK.exe is running. Fully exit the game and launcher first.'
        }
    }
}

function Test-BytesEqual([byte[]]$Data, [int]$Offset, [byte[]]$Expected) {
    if ($Offset -lt 0 -or ($Offset + $Expected.Length) -gt $Data.Length) {
        return $false
    }
    for ($index = 0; $index -lt $Expected.Length; $index++) {
        if ($Data[$Offset + $index] -ne $Expected[$index]) {
            return $false
        }
    }
    return $true
}

function Set-Bytes([byte[]]$Data, [int]$Offset, [byte[]]$Value) {
    if ($Offset -lt 0 -or ($Offset + $Value.Length) -gt $Data.Length) {
        throw ('Patch site 0x{0:X8} is outside the EXE.' -f $Offset)
    }
    [System.Buffer]::BlockCopy($Value, 0, $Data, $Offset, $Value.Length)
}

function Get-ExpandedPayload([object]$Patch) {
    if ($Patch.Kind -ne 'AppendOverlay' -or $null -eq $Patch.Append) {
        throw "Patch $($Patch.Id) has no append payload."
    }
    [byte[]]$compressed = [System.IO.File]::ReadAllBytes($Patch.Append.Path)
    $input = New-Object System.IO.MemoryStream(,$compressed)
    $gzip = New-Object System.IO.Compression.GZipStream(
        $input,
        [System.IO.Compression.CompressionMode]::Decompress
    )
    $output = New-Object System.IO.MemoryStream
    try {
        $gzip.CopyTo($output)
        [byte[]]$expanded = $output.ToArray()
    } finally {
        $gzip.Dispose()
        $input.Dispose()
        $output.Dispose()
    }
    if ($expanded.Length -ne $Patch.Append.ExpandedSize) {
        throw "Patch $($Patch.Id) expanded payload size mismatch."
    }
    $expandedHash = Get-Sha256Bytes $expanded
    if ($expandedHash -ne $Patch.Append.ExpandedSha256) {
        throw "Patch $($Patch.Id) expanded payload SHA-256 mismatch."
    }
    return ,$expanded
}

function Get-PeChecksumOffset([byte[]]$Data) {
    if ($Data.Length -lt 0x400 -or $Data[0] -ne 0x4D -or $Data[1] -ne 0x5A) {
        throw 'The unpacked image is not a valid PE executable.'
    }
    $peOffset = [BitConverter]::ToInt32($Data, 0x3C)
    if ($peOffset -lt 0x40 -or ($peOffset + 0x80) -gt $Data.Length) {
        throw 'The PE header offset is invalid.'
    }
    if ($Data[$peOffset] -ne 0x50 -or $Data[$peOffset + 1] -ne 0x45 -or $Data[$peOffset + 2] -ne 0 -or $Data[$peOffset + 3] -ne 0) {
        throw 'The PE signature is invalid.'
    }
    $optionalOffset = $peOffset + 24
    if ([BitConverter]::ToUInt16($Data, $optionalOffset) -ne 0x20B) {
        throw 'The executable is not the expected PE32+ image.'
    }
    $entryRva = [BitConverter]::ToUInt32($Data, $optionalOffset + 16)
    if ($entryRva -ne $ExpectedEntryRva) {
        throw ('Entry point mismatch. expected=0x{0:X8} actual=0x{1:X8}' -f $ExpectedEntryRva, $entryRva)
    }
    return ($optionalOffset + 64)
}

function Set-PeChecksum([byte[]]$Data, [int]$ChecksumOffset) {
    [Array]::Clear($Data, $ChecksumOffset, 4)
    [UInt64]$sum = 0
    for ($offset = 0; $offset -lt $Data.Length; $offset += 2) {
        [UInt64]$word = 0
        if ($offset -lt $ChecksumOffset -or $offset -ge ($ChecksumOffset + 4)) {
            $high = if (($offset + 1) -lt $Data.Length) { [UInt64]$Data[$offset + 1] } else { 0 }
            $word = [UInt64]$Data[$offset] -bor ($high -shl 8)
        }
        $sum += $word
        $sum = ($sum -band 0xFFFF) + ($sum -shr 16)
    }
    $sum = ($sum -band 0xFFFF) + ($sum -shr 16)
    $checksum = [UInt32](($sum + [UInt64]$Data.Length) -band 0xFFFFFFFF)
    [System.Buffer]::BlockCopy([BitConverter]::GetBytes($checksum), 0, $Data, $ChecksumOffset, 4)
}

function Get-PatchRegistry {
    $patchRoot = Join-Path $PSScriptRoot 'Patches'
    $registryPath = Join-Path $PSScriptRoot '000-PatchRegistry.psd1'
    $manifest = Import-PowerShellDataFile -LiteralPath $registryPath
    foreach ($key in @('Schema', 'Release', 'AllAppliedSha256', 'Patches')) {
        if (-not $manifest.ContainsKey($key)) {
            throw "000-PatchRegistry.psd1 is missing '$key'."
        }
    }
    if ($manifest.Schema -ne 'nobu16.static-exe-patch-registry.v3') {
        throw "Unsupported patch registry schema: $($manifest.Schema)"
    }
    if ([string]$manifest.AllAppliedSha256 -notmatch '^[0-9A-F]{64}$') {
        throw 'Patch registry has an invalid AllAppliedSha256.'
    }
    $entries = @($manifest.Patches)
    if ($entries.Count -eq 0) {
        throw 'Patch registry has no entries.'
    }
    $chainedBytes = @{}
    [long]$structuralSize = $UnpackedSize
    $ids = @{}
    $registeredFiles = @()
    $registeredPayloadFiles = @()
    $patches = @()
    foreach ($entry in $entries) {
        foreach ($key in @('Id', 'File', 'Size', 'Sha256')) {
            if (-not $entry.ContainsKey($key)) {
                throw "Patch registry entry is missing '$key'."
            }
        }
        $relative = ([string]$entry.File) -replace '/', '\'
        if ([System.IO.Path]::IsPathRooted($relative) -or $relative -notlike 'Patches\*.psd1' -or $relative -like '*..*') {
            throw "Patch registry has an unsafe file path: $($entry.File)"
        }
        $filePath = Join-Path $PSScriptRoot $relative
        Assert-FileHash $filePath ([long]$entry.Size) ([string]$entry.Sha256) "Patch definition ($($entry.Id))"
        $file = Get-Item -LiteralPath $filePath
        $registeredFiles += $file.Name
        $raw = Import-PowerShellDataFile -LiteralPath $file.FullName
        foreach ($key in @('Id', 'Name', 'Sites')) {
            if (-not $raw.ContainsKey($key)) {
                throw "$($file.Name) is missing '$key'."
            }
        }
        $id = [string]$raw.Id
        if ($id -ne [string]$entry.Id) {
            throw "$($file.Name) Id does not match 000-PatchRegistry.psd1."
        }
        if ($id -notmatch '^\d{3}$' -or -not $file.BaseName.StartsWith($id + '-')) {
            throw "$($file.Name) has an invalid or mismatched Id."
        }
        if ($ids.ContainsKey($id)) {
            throw "Duplicate patch Id: $id"
        }
        $ids[$id] = $true
        $kind = if ($raw.ContainsKey('Kind')) { [string]$raw.Kind } else { 'BytePatch' }
        if ($kind -notin @('BytePatch', 'AppendOverlay')) {
            throw "$($file.Name) has an unsupported patch kind: $kind"
        }
        $append = $null
        [long]$baseSize = $UnpackedSize
        [long]$targetSize = $UnpackedSize
        if ($kind -eq 'AppendOverlay') {
            foreach ($key in @('BaseSize', 'TargetSize', 'Append')) {
                if (-not $raw.ContainsKey($key)) {
                    throw "$($file.Name) is missing '$key'."
                }
            }
            $baseSize = [long]$raw.BaseSize
            $targetSize = [long]$raw.TargetSize
            if ($baseSize -ne $structuralSize -or $targetSize -le $baseSize) {
                throw "$($file.Name) has invalid structural patch sizes."
            }
            $rawAppend = $raw.Append
            foreach ($key in @('File', 'Size', 'Sha256', 'ExpandedSize', 'ExpandedSha256', 'Compression')) {
                if (-not $rawAppend.ContainsKey($key)) {
                    throw "$($file.Name) append payload is missing '$key'."
                }
            }
            $payloadRelative = ([string]$rawAppend.File) -replace '/', '\'
            if (
                [System.IO.Path]::IsPathRooted($payloadRelative) -or
                $payloadRelative -notlike 'Payloads\*.gz' -or
                $payloadRelative -like '*..*'
            ) {
                throw "$($file.Name) has an unsafe append payload path."
            }
            if ([string]$rawAppend.Compression -ne 'gzip') {
                throw "$($file.Name) has unsupported append compression."
            }
            if ([long]$rawAppend.ExpandedSize -ne ($targetSize - $baseSize)) {
                throw "$($file.Name) append payload length does not match TargetSize."
            }
            foreach ($hashKey in @('Sha256', 'ExpandedSha256')) {
                if ([string]$rawAppend[$hashKey] -notmatch '^[0-9A-F]{64}$') {
                    throw "$($file.Name) append payload has an invalid $hashKey."
                }
            }
            $payloadPath = Join-Path $patchRoot $payloadRelative
            Assert-FileHash $payloadPath ([long]$rawAppend.Size) ([string]$rawAppend.Sha256) "Append payload ($id)"
            $registeredPayloadFiles += [System.IO.Path]::GetFileName($payloadPath)
            $append = [pscustomobject]@{
                Path = $payloadPath
                Size = [long]$rawAppend.Size
                Sha256 = [string]$rawAppend.Sha256
                ExpandedSize = [long]$rawAppend.ExpandedSize
                ExpandedSha256 = [string]$rawAppend.ExpandedSha256
            }
            $structuralSize = $targetSize
        }
        $sites = @()
        $patchOccupied = @{}
        foreach ($rawSite in @($raw.Sites)) {
            foreach ($key in @('Name', 'Offset', 'Before', 'After')) {
                if (-not $rawSite.ContainsKey($key)) {
                    throw "$($file.Name) site is missing '$key'."
                }
            }
            $before = [byte[]](Convert-HexBytes ([string]$rawSite.Before) "$id/$($rawSite.Name)/Before")
            $after = [byte[]](Convert-HexBytes ([string]$rawSite.After) "$id/$($rawSite.Name)/After")
            if ($before.Length -ne $after.Length) {
                throw "$id/$($rawSite.Name) changes byte length."
            }
            if ([BitConverter]::ToString($before) -eq [BitConverter]::ToString($after)) {
                throw "$id/$($rawSite.Name) has identical Before and After bytes."
            }
            $site = [pscustomobject]@{
                Name = [string]$rawSite.Name
                Offset = [int]$rawSite.Offset
                Before = $before
                After = $after
                FinalAfter = $null
            }
            for ($byteOffset = $site.Offset; $byteOffset -lt ($site.Offset + $before.Length); $byteOffset++) {
                if ($patchOccupied.ContainsKey($byteOffset)) {
                    throw ('Overlapping sites inside patch {0} at 0x{1:X8}.' -f $id, $byteOffset)
                }
                $patchOccupied[$byteOffset] = $true
                $relativeOffset = $byteOffset - $site.Offset
                if (
                    $chainedBytes.ContainsKey($byteOffset) -and
                    [byte]$chainedBytes[$byteOffset] -ne $before[$relativeOffset]
                ) {
                    throw ('Patch chain preimage mismatch at 0x{0:X8}.' -f $byteOffset)
                }
                $chainedBytes[$byteOffset] = $after[$relativeOffset]
            }
            $sites += $site
        }
        if ($sites.Count -eq 0) {
            throw "$($file.Name) has no patch sites."
        }
        $patches += [pscustomobject]@{
            Id = $id
            Name = [string]$raw.Name
            Kind = $kind
            BaseSize = $baseSize
            TargetSize = $targetSize
            Append = $append
            Sites = $sites
            File = $file.Name
            LaterSites = @()
        }
    }
    foreach ($patch in $patches) {
        foreach ($site in $patch.Sites) {
            [byte[]]$finalAfter = New-Object byte[] $site.After.Length
            for ($index = 0; $index -lt $finalAfter.Length; $index++) {
                $finalAfter[$index] = [byte]$chainedBytes[$site.Offset + $index]
            }
            $site.FinalAfter = $finalAfter
        }
    }
    for ($patchIndex = 0; $patchIndex -lt $patches.Count; $patchIndex++) {
        $laterSites = @()
        for ($laterIndex = $patches.Count - 1; $laterIndex -gt $patchIndex; $laterIndex--) {
            $laterSites += @($patches[$laterIndex].Sites)
        }
        $patches[$patchIndex].LaterSites = $laterSites
    }
    $actualFiles = @(Get-ChildItem -LiteralPath $patchRoot -Filter '*.psd1' -File | Sort-Object Name | ForEach-Object { $_.Name })
    $expectedFiles = @($registeredFiles | Sort-Object)
    if (($actualFiles -join '|') -ne ($expectedFiles -join '|')) {
        throw "Patch definition set differs from 000-PatchRegistry.psd1."
    }
    $payloadRoot = Join-Path $patchRoot 'Payloads'
    $actualPayloadFiles = if (Test-Path -LiteralPath $payloadRoot) {
        @(Get-ChildItem -LiteralPath $payloadRoot -Filter '*.gz' -File | Sort-Object Name | ForEach-Object { $_.Name })
    } else {
        @()
    }
    $expectedPayloadFiles = @($registeredPayloadFiles | Sort-Object)
    if (($actualPayloadFiles -join '|') -ne ($expectedPayloadFiles -join '|')) {
        throw "Append payload set differs from registered patch definitions."
    }
    return ,([pscustomobject]@{
        Release = [string]$manifest.Release
        AllAppliedSha256 = [string]$manifest.AllAppliedSha256
        Patches = $patches
    })
}

function Get-PatchState([byte[]]$Data, [object]$Patch) {
    if ($Patch.Kind -eq 'AppendOverlay' -and $Data.Length -lt $Patch.BaseSize) {
        return 'Blocked'
    }
    $beforeCount = 0
    $afterCount = 0
    foreach ($site in $Patch.Sites) {
        if (Test-BytesEqual $Data $site.Offset $site.Before) {
            $beforeCount++
        } elseif (
            (Test-BytesEqual $Data $site.Offset $site.After) -or
            ($null -ne $site.FinalAfter -and (Test-BytesEqual $Data $site.Offset $site.FinalAfter))
        ) {
            $afterCount++
        } else {
            throw ('Patch {0} ({1}) has unknown bytes at 0x{2:X8}.' -f $Patch.Id, $Patch.Name, $site.Offset)
        }
    }
    if ($Patch.Kind -eq 'AppendOverlay') {
        if ($Data.Length -eq $Patch.BaseSize -and $beforeCount -eq $Patch.Sites.Count) {
            return 'Pending'
        }
        if ($Data.Length -ge $Patch.TargetSize -and $afterCount -eq $Patch.Sites.Count) {
            [byte[]]$tail = New-Object byte[] $Patch.Append.ExpandedSize
            [System.Buffer]::BlockCopy($Data, $Patch.BaseSize, $tail, 0, $tail.Length)
            foreach ($laterSite in $Patch.LaterSites) {
                for ($index = 0; $index -lt $laterSite.Before.Length; $index++) {
                    $absoluteOffset = $laterSite.Offset + $index
                    if ($absoluteOffset -ge $Patch.BaseSize -and $absoluteOffset -lt $Patch.TargetSize) {
                        $tail[$absoluteOffset - $Patch.BaseSize] = $laterSite.Before[$index]
                    }
                }
            }
            if ((Get-Sha256Bytes $tail) -ne $Patch.Append.ExpandedSha256) {
                throw "Patch $($Patch.Id) ($($Patch.Name)) has an unknown appended payload."
            }
            return 'Applied'
        }
    } else {
        if ($afterCount -eq $Patch.Sites.Count) {
            return 'Applied'
        }
        if ($beforeCount -eq $Patch.Sites.Count) {
            return 'Pending'
        }
    }
    throw "Patch $($Patch.Id) ($($Patch.Name)) is partially applied; refusing an unsafe repair."
}

function Assert-NormalizedBase([byte[]]$Data, [object[]]$Patches) {
    $states = @{}
    foreach ($patch in $Patches) {
        $states[$patch.Id] = Get-PatchState $Data $patch
    }
    [byte[]]$normalized = Copy-Bytes $Data
    for ($patchIndex = $Patches.Count - 1; $patchIndex -ge 0; $patchIndex--) {
        $patch = $Patches[$patchIndex]
        if ($states[$patch.Id] -eq 'Blocked') {
            continue
        }
        foreach ($site in $patch.Sites) {
            Set-Bytes $normalized $site.Offset $site.Before
        }
        if ($patch.Kind -eq 'AppendOverlay' -and $states[$patch.Id] -eq 'Applied') {
            if ($normalized.Length -ne $patch.TargetSize) {
                throw "Patch $($patch.Id) structural size chain is invalid."
            }
            [byte[]]$truncated = New-Object byte[] $patch.BaseSize
            [System.Buffer]::BlockCopy($normalized, 0, $truncated, 0, $truncated.Length)
            $normalized = $truncated
        }
    }
    if ($normalized.Length -ne $UnpackedSize) {
        throw "Normalized EXE size mismatch. expected=$UnpackedSize actual=$($normalized.Length)"
    }
    $checksumOffset = Get-PeChecksumOffset $normalized
    Set-Bytes $normalized $checksumOffset $UnpackedBaseChecksumBytes
    $normalizedHash = Get-Sha256Bytes $normalized
    if ($normalizedHash -ne $UnpackedBaseSha256) {
        throw "EXE differs outside registered patch sites. normalized=$normalizedHash"
    }
}

function Assert-SteamlessPayload([string]$SteamlessRoot) {
    foreach ($relative in $ExpectedSteamlessFiles.Keys) {
        $spec = $ExpectedSteamlessFiles[$relative]
        $path = Join-Path $SteamlessRoot ($relative -replace '/', '\')
        Assert-FileHash $path $spec.Size $spec.Sha256 "Steamless component ($relative)"
    }
}

function Find-UnpackedExecutable([string]$WorkRoot) {
    $matches = @()
    foreach ($candidate in Get-ChildItem -LiteralPath $WorkRoot -File -Recurse) {
        if ($candidate.Length -eq $UnpackedSize -and (Get-Sha256 $candidate.FullName) -eq $UnpackedBaseSha256) {
            $matches += $candidate.FullName
        }
    }
    if ($matches.Count -ne 1) {
        throw "Expected exactly one verified Steamless output. matches=$($matches.Count)"
    }
    return $matches[0]
}

function Remove-PrivateWorkRoot([string]$WorkRoot) {
    if (-not (Test-Path -LiteralPath $WorkRoot)) {
        return
    }
    $tempBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    $resolved = [System.IO.Path]::GetFullPath($WorkRoot)
    $leaf = [System.IO.Path]::GetFileName($resolved)
    if (-not $resolved.StartsWith($tempBase, [StringComparison]::OrdinalIgnoreCase) -or $leaf -notlike 'NOBU16PK_StaticPatch_*') {
        throw "Unsafe temporary cleanup target: $resolved"
    }
    Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction Stop
}

function Get-UnpackedBytes([string]$ExecutablePath, [string]$WorkRoot) {
    $steamlessRoot = Join-Path $PSScriptRoot 'Steamless'
    Assert-SteamlessPayload $steamlessRoot
    New-Item -ItemType Directory -Path $WorkRoot -Force | Out-Null
    $workInput = Join-Path $WorkRoot 'NOBU16PK.exe'
    Copy-Item -LiteralPath $ExecutablePath -Destination $workInput -ErrorAction Stop
    Push-Location $steamlessRoot
    try {
        & (Join-Path $steamlessRoot 'Steamless.CLI.exe') --quiet --recalcchecksum $workInput | Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "Steamless failed. exit=$LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
    $unpackedPath = Find-UnpackedExecutable $WorkRoot
    return ,([System.IO.File]::ReadAllBytes($unpackedPath))
}

function Show-PatchStates([byte[]]$Data, [object[]]$Patches) {
    foreach ($patch in $Patches) {
        $state = Get-PatchState $Data $patch
        Write-Host ("[{0}] {1}: {2}" -f $patch.Id, $patch.Name, $state)
    }
}

function Install-RegisteredPatches([string]$ResolvedGameRoot, [string]$ExecutablePath, [string]$BackupPath, [object[]]$Patches, [string]$ExpectedOutputHash) {
    $currentHash = Get-Sha256 $ExecutablePath
    $isProtectedOriginal = $currentHash -eq $OriginalSha256
    if ($isProtectedOriginal) {
        Assert-FileHash $ExecutablePath $OriginalSize $OriginalSha256 'Steam JP 1.1.7 original EXE'
    } elseif ((Get-Item -LiteralPath $ExecutablePath).Length -notin @($UnpackedSize) + @($Patches | Where-Object { $_.Kind -eq 'AppendOverlay' } | ForEach-Object { $_.TargetSize })) {
        throw "Unsupported NOBU16PK.exe. sha256=$currentHash"
    }

    if (Test-Path -LiteralPath $BackupPath) {
        Assert-FileHash $BackupPath $OriginalSize $OriginalSha256 'Original backup'
    } elseif ($isProtectedOriginal) {
        Copy-Item -LiteralPath $ExecutablePath -Destination $BackupPath -ErrorAction Stop
        Assert-FileHash $BackupPath $OriginalSize $OriginalSha256 'New original backup'
    } else {
        throw "An original backup is required for an existing static patch: $BackupPath"
    }

    $workRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('NOBU16PK_StaticPatch_' + [Guid]::NewGuid().ToString('N'))
    $stagePath = Join-Path $ResolvedGameRoot 'NOBU16PK.exe.staticfix.new'
    $rollbackPath = $stagePath + '.previous'
    try {
        [byte[]]$patched = if ($isProtectedOriginal) {
            Get-UnpackedBytes $ExecutablePath $workRoot
        } else {
            [System.IO.File]::ReadAllBytes($ExecutablePath)
        }
        Assert-NormalizedBase $patched $Patches

        $changedCount = 0
        foreach ($patch in $Patches) {
            $state = Get-PatchState $patched $patch
            if ($state -eq 'Applied') {
                Write-Host ("[{0}] already applied: {1}" -f $patch.Id, $patch.Name) -ForegroundColor Yellow
                continue
            }
            if ($state -eq 'Blocked') {
                throw "Patch $($patch.Id) remains blocked after its registered dependencies."
            }
            Write-Host ("[{0}] will apply: {1}" -f $patch.Id, $patch.Name)
            foreach ($site in $patch.Sites) {
                if (-not (Test-BytesEqual $patched $site.Offset $site.Before)) {
                    throw ('Patch {0} preimage changed at 0x{1:X8}.' -f $patch.Id, $site.Offset)
                }
                Set-Bytes $patched $site.Offset $site.After
            }
            if ($patch.Kind -eq 'AppendOverlay') {
                if ($patched.Length -ne $patch.BaseSize) {
                    throw "Patch $($patch.Id) cannot append from EXE size $($patched.Length)."
                }
                [byte[]]$appendBytes = Get-ExpandedPayload $patch
                [byte[]]$expandedImage = New-Object byte[] $patch.TargetSize
                [System.Buffer]::BlockCopy($patched, 0, $expandedImage, 0, $patched.Length)
                [System.Buffer]::BlockCopy($appendBytes, 0, $expandedImage, $patched.Length, $appendBytes.Length)
                $patched = $expandedImage
            }
            $changedCount++
        }

        $checksumOffset = Get-PeChecksumOffset $patched
        Set-PeChecksum $patched $checksumOffset
        Assert-NormalizedBase $patched $Patches
        foreach ($patch in $Patches) {
            if ((Get-PatchState $patched $patch) -ne 'Applied') {
                throw "Patch $($patch.Id) did not reach Applied state."
            }
        }
        $outputHash = Get-Sha256Bytes $patched
        if ($outputHash -ne $ExpectedOutputHash) {
            throw "Registered all-applied output hash mismatch. expected=$ExpectedOutputHash actual=$outputHash"
        }
        if (-not $isProtectedOriginal -and $changedCount -eq 0 -and $outputHash -eq $currentHash) {
            Write-Host 'All registered static patches are already applied.' -ForegroundColor Yellow
            return
        }

        [System.IO.File]::WriteAllBytes($stagePath, $patched)
        Assert-FileHash $stagePath $patched.Length $outputHash 'Staged patched EXE'
        [System.IO.File]::Replace($stagePath, $ExecutablePath, $rollbackPath)
        Assert-FileHash $ExecutablePath $patched.Length $outputHash 'Installed patched EXE'
        Write-Host "Applied registered patches. output SHA-256=$outputHash" -ForegroundColor Green
        Write-Host "Original backup: $BackupPath"
        Write-Host 'Launch normally from Steam. No runtime memory patcher is used.'
    } finally {
        if (Test-Path -LiteralPath $stagePath) {
            Remove-Item -LiteralPath $stagePath -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $rollbackPath) {
            Remove-Item -LiteralPath $rollbackPath -Force -ErrorAction SilentlyContinue
        }
        Remove-PrivateWorkRoot $workRoot
    }
}

function Restore-Original([string]$ExecutablePath, [string]$BackupPath, [object[]]$Patches) {
    Assert-FileHash $BackupPath $OriginalSize $OriginalSha256 'Original backup'
    $currentHash = Get-Sha256 $ExecutablePath
    if ($currentHash -eq $OriginalSha256) {
        Write-Host 'NOBU16PK.exe is already the original Steam JP 1.1.7 file.' -ForegroundColor Yellow
        return
    }
    [byte[]]$current = [System.IO.File]::ReadAllBytes($ExecutablePath)
    Assert-NormalizedBase $current $Patches

    $stagePath = Join-Path (Split-Path -Parent $ExecutablePath) 'NOBU16PK.exe.staticfix.restore.new'
    $rollbackPath = $stagePath + '.previous'
    try {
        Copy-Item -LiteralPath $BackupPath -Destination $stagePath -Force -ErrorAction Stop
        Assert-FileHash $stagePath $OriginalSize $OriginalSha256 'Staged original EXE'
        [System.IO.File]::Replace($stagePath, $ExecutablePath, $rollbackPath)
        Assert-FileHash $ExecutablePath $OriginalSize $OriginalSha256 'Restored original EXE'
        Write-Host 'Restored the original NOBU16PK.exe.' -ForegroundColor Green
    } finally {
        if (Test-Path -LiteralPath $stagePath) {
            Remove-Item -LiteralPath $stagePath -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $rollbackPath) {
            Remove-Item -LiteralPath $rollbackPath -Force -ErrorAction SilentlyContinue
        }
    }
}

try {
    if ($Restore -and $Status) {
        throw 'Use only one of -Restore or -Status.'
    }
    $resolvedGameRoot = (Resolve-Path -LiteralPath $GameRoot -ErrorAction Stop).Path
    $executablePath = Join-Path $resolvedGameRoot 'NOBU16PK.exe'
    $backupPath = Join-Path $resolvedGameRoot $BackupName
    if (-not (Test-Path -LiteralPath $executablePath -PathType Leaf)) {
        throw "NOBU16PK.exe is missing: $executablePath"
    }
    $registry = Get-PatchRegistry
    $patches = @($registry.Patches)
    Assert-NoRunningGameProcess $executablePath
    if ($Restore) {
        Restore-Original $executablePath $backupPath $patches
    } elseif ($Status) {
        $hash = Get-Sha256 $executablePath
        if ($hash -eq $OriginalSha256) {
            foreach ($patch in $patches) {
                Write-Host ("[{0}] {1}: Pending" -f $patch.Id, $patch.Name)
            }
        } else {
            [byte[]]$data = [System.IO.File]::ReadAllBytes($executablePath)
            Assert-NormalizedBase $data $patches
            Show-PatchStates $data $patches
        }
    } else {
        Install-RegisteredPatches $resolvedGameRoot $executablePath $backupPath $patches $registry.AllAppliedSha256
    }
    exit 0
} catch {
    Write-Host ''
    Write-Host ('Failed: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
