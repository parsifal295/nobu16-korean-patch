[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GameRoot,

    [switch]$Restore
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$OriginalSha256 = '29BC1ED66D27B9AEF5EB6CE3D126BA2BDBF86099E12B09615FE9F988F41E2246'
$UnpackedSha256 = 'BC885875A5E4288E5A1A424D99974F6F215777C03569C7EA707FDE63BDBC2B39'
$PatchedSha256 = '2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C'
$OriginalSize = 31978264L
$PatchedSize = 31747848L
$BackupName = 'NOBU16PK.exe.staticfix.original_1.1.7'
$ExpectedEntryRva = 0x012FE4D0
$ExpectedFunctionPrefix = [byte[]](0x48,0x89,0x5C,0x24,0x10,0x55,0x56,0x57,0x41,0x54,0x41,0x55,0x41,0x56,0x41,0x57,0x48,0x83,0xEC,0x30)
$PatchSites = @(
    @{ Name = 'visible surname characters'; Offset = 0x00BAF630; Before = [byte[]](0x0F,0x84,0xB4,0x01,0x00,0x00); After = [byte[]](0x90,0x90,0x90,0x90,0x90,0x90) },
    @{ Name = 'visible given-name characters'; Offset = 0x00BAF640; Before = [byte[]](0x0F,0x84,0xA4,0x01,0x00,0x00); After = [byte[]](0x90,0x90,0x90,0x90,0x90,0x90) },
    @{ Name = 'surname reading characters'; Offset = 0x00BAF656; Before = [byte[]](0x0F,0x84,0x8E,0x01,0x00,0x00); After = [byte[]](0x90,0x90,0x90,0x90,0x90,0x90) },
    @{ Name = 'given-name reading characters'; Offset = 0x00BAF667; Before = [byte[]](0x0F,0x84,0x7D,0x01,0x00,0x00); After = [byte[]](0x90,0x90,0x90,0x90,0x90,0x90) },
    @{ Name = 'combined name length'; Offset = 0x00BAF6C8; Before = [byte[]](0x7E,0x0C); After = [byte[]](0xEB,0x0C) }
)
$ExpectedSteamlessFiles = @{
    'Steamless.CLI.exe' = @{ Size = 113152L; Sha256 = '70CD54354865EDE605EC0FBFADF15F5302AA85A777394F28B0DE6ACFD243E795' }
    'Steamless.CLI.exe.config' = @{ Size = 189L; Sha256 = 'E8DECC96235B5494880083EB79C22C84C6D9EF312828BAF9490BEE7782C350EC' }
    'Plugins/Steamless.API.dll' = @{ Size = 34304L; Sha256 = 'D6ACC4B0CC768213A46FFAD0A6BF6070A6B13F79A22E0588F0AB50C950F9248C' }
    'Plugins/Steamless.Unpacker.Variant31.x64.dll' = @{ Size = 16384L; Sha256 = '790F1974F97258058CB57C20787E8A2FCB5C16CCA0911719B698580D74E38918' }
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Assert-FileHash([string]$Path, [long]$ExpectedSize, [string]$ExpectedHash, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label 파일이 없습니다: $Path"
    }
    $actualSize = (Get-Item -LiteralPath $Path).Length
    if ($actualSize -ne $ExpectedSize) {
        throw "$Label 크기가 맞지 않습니다. expected=$ExpectedSize actual=$actualSize"
    }
    $actualHash = Get-Sha256 $Path
    if ($actualHash -ne $ExpectedHash) {
        throw "$Label SHA-256이 맞지 않습니다. expected=$ExpectedHash actual=$actualHash"
    }
}

function Assert-NoRunningGameProcess([string]$TargetExecutablePath) {
    $running = @(Get-Process -Name 'NOBU16PK' -ErrorAction SilentlyContinue)
    $target = [System.IO.Path]::GetFullPath($TargetExecutablePath)
    foreach ($process in $running) {
        try {
            $processPath = [System.IO.Path]::GetFullPath($process.Path)
        } catch {
            throw '실행 중인 NOBU16PK.exe의 경로를 확인할 수 없습니다. 게임과 런처를 완전히 종료한 뒤 다시 실행하세요.'
        }
        if ([string]::Equals($processPath, $target, [StringComparison]::OrdinalIgnoreCase)) {
            throw '대상 NOBU16PK.exe가 실행 중입니다. 게임과 런처를 완전히 종료한 뒤 다시 실행하세요.'
        }
    }
}

function Assert-Bytes([byte[]]$Data, [int]$Offset, [byte[]]$Expected, [string]$Label) {
    if ($Offset -lt 0 -or ($Offset + $Expected.Length) -gt $Data.Length) {
        throw "$Label 위치가 EXE 범위를 벗어났습니다."
    }
    for ($index = 0; $index -lt $Expected.Length; $index++) {
        if ($Data[$Offset + $index] -ne $Expected[$index]) {
            throw "$Label 패치 전 바이트가 일치하지 않습니다. 다른 EXE에는 적용하지 않습니다."
        }
    }
}

function Get-PeChecksumOffset([byte[]]$Data) {
    if ($Data.Length -lt 0x400 -or $Data[0] -ne 0x4D -or $Data[1] -ne 0x5A) {
        throw '언팩 결과가 유효한 PE EXE가 아닙니다.'
    }
    $peOffset = [BitConverter]::ToInt32($Data, 0x3C)
    if ($peOffset -lt 0x40 -or ($peOffset + 0x80) -gt $Data.Length) {
        throw 'PE 헤더 오프셋이 유효하지 않습니다.'
    }
    if ($Data[$peOffset] -ne 0x50 -or $Data[$peOffset + 1] -ne 0x45 -or $Data[$peOffset + 2] -ne 0x00 -or $Data[$peOffset + 3] -ne 0x00) {
        throw 'PE 서명이 유효하지 않습니다.'
    }
    $optionalOffset = $peOffset + 24
    if ([BitConverter]::ToUInt16($Data, $optionalOffset) -ne 0x20B) {
        throw '예상한 64비트 PE32+ 형식이 아닙니다.'
    }
    $entryRva = [BitConverter]::ToUInt32($Data, $optionalOffset + 16)
    if ($entryRva -ne $ExpectedEntryRva) {
        throw ('언팩 EXE 진입점이 다릅니다. expected=0x{0:X8} actual=0x{1:X8}' -f $ExpectedEntryRva, $entryRva)
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

function Assert-SteamlessPayload([string]$SteamlessRoot) {
    foreach ($relative in $ExpectedSteamlessFiles.Keys) {
        $spec = $ExpectedSteamlessFiles[$relative]
        $path = Join-Path $SteamlessRoot ($relative -replace '/', '\\')
        Assert-FileHash $path $spec.Size $spec.Sha256 "Steamless 구성요소 ($relative)"
    }
}

function Find-UnpackedExecutable([string]$WorkRoot) {
    $matches = @()
    foreach ($candidate in Get-ChildItem -LiteralPath $WorkRoot -File -Recurse) {
        if ($candidate.Length -eq $PatchedSize -and (Get-Sha256 $candidate.FullName) -eq $UnpackedSha256) {
            $matches += $candidate.FullName
        }
    }
    if ($matches.Count -ne 1) {
        throw "Steamless 언팩 결과를 정확히 하나 찾지 못했습니다. matches=$($matches.Count)"
    }
    return $matches[0]
}

function Install-StaticFix([string]$ResolvedGameRoot, [string]$ExecutablePath, [string]$BackupPath) {
    $currentHash = Get-Sha256 $ExecutablePath
    if ($currentHash -eq $PatchedSha256) {
        Write-Host '이미 정적 무장 에디트 패치가 적용되어 있습니다.' -ForegroundColor Yellow
        return
    }
    Assert-FileHash $ExecutablePath $OriginalSize $OriginalSha256 'Steam JP 1.1.7 원본 NOBU16PK.exe'

    if (Test-Path -LiteralPath $BackupPath) {
        Assert-FileHash $BackupPath $OriginalSize $OriginalSha256 '기존 원본 백업'
    } else {
        Copy-Item -LiteralPath $ExecutablePath -Destination $BackupPath -ErrorAction Stop
        Assert-FileHash $BackupPath $OriginalSize $OriginalSha256 '새 원본 백업'
    }

    $steamlessRoot = Join-Path $PSScriptRoot 'Steamless'
    Assert-SteamlessPayload $steamlessRoot
    $workRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("NOBU16PK_StaticFix_" + [Guid]::NewGuid().ToString('N'))
    $stagePath = Join-Path $ResolvedGameRoot 'NOBU16PK.exe.staticfix.new'
    $rollbackPath = $stagePath + '.previous'
    try {
        New-Item -ItemType Directory -Path $workRoot -Force | Out-Null
        $workInput = Join-Path $workRoot 'NOBU16PK.exe'
        Copy-Item -LiteralPath $ExecutablePath -Destination $workInput -ErrorAction Stop

        Push-Location $steamlessRoot
        try {
            & (Join-Path $steamlessRoot 'Steamless.CLI.exe') --quiet --recalcchecksum $workInput
            if ($LASTEXITCODE -ne 0) {
                throw "Steamless 언팩이 실패했습니다. exit=$LASTEXITCODE"
            }
        } finally {
            Pop-Location
        }

        $unpackedPath = Find-UnpackedExecutable $workRoot
        [byte[]]$patched = [System.IO.File]::ReadAllBytes($unpackedPath)
        $checksumOffset = Get-PeChecksumOffset $patched
        Assert-Bytes $patched 0x00BAF510 $ExpectedFunctionPrefix '성명 검증 함수'
        foreach ($site in $PatchSites) {
            Assert-Bytes $patched $site.Offset $site.Before $site.Name
            [System.Buffer]::BlockCopy($site.After, 0, $patched, $site.Offset, $site.After.Length)
        }
        Set-PeChecksum $patched $checksumOffset
        [System.IO.File]::WriteAllBytes($stagePath, $patched)
        Assert-FileHash $stagePath $PatchedSize $PatchedSha256 '생성한 정적 패치 EXE'

        [System.IO.File]::Replace($stagePath, $ExecutablePath, $rollbackPath)
        Assert-FileHash $ExecutablePath $PatchedSize $PatchedSha256 '설치된 정적 패치 EXE'
        Write-Host '적용 완료: NOBU16PK.exe가 영구 정적 패치 EXE로 교체되었습니다.' -ForegroundColor Green
        Write-Host "원본 백업: $BackupPath"
        Write-Host '이후에는 평소처럼 Steam에서 실행하면 됩니다. 런타임 메모리 패처는 사용하지 않습니다.'
    } finally {
        if (Test-Path -LiteralPath $stagePath) {
            Remove-Item -LiteralPath $stagePath -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $rollbackPath) {
            Remove-Item -LiteralPath $rollbackPath -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $workRoot) {
            Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

function Restore-Original([string]$ExecutablePath, [string]$BackupPath) {
    Assert-FileHash $BackupPath $OriginalSize $OriginalSha256 '원본 백업'
    $currentHash = Get-Sha256 $ExecutablePath
    if ($currentHash -eq $OriginalSha256) {
        Write-Host '이미 원본 Steam JP 1.1.7 EXE입니다.' -ForegroundColor Yellow
        return
    }
    if ($currentHash -ne $PatchedSha256) {
        throw "현재 EXE가 이 패치의 원본/정적 패치본과 일치하지 않습니다: $currentHash"
    }
    $stagePath = Join-Path (Split-Path -Parent $ExecutablePath) 'NOBU16PK.exe.staticfix.restore.new'
    $rollbackPath = $stagePath + '.previous'
    try {
        Copy-Item -LiteralPath $BackupPath -Destination $stagePath -Force -ErrorAction Stop
        Assert-FileHash $stagePath $OriginalSize $OriginalSha256 '복구 준비 EXE'
        [System.IO.File]::Replace($stagePath, $ExecutablePath, $rollbackPath)
        Assert-FileHash $ExecutablePath $OriginalSize $OriginalSha256 '복구된 원본 EXE'
        Write-Host '원본 NOBU16PK.exe 복구가 완료되었습니다.' -ForegroundColor Green
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
    $resolvedGameRoot = (Resolve-Path -LiteralPath $GameRoot -ErrorAction Stop).Path
    $executablePath = Join-Path $resolvedGameRoot 'NOBU16PK.exe'
    $backupPath = Join-Path $resolvedGameRoot $BackupName
    Assert-NoRunningGameProcess $executablePath
    if ($Restore) {
        Restore-Original $executablePath $backupPath
    } else {
        Install-StaticFix $resolvedGameRoot $executablePath $backupPath
    }
    exit 0
} catch {
    Write-Host ''
    Write-Host ('실패: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
