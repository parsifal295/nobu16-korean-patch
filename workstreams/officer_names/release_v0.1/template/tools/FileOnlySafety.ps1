Set-StrictMode -Version Latest

function Get-FileOnlyFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Assert-SafeRelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [string]$Label = 'relative path'
    )
    if ([string]::IsNullOrWhiteSpace($RelativePath) -or
        [System.IO.Path]::IsPathRooted($RelativePath) -or
        $RelativePath.Contains('\') -or
        $RelativePath.Contains(':') -or
        $RelativePath.StartsWith('/') -or
        $RelativePath.EndsWith('/') -or
        $RelativePath -notmatch '\A[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\z') {
        throw "$Label is not a canonical package-relative path: $RelativePath"
    }
    foreach ($segment in $RelativePath.Split('/')) {
        if ($segment -eq '.' -or $segment -eq '..') {
            throw "$Label contains path traversal: $RelativePath"
        }
    }
}

function Resolve-FileOnlyChild {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [string]$Label = 'path'
    )
    Assert-SafeRelativePath $RelativePath $Label
    $fullRoot = (Get-FileOnlyFullPath $Root).TrimEnd('\')
    $candidate = Get-FileOnlyFullPath (Join-Path $fullRoot ($RelativePath.Replace('/', '\')))
    $prefix = $fullRoot + '\'
    if (-not $candidate.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label escapes its approved root: $RelativePath"
    }
    return $candidate
}

function Assert-OrdinaryExistingPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Label = 'path'
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Label is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "$Label must not be a symbolic link, junction, mount point, or other reparse point: $Path"
    }
}

function Assert-OrdinaryPathFromRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Label = 'path'
    )
    $fullRoot = (Get-FileOnlyFullPath $Root).TrimEnd('\')
    $fullPath = Get-FileOnlyFullPath $Path
    if ($fullPath -ne $fullRoot -and
        -not $fullPath.StartsWith($fullRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label is outside its approved root: $fullPath"
    }
    Assert-OrdinaryExistingPath $fullRoot "$Label root"
    if ($fullPath -eq $fullRoot) { return }
    $relative = $fullPath.Substring($fullRoot.Length + 1)
    $cursor = $fullRoot
    foreach ($segment in $relative.Split('\')) {
        $cursor = Join-Path $cursor $segment
        if (Test-Path -LiteralPath $cursor) {
            Assert-OrdinaryExistingPath $cursor $Label
        }
    }
}

function Assert-ExactCaseRelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [string]$Label = 'path'
    )
    Assert-SafeRelativePath $RelativePath $Label
    $cursor = Get-FileOnlyFullPath $Root
    foreach ($segment in $RelativePath.Split('/')) {
        if (-not (Test-Path -LiteralPath $cursor -PathType Container)) {
            throw "$Label parent directory is missing: $cursor"
        }
        $matches = @(Get-ChildItem -LiteralPath $cursor -Force | Where-Object {
            [string]::Equals($_.Name, $segment, [StringComparison]::OrdinalIgnoreCase)
        })
        if ($matches.Count -ne 1) {
            throw "$Label has a missing or case-colliding segment '$segment' under $cursor"
        }
        if ($matches[0].Name -cne $segment) {
            throw "$Label uses unexpected path casing: expected '$segment', found '$($matches[0].Name)'"
        }
        if (($matches[0].Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "$Label traverses a reparse point: $($matches[0].FullName)"
        }
        $cursor = $matches[0].FullName
    }
    return $cursor
}

function Assert-UniqueCanonicalPaths {
    param(
        [Parameter(Mandatory = $true)][string[]]$RelativePaths,
        [string]$Label = 'path inventory'
    )
    $folded = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($relative in $RelativePaths) {
        Assert-SafeRelativePath $relative $Label
        if (-not $folded.Add($relative)) {
            throw "$Label contains a duplicate or case-colliding path: $relative"
        }
    }
}

function Get-OrdinaryTreeFiles {
    param([Parameter(Mandatory = $true)][string]$Root)
    $fullRoot = Get-FileOnlyFullPath $Root
    Assert-OrdinaryExistingPath $fullRoot 'tree root'
    $queue = New-Object 'System.Collections.Generic.Queue[string]'
    $queue.Enqueue($fullRoot)
    $result = New-Object 'System.Collections.Generic.List[object]'
    while ($queue.Count -gt 0) {
        $directory = $queue.Dequeue()
        $names = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
        foreach ($child in @(Get-ChildItem -LiteralPath $directory -Force)) {
            if (-not $names.Add($child.Name)) {
                throw "Directory contains duplicate or case-colliding entries: $directory / $($child.Name)"
            }
            if (($child.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Tree contains a symbolic link, junction, mount point, or other reparse point: $($child.FullName)"
            }
            if ($child.PSIsContainer) {
                $queue.Enqueue($child.FullName)
            }
            else {
                $relative = $child.FullName.Substring($fullRoot.TrimEnd('\').Length + 1).Replace('\', '/')
                $result.Add([pscustomobject]@{ RelativePath = $relative; FullPath = $child.FullName })
            }
        }
    }
    [string[]]$paths = @($result | ForEach-Object { [string]$_.RelativePath })
    Assert-UniqueCanonicalPaths $paths 'tree file inventory'
    return $result.ToArray()
}

function Assert-ExactOrdinaryFileSet {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string[]]$ExpectedRelativePaths,
        [string]$Label = 'file tree'
    )
    Assert-UniqueCanonicalPaths $ExpectedRelativePaths "$Label expected paths"
    [string[]]$actual = @(Get-OrdinaryTreeFiles $Root | ForEach-Object { [string]$_.RelativePath })
    [string[]]$expected = @($ExpectedRelativePaths)
    [Array]::Sort($actual, [StringComparer]::Ordinal)
    [Array]::Sort($expected, [StringComparer]::Ordinal)
    if (($actual -join "`n") -cne ($expected -join "`n")) {
        throw "$Label contains a missing, additional, or case-colliding file."
    }
}

function Read-StrictFileOnlyJson {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not ('N16KrFileOnly.JsonKeyGuard' -as [type])) {
        throw 'Strict JSON key guard is not loaded.'
    }
    [byte[]]$bytes = [System.IO.File]::ReadAllBytes($Path)
    [N16KrFileOnly.JsonKeyGuard]::AssertNoDuplicateKeys($bytes)
    $encoding = New-Object System.Text.UTF8Encoding($false, $true)
    return ($encoding.GetString($bytes) | ConvertFrom-Json)
}

function Assert-ExactObjectProperties {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string[]]$Expected,
        [string]$Label = 'JSON object'
    )
    if ($null -eq $Object -or $Object -isnot [Management.Automation.PSCustomObject]) {
        throw "$Label must be an object."
    }
    [string[]]$actual = @($Object.PSObject.Properties.Name)
    [string[]]$wanted = @($Expected)
    [Array]::Sort($actual, [StringComparer]::Ordinal)
    [Array]::Sort($wanted, [StringComparer]::Ordinal)
    if ($actual.Count -ne $wanted.Count) {
        throw "$Label has an unexpected property count."
    }
    for ($index = 0; $index -lt $actual.Count; $index++) {
        if ($actual[$index] -ne $wanted[$index]) {
            throw "$Label contains a missing, additional, or case-colliding property: $($actual[$index])"
        }
    }
}

