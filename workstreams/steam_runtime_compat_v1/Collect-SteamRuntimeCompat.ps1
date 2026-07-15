[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$GameRoot = (Get-Location).Path,

    [string]$ExpectedReleaseMetadataPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$CollectorVersion = '1.1.0'
$ResultSchemaVersion = '1.1'
$SteamAppId = '1336980'
if ([string]::IsNullOrWhiteSpace($ExpectedReleaseMetadataPath)) {
    $ExpectedReleaseMetadataPath = Join-Path $PSScriptRoot 'expected_release.v0.4.1.json'
}

function ConvertTo-SafeRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $normalized = $Path.Replace('\', '/').Trim()
    if ([string]::IsNullOrWhiteSpace($normalized) -or
        [System.IO.Path]::IsPathRooted($Path) -or
        $normalized.StartsWith('/') -or
        $normalized -match '(^|/)\.\.($|/)' -or
        $normalized -match '(^|/)\.($|/)' -or
        $normalized.Contains(':')) {
        throw "Unsafe relative path in release metadata: $Path"
    }

    return $normalized
}

function Read-ExpectedReleaseMetadata {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Expected-release metadata was not found: $Path"
    }

    $metadata = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]$metadata.schema_version -ne '1.0' -or
        [string]::IsNullOrWhiteSpace([string]$metadata.release.tag) -or
        [string]::IsNullOrWhiteSpace([string]$metadata.release.asset_name)) {
        throw 'Expected-release metadata header is invalid.'
    }

    if ([string]$metadata.release.asset_sha256 -notmatch '^[0-9A-Fa-f]{64}$' -or
        [int64]$metadata.release.asset_size -lt 0) {
        throw 'Expected-release asset pin is invalid.'
    }

    $pins = [ordered]@{}
    foreach ($file in @($metadata.files)) {
        $relativePath = ConvertTo-SafeRelativePath -Path ([string]$file.relative_path)
        $sha256 = ([string]$file.sha256).ToUpperInvariant()
        $size = [int64]$file.size
        if ($sha256 -notmatch '^[0-9A-F]{64}$' -or $size -lt 0) {
            throw "Invalid file pin: $relativePath"
        }
        if ($pins.Contains($relativePath)) {
            throw "Duplicate file pin: $relativePath"
        }

        $pins[$relativePath] = [pscustomobject][ordered]@{
            relative_path = $relativePath
            role = [string]$file.role
            size = $size
            sha256 = $sha256
        }
    }

    if ($pins.Count -eq 0) {
        throw 'Expected-release metadata contains no file pins.'
    }

    return [pscustomobject][ordered]@{
        schema_version = [string]$metadata.schema_version
        tag = [string]$metadata.release.tag
        asset_name = [string]$metadata.release.asset_name
        asset_size = [int64]$metadata.release.asset_size
        asset_sha256 = ([string]$metadata.release.asset_sha256).ToUpperInvariant()
        pins = $pins
    }
}

