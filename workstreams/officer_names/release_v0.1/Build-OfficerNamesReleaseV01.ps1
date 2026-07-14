[CmdletBinding()]
param(
    [string]$MsguiRecipe,
    [string]$MsgdataRecipe,
    [string]$MsgevRecipe,
    [string]$FontPublicRoot,
    [string]$FinalPinsPath,
    [ValidateSet('Development', 'ReleaseCandidate')]
    [string]$Mode = 'Development',
    [string]$CandidatePinsPath,
    [string]$RecipeE2EAttestation,
    [string]$RuntimeQaAttestation,
    [string]$OutputRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ReleaseRoot = $PSScriptRoot
$KrPatchRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ReleaseRoot))
$ReleasesRoot = Join-Path $KrPatchRoot 'releases'
$TemplateRoot = Join-Path $ReleaseRoot 'template'
$SharedToolsRoot = Join-Path $KrPatchRoot 'workstreams\msgui_full\release_p4_vnext\template\tools'
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$ExpectedFontArtifacts = @(
    'licenses/OFL-NotoSansKR.txt',
    'licenses/OFL-NotoSerifKR.txt',
    'metrics/glyphs.jsonl',
    'payload/glyph_pixels_entry_6.pixels',
    'payload/glyph_pixels_entry_7.pixels'
)
$RecipeE2EPackagePath = 'attestations/four_resource_recipe_e2e.json'
$RuntimeQaPackagePath = 'attestations/runtime_qa.json'
. (Join-Path $TemplateRoot 'tools\FileOnlySafety.ps1')

if ([string]::IsNullOrWhiteSpace($MsguiRecipe)) {
    $MsguiRecipe = Join-Path $KrPatchRoot 'workstreams\msgui_full\release_p4_vnext\inputs\message\msgui_sc.recipe.json'
}
if ([string]::IsNullOrWhiteSpace($MsgdataRecipe)) {
    $MsgdataRecipe = Join-Path $KrPatchRoot 'workstreams\officer_names\full_v0.1\public\msgdata_sc.recipe.json'
}
if ([string]::IsNullOrWhiteSpace($MsgevRecipe)) {
    $MsgevRecipe = Join-Path $KrPatchRoot 'workstreams\officer_names\full_v0.1\public\msgev_sc.recipe.json'
}
if ([string]::IsNullOrWhiteSpace($FontPublicRoot)) {
    $FontPublicRoot = Join-Path $KrPatchRoot 'workstreams\officer_names\font_v5\public'
}
if ([string]::IsNullOrWhiteSpace($FinalPinsPath)) {
    $FinalPinsPath = Join-Path $ReleaseRoot 'inputs\final_pins.json'
}
if ([string]::IsNullOrWhiteSpace($CandidatePinsPath)) {
    $CandidatePinsPath = Join-Path $ReleaseRoot 'inputs\candidate_pins.json'
}
if ([string]::IsNullOrWhiteSpace($RecipeE2EAttestation)) {
    $RecipeE2EAttestation = Join-Path $ReleaseRoot 'inputs\four_resource_recipe_e2e.json'
}
if ([string]::IsNullOrWhiteSpace($RuntimeQaAttestation)) {
    $RuntimeQaAttestation = Join-Path $ReleaseRoot 'inputs\runtime_qa.json'
}
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $outputLeaf = if ($Mode -eq 'ReleaseCandidate') {
        'officer_names_file_only_v0.1-rc'
    }
    else {
        'officer_names_file_only_v0.1-dev'
    }
    $OutputRoot = Join-Path $ReleasesRoot $outputLeaf
}

function Get-FullPath([string]$Path) { return [System.IO.Path]::GetFullPath($Path) }
function Get-Sha256([string]$Path) { return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToUpperInvariant() }

function Read-StrictJson([string]$Path) {
    [byte[]]$bytes = [System.IO.File]::ReadAllBytes($Path)
    [N16KrFileOnly.JsonKeyGuard]::AssertNoDuplicateKeys($bytes)
    $encoding = New-Object System.Text.UTF8Encoding($false, $true)
    return ($encoding.GetString($bytes) | ConvertFrom-Json)
}

function Write-Json([string]$Path, $Value, [int]$Depth = 20) {
    $json = ConvertTo-Json -InputObject $Value -Depth $Depth
    [System.IO.File]::WriteAllText($Path, $json + "`n", $Utf8NoBom)
}

