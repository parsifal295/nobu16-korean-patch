[CmdletBinding()]
param(
    [ValidateSet('Apply', 'Restore', 'Verify')]
    [string]$Action = 'Apply',
    [string]$GameRoot,
    [switch]$AllowDevelopmentMilestone
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PackageRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $PackageRoot 'release_manifest.json'
$CorePath = Join-Path $PSScriptRoot 'FileRecipeCore.cs'
$JsonGuardPath = Join-Path $PSScriptRoot 'JsonKeyGuard.cs'
$SafetyPath = Join-Path $PSScriptRoot 'FileOnlySafety.ps1'
$AtomicPath = Join-Path $PSScriptRoot 'AtomicFileSet.ps1'
$EmbeddedPackageMode = '@PACKAGE_MODE@'
$EmbeddedPackageVersion = '@PACKAGE_VERSION@'
$EmbeddedDevelopmentMilestone = [Convert]::ToBoolean('@DEVELOPMENT_MILESTONE@')
$EmbeddedReleaseEligible = [Convert]::ToBoolean('@RELEASE_ELIGIBLE@')
$EmbeddedPackageFileCount = [int]'@PACKAGE_FILE_COUNT@'
$RecipeE2EPackagePath = 'attestations/four_resource_recipe_e2e.json'
$RuntimeQaPackagePath = 'attestations/runtime_qa.json'

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant()
}

function Assert-PinnedTool([string]$Path, [int64]$Size, [string]$Sha256, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 -or
        [int64]$item.Length -ne $Size -or
        (Get-Sha256 $Path) -ne $Sha256.ToUpperInvariant()) {
        throw "$Label does not match the pinned file-only verifier."
    }
}

Assert-PinnedTool $JsonGuardPath 11304 '6A1ABEC0899A1D4256153E49E8204DAE343EC5D7887DB3047192A8168678DA60' 'JSON key guard'
Assert-PinnedTool $CorePath 28466 '04643FDDA1617663DB4B2812582C5F87FA9D55A46D1861F22570C7C1B7266B79' 'file recipe core'
Assert-PinnedTool $SafetyPath ([int64]'@SAFETY_SIZE@') '@SAFETY_SHA256@' 'file-only safety module'
Assert-PinnedTool $AtomicPath ([int64]'@ATOMIC_SIZE@') '@ATOMIC_SHA256@' 'four-resource transaction module'

Add-Type -Path $JsonGuardPath
Add-Type -Path $CorePath
. $SafetyPath
. $AtomicPath

function Assert-FileSpec([string]$Path, $Spec, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "$Label must not be a reparse point: $Path"
    }
    if ([int64]$item.Length -ne [int64]$Spec.size) {
        throw "$Label size mismatch: $($item.Length), expected $($Spec.size)"
    }
    $actual = Get-Sha256 $Path
    $expected = ([string]$Spec.sha256).ToUpperInvariant()
    if ($actual -ne $expected) {
        throw "$Label SHA-256 mismatch: $actual, expected $expected"
    }
}

function Assert-Bytes([byte[]]$Bytes, $Spec, [string]$Label) {
    if ([int64]$Bytes.Length -ne [int64]$Spec.size) {
        throw "$Label size mismatch: $($Bytes.Length), expected $($Spec.size)"
    }
    $actual = [N16KrFileOnly.FileRecipeCore]::Sha256($Bytes)
    $expected = ([string]$Spec.sha256).ToUpperInvariant()
    if ($actual -ne $expected) {
        throw "$Label SHA-256 mismatch: $actual, expected $expected"
    }
}

function Assert-HashSpec($Spec, [string]$Label) {
    Assert-ExactObjectProperties $Spec @('sha256', 'size') $Label
    if ([int64]$Spec.size -le 0 -or [string]$Spec.sha256 -notmatch '\A[0-9A-F]{64}\z') {
        throw "$Label is malformed."
    }
}

function Assert-E2EAttestation([string]$Path, $Resources) {
    $attestation = Read-StrictFileOnlyJson $Path
    Assert-ExactObjectProperties $attestation @('passed', 'release_id', 'resources', 'schema') 'four-resource recipe E2E attestation'
    if ($attestation.schema -ne 'nobu16.officer-names-four-resource-recipe-e2e.v1' -or
        $attestation.release_id -ne 'officer-names-v0.1' -or
        $attestation.passed -ne $true) {
        throw 'Four-resource recipe E2E attestation is not a passing v0.1 attestation.'
    }
    Assert-ExactObjectProperties $attestation.resources @('font', 'msgdata', 'msgev', 'msgui') 'four-resource recipe E2E resource pins'
    foreach ($resource in $Resources) {
        $actual = $attestation.resources.PSObject.Properties[[string]$resource.id].Value
        Assert-ExactObjectProperties $actual @('recipe_sha256', 'stock_sha256', 'target_sha256') "four-resource recipe E2E $($resource.id)"
        if (([string]$actual.recipe_sha256).ToUpperInvariant() -ne ([string]$resource.recipe.sha256).ToUpperInvariant() -or
            ([string]$actual.stock_sha256).ToUpperInvariant() -ne ([string]$resource.stock.sha256).ToUpperInvariant() -or
            ([string]$actual.target_sha256).ToUpperInvariant() -ne ([string]$resource.target.sha256).ToUpperInvariant()) {
            throw "Four-resource recipe E2E attestation differs from embedded pins for $($resource.id)."
        }
    }
}

function Assert-RuntimeQaAttestation([string]$Path, $Resources) {
    $attestation = Read-StrictFileOnlyJson $Path
    Assert-ExactObjectProperties $attestation @(
        'error_9001_observed', 'passed', 'release_id', 'resource_targets',
        'schema', 'working_directory'
    ) 'runtime QA attestation'
    if ($attestation.schema -ne 'nobu16.officer-names-runtime-qa.v1' -or
        $attestation.release_id -ne 'officer-names-v0.1' -or
        $attestation.passed -ne $true -or
        $attestation.error_9001_observed -ne $false -or
        $attestation.working_directory -ne 'game_root') {
        throw 'Runtime QA attestation is not a passing game-root v0.1 attestation.'
    }
    Assert-ExactObjectProperties $attestation.resource_targets @('font', 'msgdata', 'msgev', 'msgui') 'runtime QA target hashes'
    foreach ($resource in $Resources) {
        $actual = ([string]$attestation.resource_targets.PSObject.Properties[[string]$resource.id].Value).ToUpperInvariant()
        if ($actual -ne ([string]$resource.target.sha256).ToUpperInvariant()) {
            throw "Runtime QA attestation differs from embedded target pins for $($resource.id)."
        }
    }
}

function Assert-NoFullCommercialResource([string]$Path, [string]$RelativePath) {
    $extension = [System.IO.Path]::GetExtension($RelativePath).ToLowerInvariant()
    if ($extension -in @('.exe', '.dll', '.g1n')) {
        throw "Package contains a forbidden native or complete-resource file: $RelativePath"
    }
    if ($extension -eq '.bin') {
        throw "Package contains an unexpected binary payload. Font-v5 must use generated .pixels payloads: $RelativePath"
    }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ge 4) {
        [byte[]]$header = New-Object byte[] 8
        $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        try { [void]$stream.Read($header, 0, [Math]::Min(8, [int]$item.Length)) }
        finally { $stream.Dispose() }
        if ([Text.Encoding]::ASCII.GetString($header, 0, 4) -eq 'LINK' -or
            (($header[0] -eq 1) -and ($header[1] -eq 1) -and ($header[2] -eq 0xC4) -and ($header[3] -eq 0xC1))) {
            throw "Package contains a complete commercial-resource signature: $RelativePath"
        }
    }
}