function Get-ProbedFile {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.DirectoryInfo]$Root,

        [Parameter(Mandatory = $true)]
        [string]$RelativePath,

        [Parameter(Mandatory = $true)]
        [string]$Role,

        [AllowNull()]
        [object]$ExpectedPin
    )

    $nativeRelativePath = $RelativePath.Replace(
        '/',
        [System.IO.Path]::DirectorySeparatorChar
    )
    $absolutePath = Join-Path $Root.FullName $nativeRelativePath
    $exists = Test-Path -LiteralPath $absolutePath -PathType Leaf
    $size = $null
    $sha256 = $null
    $fileVersion = $null
    $productVersion = $null
    $readErrorType = $null

    if ($exists) {
        try {
            $item = Get-Item -LiteralPath $absolutePath
            $size = [int64]$item.Length
            $sha256 = (Get-FileHash -LiteralPath $absolutePath -Algorithm SHA256).Hash.ToUpperInvariant()

            if ($item.Extension -ieq '.exe' -or $item.Extension -ieq '.dll') {
                $fileVersion = [string]$item.VersionInfo.FileVersion
                $productVersion = [string]$item.VersionInfo.ProductVersion
                if ([string]::IsNullOrWhiteSpace($fileVersion)) {
                    $fileVersion = $null
                }
                if ([string]::IsNullOrWhiteSpace($productVersion)) {
                    $productVersion = $null
                }
            }
        }
        catch {
            $readErrorType = $_.Exception.GetType().FullName
        }
    }

    $expectedRelease = $null
    $matchesExpectedRelease = $null
    if ($null -ne $ExpectedPin) {
        $expectedRelease = [pscustomobject][ordered]@{
            size = [int64]$ExpectedPin.size
            sha256 = [string]$ExpectedPin.sha256
        }
        $matchesExpectedRelease = (
            $exists -and
            $null -eq $readErrorType -and
            $size -eq [int64]$ExpectedPin.size -and
            $sha256 -eq [string]$ExpectedPin.sha256
        )
    }

    return [pscustomobject][ordered]@{
        relative_path = $RelativePath
        role = $Role
        exists = [bool]$exists
        size = $size
        sha256 = $sha256
        file_version = $fileVersion
        product_version = $productVersion
        expected_release = $expectedRelease
        matches_expected_release = $matchesExpectedRelease
        read_error_type = $readErrorType
    }
}

function Find-SteamAppManifest {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.DirectoryInfo]$Root,

        [Parameter(Mandatory = $true)]
        [string]$AppId
    )

    $cursor = $Root
    while ($null -ne $cursor) {
        if ($cursor.Name -ieq 'steamapps') {
            $candidate = Join-Path $cursor.FullName "appmanifest_$AppId.acf"
            if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                return $candidate
            }
        }
        $cursor = $cursor.Parent
    }

    return $null
}

function Read-SteamAppManifest {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $sections = [System.Collections.Generic.List[string]]::new()
    $depotIds = [System.Collections.Generic.List[string]]::new()
    $pendingSection = $null
    $appId = $null
    $buildId = $null
    $userLanguage = $null
    $mountedLanguage = $null

    foreach ($line in @(Get-Content -LiteralPath $Path -Encoding UTF8)) {
        $trimmed = $line.Trim()
        if ($trimmed -match '^"(?<key>(?:\\.|[^"])*)"\s+"(?<value>(?:\\.|[^"])*)"\s*$') {
            $key = [string]$Matches.key
            $value = [string]$Matches.value
            $leaf = if ($sections.Count -gt 0) {
                $sections[$sections.Count - 1]
            }
            else {
                $null
            }

            if ($key -ieq 'appid' -and $null -eq $appId) {
                $appId = $value
            }
            elseif ($key -ieq 'buildid' -and $leaf -ieq 'AppState') {
                $buildId = $value
            }
            elseif ($key -ieq 'language' -and $leaf -ieq 'UserConfig') {
                $userLanguage = $value
            }
            elseif ($key -ieq 'language' -and $leaf -ieq 'MountedConfig') {
                $mountedLanguage = $value
            }

            $pendingSection = $null
            continue
        }

        if ($trimmed -match '^"(?<key>(?:\\.|[^"])*)"\s*$') {
            $pendingSection = [string]$Matches.key
            continue
        }

        if ($trimmed -eq '{') {
            if ($null -ne $pendingSection) {
                $parent = if ($sections.Count -gt 0) {
                    $sections[$sections.Count - 1]
                }
                else {
                    $null
                }
                if ($parent -ieq 'InstalledDepots' -and
                    $pendingSection -match '^\d+$' -and
                    -not $depotIds.Contains($pendingSection)) {
                    $depotIds.Add($pendingSection)
                }
                $sections.Add($pendingSection)
                $pendingSection = $null
            }
            continue
        }

        if ($trimmed -eq '}') {
            if ($sections.Count -gt 0) {
                $sections.RemoveAt($sections.Count - 1)
            }
            $pendingSection = $null
        }
    }

    return [pscustomobject][ordered]@{
        app_id = $appId
        build_id = $buildId
        user_language = $userLanguage
        mounted_language = $mountedLanguage
        installed_depot_ids = @($depotIds | Sort-Object)
    }
}

