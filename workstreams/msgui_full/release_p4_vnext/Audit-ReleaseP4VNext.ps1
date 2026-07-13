[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackageRoot,
    [string]$ZipPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PackageRoot = [IO.Path]::GetFullPath($PackageRoot)
$expectedRelative = @(
    'APPLY_KOREAN_PATCH.bat',
    'components/font/licenses/OFL-NotoSansKR.txt',
    'components/font/licenses/OFL-NotoSerifKR.txt',
    'components/font/metrics/glyphs.jsonl',
    'components/font/payload/glyph_pixels_entry_6.bin',
    'components/font/payload/glyph_pixels_entry_7.bin',
    'components/font/recipe.json',
    'components/message/msgui_sc.recipe.json',
    'FILE_ONLY_POLICY_KO.md',
    'README_KO.md',
    'release_manifest.json',
    'RESTORE_ORIGINALS.bat',
    'tools/FileRecipeCore.cs',
    'tools/Invoke-FileOnlyPatch.ps1',
    'tools/JsonKeyGuard.cs',
    'VALIDATION_EVIDENCE.json',
    'VERIFY_PACKAGE.bat'
)
$expected = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
foreach ($path in $expectedRelative) { [void]$expected.Add($path) }

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Get-StreamSha256([IO.Stream]$Stream) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha.ComputeHash($Stream))).Replace('-', '')
    }
    finally {
        $sha.Dispose()
    }
}

function Read-GuardedJson([string]$Path) {
    [byte[]]$bytes = [IO.File]::ReadAllBytes($Path)
    [N16KrFileOnly.JsonKeyGuard]::AssertNoDuplicateKeys($bytes)
    $strictUtf8 = New-Object Text.UTF8Encoding($false, $true)
    return ($strictUtf8.GetString($bytes) | ConvertFrom-Json)
}

function Assert-NotArchive([string]$Path, [string]$Label) {
    $extension = [IO.Path]::GetExtension($Path).ToLowerInvariant()
    if ($extension -in @('.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.xz', '.cab')) {
        throw "Nested archive is forbidden: $Label"
    }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ge 8) {
        [byte[]]$header = New-Object byte[] 8
        $stream = [IO.File]::OpenRead($Path)
        try { [void]$stream.Read($header, 0, 8) } finally { $stream.Dispose() }
        $hex = ([BitConverter]::ToString($header)).Replace('-', '')
        if ($hex.StartsWith('504B0304') -or $hex.StartsWith('504B0506') -or
            $hex.StartsWith('377ABCAF271C') -or $hex.StartsWith('52617221')) {
            throw "Nested archive signature is forbidden: $Label"
        }
    }
}

function Assert-NoCompleteCommercialResource([string]$Path, [string]$Label) {
    $item = Get-Item -LiteralPath $Path
    $forbiddenSizes = @(
        [int64]60829, [int64]87274, [int64]114448, [int64]114770,
        [int64]160318119, [int64]180350761, [int64]181011663, [int64]181015052,
        [int64]25817936, [int64]26628080, [int64]27082040, [int64]27084368,
        [int64]11771536, [int64]12136240, [int64]12340600, [int64]12341648
    )
    $forbiddenHashes = @(
        'C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82',
        '5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984',
        'E119ED2375389FB8B05984534E0BC190788B5DC2B94EABFF9E6AF1B591C11746',
        '50875851C3F87F7D83DC5C1AF41D93D4E14043FE841D28A429644F60CDD13BA5',
        '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99',
        '3BC57379D9AF95E83A77C96C1EE2D104AAF4A8BEA1733EA33FC3D1BCF056D1A9',
        '02F0D4E09F8F1B13CD90D23A92F75302F49E34059CB659C4E59C1569EE2D3A8A',
        '9E0FFEAFCF3C50060E1E223988FD01BA2470987FB97A3B6DA75E0B7E3591AE9A',
        '414A8E98DCF0F52633CD039A74E97AE61A97D98A96684D450EBADD4C3C85CAEB',
        '951906C6870F60F9342E9A90DF8DBF920D555092D3E06B1B822A41448740DD61',
        'F2C76E79ADE0024F237DA1061E0DCFFCC18CB7D4DCCB54B7C72BFDD0F9CAC996',
        '99E5FBEA27ACE3BB88AEA6BC7DE97A4AE60707E48E0790442C6AE371DECB6B29',
        'DADBE4EEA223FD48CEFA9A93A08EF1F2458B3BD543ADFCEBD6D888B9EE2AFBB0',
        'C96704BF3A7FE1B29E3CB29361D1E56FCA8062CA73210CBCFCD73BE2E7C7CC66',
        '769C94F7C9E8E7EA5BF47644A56328EF2B8761DC43F9E6D26E46C127C716BC1B',
        '38F549994AFDB24BF60ABCDFF005D303E0C0BA4D7F420D8332954C66FFF0A55F'
    )
    if ($forbiddenSizes -contains [int64]$item.Length -or
        $forbiddenHashes -contains (Get-Sha256 $Path)) {
        throw "Package contains a complete commercial resource: $Label"
    }
}