function Assert-MessageRecipe($Resource, $Recipe, [string]$RecipePath) {
    if ($Recipe.schema -ne 'nobu16.file-only-msg-recipe.v1' -or
        $Recipe.language -ne 'SC' -or
        $Recipe.file_only -ne $true -or
        [string]$Recipe.source.relative_path -ne [string]$Resource.relative_path -or
        [int64]$Recipe.source.size -ne [int64]$Resource.stock.size -or
        ([string]$Recipe.source.sha256).ToUpperInvariant() -ne ([string]$Resource.stock.sha256).ToUpperInvariant() -or
        [int64]$Recipe.target.size -ne [int64]$Resource.target.size -or
        ([string]$Recipe.target.sha256).ToUpperInvariant() -ne ([string]$Resource.target.sha256).ToUpperInvariant() -or
        [int]$Recipe.source.string_count -le 0 -or
        $Recipe.payload_policy.contains_complete_source -ne $false -or
        $Recipe.payload_policy.contains_complete_target -ne $false -or
        $Recipe.payload_policy.contains_executable_bytes -ne $false -or
        $Recipe.payload_policy.stock_file_is_required_at_apply_time -ne $true) {
        throw "Message recipe contract is invalid for $($Resource.id)."
    }
    $operations = @($Recipe.operations)
    if ($operations.Count -le 0) {
        throw "Message recipe contains no operations for $($Resource.id)."
    }
    $previous = -1
    foreach ($operation in $operations) {
        $id = [int]$operation.id
        if ($id -le $previous -or $id -lt 0 -or $id -ge [int]$Recipe.source.string_count -or
            [string]$operation.source_utf16le_sha256 -notmatch '\A[0-9A-F]{64}\z' -or
            [string]::IsNullOrEmpty([string]$operation.replacement) -or
            ([string]$operation.replacement).IndexOf([char]0) -ge 0) {
            throw "Message recipe operation is invalid for $($Resource.id), id $id."
        }
        $previous = $id
    }
    Assert-FileSpec $RecipePath $Resource.recipe "message recipe $($Resource.id)"
}