function Get-LauncherLanguageRegistryProbe {
    $keyPaths = @(
        'HKCU:\Software\KoeiTecmo\NOBU16\Configs',
        'HKCU:\Software\KoeiTecmo\NOBU16_SC\Configs',
        'HKCU:\Software\KoeiTecmo\NOBU16_TC\Configs',
        'HKCU:\Software\KoeiTecmo\NOBU16_EN\Configs'
    )
    $entries = @()

    foreach ($keyPath in $keyPaths) {
        $exists = $false
        $languagePresent = $false
        $languageValue = $null
        $languageKind = $null
        $readErrorType = $null

        try {
            if (Test-Path -LiteralPath $keyPath) {
                $exists = $true
                $key = Get-Item -LiteralPath $keyPath
                if (@($key.GetValueNames()) -icontains 'LANGUAGE') {
                    $languagePresent = $true
                    $languageValue = $key.GetValue('LANGUAGE')
                    $languageKind = $key.GetValueKind('LANGUAGE').ToString()
                }
            }
        }
        catch {
            $readErrorType = $_.Exception.GetType().FullName
        }

        $entries += [pscustomobject][ordered]@{
            key = $keyPath.Replace('HKCU:', 'HKEY_CURRENT_USER')
            exists = [bool]$exists
            language_present = [bool]$languagePresent
            language_value = $languageValue
            language_kind = $languageKind
            read_error_type = $readErrorType
        }
    }

    return $entries
}

function Get-WindowsLocaleProbe {
    $source = 'Get-WinSystemLocale'
    try {
        $locale = Get-WinSystemLocale
    }
    catch {
        $source = 'CultureInfo.InstalledUICulture fallback'
        $locale = [System.Globalization.CultureInfo]::InstalledUICulture
    }

    return [pscustomobject][ordered]@{
        source = $source
        name = [string]$locale.Name
        english_name = [string]$locale.EnglishName
        lcid = [int]$locale.LCID
        values_are_culture_defaults = $true
        culture_default_ansi_code_page = [int]$locale.TextInfo.ANSICodePage
        culture_default_oem_code_page = [int]$locale.TextInfo.OEMCodePage
    }
}

function Get-SystemNlsCodePageProbe {
    $keyPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage'
    $valueNames = @('ACP', 'OEMCP', 'MACCP')
    $keyExists = $false
    $readErrorType = $null
    $values = [ordered]@{}

    foreach ($valueName in $valueNames) {
        $values[$valueName.ToLowerInvariant()] = [pscustomobject][ordered]@{
            name = $valueName
            present = $false
            raw_value = $null
            registry_kind = $null
            parsed_code_page = $null
        }
    }

    try {
        if (Test-Path -LiteralPath $keyPath) {
            $keyExists = $true
            $key = Get-Item -LiteralPath $keyPath
            $availableNames = @($key.GetValueNames())
            foreach ($valueName in $valueNames) {
                if ($availableNames -icontains $valueName) {
                    $rawValue = $key.GetValue($valueName)
                    $parsedCodePage = 0
                    $hasParsedCodePage = [int]::TryParse(
                        [string]$rawValue,
                        [ref]$parsedCodePage
                    )
                    $values[$valueName.ToLowerInvariant()] = [pscustomobject][ordered]@{
                        name = $valueName
                        present = $true
                        raw_value = $rawValue
                        registry_kind = $key.GetValueKind($valueName).ToString()
                        parsed_code_page = if ($hasParsedCodePage) {
                            $parsedCodePage
                        }
                        else {
                            $null
                        }
                    }
                }
            }
        }
    }
    catch {
        $readErrorType = $_.Exception.GetType().FullName
    }

    return [pscustomobject][ordered]@{
        key = $keyPath.Replace('HKLM:', 'HKEY_LOCAL_MACHINE')
        registry_read_only = $true
        key_exists = [bool]$keyExists
        acp = $values.acp
        oemcp = $values.oemcp
        maccp = $values.maccp
        read_error_type = $readErrorType
    }
}