function Assert-PinnedArtifactSet {
    param(
        [Parameter(Mandatory = $true)][object[]]$Artifacts,
        [Parameter(Mandatory = $true)][string[]]$ExpectedRelativePaths,
        [string]$Root,
        [string]$Label = 'artifact pins'
    )
    if ($Artifacts.Count -ne $ExpectedRelativePaths.Count) {
        throw "$Label has an unexpected artifact count."
    }
    Assert-UniqueCanonicalPaths $ExpectedRelativePaths "$Label expected paths"
    for ($index = 0; $index -lt $ExpectedRelativePaths.Count; $index++) {
        $artifact = $Artifacts[$index]
        Assert-ExactObjectProperties $artifact @('path', 'sha256', 'size') "$Label item $index"
        if ([string]$artifact.path -cne $ExpectedRelativePaths[$index] -or
            [int64]$artifact.size -le 0 -or
            [string]$artifact.sha256 -notmatch '\A[0-9A-F]{64}\z') {
            throw "$Label item $index is not the exact reviewed path, size, and SHA-256 pin."
        }
        if (-not [string]::IsNullOrWhiteSpace($Root)) {
            $path = Resolve-FileOnlyChild $Root ([string]$artifact.path) "$Label item $index"
            Assert-OrdinaryPathFromRoot $Root $path "$Label item $index"
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
                throw "$Label item $index is missing: $path"
            }
            $item = Get-Item -LiteralPath $path -Force
            $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToUpperInvariant()
            if ([int64]$item.Length -ne [int64]$artifact.size -or
                $hash -ne ([string]$artifact.sha256).ToUpperInvariant()) {
                throw "$Label item $index bytes differ from the reviewed pin."
            }
        }
    }
}