if (-not (Test-Path -LiteralPath $PackageRoot -PathType Container)) {
    throw "Package root does not exist: $PackageRoot"
}
$rootItem = Get-Item -LiteralPath $PackageRoot -Force
if (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'Package root must not be a reparse point'
}

$jsonGuardPath = Join-Path $PackageRoot 'tools\JsonKeyGuard.cs'
if (-not (Test-Path -LiteralPath $jsonGuardPath -PathType Leaf) -or
    [int64](Get-Item -LiteralPath $jsonGuardPath).Length -ne 11304 -or
    (Get-Sha256 $jsonGuardPath) -ne '6A1ABEC0899A1D4256153E49E8204DAE343EC5D7887DB3047192A8168678DA60') {
    throw 'Package JSON key guard does not match the pinned raw UTF-8 verifier'
}
if (-not ('N16KrFileOnly.JsonKeyGuard' -as [type])) {
    Add-Type -Path $jsonGuardPath
}

$actual = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
$items = @(Get-ChildItem -LiteralPath $PackageRoot -Recurse -Force)
foreach ($item in $items) {
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Package contains a reparse point: $($item.FullName)"
    }
    if (-not $item.PSIsContainer) {
        $relative = $item.FullName.Substring($PackageRoot.TrimEnd('\').Length + 1).Replace('\', '/')
        if (-not $actual.Add($relative)) {
            throw "Package has a case-colliding or duplicate path: $relative"
        }
        if (-not $expected.Contains($relative)) {
            throw "Package path is outside the strict allowlist: $relative"
        }
        Assert-NotArchive $item.FullName $relative
        Assert-NoCompleteCommercialResource $item.FullName $relative
        if ([IO.Path]::GetExtension($relative).Equals('.json', [StringComparison]::OrdinalIgnoreCase)) {
            [N16KrFileOnly.JsonKeyGuard]::AssertFile($item.FullName)
        }
    }
}
if ($actual.Count -ne $expected.Count) {
    throw 'Package file count differs from the strict allowlist'
}
foreach ($relative in $expectedRelative) {
    if (-not $actual.Contains($relative)) {
        throw "Package is missing a required file: $relative"
    }
}

$manifest = Read-GuardedJson (Join-Path $PackageRoot 'release_manifest.json')
$manifestPaths = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
foreach ($file in @($manifest.files)) {
    $relative = ([string]$file.path).Replace('\', '/')
    if (-not $manifestPaths.Add($relative)) {
        throw 'Manifest contains a duplicate or case-colliding file path'
    }
    if (-not $expected.Contains($relative) -or $relative -eq 'release_manifest.json') {
        throw "Manifest path is outside the standalone audit allowlist: $relative"
    }
    $full = Join-Path $PackageRoot $relative.Replace('/', '\')
    if ([int64](Get-Item -LiteralPath $full).Length -ne [int64]$file.size -or
        (Get-Sha256 $full) -ne ([string]$file.sha256).ToUpperInvariant()) {
        throw "Manifest size/hash does not match the package tree: $relative"
    }
}
if ($manifestPaths.Count -ne ($expected.Count - 1)) {
    throw 'Manifest inventory count is not exact'
}
foreach ($relative in $expectedRelative | Where-Object { $_ -ne 'release_manifest.json' }) {
    if (-not $manifestPaths.Contains($relative)) {
        throw "Manifest omits a required file: $relative"
    }
}

if ($manifest.schema -ne 'nobu16.korean-file-only-release.v2' -or
    $manifest.release_id -ne 'msgui-full-font-v4-v0.3' -or
    $manifest.release_name -ne 'NOBU16 Korean MSGUI Full / Font-v4 file-only v0.3' -or
    (($manifest.release_eligible -eq $true -and $manifest.version -ne '0.3') -or
        ($manifest.release_eligible -eq $false -and $manifest.version -ne '0.3-dev')) -or
    $manifest.architecture -ne 'file-only-offline' -or
    $manifest.process_memory_access -ne $false -or
    $manifest.executable_modified -ne $false -or
    $manifest.registry_modified -ne $false -or
    $manifest.launches_game -ne $false -or
    $manifest.resident_component -ne $false -or
    $manifest.commercial_full_files_included -ne $false -or
    $manifest.requires_process_running -ne $false -or
    $manifest.payload_format -ne 'recipes-and-deltas-only') {
    throw 'Manifest fails the standalone pre-execution safety contract'
}

$legacyReleaseId = [string]::Concat('msgui-', 'p', '3-font-', 'v', '3-v0', '.2')
$legacyReleaseName = [string]::Concat('NOBU16 Korean MSGUI ', 'P', '3 / Font-', 'v', '3 file-only v0', '.2')
$legacyBackupName = [string]::Concat('msgui_', 'p', '3_font_', 'v', '3_v0', '_2')
$legacyP4ReleaseId = [string]::Concat('msgui-', 'p', '4-font-', 'v', '4-v0', '.3')
$legacyP4ReleaseName = [string]::Concat('NOBU16 Korean MSGUI ', 'P', '4 / Font-', 'v', '4 file-only v0', '.3')
$legacyP4BackupName = [string]::Concat('msgui_', 'p', '4_font_', 'v', '4_v0', '_3')
$strictUtf8 = New-Object Text.UTF8Encoding($false, $true)
foreach ($relative in $expectedRelative) {
    if ([IO.Path]::GetExtension($relative) -in @('.ps1', '.cs', '.md', '.bat', '.json', '.jsonl')) {
        $path = Join-Path $PackageRoot $relative.Replace('/', '\')
        $text = $strictUtf8.GetString([IO.File]::ReadAllBytes($path))
        if ($text.Contains($legacyReleaseId) -or $text.Contains($legacyReleaseName) -or
            $text.Contains($legacyBackupName) -or $text.Contains($legacyP4ReleaseId) -or
            $text.Contains($legacyP4ReleaseName) -or $text.Contains($legacyP4BackupName)) {
            throw "Package contains a legacy release identity: $relative"
        }
    }
}

$trustedTemplate = Join-Path $PSScriptRoot 'template'
$criticalPaths = @(
    'APPLY_KOREAN_PATCH.bat', 'RESTORE_ORIGINALS.bat', 'VERIFY_PACKAGE.bat',
    'tools/FileRecipeCore.cs', 'tools/Invoke-FileOnlyPatch.ps1', 'tools/JsonKeyGuard.cs'
)
$criticalPins = @{
    'APPLY_KOREAN_PATCH.bat' = '270|4A3F9325C1D8BFBF96548AB8D8D37EBCF6F66CB5A9572AA3BB459D2EB97B74CF'
    'RESTORE_ORIGINALS.bat' = '266|5E5F629256C6C9E4151F9C1F81E2F256CF9A51836A5F8ABD2E10780D8152AFAE'
    'VERIFY_PACKAGE.bat' = '271|176238C8C94925231B5B3FFB3505B45987CB90F75399046459847B517448B088'
    'tools/FileRecipeCore.cs' = '28466|04643FDDA1617663DB4B2812582C5F87FA9D55A46D1861F22570C7C1B7266B79'
    'tools/Invoke-FileOnlyPatch.ps1' = '76603|79DF6A85D43D9467EF53E508852F3D0A9CA09618766CC9AEE33E80A49BD5D01A'
    'tools/JsonKeyGuard.cs' = '11304|6A1ABEC0899A1D4256153E49E8204DAE343EC5D7887DB3047192A8168678DA60'
}
foreach ($relative in $criticalPaths) {
    $trusted = Join-Path $trustedTemplate $relative.Replace('/', '\')
    $packaged = Join-Path $PackageRoot $relative.Replace('/', '\')
    $pinParts = ([string]$criticalPins[$relative]).Split('|')
    $expectedSize = [int64]$pinParts[0]
    $expectedHash = $pinParts[1]
    if (-not (Test-Path -LiteralPath $trusted -PathType Leaf) -or
        [int64](Get-Item -LiteralPath $packaged).Length -ne $expectedSize -or
        (Get-Sha256 $packaged) -ne $expectedHash -or
        [int64](Get-Item -LiteralPath $trusted).Length -ne $expectedSize -or
        (Get-Sha256 $trusted) -ne $expectedHash -or
        [int64](Get-Item -LiteralPath $trusted).Length -ne [int64](Get-Item -LiteralPath $packaged).Length -or
        (Get-Sha256 $trusted) -ne (Get-Sha256 $packaged)) {
        throw "Executable package code differs from the trusted external pin: $relative"
    }
}

$forbiddenCapabilities = @(
    'WriteProcessMemory', 'ReadProcessMemory', 'VirtualAllocEx', 'OpenProcess(',
    'CreateRemoteThread', 'SetWindowsHookEx', 'NtWriteVirtualMemory',
    'Microsoft.Win32.Registry', 'RegistryKey', 'reg.exe', 'rundll32',
    'Process.Start(', 'Start-Process', 'DllImport'
)
foreach ($relative in $criticalPaths) {
    $path = Join-Path $PackageRoot $relative.Replace('/', '\')
    $text = [IO.File]::ReadAllText($path, (New-Object Text.UTF8Encoding($false, $true)))
    foreach ($pattern in $forbiddenCapabilities) {
        if ($text.IndexOf($pattern, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
            throw "Forbidden capability marker '$pattern' appears in executable package code: $relative"
        }
    }
}

# Only execute the packaged verifier after the standalone inventory, hashes,
# external code pins, and capability scan have all succeeded.
$installer = Join-Path $PackageRoot 'tools\Invoke-FileOnlyPatch.ps1'
& 'C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo -NoProfile `
    -ExecutionPolicy Bypass -File $installer -Action Verify | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Packaged Verify failed with exit code $LASTEXITCODE"
}

if ($ZipPath) {
    $ZipPath = [IO.Path]::GetFullPath($ZipPath)
    if (-not (Test-Path -LiteralPath $ZipPath -PathType Leaf)) {
        throw "ZIP does not exist: $ZipPath"
    }
    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        $prefix = [IO.Path]::GetFileName($PackageRoot) + '/'
        $zipFiles = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
        foreach ($entry in $archive.Entries) {
            $name = $entry.FullName
            if ($name.Contains('\') -or $name.StartsWith('/') -or $name.Contains(':') -or
                -not $name.StartsWith($prefix, [StringComparison]::Ordinal)) {
                throw "Unsafe ZIP member path: $name"
            }
            $parts = @($name.Split('/') | Where-Object { $_ -ne '' })
            if ($parts -contains '.' -or $parts -contains '..') {
                throw "ZIP member traversal is forbidden: $name"
            }
            $unixType = (($entry.ExternalAttributes -shr 16) -band 0xF000)
            if ($unixType -eq 0xA000) {
                throw "ZIP symlink is forbidden: $name"
            }
            if ([string]::IsNullOrEmpty($entry.Name)) {
                continue
            }
            $relative = $name.Substring($prefix.Length)
            if (-not $zipFiles.Add($relative)) {
                throw "ZIP contains a duplicate or case-colliding member: $relative"
            }
            if (-not $expected.Contains($relative)) {
                throw "ZIP member is outside the strict allowlist: $relative"
            }
            $extension = [IO.Path]::GetExtension($relative).ToLowerInvariant()
            if ($extension -in @('.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.xz', '.cab')) {
                throw "ZIP contains a nested archive: $relative"
            }
            $folderPath = Join-Path $PackageRoot $relative.Replace('/', '\')
            if ([int64]$entry.Length -ne [int64](Get-Item -LiteralPath $folderPath).Length) {
                throw "ZIP member size differs from the audited folder: $relative"
            }
            $stream = $entry.Open()
            try { $zipHash = Get-StreamSha256 $stream } finally { $stream.Dispose() }
            if ($zipHash -ne (Get-Sha256 $folderPath)) {
                throw "ZIP member hash differs from the audited folder: $relative"
            }
            if ($extension -eq '.json') {
                $jsonStream = $entry.Open()
                $buffer = New-Object IO.MemoryStream
                try {
                    $jsonStream.CopyTo($buffer)
                    [N16KrFileOnly.JsonKeyGuard]::AssertNoDuplicateKeys($buffer.ToArray())
                }
                finally {
                    $buffer.Dispose()
                    $jsonStream.Dispose()
                }
            }
        }
        if ($zipFiles.Count -ne $expected.Count) {
            throw 'ZIP file inventory count is not exact'
        }
        foreach ($relative in $expectedRelative) {
            if (-not $zipFiles.Contains($relative)) {
                throw "ZIP is missing a required file: $relative"
            }
        }
    }
    finally {
        $archive.Dispose()
    }
}

[pscustomobject]@{
    schema = 'nobu16.file-only-public-audit.v2'
    passed = $true
    package_root = $PackageRoot
    package_file_count = $expected.Count
    manifest_sha256 = Get-Sha256 (Join-Path $PackageRoot 'release_manifest.json')
    zip_path = $ZipPath
    zip_sha256 = if ($ZipPath) { Get-Sha256 $ZipPath } else { $null }
}
