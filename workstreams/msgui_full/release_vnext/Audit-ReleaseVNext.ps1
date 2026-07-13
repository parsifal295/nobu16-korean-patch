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

$trustedTemplate = Join-Path $PSScriptRoot 'template'
$criticalPaths = @(
    'APPLY_KOREAN_PATCH.bat', 'RESTORE_ORIGINALS.bat', 'VERIFY_PACKAGE.bat',
    'tools/FileRecipeCore.cs', 'tools/Invoke-FileOnlyPatch.ps1', 'tools/JsonKeyGuard.cs'
)
$criticalPins = @{
    'APPLY_KOREAN_PATCH.bat' = '270|4A3F9325C1D8BFBF96548AB8D8D37EBCF6F66CB5A9572AA3BB459D2EB97B74CF'
    'RESTORE_ORIGINALS.bat' = '266|5E5F629256C6C9E4151F9C1F81E2F256CF9A51836A5F8ABD2E10780D8152AFAE'
    'VERIFY_PACKAGE.bat' = '271|176238C8C94925231B5B3FFB3505B45987CB90F75399046459847B517448B088'
    'tools/FileRecipeCore.cs' = '27726|D6CB27BD8C1FA8567B04B1852C8478B03BA29D533DCE8D980DE0E7184AF395FC'
    'tools/Invoke-FileOnlyPatch.ps1' = '63305|02697DA7DD8CE588519B0CEE4CE13A2F94CD99A406A6BB7DB6AD20FE70E842DB'
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