$rootItem = Get-Item -LiteralPath $GameRoot
if (-not $rootItem.PSIsContainer) {
    throw "GameRoot is not a directory: $GameRoot"
}
$root = [System.IO.DirectoryInfo]$rootItem
$expected = Read-ExpectedReleaseMetadata -Path $ExpectedReleaseMetadataPath

$probeDefinitions = [ordered]@{
    'NOBU16PK.exe' = 'pk_executable'
    'NOBU16_Launcher.exe' = 'official_launcher'
    'steam_api64.dll' = 'steam_runtime_marker'
    'UpdateVer.txt' = 'game_revision_marker'
    'RES_SC/res_lang.bin' = 'sc_shared_font_archive'
    'RES_SC/res_lang_exp.bin' = 'sc_shared_expansion_archive'
    'RES_SC_PK/res_lang_pk.bin' = 'sc_pk_resource_archive'
}

foreach ($pin in $expected.pins.Values) {
    if (-not $probeDefinitions.Contains($pin.relative_path)) {
        $probeDefinitions[$pin.relative_path] = $pin.role
    }
}

$files = @()
foreach ($definition in $probeDefinitions.GetEnumerator()) {
    $relativePath = [string]$definition.Key
    $expectedPin = if ($expected.pins.Contains($relativePath)) {
        $expected.pins[$relativePath]
    }
    else {
        $null
    }
    $files += Get-ProbedFile `
        -Root $root `
        -RelativePath $relativePath `
        -Role ([string]$definition.Value) `
        -ExpectedPin $expectedPin
}

$releaseFiles = @($files | Where-Object { $null -ne $_.expected_release })
$releaseMismatches = @(
    $releaseFiles |
        Where-Object { $_.matches_expected_release -ne $true } |
        ForEach-Object { $_.relative_path }
)

$fileByPath = [ordered]@{}
foreach ($file in $files) {
    $fileByPath[$file.relative_path] = $file
}

$manifestPath = Find-SteamAppManifest -Root $root -AppId $SteamAppId
$steamManifest = [pscustomobject][ordered]@{
    present = $false
    file_name = "appmanifest_$SteamAppId.acf"
    location_class = $null
    size = $null
    sha256 = $null
    app_id = $null
    build_id = $null
    user_language = $null
    mounted_language = $null
    installed_depot_ids = @()
    read_error_type = $null
}

if ($null -ne $manifestPath) {
    try {
        $manifestItem = Get-Item -LiteralPath $manifestPath
        $parsedManifest = Read-SteamAppManifest -Path $manifestPath
        $steamManifest = [pscustomobject][ordered]@{
            present = $true
            file_name = $manifestItem.Name
            location_class = 'nearest_ancestor_steamapps'
            size = [int64]$manifestItem.Length
            sha256 = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToUpperInvariant()
            app_id = $parsedManifest.app_id
            build_id = $parsedManifest.build_id
            user_language = $parsedManifest.user_language
            mounted_language = $parsedManifest.mounted_language
            installed_depot_ids = @($parsedManifest.installed_depot_ids)
            read_error_type = $null
        }
    }
    catch {
        $steamManifest.present = $true
        $steamManifest.location_class = 'nearest_ancestor_steamapps'
        $steamManifest.read_error_type = $_.Exception.GetType().FullName
    }
}