function Assert-RequiredInputs([object[]]$Requirements) {
    $missing = New-Object 'System.Collections.Generic.List[string]'
    foreach ($requirement in $Requirements) {
        $exists = if ($requirement.kind -eq 'directory') {
            Test-Path -LiteralPath $requirement.path -PathType Container
        }
        else {
            Test-Path -LiteralPath $requirement.path -PathType Leaf
        }
        if (-not $exists) { $missing.Add("$($requirement.label): $($requirement.path)") }
    }
    if ($missing.Count -gt 0) {
        throw "Complete officer-name release inputs are not ready. No placeholder package was created.`nMissing:`n - $($missing -join "`n - ")"
    }
}

function Assert-FinalPins($Pins) {
    Assert-ExactObjectProperties $Pins @('font_artifacts', 'resources', 'schema') 'final release pins'
    if ($Pins.schema -ne 'nobu16.officer-names-final-pins.v1') {
        throw 'Final release pin file has an unsupported schema.'
    }
    $fixedStocks = [ordered]@{
        msgui = 'C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82'
        msgdata = '0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E'
        msgev = '7221A53E6E5CF493A3FAFFFCE35280E8147898120EEC59E460A2429AA265C1F9'
        font = '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99'
    }
    [string[]]$names = @($Pins.resources.PSObject.Properties.Name)
    [string[]]$expectedNames = @('font', 'msgdata', 'msgev', 'msgui')
    [Array]::Sort($names, [StringComparer]::Ordinal)
    [Array]::Sort($expectedNames, [StringComparer]::Ordinal)
    if (($names -join ',') -cne ($expectedNames -join ',')) {
        throw 'Final release pins must contain exactly msgui, msgdata, msgev, and font.'
    }
    foreach ($name in @('msgui', 'msgdata', 'msgev', 'font')) {
        $pin = $Pins.resources.PSObject.Properties[$name].Value
        [string[]]$properties = @($pin.PSObject.Properties.Name)
        [Array]::Sort($properties, [StringComparer]::Ordinal)
        [string[]]$expectedProperties = @('recipe_sha256', 'stock_sha256', 'target_sha256')
        [Array]::Sort($expectedProperties, [StringComparer]::Ordinal)
        if (($properties -join ',') -cne ($expectedProperties -join ',') -or
            ([string]$pin.stock_sha256).ToUpperInvariant() -ne $fixedStocks[$name] -or
            [string]$pin.recipe_sha256 -notmatch '\A[0-9A-F]{64}\z' -or
            [string]$pin.target_sha256 -notmatch '\A[0-9A-F]{64}\z') {
            throw "Final release pin contract is invalid for $name."
        }
    }
    Assert-PinnedArtifactSet @($Pins.font_artifacts) $ExpectedFontArtifacts $null 'final font artifact pins'
}

function Assert-CandidatePins($Pins) {
    Assert-ExactObjectProperties $Pins @('recipe_e2e', 'runtime_qa', 'schema') 'release-candidate pins'
    if ($Pins.schema -ne 'nobu16.officer-names-candidate-pins.v1') {
        throw 'Release-candidate pin file has an unsupported schema.'
    }
    foreach ($name in @('recipe_e2e', 'runtime_qa')) {
        $pin = $Pins.PSObject.Properties[$name].Value
        Assert-ExactObjectProperties $pin @('sha256', 'size') "release-candidate $name pin"
        if ([int64]$pin.size -le 0 -or [string]$pin.sha256 -notmatch '\A[0-9A-F]{64}\z') {
            throw "Release-candidate $name pin is malformed."
        }
    }
}

function Assert-PinnedInputFile([string]$Path, $Pin, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label is missing: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 -or
        [int64]$item.Length -ne [int64]$Pin.size -or
        (Get-Sha256 $Path) -ne ([string]$Pin.sha256).ToUpperInvariant()) {
        throw "$Label differs from the reviewed release-candidate pin."
    }
}

function Assert-E2EAttestation($Attestation, $FinalPins) {
    Assert-ExactObjectProperties $Attestation @('passed', 'release_id', 'resources', 'schema') 'four-resource recipe E2E attestation'
    if ($Attestation.schema -ne 'nobu16.officer-names-four-resource-recipe-e2e.v1' -or
        $Attestation.release_id -ne 'officer-names-v0.1' -or
        $Attestation.passed -ne $true) {
        throw 'Four-resource recipe E2E attestation is not a passing v0.1 attestation.'
    }
    Assert-ExactObjectProperties $Attestation.resources @('font', 'msgdata', 'msgev', 'msgui') 'four-resource recipe E2E resource pins'
    foreach ($name in @('msgui', 'msgdata', 'msgev', 'font')) {
        $actual = $Attestation.resources.PSObject.Properties[$name].Value
        $expected = $FinalPins.resources.PSObject.Properties[$name].Value
        Assert-ExactObjectProperties $actual @('recipe_sha256', 'stock_sha256', 'target_sha256') "four-resource recipe E2E $name"
        if (([string]$actual.recipe_sha256).ToUpperInvariant() -ne ([string]$expected.recipe_sha256).ToUpperInvariant() -or
            ([string]$actual.stock_sha256).ToUpperInvariant() -ne ([string]$expected.stock_sha256).ToUpperInvariant() -or
            ([string]$actual.target_sha256).ToUpperInvariant() -ne ([string]$expected.target_sha256).ToUpperInvariant()) {
            throw "Four-resource recipe E2E attestation does not cover the final $name pins."
        }
    }
}

function Assert-RuntimeQaAttestation($Attestation, $FinalPins) {
    Assert-ExactObjectProperties $Attestation @(
        'error_9001_observed', 'passed', 'release_id', 'resource_targets',
        'schema', 'working_directory'
    ) 'runtime QA attestation'
    if ($Attestation.schema -ne 'nobu16.officer-names-runtime-qa.v1' -or
        $Attestation.release_id -ne 'officer-names-v0.1' -or
        $Attestation.passed -ne $true -or
        $Attestation.error_9001_observed -ne $false -or
        $Attestation.working_directory -ne 'game_root') {
        throw 'Runtime QA attestation is not a passing game-root v0.1 attestation.'
    }
    Assert-ExactObjectProperties $Attestation.resource_targets @('font', 'msgdata', 'msgev', 'msgui') 'runtime QA target hashes'
    foreach ($name in @('msgui', 'msgdata', 'msgev', 'font')) {
        $actual = ([string]$Attestation.resource_targets.PSObject.Properties[$name].Value).ToUpperInvariant()
        $expected = ([string]$FinalPins.resources.PSObject.Properties[$name].Value.target_sha256).ToUpperInvariant()
        if ($actual -ne $expected) {
            throw "Runtime QA attestation does not cover the final $name target."
        }
    }
}

function Assert-MessageInput(
    [string]$Path,
    [string]$RelativePath,
    [string]$ExpectedStockHash,
    [string]$ExpectedTargetHash,
    [string]$ExpectedRecipeHash,
    [int]$MinimumOperationCount
) {
    if ((Get-Sha256 $Path) -ne $ExpectedRecipeHash) {
        throw "Message recipe is not the pinned full artifact: $Path"
    }
    $recipe = Read-StrictJson $Path
    if ($recipe.schema -ne 'nobu16.file-only-msg-recipe.v1' -or
        $recipe.language -ne 'SC' -or
        $recipe.file_only -ne $true -or
        [string]$recipe.source.relative_path -ne $RelativePath -or
        ([string]$recipe.source.sha256).ToUpperInvariant() -ne $ExpectedStockHash -or
        ([string]$recipe.target.sha256).ToUpperInvariant() -ne $ExpectedTargetHash -or
        @($recipe.operations).Count -lt $MinimumOperationCount -or
        $recipe.payload_policy.contains_complete_source -ne $false -or
        $recipe.payload_policy.contains_complete_target -ne $false -or
        $recipe.payload_policy.contains_executable_bytes -ne $false -or
        $recipe.payload_policy.stock_file_is_required_at_apply_time -ne $true) {
        throw "Message recipe failed the complete source-free contract: $Path"
    }
    return $recipe
}

function Get-MessageResource([string]$Id, [string]$RecipePath, $Recipe, [string[]]$Predecessors) {
    return [ordered]@{
        id = $Id
        kind = 'message'
        relative_path = [string]$Recipe.source.relative_path
        recipe_path = "components/message/${Id}_sc.recipe.json"
        component_root = 'components/message'
        stock = [ordered]@{ size = [int64]$Recipe.source.size; sha256 = ([string]$Recipe.source.sha256).ToUpperInvariant() }
        target = [ordered]@{ size = [int64]$Recipe.target.size; sha256 = ([string]$Recipe.target.sha256).ToUpperInvariant() }
        recipe = [ordered]@{ size = [int64](Get-Item -LiteralPath $RecipePath).Length; sha256 = Get-Sha256 $RecipePath }
        predecessor_hashes = @($Predecessors)
    }
}

function Read-PredecessorTarget(
    [string]$Path,
    [string]$RelativePath,
    [string]$StockHash,
    [int64]$PinnedSize,
    [string]$PinnedSha256,
    [string]$PinnedTargetSha256
) {
    if ($PinnedSize -le 0 -or
        $StockHash -notmatch '\A[0-9A-F]{64}\z' -or
        $PinnedSha256 -notmatch '\A[0-9A-F]{64}\z' -or
        $PinnedTargetSha256 -notmatch '\A[0-9A-F]{64}\z') {
        throw "Predecessor pin contract is malformed: $Path"
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 -or
        [int64]$item.Length -ne $PinnedSize -or
        (Get-Sha256 $Path) -ne $PinnedSha256.ToUpperInvariant()) {
        throw "Predecessor recipe differs from the reviewed size+SHA-256 pin: $Path"
    }
    $recipe = Read-StrictJson $Path
    if ($recipe.schema -eq 'nobu16.file-only-msg-recipe.v1') {
        if ([string]$recipe.source.relative_path -ne $RelativePath -or
            ([string]$recipe.source.sha256).ToUpperInvariant() -ne $StockHash -or
            ([string]$recipe.target.sha256).ToUpperInvariant() -ne $PinnedTargetSha256.ToUpperInvariant()) {
            throw "Predecessor message recipe does not share the pinned stock: $Path"
        }
        return $PinnedTargetSha256.ToUpperInvariant()
    }
    if ($recipe.schema -eq 'nobu16.file-only-g1n-tail-recipe.v2') {
        $language = $recipe.languages.SC
        if ([string]$language.stock_archive.path -ne $RelativePath -or
            ([string]$language.stock_archive.sha256).ToUpperInvariant() -ne $StockHash -or
            ([string]$language.target_archive.sha256).ToUpperInvariant() -ne $PinnedTargetSha256.ToUpperInvariant()) {
            throw "Predecessor font recipe does not share the pinned stock: $Path"
        }
        return $PinnedTargetSha256.ToUpperInvariant()
    }
    throw "Unsupported predecessor recipe schema: $Path"
}

$MsguiRecipe = Get-FullPath $MsguiRecipe
$MsgdataRecipe = Get-FullPath $MsgdataRecipe
$MsgevRecipe = Get-FullPath $MsgevRecipe
$FontPublicRoot = Get-FullPath $FontPublicRoot
$FinalPinsPath = Get-FullPath $FinalPinsPath
$CandidatePinsPath = Get-FullPath $CandidatePinsPath
$RecipeE2EAttestation = Get-FullPath $RecipeE2EAttestation
$RuntimeQaAttestation = Get-FullPath $RuntimeQaAttestation
$OutputRoot = Get-FullPath $OutputRoot
$isCandidate = $Mode -eq 'ReleaseCandidate'
$CoreSource = Join-Path $SharedToolsRoot 'FileRecipeCore.cs'
$GuardSource = Join-Path $SharedToolsRoot 'JsonKeyGuard.cs'
$MsgdataProbeRecipe = Join-Path $KrPatchRoot 'workstreams\officer_names\probe_v0.1\public\msgdata_sc.recipe.json'
$MsgevProbeRecipe = Join-Path $KrPatchRoot 'workstreams\officer_names\probe_v0.1\public\msgev_sc.recipe.json'
$FontV4Recipe = Join-Path $KrPatchRoot 'workstreams\msgui_full\release_p4_vnext\inputs\font\recipe.json'
$FontRecipe = Join-Path $FontPublicRoot 'recipe.json'
$FontPayload6 = Join-Path $FontPublicRoot 'payload\glyph_pixels_entry_6.pixels'
$FontPayload7 = Join-Path $FontPublicRoot 'payload\glyph_pixels_entry_7.pixels'
$FontMetrics = Join-Path $FontPublicRoot 'metrics\glyphs.jsonl'
$FontSansLicense = Join-Path $FontPublicRoot 'licenses\OFL-NotoSansKR.txt'
$FontSerifLicense = Join-Path $FontPublicRoot 'licenses\OFL-NotoSerifKR.txt'

if ($isCandidate) {
    Assert-RequiredInputs @(
        [pscustomobject]@{ label = 'reviewed release-candidate pins'; path = $CandidatePinsPath; kind = 'file' },
        [pscustomobject]@{ label = 'passing four-resource recipe E2E attestation'; path = $RecipeE2EAttestation; kind = 'file' },
        [pscustomobject]@{ label = 'passing runtime QA attestation'; path = $RuntimeQaAttestation; kind = 'file' }
    )
}

$requirements = @(
    [pscustomobject]@{ label = 'reviewed final release pins'; path = $FinalPinsPath; kind = 'file' },
    [pscustomobject]@{ label = 'full msgui recipe'; path = $MsguiRecipe; kind = 'file' },
    [pscustomobject]@{ label = 'full msgdata recipe'; path = $MsgdataRecipe; kind = 'file' },
    [pscustomobject]@{ label = 'full msgev recipe'; path = $MsgevRecipe; kind = 'file' },
    [pscustomobject]@{ label = 'font-v5 public root'; path = $FontPublicRoot; kind = 'directory' },
    [pscustomobject]@{ label = 'font-v5 recipe'; path = $FontRecipe; kind = 'file' },
    [pscustomobject]@{ label = 'font-v5 entry 6 generated pixels'; path = $FontPayload6; kind = 'file' },
    [pscustomobject]@{ label = 'font-v5 entry 7 generated pixels'; path = $FontPayload7; kind = 'file' },
    [pscustomobject]@{ label = 'font-v5 metrics'; path = $FontMetrics; kind = 'file' },
    [pscustomobject]@{ label = 'font-v5 sans license'; path = $FontSansLicense; kind = 'file' },
    [pscustomobject]@{ label = 'font-v5 serif license'; path = $FontSerifLicense; kind = 'file' },
    [pscustomobject]@{ label = 'msgdata probe predecessor recipe'; path = $MsgdataProbeRecipe; kind = 'file' },
    [pscustomobject]@{ label = 'msgev probe predecessor recipe'; path = $MsgevProbeRecipe; kind = 'file' },
    [pscustomobject]@{ label = 'font-v4 predecessor recipe'; path = $FontV4Recipe; kind = 'file' },
    [pscustomobject]@{ label = 'shared file recipe core'; path = $CoreSource; kind = 'file' },
    [pscustomobject]@{ label = 'shared strict JSON guard'; path = $GuardSource; kind = 'file' }
)
Assert-RequiredInputs $requirements

if ((Get-Sha256 $CoreSource) -ne '04643FDDA1617663DB4B2812582C5F87FA9D55A46D1861F22570C7C1B7266B79' -or
    [int64](Get-Item -LiteralPath $CoreSource).Length -ne 28466 -or
    (Get-Sha256 $GuardSource) -ne '6A1ABEC0899A1D4256153E49E8204DAE343EC5D7887DB3047192A8168678DA60' -or
    [int64](Get-Item -LiteralPath $GuardSource).Length -ne 11304) {
    throw 'Shared C# verifier sources changed; review and repin before building.'
}
Add-Type -Path $GuardSource
$finalPins = Read-StrictJson $FinalPinsPath
Assert-FinalPins $finalPins
$msguiPin = $finalPins.resources.msgui
$msgdataPin = $finalPins.resources.msgdata
$msgevPin = $finalPins.resources.msgev
$fontPin = $finalPins.resources.font
$recipeE2ESpec = $null
$runtimeQaSpec = $null
if ($isCandidate) {
    $candidatePins = Read-StrictJson $CandidatePinsPath
    Assert-CandidatePins $candidatePins
    Assert-PinnedInputFile $RecipeE2EAttestation $candidatePins.recipe_e2e 'four-resource recipe E2E attestation'
    Assert-PinnedInputFile $RuntimeQaAttestation $candidatePins.runtime_qa 'runtime QA attestation'
    $recipeE2E = Read-StrictJson $RecipeE2EAttestation
    $runtimeQa = Read-StrictJson $RuntimeQaAttestation
    Assert-E2EAttestation $recipeE2E $finalPins
    Assert-RuntimeQaAttestation $runtimeQa $finalPins
    $recipeE2ESpec = [ordered]@{
        path = $RecipeE2EPackagePath
        size = [int64]$candidatePins.recipe_e2e.size
        sha256 = ([string]$candidatePins.recipe_e2e.sha256).ToUpperInvariant()
    }
    $runtimeQaSpec = [ordered]@{
        path = $RuntimeQaPackagePath
        size = [int64]$candidatePins.runtime_qa.size
        sha256 = ([string]$candidatePins.runtime_qa.sha256).ToUpperInvariant()
    }
}

$msgui = Assert-MessageInput $MsguiRecipe 'MSG_PK/SC/msgui.bin' `
    ([string]$msguiPin.stock_sha256).ToUpperInvariant() `
    ([string]$msguiPin.target_sha256).ToUpperInvariant() `
    ([string]$msguiPin.recipe_sha256).ToUpperInvariant() 3000
$msgdata = Assert-MessageInput $MsgdataRecipe 'MSG_PK/SC/msgdata.bin' `
    ([string]$msgdataPin.stock_sha256).ToUpperInvariant() `
    ([string]$msgdataPin.target_sha256).ToUpperInvariant() `
    ([string]$msgdataPin.recipe_sha256).ToUpperInvariant() 1000
$msgev = Assert-MessageInput $MsgevRecipe 'MSG_PK/SC/msgev.bin' `
    ([string]$msgevPin.stock_sha256).ToUpperInvariant() `
    ([string]$msgevPin.target_sha256).ToUpperInvariant() `
    ([string]$msgevPin.recipe_sha256).ToUpperInvariant() 2000

$font = Read-StrictJson $FontRecipe
$fontLanguage = $font.languages.SC
$fontPublicFiles = @($ExpectedFontArtifacts + 'recipe.json')
Assert-ExactOrdinaryFileSet $FontPublicRoot $fontPublicFiles 'font-v5 public input tree'
if ($font.schema -ne 'nobu16.file-only-g1n-tail-recipe.v2' -or
    $font.file_only -ne $true -or
    $font.process_memory_access -ne $false -or
    $font.registry_access -ne $false -or
    @($font.runtime_patch_features).Count -ne 0 -or
    $font.payload_policy.commercial_original_bytes_in_public_payload -ne $false -or
    [string]$fontLanguage.stock_archive.path -ne 'RES_SC/res_lang.bin' -or
    ([string]$fontLanguage.stock_archive.sha256).ToUpperInvariant() -ne ([string]$fontPin.stock_sha256).ToUpperInvariant() -or
    ([string]$fontLanguage.target_archive.sha256).ToUpperInvariant() -ne ([string]$fontPin.target_sha256).ToUpperInvariant() -or
    (Get-Sha256 $FontRecipe) -ne ([string]$fontPin.recipe_sha256).ToUpperInvariant()) {
    throw 'Font-v5 public input failed the complete source-free contract.'
}
Assert-PinnedArtifactSet @($finalPins.font_artifacts) $ExpectedFontArtifacts $FontPublicRoot 'final font artifact pins'
$fontPayloadInventory = @($font.payload_inventory)
if ($fontPayloadInventory.Count -ne $ExpectedFontArtifacts.Count) {
    throw 'Font-v5 recipe must reference exactly the five reviewed license, metrics, and pixel artifacts.'
}
[string[]]$fontPayloadInventoryPaths = @($fontPayloadInventory | ForEach-Object { [string]$_.path })
Assert-UniqueCanonicalPaths $fontPayloadInventoryPaths 'font-v5 recipe payload inventory'
[string[]]$sortedFontPayloadInventoryPaths = @($fontPayloadInventoryPaths)
[string[]]$sortedExpectedFontArtifacts = @($ExpectedFontArtifacts)
[Array]::Sort($sortedFontPayloadInventoryPaths, [StringComparer]::Ordinal)
[Array]::Sort($sortedExpectedFontArtifacts, [StringComparer]::Ordinal)
if (($sortedFontPayloadInventoryPaths -join "`n") -cne ($sortedExpectedFontArtifacts -join "`n")) {
    throw 'Font-v5 recipe payload inventory contains a missing, additional, or case-colliding artifact path.'
}
foreach ($artifactPin in @($finalPins.font_artifacts)) {
    $matches = @($fontPayloadInventory | Where-Object { [string]$_.path -ceq [string]$artifactPin.path })
    if ($matches.Count -ne 1) {
        throw "Font-v5 recipe does not uniquely reference $($artifactPin.path)."
    }
    $inventoryItem = $matches[0]
    Assert-ExactObjectProperties $inventoryItem @('origin', 'path', 'sha256', 'size') "font-v5 recipe payload $($artifactPin.path)"
    if ([string]::IsNullOrWhiteSpace([string]$inventoryItem.origin) -or
        [int64]$inventoryItem.size -ne [int64]$artifactPin.size -or
        ([string]$inventoryItem.sha256).ToUpperInvariant() -ne ([string]$artifactPin.sha256).ToUpperInvariant()) {
        throw "Font-v5 recipe payload pin differs from final pins for $($artifactPin.path)."
    }
}
foreach ($entryName in @('6', '7')) {
    $payload = $fontLanguage.entries.PSObject.Properties[$entryName].Value.pixel_payload
    $expectedPath = "payload/glyph_pixels_entry_${entryName}.pixels"
    $artifactPin = @($finalPins.font_artifacts | Where-Object { [string]$_.path -ceq $expectedPath })[0]
    if ([string]$payload.file -cne $expectedPath -or
        [int64]$payload.size -ne [int64]$artifactPin.size -or
        ([string]$payload.sha256).ToUpperInvariant() -ne ([string]$artifactPin.sha256).ToUpperInvariant()) {
        throw "Font-v5 entry $entryName does not reference the exact reviewed pixel artifact."
    }
}

$msgdataProbeHash = Read-PredecessorTarget `
    $MsgdataProbeRecipe 'MSG_PK/SC/msgdata.bin' `
    '0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E' `
    2929 '1D9B00EA9C6A26F0ABF012F10A8E505BC20FACA17A99677AB9A3A9FD935F4CB8' `
    '4BC5079DA4ADF787BFCF5D7B2479F659E6F57BFB13572A6B696D26CB45F5063F'
$msgevProbeHash = Read-PredecessorTarget `
    $MsgevProbeRecipe 'MSG_PK/SC/msgev.bin' `
    '7221A53E6E5CF493A3FAFFFCE35280E8147898120EEC59E460A2429AA265C1F9' `
    1969 '923414FCEB03552B5370ED495F4E29439AF38D33D888679B0377175C78FE93D1' `
    'AFE9F0CCA5518F6BA04B44449971C004A9D674F0663DAF310780988C4A1977B9'
$fontV4Hash = Read-PredecessorTarget `
    $FontV4Recipe 'RES_SC/res_lang.bin' `
    '916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99' `
    482506 '6E88317D4A48EF38EDE015E8D61FE48625D8CC2B758B2B2760374021511BC7DE' `
    '9E0FFEAFCF3C50060E1E223988FD01BA2470987FB97A3B6DA75E0B7E3591AE9A'

$resources = @(
    (Get-MessageResource 'msgui' $MsguiRecipe $msgui @()),
    (Get-MessageResource 'msgdata' $MsgdataRecipe $msgdata @($msgdataProbeHash)),
    (Get-MessageResource 'msgev' $MsgevRecipe $msgev @($msgevProbeHash)),
    [ordered]@{
        id = 'font'
        kind = 'font'
        relative_path = 'RES_SC/res_lang.bin'
        recipe_path = 'components/font/recipe.json'
        component_root = 'components/font'
        stock = [ordered]@{ size = [int64]$fontLanguage.stock_archive.size; sha256 = ([string]$fontLanguage.stock_archive.sha256).ToUpperInvariant() }
        target = [ordered]@{ size = [int64]$fontLanguage.target_archive.size; sha256 = ([string]$fontLanguage.target_archive.sha256).ToUpperInvariant() }
        recipe = [ordered]@{ size = [int64](Get-Item -LiteralPath $FontRecipe).Length; sha256 = Get-Sha256 $FontRecipe }
        predecessor_hashes = @($fontV4Hash)
    }
)
$acceptedVectors = @(
    [ordered]@{
        id = 'stock'
        hashes = @($resources | ForEach-Object { ([string]$_.stock.sha256).ToUpperInvariant() })
    },
    [ordered]@{
        id = 'final'
        hashes = @($resources | ForEach-Object { ([string]$_.target.sha256).ToUpperInvariant() })
    },
    [ordered]@{
        id = 'officer_probe_v0.1_on_msgui_full_font_v4'
        hashes = @(
            ([string]$resources[0].target.sha256).ToUpperInvariant(),
            $msgdataProbeHash,
            $msgevProbeHash,
            $fontV4Hash
        )
    }
)

$fullReleasesRoot = (Get-FullPath $ReleasesRoot).TrimEnd('\')
$outputParent = (Get-FullPath ([System.IO.Path]::GetDirectoryName($OutputRoot))).TrimEnd('\')
$outputLeaf = [System.IO.Path]::GetFileName($OutputRoot)
Assert-SafeRelativePath $outputLeaf 'release output directory name'
if (-not [string]::Equals($outputParent, $fullReleasesRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'OutputRoot must be a direct child of KR_PATCH_WORK\releases.'
}
if (Test-Path -LiteralPath $OutputRoot) {
    throw "OutputRoot already exists; refusing to overwrite it: $OutputRoot"
}
[void](Assert-OrdinaryPathFromRoot $KrPatchRoot $KrPatchRoot 'KR_PATCH_WORK root')
if (Test-Path -LiteralPath $ReleasesRoot) {
    [void](Assert-ExactCaseRelativePath $KrPatchRoot 'releases' 'release output root')
    Assert-OrdinaryPathFromRoot $KrPatchRoot $ReleasesRoot 'release output root'
}
[System.IO.Directory]::CreateDirectory($ReleasesRoot) | Out-Null
[void](Assert-ExactCaseRelativePath $KrPatchRoot 'releases' 'release output root')
Assert-OrdinaryPathFromRoot $KrPatchRoot $ReleasesRoot 'release output root'
$staging = Join-Path $ReleasesRoot ('.officer_names_v0.1.staging.' + [Guid]::NewGuid().ToString('N'))
[System.IO.Directory]::CreateDirectory($staging) | Out-Null
$manifestMode = if ($isCandidate) { 'release-candidate' } else { 'development' }
$manifestVersion = if ($isCandidate) { '0.1-rc' } else { '0.1-dev' }
$developmentMilestone = -not $isCandidate
$releaseEligible = $isCandidate
$packageFileCount = if ($isCandidate) { 21 } else { 19 }
$validation = [ordered]@{
    recipe_e2e = $recipeE2ESpec
    runtime_qa = $runtimeQaSpec
}

try {
    foreach ($relative in @('components\message', 'components\font\payload', 'components\font\metrics', 'components\font\licenses', 'tools')) {
        [System.IO.Directory]::CreateDirectory((Join-Path $staging $relative)) | Out-Null
    }
    Copy-Item -LiteralPath $MsguiRecipe -Destination (Join-Path $staging 'components\message\msgui_sc.recipe.json')
    Copy-Item -LiteralPath $MsgdataRecipe -Destination (Join-Path $staging 'components\message\msgdata_sc.recipe.json')
    Copy-Item -LiteralPath $MsgevRecipe -Destination (Join-Path $staging 'components\message\msgev_sc.recipe.json')
    foreach ($relative in $fontPublicFiles) {
        $source = Join-Path $FontPublicRoot ($relative.Replace('/', '\'))
        $destination = Join-Path $staging ('components\font\' + $relative.Replace('/', '\'))
        Copy-Item -LiteralPath $source -Destination $destination
    }
    for ($index = 0; $index -lt 3; $index++) {
        $stagedRecipe = Join-Path $staging ([string]$resources[$index].recipe_path).Replace('/', '\')
        Assert-PinnedInputFile $stagedRecipe $resources[$index].recipe "staged $($resources[$index].id) recipe"
    }
    $stagedFontRoot = Join-Path $staging 'components\font'
    Assert-ExactOrdinaryFileSet $stagedFontRoot $fontPublicFiles 'staged font component'
    Assert-PinnedArtifactSet @($finalPins.font_artifacts) $ExpectedFontArtifacts $stagedFontRoot 'staged font artifacts'
    Assert-PinnedInputFile (Join-Path $stagedFontRoot 'recipe.json') $resources[3].recipe 'staged font recipe'
    if ($isCandidate) {
        [System.IO.Directory]::CreateDirectory((Join-Path $staging 'attestations')) | Out-Null
        Copy-Item -LiteralPath $RecipeE2EAttestation -Destination (Join-Path $staging ($RecipeE2EPackagePath.Replace('/', '\')))
        Copy-Item -LiteralPath $RuntimeQaAttestation -Destination (Join-Path $staging ($RuntimeQaPackagePath.Replace('/', '\')))
        Assert-PinnedInputFile (Join-Path $staging ($RecipeE2EPackagePath.Replace('/', '\'))) $recipeE2ESpec 'packaged four-resource recipe E2E attestation'
        Assert-PinnedInputFile (Join-Path $staging ($RuntimeQaPackagePath.Replace('/', '\'))) $runtimeQaSpec 'packaged runtime QA attestation'
    }
    Copy-Item -LiteralPath $CoreSource -Destination (Join-Path $staging 'tools\FileRecipeCore.cs')
    Copy-Item -LiteralPath $GuardSource -Destination (Join-Path $staging 'tools\JsonKeyGuard.cs')
    Copy-Item -LiteralPath (Join-Path $TemplateRoot 'tools\AtomicFileSet.ps1') -Destination (Join-Path $staging 'tools\AtomicFileSet.ps1')
    Copy-Item -LiteralPath (Join-Path $TemplateRoot 'tools\FileOnlySafety.ps1') -Destination (Join-Path $staging 'tools\FileOnlySafety.ps1')

    $atomicPath = Join-Path $staging 'tools\AtomicFileSet.ps1'
    $safetyPath = Join-Path $staging 'tools\FileOnlySafety.ps1'
    $installerText = [System.IO.File]::ReadAllText((Join-Path $TemplateRoot 'tools\Invoke-OfficerNamesFileOnlyPatch.ps1'))
    $installerText = $installerText.Replace('@ATOMIC_SIZE@', ([string](Get-Item -LiteralPath $atomicPath).Length))
    $installerText = $installerText.Replace('@ATOMIC_SHA256@', (Get-Sha256 $atomicPath))
    $installerText = $installerText.Replace('@SAFETY_SIZE@', ([string](Get-Item -LiteralPath $safetyPath).Length))
    $installerText = $installerText.Replace('@SAFETY_SHA256@', (Get-Sha256 $safetyPath))
    $resourceTokens = @('MSGUI', 'MSGDATA', 'MSGEV', 'FONT')
    for ($index = 0; $index -lt 4; $index++) {
        $token = $resourceTokens[$index]
        $resource = $resources[$index]
        $installerText = $installerText.Replace("@${token}_STOCK_SIZE@", [string]$resource.stock.size)
        $installerText = $installerText.Replace("@${token}_STOCK_SHA256@", ([string]$resource.stock.sha256).ToUpperInvariant())
        $installerText = $installerText.Replace("@${token}_TARGET_SIZE@", [string]$resource.target.size)
        $installerText = $installerText.Replace("@${token}_TARGET_SHA256@", ([string]$resource.target.sha256).ToUpperInvariant())
        $installerText = $installerText.Replace("@${token}_RECIPE_SIZE@", [string]$resource.recipe.size)
        $installerText = $installerText.Replace("@${token}_RECIPE_SHA256@", ([string]$resource.recipe.sha256).ToUpperInvariant())
    }
    $installerText = $installerText.Replace('@MSGDATA_PREDECESSOR_SHA256@', $msgdataProbeHash)
    $installerText = $installerText.Replace('@MSGEV_PREDECESSOR_SHA256@', $msgevProbeHash)
    $installerText = $installerText.Replace('@FONT_PREDECESSOR_SHA256@', $fontV4Hash)
    for ($index = 0; $index -lt $ExpectedFontArtifacts.Count; $index++) {
        $artifact = $finalPins.font_artifacts[$index]
        $installerText = $installerText.Replace("@FONT_ARTIFACT_${index}_SIZE@", [string]$artifact.size)
        $installerText = $installerText.Replace("@FONT_ARTIFACT_${index}_SHA256@", ([string]$artifact.sha256).ToUpperInvariant())
    }
    $installerText = $installerText.Replace('@PACKAGE_MODE@', $manifestMode)
    $installerText = $installerText.Replace('@PACKAGE_VERSION@', $manifestVersion)
    $installerText = $installerText.Replace('@DEVELOPMENT_MILESTONE@', ([string]$developmentMilestone).ToLowerInvariant())
    $installerText = $installerText.Replace('@RELEASE_ELIGIBLE@', ([string]$releaseEligible).ToLowerInvariant())
    $installerText = $installerText.Replace('@PACKAGE_FILE_COUNT@', [string]$packageFileCount)
    $recipeE2ETokenSpec = if ($isCandidate) { $recipeE2ESpec } else { [pscustomobject]@{ size = 0; sha256 = ('0' * 64) } }
    $runtimeQaTokenSpec = if ($isCandidate) { $runtimeQaSpec } else { [pscustomobject]@{ size = 0; sha256 = ('0' * 64) } }
    $installerText = $installerText.Replace('@RECIPE_E2E_SIZE@', [string]$recipeE2ETokenSpec.size)
    $installerText = $installerText.Replace('@RECIPE_E2E_SHA256@', ([string]$recipeE2ETokenSpec.sha256).ToUpperInvariant())
    $installerText = $installerText.Replace('@RUNTIME_QA_SIZE@', [string]$runtimeQaTokenSpec.size)
    $installerText = $installerText.Replace('@RUNTIME_QA_SHA256@', ([string]$runtimeQaTokenSpec.sha256).ToUpperInvariant())
    if ($installerText -match '@[A-Z0-9_]+@') {
        throw "Installer template contains an unresolved release token: $($Matches[0])"
    }
    $installerTokens = $null
    $installerParseErrors = $null
    $installerAst = [System.Management.Automation.Language.Parser]::ParseInput(
        $installerText, [ref]$installerTokens, [ref]$installerParseErrors)
    if ($installerParseErrors.Count -ne 0) {
        throw "Generated installer failed PowerShell AST parsing: $($installerParseErrors[0].Message)"
    }
    $forbiddenInstallerCommands = @(
        'Get-Process', 'Start-Process', 'Stop-Process', 'Invoke-Expression',
        'Invoke-Command', 'Start-Job', 'Set-ItemProperty', 'New-ItemProperty'
    )
    foreach ($command in $installerAst.FindAll({
                param($node)
                $node -is [System.Management.Automation.Language.CommandAst]
            }, $true)) {
        $commandName = $command.GetCommandName()
        if (-not [string]::IsNullOrWhiteSpace($commandName) -and
            $commandName -in $forbiddenInstallerCommands) {
            throw "Generated installer contains a forbidden command: $commandName"
        }
    }
    foreach ($marker in @(
            'System.Diagnostics.Process', 'Microsoft.Win32.Registry',
            'OpenProcess(', 'ReadProcessMemory', 'WriteProcessMemory',
            'VirtualAllocEx', 'CreateRemoteThread', 'LoadLibrary('
        )) {
        if ($installerText.IndexOf($marker, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
            throw "Generated installer contains a forbidden runtime-access marker: $marker"
        }
    }
    [System.IO.File]::WriteAllText((Join-Path $staging 'tools\Invoke-OfficerNamesFileOnlyPatch.ps1'), $installerText, $Utf8NoBom)

    foreach ($name in @('APPLY_KOREAN_PATCH.bat', 'RESTORE_ORIGINALS.bat', 'VERIFY_PACKAGE.bat', 'FILE_ONLY_POLICY_KO.md')) {
        Copy-Item -LiteralPath (Join-Path $TemplateRoot $name) -Destination (Join-Path $staging $name)
    }
    $readme = [System.IO.File]::ReadAllText((Join-Path $TemplateRoot 'README_KO.md.in'))
    $readme = $readme.Replace('@FONT_TARGET_SHA256@', ([string]$fontLanguage.target_archive.sha256).ToUpperInvariant())
    $readme = $readme.Replace('@FONT_TARGET_SIZE@', [string]$fontLanguage.target_archive.size)
    $readme = $readme.Replace('@PACKAGE_MODE@', $manifestMode)
    if ($readme -match '@[A-Z0-9_]+@') {
        throw "README template contains an unresolved release token: $($Matches[0])"
    }
    [System.IO.File]::WriteAllText((Join-Path $staging 'README_KO.md'), $readme, $Utf8NoBom)

    $packageFiles = @()
    foreach ($file in @(Get-ChildItem -LiteralPath $staging -File -Recurse | Sort-Object FullName)) {
        $relative = $file.FullName.Substring($staging.TrimEnd('\').Length + 1).Replace('\', '/')
        if ($relative -eq 'release_manifest.json') { continue }
        $role = if ($relative.StartsWith('components/message/', [StringComparison]::Ordinal)) { 'message recipe' }
            elseif ($relative.StartsWith('components/font/payload/', [StringComparison]::Ordinal)) { 'generated OFL glyph pixels' }
            elseif ($relative.StartsWith('components/font/metrics/', [StringComparison]::Ordinal)) { 'generated font metrics' }
            elseif ($relative.StartsWith('components/font/licenses/', [StringComparison]::Ordinal)) { 'font license' }
            elseif ($relative -eq 'components/font/recipe.json') { 'font recipe' }
            elseif ($relative.StartsWith('attestations/', [StringComparison]::Ordinal)) { 'promotion attestation' }
            elseif ($relative.StartsWith('tools/', [StringComparison]::Ordinal)) { 'installer source' }
            else { 'documentation or launcher wrapper' }
        if ([System.IO.Path]::GetExtension($relative).ToLowerInvariant() -in @('.exe', '.dll', '.g1n', '.bin')) {
            throw "Forbidden complete/native binary escaped into package: $relative"
        }
        $packageFiles += [ordered]@{
            path = $relative
            size = [int64]$file.Length
            sha256 = Get-Sha256 $file.FullName
            role = $role
        }
    }
    if ($packageFiles.Count -ne $packageFileCount) {
        throw "Staged $manifestMode package has $($packageFiles.Count) files; expected exactly $packageFileCount."
    }

    $manifest = [ordered]@{
        schema = 'nobu16.officer-names-release.v1'
        release_id = 'officer-names-v0.1'
        release_name = 'NOBU16 Korean officer names four-resource file-only v0.1'
        version = $manifestVersion
        mode = $manifestMode
        language = 'SC'
        file_only = $true
        source_free = $true
        development_milestone = $developmentMilestone
        release_eligible = $releaseEligible
        backup_directory = 'officer_names_v0_1'
        distribution_assumption = 'storefront-independent; verified copy is non-Steam; detect only by resource tree and pinned hashes'
        launch_working_directory = 'game_root'
        prohibited_access = @('memory', 'process', 'executable', 'registry')
        resources = $resources
        accepted_vectors = $acceptedVectors
        font_artifacts = @($finalPins.font_artifacts)
        validation = $validation
        package_files = $packageFiles
    }
    Write-Json (Join-Path $staging 'release_manifest.json') $manifest 30
    [System.IO.Directory]::Move($staging, $OutputRoot)
    Write-Host "Officer-name release package built: $OutputRoot"
    Write-Host "mode=$manifestMode; release_eligible=$([string]$releaseEligible)"
}
catch {
    if (Test-Path -LiteralPath $staging -PathType Container) {
        $fullStaging = Get-FullPath $staging
        if ($fullStaging.StartsWith((Get-FullPath $ReleasesRoot).TrimEnd('\') + '\.officer_names_v0.1.staging.', [StringComparison]::OrdinalIgnoreCase)) {
            [System.IO.Directory]::Delete($fullStaging, $true)
        }
    }
    throw
}