function Assert-FontRecipe($Resource, $Recipe, [string]$RecipePath, [object[]]$FontArtifacts) {
    $languageNames = @($Recipe.languages.PSObject.Properties.Name)
    $language = $Recipe.languages.SC
    if ($Recipe.schema -ne 'nobu16.file-only-g1n-tail-recipe.v2' -or
        $Recipe.file_only -ne $true -or
        $Recipe.process_memory_access -ne $false -or
        $Recipe.registry_access -ne $false -or
        @($Recipe.runtime_patch_features).Count -ne 0 -or
        $Recipe.payload_policy.commercial_original_bytes_in_public_payload -ne $false -or
        $languageNames.Count -ne 1 -or $languageNames[0] -ne 'SC' -or
        [string]$language.stock_archive.path -ne [string]$Resource.relative_path -or
        [int64]$language.stock_archive.size -ne [int64]$Resource.stock.size -or
        ([string]$language.stock_archive.sha256).ToUpperInvariant() -ne ([string]$Resource.stock.sha256).ToUpperInvariant() -or
        [int64]$language.target_archive.size -ne [int64]$Resource.target.size -or
        ([string]$language.target_archive.sha256).ToUpperInvariant() -ne ([string]$Resource.target.sha256).ToUpperInvariant()) {
        throw 'Font-v5 recipe contract is invalid.'
    }
    $expectedArtifactPaths = @(
        'licenses/OFL-NotoSansKR.txt',
        'licenses/OFL-NotoSerifKR.txt',
        'metrics/glyphs.jsonl',
        'payload/glyph_pixels_entry_6.pixels',
        'payload/glyph_pixels_entry_7.pixels'
    )
    $payloadInventory = @($Recipe.payload_inventory)
    if ($payloadInventory.Count -ne $expectedArtifactPaths.Count) {
        throw 'Font-v5 recipe must reference exactly the five reviewed public artifacts.'
    }
    [string[]]$payloadPaths = @($payloadInventory | ForEach-Object { [string]$_.path })
    Assert-UniqueCanonicalPaths $payloadPaths 'font-v5 recipe payload inventory'
    [string[]]$sortedPayloadPaths = @($payloadPaths)
    [string[]]$sortedExpectedPaths = @($expectedArtifactPaths)
    [Array]::Sort($sortedPayloadPaths, [StringComparer]::Ordinal)
    [Array]::Sort($sortedExpectedPaths, [StringComparer]::Ordinal)
    if (($sortedPayloadPaths -join "`n") -cne ($sortedExpectedPaths -join "`n")) {
        throw 'Font-v5 recipe payload inventory contains a missing, additional, or case-colliding path.'
    }
    foreach ($artifact in $FontArtifacts) {
        $matches = @($payloadInventory | Where-Object { [string]$_.path -ceq [string]$artifact.path })
        if ($matches.Count -ne 1) {
            throw "Font-v5 recipe does not uniquely reference $($artifact.path)."
        }
        $item = $matches[0]
        Assert-ExactObjectProperties $item @('origin', 'path', 'sha256', 'size') "font-v5 recipe payload $($artifact.path)"
        if ([string]::IsNullOrWhiteSpace([string]$item.origin) -or
            [int64]$item.size -ne [int64]$artifact.size -or
            ([string]$item.sha256).ToUpperInvariant() -ne ([string]$artifact.sha256).ToUpperInvariant()) {
            throw "Font-v5 recipe payload differs from embedded artifact pin for $($artifact.path)."
        }
    }
    foreach ($entryName in @('6', '7')) {
        $entry = $language.entries.PSObject.Properties[$entryName].Value
        if ([int]$entry.entry -ne [int]$entryName -or @($entry.tables).Count -ne 2) {
            throw "Font-v5 entry $entryName contract is invalid."
        }
        $payloadRelative = [string]$entry.pixel_payload.file
        $payloadPath = Resolve-FileOnlyChild (Join-Path $PackageRoot ([string]$Resource.component_root).Replace('/', '\')) $payloadRelative "font payload entry $entryName"
        Assert-FileSpec $payloadPath $entry.pixel_payload "font payload entry $entryName"
        if ([System.IO.Path]::GetExtension($payloadPath).ToLowerInvariant() -ne '.pixels') {
            throw "Font-v5 entry $entryName must use a generated .pixels payload."
        }
    }
    Assert-FileSpec $RecipePath $Resource.recipe 'font-v5 recipe'
}

function Assert-Package {
    Assert-OrdinaryExistingPath $PackageRoot 'package root'
    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw 'release_manifest.json is missing.'
    }
    $manifest = Read-StrictFileOnlyJson $ManifestPath
    Assert-ExactObjectProperties $manifest @(
        'accepted_vectors', 'backup_directory', 'development_milestone',
        'distribution_assumption', 'file_only', 'font_artifacts', 'language',
        'launch_working_directory', 'mode', 'package_files', 'prohibited_access',
        'release_eligible', 'release_id', 'release_name', 'resources', 'schema',
        'source_free', 'validation', 'version'
    ) 'release manifest'
    if ($manifest.schema -ne 'nobu16.officer-names-release.v1' -or
        $manifest.release_id -ne 'officer-names-v0.1' -or
        $manifest.version -ne $EmbeddedPackageVersion -or
        $manifest.mode -ne $EmbeddedPackageMode -or
        $manifest.language -ne 'SC' -or
        $manifest.file_only -ne $true -or
        $manifest.source_free -ne $true -or
        $manifest.development_milestone -ne $EmbeddedDevelopmentMilestone -or
        $manifest.release_eligible -ne $EmbeddedReleaseEligible -or
        $manifest.backup_directory -ne 'officer_names_v0_1' -or
        $manifest.distribution_assumption -ne 'storefront-independent; verified copy is non-Steam; detect only by resource tree and pinned hashes' -or
        $manifest.launch_working_directory -ne 'game_root' -or
        (@($manifest.prohibited_access) -join ',') -ne 'memory,process,executable,registry') {
        throw 'Release manifest contract is invalid.'
    }
    if (($EmbeddedPackageMode -eq 'development' -and
            ($EmbeddedPackageVersion -ne '0.1-dev' -or -not $EmbeddedDevelopmentMilestone -or $EmbeddedReleaseEligible)) -or
        ($EmbeddedPackageMode -eq 'release-candidate' -and
            ($EmbeddedPackageVersion -ne '0.1-rc' -or $EmbeddedDevelopmentMilestone -or -not $EmbeddedReleaseEligible)) -or
        $EmbeddedPackageMode -notin @('development', 'release-candidate')) {
        throw 'Installer-embedded promotion mode is invalid.'
    }

    $resources = @($manifest.resources)
    $fixed = @(
        @('msgui', 'message', 'MSG_PK/SC/msgui.bin', 'components/message/msgui_sc.recipe.json', 'components/message'),
        @('msgdata', 'message', 'MSG_PK/SC/msgdata.bin', 'components/message/msgdata_sc.recipe.json', 'components/message'),
        @('msgev', 'message', 'MSG_PK/SC/msgev.bin', 'components/message/msgev_sc.recipe.json', 'components/message'),
        @('font', 'font', 'RES_SC/res_lang.bin', 'components/font/recipe.json', 'components/font')
    )
    $hardPins = @(
        [pscustomobject]@{
            stock_size = [int64]'@MSGUI_STOCK_SIZE@'; stock_sha256 = '@MSGUI_STOCK_SHA256@'
            target_size = [int64]'@MSGUI_TARGET_SIZE@'; target_sha256 = '@MSGUI_TARGET_SHA256@'
            recipe_size = [int64]'@MSGUI_RECIPE_SIZE@'; recipe_sha256 = '@MSGUI_RECIPE_SHA256@'
            predecessor_hashes = @()
        },
        [pscustomobject]@{
            stock_size = [int64]'@MSGDATA_STOCK_SIZE@'; stock_sha256 = '@MSGDATA_STOCK_SHA256@'
            target_size = [int64]'@MSGDATA_TARGET_SIZE@'; target_sha256 = '@MSGDATA_TARGET_SHA256@'
            recipe_size = [int64]'@MSGDATA_RECIPE_SIZE@'; recipe_sha256 = '@MSGDATA_RECIPE_SHA256@'
            predecessor_hashes = @('@MSGDATA_PREDECESSOR_SHA256@')
        },
        [pscustomobject]@{
            stock_size = [int64]'@MSGEV_STOCK_SIZE@'; stock_sha256 = '@MSGEV_STOCK_SHA256@'
            target_size = [int64]'@MSGEV_TARGET_SIZE@'; target_sha256 = '@MSGEV_TARGET_SHA256@'
            recipe_size = [int64]'@MSGEV_RECIPE_SIZE@'; recipe_sha256 = '@MSGEV_RECIPE_SHA256@'
            predecessor_hashes = @('@MSGEV_PREDECESSOR_SHA256@')
        },
        [pscustomobject]@{
            stock_size = [int64]'@FONT_STOCK_SIZE@'; stock_sha256 = '@FONT_STOCK_SHA256@'
            target_size = [int64]'@FONT_TARGET_SIZE@'; target_sha256 = '@FONT_TARGET_SHA256@'
            recipe_size = [int64]'@FONT_RECIPE_SIZE@'; recipe_sha256 = '@FONT_RECIPE_SHA256@'
            predecessor_hashes = @('@FONT_PREDECESSOR_SHA256@')
        }
    )
    if ($resources.Count -ne 4) { throw 'Release must contain exactly four resources.' }
    for ($index = 0; $index -lt 4; $index++) {
        $resource = $resources[$index]
        Assert-ExactObjectProperties $resource @(
            'component_root', 'id', 'kind', 'predecessor_hashes', 'recipe',
            'recipe_path', 'relative_path', 'stock', 'target'
        ) "resource $index"
        if ([string]$resource.id -ne $fixed[$index][0] -or
            [string]$resource.kind -ne $fixed[$index][1] -or
            [string]$resource.relative_path -ne $fixed[$index][2] -or
            [string]$resource.recipe_path -ne $fixed[$index][3] -or
            [string]$resource.component_root -ne $fixed[$index][4]) {
            throw "Resource $index does not match the fixed four-file layout."
        }
        Assert-HashSpec $resource.stock "resource $($resource.id) stock"
        Assert-HashSpec $resource.target "resource $($resource.id) target"
        Assert-HashSpec $resource.recipe "resource $($resource.id) recipe"
        $hardPin = $hardPins[$index]
        if ([int64]$resource.stock.size -ne [int64]$hardPin.stock_size -or
            ([string]$resource.stock.sha256).ToUpperInvariant() -ne ([string]$hardPin.stock_sha256).ToUpperInvariant() -or
            [int64]$resource.target.size -ne [int64]$hardPin.target_size -or
            ([string]$resource.target.sha256).ToUpperInvariant() -ne ([string]$hardPin.target_sha256).ToUpperInvariant() -or
            [int64]$resource.recipe.size -ne [int64]$hardPin.recipe_size -or
            ([string]$resource.recipe.sha256).ToUpperInvariant() -ne ([string]$hardPin.recipe_sha256).ToUpperInvariant() -or
            (@($resource.predecessor_hashes) -join ',').ToUpperInvariant() -ne
                (@($hardPin.predecessor_hashes) -join ',').ToUpperInvariant()) {
            throw "Resource $($resource.id) differs from the installer-embedded release pins."
        }
        $known = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
        [void]$known.Add(([string]$resource.stock.sha256).ToUpperInvariant())
        [void]$known.Add(([string]$resource.target.sha256).ToUpperInvariant())
        foreach ($hash in @($resource.predecessor_hashes)) {
            if ([string]$hash -notmatch '\A[0-9A-F]{64}\z' -or -not $known.Add([string]$hash)) {
                throw "Resource $($resource.id) has a malformed or duplicate predecessor hash."
            }
        }
    }

    $expectedVectors = @(
        [pscustomobject]@{
            id = 'stock'
            hashes = @($hardPins | ForEach-Object { ([string]$_.stock_sha256).ToUpperInvariant() })
        },
        [pscustomobject]@{
            id = 'final'
            hashes = @($hardPins | ForEach-Object { ([string]$_.target_sha256).ToUpperInvariant() })
        },
        [pscustomobject]@{
            id = 'officer_probe_v0.1_on_msgui_full_font_v4'
            hashes = @(
                ([string]$hardPins[0].target_sha256).ToUpperInvariant(),
                ([string]$hardPins[1].predecessor_hashes[0]).ToUpperInvariant(),
                ([string]$hardPins[2].predecessor_hashes[0]).ToUpperInvariant(),
                ([string]$hardPins[3].predecessor_hashes[0]).ToUpperInvariant()
            )
        }
    )
    $acceptedVectors = @($manifest.accepted_vectors)
    if ($acceptedVectors.Count -ne $expectedVectors.Count) {
        throw 'Release manifest must contain exactly the stock, final, and reviewed predecessor vectors.'
    }
    for ($index = 0; $index -lt $expectedVectors.Count; $index++) {
        $actual = $acceptedVectors[$index]
        $expected = $expectedVectors[$index]
        Assert-ExactObjectProperties $actual @('hashes', 'id') "accepted vector $index"
        [string[]]$actualHashes = @($actual.hashes | ForEach-Object { ([string]$_).ToUpperInvariant() })
        [string[]]$expectedHashes = @($expected.hashes | ForEach-Object { ([string]$_).ToUpperInvariant() })
        if ([string]$actual.id -cne [string]$expected.id -or
            ($actualHashes -join ',') -cne ($expectedHashes -join ',')) {
            throw "Accepted vector $index differs from the installer-embedded release pins."
        }
        $matchedId = Assert-KnownHashVector $expectedHashes $acceptedVectors "accepted vector $($expected.id)"
        if ($matchedId -cne [string]$expected.id) {
            throw "Accepted vector $index resolved to an unexpected id."
        }
    }

    $expectedFontArtifactPaths = @(
        'licenses/OFL-NotoSansKR.txt',
        'licenses/OFL-NotoSerifKR.txt',
        'metrics/glyphs.jsonl',
        'payload/glyph_pixels_entry_6.pixels',
        'payload/glyph_pixels_entry_7.pixels'
    )
    $embeddedFontArtifacts = @(
        [pscustomobject]@{ path = $expectedFontArtifactPaths[0]; size = [int64]'@FONT_ARTIFACT_0_SIZE@'; sha256 = '@FONT_ARTIFACT_0_SHA256@' },
        [pscustomobject]@{ path = $expectedFontArtifactPaths[1]; size = [int64]'@FONT_ARTIFACT_1_SIZE@'; sha256 = '@FONT_ARTIFACT_1_SHA256@' },
        [pscustomobject]@{ path = $expectedFontArtifactPaths[2]; size = [int64]'@FONT_ARTIFACT_2_SIZE@'; sha256 = '@FONT_ARTIFACT_2_SHA256@' },
        [pscustomobject]@{ path = $expectedFontArtifactPaths[3]; size = [int64]'@FONT_ARTIFACT_3_SIZE@'; sha256 = '@FONT_ARTIFACT_3_SHA256@' },
        [pscustomobject]@{ path = $expectedFontArtifactPaths[4]; size = [int64]'@FONT_ARTIFACT_4_SIZE@'; sha256 = '@FONT_ARTIFACT_4_SHA256@' }
    )
    $fontRoot = Resolve-FileOnlyChild $PackageRoot 'components/font' 'font component root'
    Assert-PinnedArtifactSet @($manifest.font_artifacts) $expectedFontArtifactPaths $fontRoot 'release font artifacts'
    for ($index = 0; $index -lt $embeddedFontArtifacts.Count; $index++) {
        $actual = $manifest.font_artifacts[$index]
        $embedded = $embeddedFontArtifacts[$index]
        if ([int64]$actual.size -ne [int64]$embedded.size -or
            ([string]$actual.sha256).ToUpperInvariant() -ne ([string]$embedded.sha256).ToUpperInvariant()) {
            throw "Font artifact $($embedded.path) differs from the installer-embedded release pin."
        }
    }
    Assert-ExactOrdinaryFileSet $fontRoot @($expectedFontArtifactPaths + 'recipe.json') 'font component'

    Assert-ExactObjectProperties $manifest.validation @('recipe_e2e', 'runtime_qa') 'release validation'
    if ($EmbeddedPackageMode -eq 'development') {
        if ($null -ne $manifest.validation.recipe_e2e -or $null -ne $manifest.validation.runtime_qa) {
            throw 'Development packages must not claim promotion attestations.'
        }
    }
    else {
        $embeddedRecipeE2E = [pscustomobject]@{
            path = $RecipeE2EPackagePath
            size = [int64]'@RECIPE_E2E_SIZE@'
            sha256 = '@RECIPE_E2E_SHA256@'
        }
        $embeddedRuntimeQa = [pscustomobject]@{
            path = $RuntimeQaPackagePath
            size = [int64]'@RUNTIME_QA_SIZE@'
            sha256 = '@RUNTIME_QA_SHA256@'
        }
        foreach ($pair in @(
            [pscustomobject]@{ actual = $manifest.validation.recipe_e2e; embedded = $embeddedRecipeE2E; label = 'four-resource recipe E2E attestation' },
            [pscustomobject]@{ actual = $manifest.validation.runtime_qa; embedded = $embeddedRuntimeQa; label = 'runtime QA attestation' }
        )) {
            Assert-ExactObjectProperties $pair.actual @('path', 'sha256', 'size') $pair.label
            Assert-HashSpec $pair.actual $pair.label
            if ([string]$pair.actual.path -cne [string]$pair.embedded.path -or
                [int64]$pair.actual.size -ne [int64]$pair.embedded.size -or
                ([string]$pair.actual.sha256).ToUpperInvariant() -ne ([string]$pair.embedded.sha256).ToUpperInvariant()) {
                throw "$($pair.label) differs from the installer-embedded promotion pin."
            }
            $attestationPath = Resolve-FileOnlyChild $PackageRoot ([string]$pair.actual.path) $pair.label
            Assert-FileSpec $attestationPath $pair.actual $pair.label
        }
    }

    $inventory = @($manifest.package_files)
    if ($inventory.Count -ne $EmbeddedPackageFileCount) {
        throw "Package inventory must contain exactly $EmbeddedPackageFileCount reviewed files."
    }
    [string[]]$inventoryPaths = @($inventory | ForEach-Object { [string]$_.path })
    Assert-UniqueCanonicalPaths $inventoryPaths 'package inventory'
    foreach ($entry in $inventory) {
        Assert-ExactObjectProperties $entry @('path', 'role', 'sha256', 'size') "package inventory $($entry.path)"
        Assert-HashSpec ([pscustomobject]@{ size = $entry.size; sha256 = $entry.sha256 }) "package inventory $($entry.path)"
        $path = Resolve-FileOnlyChild $PackageRoot ([string]$entry.path) 'package inventory path'
        Assert-FileSpec $path $entry "package file $($entry.path)"
        Assert-NoFullCommercialResource $path ([string]$entry.path)
    }
    $treeFiles = @(Get-OrdinaryTreeFiles $PackageRoot)
    [string[]]$actualPaths = @($treeFiles | ForEach-Object { [string]$_.RelativePath })
    [string[]]$expectedPaths = @('release_manifest.json') + $inventoryPaths
    Assert-UniqueCanonicalPaths $expectedPaths 'expected package tree'
    [Array]::Sort($actualPaths, [StringComparer]::Ordinal)
    [Array]::Sort($expectedPaths, [StringComparer]::Ordinal)
    if (($actualPaths -join "`n") -cne ($expectedPaths -join "`n")) {
        throw 'Package tree contains a missing, additional, or case-colliding file.'
    }

    foreach ($resource in $resources) {
        $recipePath = Resolve-FileOnlyChild $PackageRoot ([string]$resource.recipe_path) "recipe $($resource.id)"
        $recipe = Read-StrictFileOnlyJson $recipePath
        if ($resource.kind -eq 'message') {
            Assert-MessageRecipe $resource $recipe $recipePath
        }
        else {
            Assert-FontRecipe $resource $recipe $recipePath @($manifest.font_artifacts)
        }
    }
    if ($EmbeddedPackageMode -eq 'release-candidate') {
        Assert-E2EAttestation (Resolve-FileOnlyChild $PackageRoot $RecipeE2EPackagePath 'four-resource recipe E2E attestation') $resources
        Assert-RuntimeQaAttestation (Resolve-FileOnlyChild $PackageRoot $RuntimeQaPackagePath 'runtime QA attestation') $resources
    }
    return $manifest
}

function Resolve-GameRoot([string]$Requested) {
    if (-not [string]::IsNullOrWhiteSpace($Requested)) {
        $candidate = Get-FileOnlyFullPath $Requested
        if (-not (Test-Path -LiteralPath $candidate -PathType Container)) {
            throw "Game root does not exist: $candidate"
        }
        return $candidate
    }
    foreach ($candidate in @($PackageRoot, (Split-Path -Parent $PackageRoot))) {
        $found = $true
        foreach ($relative in @('MSG_PK/SC/msgui.bin', 'MSG_PK/SC/msgdata.bin', 'MSG_PK/SC/msgev.bin', 'RES_SC/res_lang.bin')) {
            $path = Resolve-FileOnlyChild $candidate $relative 'game resource probe'
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { $found = $false; break }
        }
        if ($found) { return (Get-FileOnlyFullPath $candidate) }
    }
    throw 'Game root was not found. Pass -GameRoot or place the release folder directly inside the game root.'
}

function Convert-HexToBytes([string]$Hex) {
    if ($Hex.Length % 2 -ne 0 -or $Hex -notmatch '\A[0-9A-Fa-f]*\z') {
        throw 'Invalid hexadecimal recipe payload.'
    }
    [byte[]]$result = New-Object byte[] ($Hex.Length / 2)
    for ($index = 0; $index -lt $result.Length; $index++) {
        $result[$index] = [Convert]::ToByte($Hex.Substring($index * 2, 2), 16)
    }
    return ,$result
}

function Build-Message([string]$StockPath, [string]$RecipePath, $Resource) {
    $recipe = Read-StrictFileOnlyJson $RecipePath
    [byte[]]$stock = [System.IO.File]::ReadAllBytes($StockPath)
    Assert-Bytes $stock $Resource.stock "stock $($Resource.id)"
    $operations = @($recipe.operations)
    [int[]]$ids = @($operations | ForEach-Object { [int]$_.id })
    [string[]]$sourceHashes = @($operations | ForEach-Object { [string]$_.source_utf16le_sha256 })
    [string[]]$replacements = @($operations | ForEach-Object { [string]$_.replacement })
    [byte[]]$target = [N16KrFileOnly.FileRecipeCore]::ApplyMessageRecipe(
        $stock, [int]$recipe.source.string_count, $ids, $sourceHashes, $replacements)
    Assert-Bytes $target $Resource.target "rebuilt $($Resource.id)"
    return ,$target
}

function Build-FontEntry([byte[]]$StockArchive, $EntryRecipe, [string]$ComponentRoot) {
    $entry = [int]$EntryRecipe.entry
    [byte[]]$stockRaw = [N16KrFileOnly.FileRecipeCore]::ExtractLinkEntryRaw($StockArchive, $entry)
    Assert-Bytes $stockRaw $EntryRecipe.stock "stock font-v5 entry $entry"
    $payloadPath = Resolve-FileOnlyChild $ComponentRoot ([string]$EntryRecipe.pixel_payload.file) "font-v5 payload $entry"
    [byte[]]$pixels = [System.IO.File]::ReadAllBytes($payloadPath)
    Assert-Bytes $pixels $EntryRecipe.pixel_payload "font-v5 payload $entry"
    $tables = @($EntryRecipe.tables)
    [int[]]$codepoints0 = @($tables[0].map_changes | ForEach-Object { [Convert]::ToInt32(([string]$_.codepoint).Substring(2), 16) })
    [int[]]$codepoints1 = @($tables[1].map_changes | ForEach-Object { [Convert]::ToInt32(([string]$_.codepoint).Substring(2), 16) })
    [int[]]$ordinals0 = @($tables[0].map_changes | ForEach-Object { [int]$_.new_ordinal })
    [int[]]$ordinals1 = @($tables[1].map_changes | ForEach-Object { [int]$_.new_ordinal })
    [byte[]]$appended0 = Convert-HexToBytes ([string]$tables[0].appended_records_hex)
    [byte[]]$appended1 = Convert-HexToBytes ([string]$tables[1].appended_records_hex)
    if ([N16KrFileOnly.FileRecipeCore]::Sha256($appended0) -ne ([string]$tables[0].appended_records_sha256).ToUpperInvariant() -or
        [N16KrFileOnly.FileRecipeCore]::Sha256($appended1) -ne ([string]$tables[1].appended_records_sha256).ToUpperInvariant()) {
        throw "Font-v5 appended-record hash mismatch for entry $entry."
    }
    [int[]]$targetOffsets = @($EntryRecipe.target.table_offsets | ForEach-Object { [int]$_ })
    [byte[]]$targetRaw = [N16KrFileOnly.FileRecipeCore]::BuildG1n(
        $stockRaw, [int]$EntryRecipe.target.size, [int]$EntryRecipe.target.atlas_offset,
        $targetOffsets, $codepoints0, $ordinals0, $codepoints1, $ordinals1,
        $appended0, $appended1, $pixels)
    Assert-Bytes $targetRaw $EntryRecipe.target "rebuilt font-v5 entry $entry"
    return ,$targetRaw
}

function Build-Font([string]$StockPath, [string]$RecipePath, [string]$ComponentRoot, $Resource) {
    $recipe = Read-StrictFileOnlyJson $RecipePath
    $language = $recipe.languages.SC
    [byte[]]$stockArchive = [System.IO.File]::ReadAllBytes($StockPath)
    Assert-Bytes $stockArchive $Resource.stock 'stock font archive'
    [byte[]]$entry6 = Build-FontEntry $stockArchive $language.entries.'6' $ComponentRoot
    [byte[]]$entry7 = Build-FontEntry $stockArchive $language.entries.'7' $ComponentRoot
    [int[]]$indices = @(6, 7)
    [byte[][]]$entries = [byte[][]]::new(2)
    $entries[0] = $entry6
    $entries[1] = $entry7
    [byte[]]$target = [N16KrFileOnly.FileRecipeCore]::ReplaceLinkRawEntries($stockArchive, $indices, $entries)
    Assert-Bytes $target $Resource.target 'rebuilt font archive'
    return ,$target
}

function New-SiblingPath([string]$Destination, [string]$Tag) {
    $parent = [System.IO.Path]::GetDirectoryName($Destination)
    $name = [System.IO.Path]::GetFileName($Destination)
    return (Join-Path $parent ('.' + $name + '.krpatch.' + $Tag + '.' + [Guid]::NewGuid().ToString('N')))
}

function New-TransitionItems($Resources, $Paths, [string[]]$BeforeHashes, [string[]]$AfterHashes, [string[]]$StagedPaths) {
    $items = @()
    for ($index = 0; $index -lt 4; $index++) {
        $items += [pscustomobject]@{
            Id = [string]$Resources[$index].id
            Destination = [string]$Paths[$index]
            Staged = [string]$StagedPaths[$index]
            Rollback = New-SiblingPath ([string]$Paths[$index]) 'rollback'
            BeforeSha256 = ([string]$BeforeHashes[$index]).ToUpperInvariant()
            AfterSha256 = ([string]$AfterHashes[$index]).ToUpperInvariant()
        }
    }
    return @($items)
}

function Get-InstalledHashes([string[]]$Paths) {
    return @($Paths | ForEach-Object { Get-Sha256 $_ })
}

function Test-HashVector([string[]]$Actual, [string[]]$Expected) {
    if ($Actual.Count -ne $Expected.Count) { return $false }
    for ($index = 0; $index -lt $Actual.Count; $index++) {
        if ($Actual[$index] -ne $Expected[$index]) { return $false }
    }
    return $true
}

function Find-VerifiedStockSource($Resource, [string]$Destination, [string]$BackupParent) {
    if ((Get-Sha256 $Destination) -eq ([string]$Resource.stock.sha256).ToUpperInvariant() -and
        [int64](Get-Item -LiteralPath $Destination).Length -eq [int64]$Resource.stock.size) {
        return $Destination
    }
    if (-not (Test-Path -LiteralPath $BackupParent -PathType Container)) {
        throw "No backup tree exists for non-stock resource $($Resource.id)."
    }
    Assert-OrdinaryPathFromRoot $BackupParent $BackupParent 'backup tree'
    $candidates = @(Get-OrdinaryTreeFiles $BackupParent | Where-Object {
        [int64](Get-Item -LiteralPath $_.FullPath).Length -eq [int64]$Resource.stock.size
    } | Sort-Object RelativePath)
    foreach ($candidate in $candidates) {
        if ((Get-Sha256 $candidate.FullPath) -eq ([string]$Resource.stock.sha256).ToUpperInvariant()) {
            return [string]$candidate.FullPath
        }
    }
    throw "No exact size+SHA-256 stock backup was found for $($Resource.id)."
}

function Ensure-OwnStockBackups($Resources, [string[]]$Paths, [string]$BackupParent, [string]$OwnBackupRoot) {
    $stockRoot = Join-Path $OwnBackupRoot 'stock'
    [System.IO.Directory]::CreateDirectory($stockRoot) | Out-Null
    [void](Assert-ExactCaseRelativePath $OwnBackupRoot 'stock' 'stock backup directory')
    Assert-OrdinaryPathFromRoot $OwnBackupRoot $stockRoot 'stock backup directory'
    $result = @()
    for ($index = 0; $index -lt 4; $index++) {
        $resource = $Resources[$index]
        $backup = Join-Path $stockRoot ([string]$resource.id + '.stock.bak')
        if (Test-Path -LiteralPath $backup) {
            [void](Assert-ExactCaseRelativePath $stockRoot ([string]$resource.id + '.stock.bak') "stock backup $($resource.id)")
            Assert-OrdinaryPathFromRoot $OwnBackupRoot $backup "stock backup $($resource.id)"
            Assert-FileSpec $backup $resource.stock "stock backup $($resource.id)"
        }
        else {
            $source = Find-VerifiedStockSource $resource $Paths[$index] $BackupParent
            $temporary = Join-Path $stockRoot ('.' + [string]$resource.id + '.stock.' + [Guid]::NewGuid().ToString('N'))
            try {
                [N16KrFileOnly.FileRecipeCore]::CopyDurable($source, $temporary)
                Assert-FileSpec $temporary $resource.stock "new stock backup $($resource.id)"
                [System.IO.File]::Move($temporary, $backup)
            }
            finally {
                Remove-AtomicTemporary @($temporary)
            }
        }
        $result += $backup
    }
    return @($result)
}

function Assert-KnownInstalledVector($Manifest, [string[]]$Hashes, [string]$Label = 'installed resource vector') {
    return Assert-KnownHashVector $Hashes @($Manifest.accepted_vectors) $Label
}

function Write-InstallState([string]$Path, $Manifest, [string]$Status, [string[]]$Hashes) {
    $state = [ordered]@{
        schema = 'nobu16.officer-names-install-state.v1'
        release_id = [string]$Manifest.release_id
        release_manifest_sha256 = Get-Sha256 $ManifestPath
        status = $Status
        resource_hashes = [ordered]@{
            msgui = $Hashes[0]
            msgdata = $Hashes[1]
            msgev = $Hashes[2]
            font = $Hashes[3]
        }
        updated_utc = [DateTime]::UtcNow.ToString('o')
    }
    Write-AtomicJournal $Path $state
}

function Get-ExactDirectChildPath(
    [string]$Parent,
    [string]$Path,
    [string]$ExpectedLeaf,
    [string]$Label
) {
    $fullParent = (Get-FileOnlyFullPath $Parent).TrimEnd('\')
    $fullPath = Get-FileOnlyFullPath $Path
    $actualParent = (Get-FileOnlyFullPath ([System.IO.Path]::GetDirectoryName($fullPath))).TrimEnd('\')
    if (-not [string]::Equals($actualParent, $fullParent, [StringComparison]::OrdinalIgnoreCase) -or
        [System.IO.Path]::GetFileName($fullPath) -cne $ExpectedLeaf) {
        throw "$Label is not the exact reviewed direct child of its backup directory."
    }
    return $fullPath
}

function Read-ValidatedMigrationJournal(
    $Manifest,
    $Resources,
    [string]$OwnBackupRoot,
    [string]$MigrationPath
) {
    Assert-OrdinaryPathFromRoot $OwnBackupRoot $MigrationPath 'migration journal'
    $journalHash = Get-Sha256 $MigrationPath
    $migration = Read-StrictFileOnlyJson $MigrationPath
    Assert-ExactObjectProperties $migration @(
        'input_hashes', 'input_vector_id', 'schema', 'snapshot_root',
        'snapshots', 'status'
    ) 'migration journal'
    if ($migration.schema -ne 'nobu16.officer-names-durable-migration.v1' -or
        $migration.status -notin @('prepared', 'cleanup_pending')) {
        throw 'Migration journal has an unsupported schema or state.'
    }
    [string[]]$inputHashes = @($migration.input_hashes | ForEach-Object { ([string]$_).ToUpperInvariant() })
    if ($inputHashes.Count -ne 4 -or
        @($inputHashes | Where-Object { $_ -notmatch '\A[0-9A-F]{64}\z' }).Count -ne 0) {
        throw 'Migration journal input vector is malformed.'
    }
    $inputVectorId = Assert-KnownInstalledVector $Manifest $inputHashes 'migration input vector'
    if ([string]$migration.input_vector_id -cne $inputVectorId -or
        $inputVectorId -notin @('stock', 'officer_probe_v0.1_on_msgui_full_font_v4')) {
        throw 'Migration journal input vector id is not an approved apply input.'
    }

    $snapshotRootLeaf = [System.IO.Path]::GetFileName([string]$migration.snapshot_root)
    if ($snapshotRootLeaf -notmatch '\Amigration_snapshot_[0-9a-f]{32}\z') {
        throw 'Migration snapshot directory name is malformed.'
    }
    $snapshotRoot = Get-ExactDirectChildPath `
        $OwnBackupRoot ([string]$migration.snapshot_root) $snapshotRootLeaf 'migration snapshot root'
    $snapshotRootExists = Test-Path -LiteralPath $snapshotRoot -PathType Container
    if (-not $snapshotRootExists -and $migration.status -eq 'prepared') {
        throw 'Migration snapshot directory is missing.'
    }
    if ($snapshotRootExists) {
        Assert-OrdinaryPathFromRoot $OwnBackupRoot $snapshotRoot 'migration snapshot root'
    }

    $snapshotRows = @($migration.snapshots)
    if ($snapshotRows.Count -ne 4) {
        throw 'Migration journal must contain exactly four snapshots.'
    }
    $validatedSnapshots = @()
    for ($index = 0; $index -lt 4; $index++) {
        $row = $snapshotRows[$index]
        $resource = $Resources[$index]
        Assert-ExactObjectProperties $row @('id', 'path', 'sha256', 'size') "migration snapshot $index"
        $expectedLeaf = [string]$resource.id + '.before.bak'
        $snapshotPath = Get-ExactDirectChildPath `
            $snapshotRoot ([string]$row.path) $expectedLeaf "migration snapshot $($resource.id)"
        if ([string]$row.id -cne [string]$resource.id -or
            [string]$row.sha256 -notmatch '\A[0-9A-F]{64}\z' -or
            ([string]$row.sha256).ToUpperInvariant() -ne $inputHashes[$index] -or
            [int64]$row.size -le 0) {
            throw "Migration snapshot pin is malformed for $($resource.id)."
        }
        $snapshotExists = Test-Path -LiteralPath $snapshotPath -PathType Leaf
        if (-not $snapshotExists -and $migration.status -eq 'prepared') {
            throw "Migration snapshot is missing for $($resource.id)."
        }
        if ($snapshotExists) {
            Assert-OrdinaryPathFromRoot $snapshotRoot $snapshotPath "migration snapshot $($resource.id)"
            $snapshotItem = Get-Item -LiteralPath $snapshotPath -Force
            if ([int64]$snapshotItem.Length -ne [int64]$row.size -or
                (Get-Sha256 $snapshotPath) -ne $inputHashes[$index]) {
                throw "Migration snapshot bytes differ from the input vector for $($resource.id)."
            }
        }
        $validatedSnapshots += [pscustomobject]@{
            Id = [string]$resource.id
            Path = $snapshotPath
            Size = [int64]$row.size
            Sha256 = $inputHashes[$index]
            Exists = $snapshotExists
        }
    }
    if ($snapshotRootExists) {
        Assert-ExactOrdinaryFileSet $snapshotRoot @(
            $validatedSnapshots | Where-Object { $_.Exists } | ForEach-Object {
                [System.IO.Path]::GetFileName([string]$_.Path)
            }
        ) 'migration snapshot directory'
    }
    elseif (@($validatedSnapshots | Where-Object { $_.Exists }).Count -ne 0) {
        throw 'Migration snapshot files exist without their reviewed snapshot directory.'
    }
    return [pscustomobject]@{
        Status = [string]$migration.status
        InputVectorId = $inputVectorId
        InputHashes = $inputHashes
        SnapshotRoot = $snapshotRoot
        Snapshots = $validatedSnapshots
        JournalSha256 = $journalHash
    }
}

function Write-DurableMigrationJournal(
    $Manifest,
    $Resources,
    [string]$OwnBackupRoot,
    [string]$MigrationPath,
    [string]$InputVectorId,
    [string[]]$InputHashes,
    [string]$SnapshotRoot,
    [string[]]$SnapshotPaths
) {
    $reviewedInputId = Assert-KnownInstalledVector $Manifest $InputHashes 'new migration input vector'
    if ($reviewedInputId -cne $InputVectorId -or
        $InputVectorId -notin @('stock', 'officer_probe_v0.1_on_msgui_full_font_v4') -or
        $SnapshotPaths.Count -ne 4) {
        throw 'New durable migration journal has an invalid input contract.'
    }
    $snapshotRows = @()
    for ($index = 0; $index -lt 4; $index++) {
        $snapshot = $SnapshotPaths[$index]
        $snapshotRows += [ordered]@{
            id = [string]$Resources[$index].id
            path = Get-FileOnlyFullPath $snapshot
            size = [int64](Get-Item -LiteralPath $snapshot).Length
            sha256 = (Get-Sha256 $snapshot)
        }
    }
    $value = [ordered]@{
        schema = 'nobu16.officer-names-durable-migration.v1'
        status = 'prepared'
        input_vector_id = $InputVectorId
        input_hashes = @($InputHashes | ForEach-Object { $_.ToUpperInvariant() })
        snapshot_root = Get-FileOnlyFullPath $SnapshotRoot
        snapshots = $snapshotRows
    }
    Write-AtomicJournal $MigrationPath $value
    return Read-ValidatedMigrationJournal $Manifest $Resources $OwnBackupRoot $MigrationPath
}

function Remove-ValidatedMigration(
    $Manifest,
    $Resources,
    [string]$OwnBackupRoot,
    [string]$MigrationPath,
    $Migration
) {
    if ((Get-Sha256 $MigrationPath) -ne [string]$Migration.JournalSha256) {
        throw 'Migration journal changed after validation; refusing cleanup.'
    }
    if ($Migration.Status -eq 'prepared') {
        $rawMigration = Read-StrictFileOnlyJson $MigrationPath
        $rawMigration.status = 'cleanup_pending'
        Write-AtomicJournal $MigrationPath $rawMigration
        $Migration = Read-ValidatedMigrationJournal $Manifest $Resources $OwnBackupRoot $MigrationPath
    }
    foreach ($snapshot in @($Migration.Snapshots)) {
        if (-not (Test-Path -LiteralPath $snapshot.Path -PathType Leaf)) { continue }
        Assert-OrdinaryPathFromRoot $Migration.SnapshotRoot $snapshot.Path "migration cleanup $($snapshot.Id)"
        $item = Get-Item -LiteralPath $snapshot.Path -Force
        if ([int64]$item.Length -ne [int64]$snapshot.Size -or
            (Get-Sha256 $snapshot.Path) -ne [string]$snapshot.Sha256) {
            throw "Migration snapshot changed before cleanup: $($snapshot.Id)"
        }
        [System.IO.File]::Delete([string]$snapshot.Path)
    }
    if (Test-Path -LiteralPath $Migration.SnapshotRoot -PathType Container) {
        if (@(Get-ChildItem -LiteralPath $Migration.SnapshotRoot -Force).Count -ne 0) {
            throw 'Migration snapshot directory contains an unexpected file; refusing cleanup.'
        }
        [System.IO.Directory]::Delete([string]$Migration.SnapshotRoot, $false)
    }
    if ((Get-Sha256 $MigrationPath) -ne [string]$Migration.JournalSha256) {
        throw 'Migration journal changed during cleanup; refusing final deletion.'
    }
    Assert-OrdinaryPathFromRoot $OwnBackupRoot $MigrationPath 'migration journal cleanup'
    [System.IO.File]::Delete($MigrationPath)
}

function Recover-DurableMigrationIfPresent(
    $Manifest,
    $Resources,
    [string[]]$Paths,
    [string]$OwnBackupRoot,
    [string]$MigrationPath,
    [string]$JournalPath,
    [string]$StatePath
) {
    if (-not (Test-Path -LiteralPath $MigrationPath -PathType Leaf)) { return }
    $migration = Read-ValidatedMigrationJournal $Manifest $Resources $OwnBackupRoot $MigrationPath
    [string[]]$currentHashes = Get-InstalledHashes $Paths
    $currentId = Assert-KnownInstalledVector $Manifest $currentHashes 'durable migration recovery vector'
    if ($migration.Status -eq 'cleanup_pending') {
        if ($currentId -ne 'final' -and -not (Test-HashVector $currentHashes $migration.InputHashes)) {
            throw 'Cleanup-pending migration journal is not paired with a safe final or input vector.'
        }
        Write-Host "Resuming durable migration cleanup from state: $currentId"
        Remove-ValidatedMigration $Manifest $Resources $OwnBackupRoot $MigrationPath $migration
        return
    }
    if ($currentId -eq 'final' -or (Test-HashVector $currentHashes $migration.InputHashes)) {
        Write-Host "Completing durable migration cleanup from state: $currentId"
        Remove-ValidatedMigration $Manifest $Resources $OwnBackupRoot $MigrationPath $migration
        return
    }
    if ($migration.InputVectorId -eq 'officer_probe_v0.1_on_msgui_full_font_v4' -and
        $currentId -eq 'stock') {
        Write-Host 'Recovering the predecessor input vector from durable migration snapshots...'
        $stages = @()
        try {
            for ($index = 0; $index -lt 4; $index++) {
                $stage = New-SiblingPath $Paths[$index] 'durable-input'
                [N16KrFileOnly.FileRecipeCore]::CopyDurable($migration.Snapshots[$index].Path, $stage)
                $stages += $stage
            }
            $items = New-TransitionItems `
                $Resources $Paths $currentHashes $migration.InputHashes $stages
            [void](Invoke-AtomicFileSetTransaction $items $JournalPath 'rollback-input')
            Write-InstallState $StatePath $Manifest 'interrupted_migration_input_restored' $migration.InputHashes
            Remove-AtomicTemporary @($JournalPath)
            Remove-ValidatedMigration $Manifest $Resources $OwnBackupRoot $MigrationPath $migration
        }
        finally {
            Remove-AtomicTemporary $stages
        }
        return
    }
    throw "Durable migration journal cannot reconcile installed vector '$currentId' with input '$($migration.InputVectorId)'."
}

function Recover-InterruptedIfPresent($Manifest, $Resources, [string[]]$Paths, [string]$JournalPath) {
    if (-not (Test-Path -LiteralPath $JournalPath -PathType Leaf)) { return }
    Assert-OrdinaryExistingPath $JournalPath 'transaction journal'
    $journal = Read-StrictFileOnlyJson $JournalPath
    $operation = [string]$journal.operation
    if ($operation -notin @('normalize-stock', 'apply', 'restore', 'rollback-input')) {
        throw 'Interrupted transaction has an unsupported operation.'
    }
    [string[]]$stock = @($Resources | ForEach-Object { ([string]$_.stock.sha256).ToUpperInvariant() })
    [string[]]$target = @($Resources | ForEach-Object { ([string]$_.target.sha256).ToUpperInvariant() })
    [string[]]$before = @($journal.items | ForEach-Object { ([string]$_.before_sha256).ToUpperInvariant() })
    [string[]]$after = @($journal.items | ForEach-Object { ([string]$_.after_sha256).ToUpperInvariant() })
    if ($operation -eq 'apply' -and (-not (Test-HashVector $before $stock) -or -not (Test-HashVector $after $target))) {
        throw 'Interrupted apply journal violates the pinned stock-to-target transition.'
    }
    if ($operation -eq 'restore') {
        $restoreBeforeId = Assert-KnownInstalledVector $Manifest $before 'interrupted restore input vector'
        $restoreAfterId = Assert-KnownInstalledVector $Manifest $after 'interrupted restore target vector'
        if ($restoreBeforeId -eq 'stock' -or $restoreAfterId -ne 'stock' -or -not (Test-HashVector $after $stock)) {
            throw 'Interrupted restore journal violates an accepted-vector-to-stock transition.'
        }
    }
    if ($operation -eq 'normalize-stock') {
        $normalizeBeforeId = Assert-KnownInstalledVector $Manifest $before 'interrupted normalization input vector'
        $normalizeAfterId = Assert-KnownInstalledVector $Manifest $after 'interrupted normalization target vector'
        if ($normalizeBeforeId -ne 'officer_probe_v0.1_on_msgui_full_font_v4' -or
            $normalizeAfterId -ne 'stock' -or -not (Test-HashVector $after $stock)) {
            throw 'Interrupted stock-normalization journal violates the reviewed predecessor-to-stock transition.'
        }
    }
    if ($operation -eq 'rollback-input') {
        [void](Assert-KnownInstalledVector $Manifest $before 'interrupted input-rollback source vector')
        [void](Assert-KnownInstalledVector $Manifest $after 'interrupted input-rollback target vector')
    }
    $dummy = @()
    for ($index = 0; $index -lt 4; $index++) {
        $dummy += [pscustomobject]@{
            Id = [string]$Resources[$index].id
            Destination = $Paths[$index]
            Staged = New-SiblingPath $Paths[$index] 'recovery-stage'
            Rollback = New-SiblingPath $Paths[$index] 'recovery-rollback'
            BeforeSha256 = $before[$index]
            AfterSha256 = $after[$index]
        }
    }
    [void](Recover-AtomicFileSetTransaction $journal $dummy $JournalPath)
    Remove-AtomicTemporary @($JournalPath)
}

$manifest = Assert-Package
if ($Action -eq 'Verify') {
    Write-Host 'Officer-name v0.1 four-resource package verification: OK'
    if ($manifest.release_eligible -ne $true) {
        Write-Warning 'This is a development milestone. Installation requires -AllowDevelopmentMilestone.'
    }
    Write-Host 'This package is storefront-independent and validates only the game resource tree and pinned hashes.'
    exit 0
}
if ($manifest.release_eligible -ne $true -and -not $AllowDevelopmentMilestone) {
    throw 'This development milestone is not approved for end-user installation.'
}

$resolvedGameRoot = Resolve-GameRoot $GameRoot
Assert-OrdinaryExistingPath $resolvedGameRoot 'game root'
$resources = @($manifest.resources)
$paths = @()
foreach ($resource in $resources) {
    $path = Assert-ExactCaseRelativePath $resolvedGameRoot ([string]$resource.relative_path) "game resource $($resource.id)"
    Assert-OrdinaryPathFromRoot $resolvedGameRoot $path "game resource $($resource.id)"
    $paths += $path
}

$backupParent = Join-Path $resolvedGameRoot 'KR_PATCH_BACKUP'
$ownBackupRoot = Join-Path $backupParent ([string]$manifest.backup_directory)
if (Test-Path -LiteralPath $backupParent) {
    Assert-OrdinaryPathFromRoot $resolvedGameRoot $backupParent 'patch backup root'
}
[System.IO.Directory]::CreateDirectory($ownBackupRoot) | Out-Null
[void](Assert-ExactCaseRelativePath $resolvedGameRoot 'KR_PATCH_BACKUP' 'patch backup root')
[void](Assert-ExactCaseRelativePath $backupParent ([string]$manifest.backup_directory) 'officer-name backup root')
Assert-OrdinaryPathFromRoot $resolvedGameRoot $backupParent 'patch backup root'
Assert-OrdinaryPathFromRoot $backupParent $ownBackupRoot 'officer-name backup root'
$statePath = Join-Path $ownBackupRoot 'install_state.json'
$journalPath = Join-Path $ownBackupRoot 'transaction.json'
$migrationPath = Join-Path $ownBackupRoot 'migration.json'
$lockPath = Join-Path $ownBackupRoot 'operation.lock'
foreach ($existing in @($statePath, $journalPath, $migrationPath, $lockPath)) {
    if (Test-Path -LiteralPath $existing) {
        [void](Assert-ExactCaseRelativePath $ownBackupRoot ([System.IO.Path]::GetFileName($existing)) 'patch state file')
        Assert-OrdinaryPathFromRoot $ownBackupRoot $existing 'patch state file'
    }
}

try {
    $operationLock = [System.IO.File]::Open(
        $lockPath, [System.IO.FileMode]::OpenOrCreate,
        [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
}
catch {
    throw 'Another file-only patch operation is already using this game folder.'
}

try {
    Recover-InterruptedIfPresent $manifest $resources $paths $journalPath
    Recover-DurableMigrationIfPresent `
        $manifest $resources $paths $ownBackupRoot $migrationPath $journalPath $statePath
    [string[]]$stockHashes = @($resources | ForEach-Object { ([string]$_.stock.sha256).ToUpperInvariant() })
    [string[]]$targetHashes = @($resources | ForEach-Object { ([string]$_.target.sha256).ToUpperInvariant() })
    [string[]]$currentHashes = Get-InstalledHashes $paths

    if ($Action -eq 'Restore') {
        $currentVectorId = Assert-KnownInstalledVector $manifest $currentHashes 'restore input vector'
        if ($currentVectorId -eq 'stock') {
            Write-Host 'All four original resources are already restored.'
            exit 0
        }
        [string[]]$stockBackups = Ensure-OwnStockBackups $resources $paths $backupParent $ownBackupRoot
        $staged = @()
        try {
            for ($index = 0; $index -lt 4; $index++) {
                $stage = New-SiblingPath $paths[$index] 'restore'
                [N16KrFileOnly.FileRecipeCore]::CopyDurable($stockBackups[$index], $stage)
                Assert-FileSpec $stage $resources[$index].stock "restore stage $($resources[$index].id)"
                $staged += $stage
            }
            $items = New-TransitionItems $resources $paths $currentHashes $stockHashes $staged
            [void](Invoke-AtomicFileSetTransaction $items $journalPath 'restore')
            Write-InstallState $statePath $manifest 'restored' $stockHashes
            Remove-AtomicTemporary @($journalPath)
            Write-Host 'Four-resource original restoration: OK'
        }
        finally {
            Remove-AtomicTemporary $staged
        }
        exit 0
    }

    $currentVectorId = Assert-KnownInstalledVector $manifest $currentHashes 'apply input vector'
    if ($currentVectorId -eq 'final') {
        [void](Ensure-OwnStockBackups $resources $paths $backupParent $ownBackupRoot)
        Write-Host 'The four-resource officer-name patch is already applied.'
        exit 0
    }

    [string[]]$stockBackups = Ensure-OwnStockBackups $resources $paths $backupParent $ownBackupRoot
    $targetStages = @()
    $snapshotPaths = @()
    $preserveSnapshots = $false
    $snapshotRoot = Join-Path $ownBackupRoot ('migration_snapshot_' + [Guid]::NewGuid().ToString('N'))
    [System.IO.Directory]::CreateDirectory($snapshotRoot) | Out-Null
    Assert-OrdinaryPathFromRoot $ownBackupRoot $snapshotRoot 'migration snapshot root'
    try {
        Write-Host 'Rebuilding all four final resources from verified stock backups...'
        for ($index = 0; $index -lt 4; $index++) {
            $resource = $resources[$index]
            $recipePath = Resolve-FileOnlyChild $PackageRoot ([string]$resource.recipe_path) "recipe $($resource.id)"
            if ($resource.kind -eq 'message') {
                [byte[]]$targetBytes = Build-Message $stockBackups[$index] $recipePath $resource
            }
            else {
                [byte[]]$targetBytes = Build-Font $stockBackups[$index] $recipePath (Join-Path $PackageRoot ([string]$resource.component_root).Replace('/', '\')) $resource
            }
            $stage = New-SiblingPath $paths[$index] 'target'
            [N16KrFileOnly.FileRecipeCore]::WriteDurable($stage, $targetBytes)
            $targetBytes = $null
            Assert-FileSpec $stage $resource.target "target stage $($resource.id)"
            $targetStages += $stage
        }

        for ($index = 0; $index -lt 4; $index++) {
            $snapshot = Join-Path $snapshotRoot ([string]$resources[$index].id + '.before.bak')
            [N16KrFileOnly.FileRecipeCore]::CopyDurable($paths[$index], $snapshot)
            if ((Get-Sha256 $snapshot) -ne $currentHashes[$index]) {
                throw "Migration snapshot verification failed for $($resources[$index].id)."
            }
            $snapshotPaths += $snapshot
        }
        $preserveSnapshots = $true
        [void](Write-DurableMigrationJournal `
            $manifest $resources $ownBackupRoot $migrationPath $currentVectorId `
            $currentHashes $snapshotRoot $snapshotPaths)

        try {
            if (-not (Test-HashVector $currentHashes $stockHashes)) {
                Write-Host 'Normalizing the pinned predecessor vector to verified stock as one four-file transaction...'
                $stockStages = @()
                try {
                    for ($index = 0; $index -lt 4; $index++) {
                        $stage = New-SiblingPath $paths[$index] 'stock'
                        [N16KrFileOnly.FileRecipeCore]::CopyDurable($stockBackups[$index], $stage)
                        $stockStages += $stage
                    }
                    $normalizeItems = New-TransitionItems $resources $paths $currentHashes $stockHashes $stockStages
                    [void](Invoke-AtomicFileSetTransaction $normalizeItems $journalPath 'normalize-stock')
                    Write-InstallState $statePath $manifest 'normalized_stock' $stockHashes
                    Remove-AtomicTemporary @($journalPath)
                }
                finally {
                    Remove-AtomicTemporary $stockStages
                }
            }

            $applyItems = New-TransitionItems $resources $paths $stockHashes $targetHashes $targetStages
            [void](Invoke-AtomicFileSetTransaction $applyItems $journalPath 'apply')
            Write-InstallState $statePath $manifest 'applied' $targetHashes
            Remove-AtomicTemporary @($journalPath)
            $preserveSnapshots = $false
        }
        catch {
            $applyError = $_.Exception.Message
            [string[]]$afterFailure = Get-InstalledHashes $paths
            if (-not (Test-HashVector $afterFailure $currentHashes)) {
                [void](Assert-KnownInstalledVector $manifest $afterFailure 'post-failure resource vector')
                $rollbackStages = @()
                try {
                    for ($index = 0; $index -lt 4; $index++) {
                        $stage = New-SiblingPath $paths[$index] 'input'
                        [N16KrFileOnly.FileRecipeCore]::CopyDurable($snapshotPaths[$index], $stage)
                        $rollbackStages += $stage
                    }
                    $rollbackItems = New-TransitionItems $resources $paths $afterFailure $currentHashes $rollbackStages
                    [void](Invoke-AtomicFileSetTransaction $rollbackItems $journalPath 'rollback-input')
                    Write-InstallState $statePath $manifest 'apply_failed_input_restored' $currentHashes
                    Remove-AtomicTemporary @($journalPath)
                    $preserveSnapshots = $false
                }
                finally {
                    Remove-AtomicTemporary $rollbackStages
                }
            }
            else {
                $preserveSnapshots = $false
            }
            throw "Apply failed; the four-file input vector was restored when possible: $applyError"
        }
        Write-Host 'Officer-name v0.1 four-resource file-only application: OK'
        Write-Host 'Use Simplified Chinese. For direct launch, set the working directory to the game root to avoid ERROR:-9001.'
    }
    finally {
        Remove-AtomicTemporary $targetStages
        if (-not $preserveSnapshots) {
            if (Test-Path -LiteralPath $migrationPath -PathType Leaf) {
                try {
                    $completedMigration = Read-ValidatedMigrationJournal `
                        $manifest $resources $ownBackupRoot $migrationPath
                    [string[]]$completedHashes = Get-InstalledHashes $paths
                    $completedVectorId = Assert-KnownInstalledVector `
                        $manifest $completedHashes 'completed migration vector'
                    if ($completedVectorId -ne 'final' -and
                        -not (Test-HashVector $completedHashes $completedMigration.InputHashes)) {
                        throw 'Completed migration cleanup is not paired with a safe final or input vector.'
                    }
                    Remove-ValidatedMigration `
                        $manifest $resources $ownBackupRoot $migrationPath $completedMigration
                }
                catch {
                    $preserveSnapshots = $true
                    Write-Warning "Durable migration cleanup will resume on the next run: $($_.Exception.Message)"
                }
            }
            else {
                Remove-AtomicTemporary $snapshotPaths
                if ((Test-Path -LiteralPath $snapshotRoot -PathType Container) -and
                    @(Get-ChildItem -LiteralPath $snapshotRoot -Force).Count -eq 0) {
                    [System.IO.Directory]::Delete($snapshotRoot, $false)
                }
            }
        }
        if ($preserveSnapshots -and $snapshotPaths.Count -gt 0) {
            Write-Warning "Preserving verified input snapshots after incomplete recovery: $snapshotRoot"
        }
    }
}
finally {
    $operationLock.Dispose()
}