$underSteamAppsCommon = (
    $null -ne $root.Parent -and
    $root.Parent.Name -ieq 'common' -and
    $null -ne $root.Parent.Parent -and
    $root.Parent.Parent.Name -ieq 'steamapps'
)

$launcherRegistry = @(Get-LauncherLanguageRegistryProbe)
$selectedLauncherLanguage = $null
foreach ($entry in $launcherRegistry) {
    if ($entry.language_present -and $null -eq $selectedLauncherLanguage) {
        $selectedLauncherLanguage = [pscustomobject][ordered]@{
            key = $entry.key
            value = $entry.language_value
            kind = $entry.language_kind
        }
    }
}

$fontMatch = $false
if ($fileByPath.Contains('RES_SC/res_lang.bin')) {
    $fontMatch = $fileByPath['RES_SC/res_lang.bin'].matches_expected_release -eq $true
}
$msguiMatch = $false
if ($fileByPath.Contains('MSG_PK/SC/msgui.bin')) {
    $msguiMatch = $fileByPath['MSG_PK/SC/msgui.bin'].matches_expected_release -eq $true
}

$pkExecutableFile = $fileByPath['NOBU16PK.exe']
$runtimeExecutable = [pscustomobject][ordered]@{
    relative_path = $pkExecutableFile.relative_path
    exists = $pkExecutableFile.exists
    size = $pkExecutableFile.size
    sha256 = $pkExecutableFile.sha256
    file_version = $pkExecutableFile.file_version
    product_version = $pkExecutableFile.product_version
    read_error_type = $pkExecutableFile.read_error_type
}

$result = [pscustomobject][ordered]@{
    schema_version = $ResultSchemaVersion
    collector_version = $CollectorVersion
    collected_at_utc = [DateTime]::UtcNow.ToString('o')
    game_root = [pscustomobject][ordered]@{
        leaf_name = $root.Name
        under_steamapps_common = [bool]$underSteamAppsCommon
        absolute_path_included = $false
    }
    runtime_executable = $runtimeExecutable
    platform = [pscustomobject][ordered]@{
        windows_system_locale = Get-WindowsLocaleProbe
        system_nls_code_pages = Get-SystemNlsCodePageProbe
        powershell_edition = [string]$PSVersionTable.PSEdition
        powershell_version = [string]$PSVersionTable.PSVersion
        process_is_64_bit = [bool][Environment]::Is64BitProcess
        os_is_64_bit = [bool][Environment]::Is64BitOperatingSystem
    }
    launcher = [pscustomobject][ordered]@{
        registry_read_only = $true
        registry_entries = @($launcherRegistry)
        selected_language_raw = $selectedLauncherLanguage
        language_mapping_assumed = $false
    }
    steam = [pscustomobject][ordered]@{
        app_id_requested = $SteamAppId
        detected_from_nearby_appmanifest = [bool]$steamManifest.present
        appmanifest = $steamManifest
    }
    expected_release = [pscustomobject][ordered]@{
        tag = $expected.tag
        asset_name = $expected.asset_name
        asset_size = $expected.asset_size
        asset_sha256 = $expected.asset_sha256
        pinned_file_count = [int]$expected.pins.Count
    }
    files = @($files)
    summary = [pscustomobject][ordered]@{
        expected_release_file_count = [int]$releaseFiles.Count
        matched_release_file_count = [int]($releaseFiles.Count - $releaseMismatches.Count)
        all_expected_release_files_match = [bool]($releaseMismatches.Count -eq 0)
        mismatch_or_missing_paths = @($releaseMismatches)
        font_archive_matches_release = [bool]$fontMatch
        msgui_matches_release = [bool]$msguiMatch
    }
    policy = [pscustomobject][ordered]@{
        stdout_only = $true
        filesystem_writes = $false
        registry_reads = $true
        registry_writes = $false
        process_launches = $false
        network_access = $false
        game_process_access = $false
        executable_modification = $false
    }
}

$result | ConvertTo-Json -Depth 10
